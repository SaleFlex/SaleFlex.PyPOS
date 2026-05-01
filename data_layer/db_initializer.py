"""
SaleFlex.PyPOS - Database Initializer
Copyright (C) 2025-2026 Mousavi.Tech

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os

from data_layer.model import metadata
from data_layer.engine import Engine
from data_layer.db_init_data import insert_initial_data

from sqlalchemy.exc import SQLAlchemyError

from core.logger import get_logger
from settings import env_data

logger = get_logger(__name__)
try:
    from user_interface.control.virtual_keyboard.keyboard_settings_loader import KeyboardSettingsLoader
    KEYBOARD_LOADER_AVAILABLE = True
except ImportError:
    KEYBOARD_LOADER_AVAILABLE = False


def _ensure_office_push_queue_schema(temp_engine: Engine) -> None:
    """
    Ensure the office_push_queue table exists with all required columns.

    metadata.create_all() creates the table for new databases; this function
    handles existing databases where the table may not yet exist.
    """
    with temp_engine.engine.begin() as connection:
        tables = {
            row[0]
            for row in connection.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        if "office_push_queue" not in tables:
            # Table absent (old database) – let create_all handle it, or create minimal version.
            connection.exec_driver_sql(
                """
                CREATE TABLE IF NOT EXISTS office_push_queue (
                    id TEXT PRIMARY KEY,
                    fk_transaction_head_id TEXT NOT NULL,
                    transaction_unique_id TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    retry_count INTEGER NOT NULL DEFAULT 0,
                    sent_at DATETIME,
                    last_attempt_at DATETIME,
                    error_message TEXT,
                    created_at DATETIME,
                    updated_at DATETIME,
                    created_by TEXT,
                    updated_by TEXT,
                    is_deleted BOOLEAN NOT NULL DEFAULT 0
                )
                """
            )

        if "office_closure_push_queue" not in tables:
            connection.exec_driver_sql(
                """
                CREATE TABLE IF NOT EXISTS office_closure_push_queue (
                    id TEXT PRIMARY KEY,
                    fk_closure_id TEXT NOT NULL,
                    closure_unique_id TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    retry_count INTEGER NOT NULL DEFAULT 0,
                    sent_at DATETIME,
                    last_attempt_at DATETIME,
                    error_message TEXT,
                    created_at DATETIME,
                    updated_at DATETIME,
                    created_by TEXT,
                    updated_by TEXT,
                    is_deleted BOOLEAN NOT NULL DEFAULT 0
                )
                """
            )
            connection.exec_driver_sql(
                "CREATE INDEX IF NOT EXISTS idx_office_closure_push_status "
                "ON office_closure_push_queue (status)"
            )
            connection.exec_driver_sql(
                "CREATE INDEX IF NOT EXISTS idx_office_closure_push_closure "
                "ON office_closure_push_queue (fk_closure_id)"
            )


def _ensure_cashier_schema(temp_engine: Engine) -> None:
    """Apply lightweight cashier table migrations required by current models."""
    with temp_engine.engine.begin() as connection:
        columns = {
            row[1]
            for row in connection.exec_driver_sql("PRAGMA table_info(cashier)").fetchall()
        }
        if columns and "is_manager" not in columns:
            connection.exec_driver_sql(
                "ALTER TABLE cashier ADD COLUMN is_manager BOOLEAN NOT NULL DEFAULT 0"
            )


def _is_new_database() -> bool:
    """
    Return True when the configured SQLite database file does not yet exist.

    This is used to decide whether to run the standard seed or to pull data
    from SaleFlex.OFFICE (when app mode == 'office').
    """
    db_name = env_data.db_name
    if not db_name:
        return True
    return not os.path.exists(db_name)


def _seed_from_office(temp_engine: Engine) -> bool:
    """
    Connect to SaleFlex.OFFICE and populate the local database with the
    initialisation data returned by the OFFICE REST API.

    Returns True on success, False on any error.
    """
    from integration.office_client import (
        OfficeClient,
        OfficeConnectionError,
        OfficeAuthError,
    )
    from data_layer.office_seeder import seed_from_office_data

    try:
        client = OfficeClient()

        logger.info("Checking connectivity to SaleFlex.OFFICE...")
        if not client.check_health():
            logger.error(
                "✗ SaleFlex.OFFICE is unreachable. "
                "Ensure the OFFICE application is running and [office].base_url "
                "in settings.toml is correct."
            )
            return False

        logger.info("Fetching initialization data from SaleFlex.OFFICE...")
        init_data = client.fetch_init_data()

        logger.info("Populating local database from OFFICE data...")
        seed_from_office_data(temp_engine, init_data)
        return True

    except OfficeConnectionError as exc:
        logger.error("✗ Cannot reach SaleFlex.OFFICE: %s", exc)
        return False
    except OfficeAuthError as exc:
        logger.error(
            "✗ OFFICE rejected terminal credentials: %s. "
            "Check office_code, store_code and terminal_code in settings.toml.",
            exc,
        )
        return False
    except Exception as exc:
        logger.error("✗ Unexpected error during OFFICE seeding: %s", exc, exc_info=True)
        return False


def init_db():
    """
    Initialize the database: create tables and populate initial data.

    Behavior depends on app mode and whether the database already exists:

    * Existing database  → create any missing tables (idempotent) and run
      lightweight schema migrations.  No data seeding is performed.
    * New database + mode == 'office'  → create tables, then pull all seed
      data from SaleFlex.OFFICE via the REST API.
    * New database + other modes  → create tables, then insert built-in
      default seed data.
    """
    try:
        is_new_db = _is_new_database()
        temp_engine = Engine()

        logger.debug("Creating database tables...")
        metadata.create_all(bind=temp_engine.engine)
        _ensure_cashier_schema(temp_engine)
        _ensure_office_push_queue_schema(temp_engine)
        logger.info("✓ Tables created successfully")

        if is_new_db:
            app_mode = env_data.app_mode
            if app_mode == "office":
                logger.info(
                    "New database detected – mode is 'office'. "
                    "Seeding from SaleFlex.OFFICE..."
                )
                success = _seed_from_office(temp_engine)
                if not success:
                    logger.error(
                        "✗ OFFICE seeding failed. "
                        "Cannot start in 'office' mode without a connection to SaleFlex.OFFICE. "
                        "Ensure the OFFICE application is running and [office].base_url in settings.toml is correct."
                    )
                    temp_engine.engine.dispose()
                    db_name = env_data.db_name
                    if db_name and os.path.exists(db_name):
                        os.remove(db_name)
                        logger.info("Removed incomplete database file so the next start retries seeding.")
                    return False
            else:
                insert_initial_data(temp_engine)
            logger.info("✓ Initial data inserted successfully")
        else:
            logger.debug("Existing database detected – skipping seed phase.")

        if KEYBOARD_LOADER_AVAILABLE:
            KeyboardSettingsLoader.initialize(temp_engine)
            logger.info("✓ Virtual keyboard settings loaded")

        return True

    except SQLAlchemyError as e:
        logger.error("✗ Database initialization error: %s", e)
        return False
    except Exception as e:
        logger.error("✗ Unexpected error: %s", e)
        return False


def create_tables():
    """
    Creates database tables only (without initial data)
    """
    try:
        temp_engine = Engine()
        
        logger.debug("Creating database tables...")
        metadata.create_all(bind=temp_engine.engine)
        _ensure_cashier_schema(temp_engine)
        _ensure_office_push_queue_schema(temp_engine)
        logger.info("✓ Tables created successfully")
        
        return True
        
    except SQLAlchemyError as e:
        logger.error("✗ Table creation error: %s", e)
        return False
    except Exception as e:
        logger.error("✗ Unexpected error: %s", e)
        return False


def drop_tables():
    """
    Drops all database tables
    """
    try:
        temp_engine = Engine()
        
        logger.debug("Dropping database tables...")
        metadata.drop_all(bind=temp_engine.engine)
        logger.info("✓ Tables dropped successfully")
        
        return True
        
    except SQLAlchemyError as e:
        logger.error("✗ Table drop error: %s", e)
        return False
    except Exception as e:
        logger.error("✗ Unexpected error: %s", e)
        return False 