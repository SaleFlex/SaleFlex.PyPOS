"""
SaleFlex.PyPOS - Database Utils

Copyright (c) 2025 Ferhat Mousavi (ferhat.mousavi@gmail.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from data_layer.engine import Engine
from data_layer.db_initializer import drop_tables, create_tables
from data_layer.db_init_data import insert_initial_data
from sqlalchemy.exc import SQLAlchemyError


def check_db_connection():
    """
    Tests database connection
    """
    try:
        temp_engine = Engine()
        with temp_engine.get_session() as session:
            # Execute simple query
            session.execute("SELECT 1")
            print("✓ Database connection successful")
            return True
    except Exception as e:
        print(f"✗ Database connection error: {e}")
        return False


def reset_db():
    """
    Completely resets database (WARNING: All data will be deleted!)
    """
    try:
        print("⚠️  Resetting database... (All data will be deleted)")
        
        # Drop tables
        if not drop_tables():
            return False
        
        # Recreate tables
        if not create_tables():
            return False
        
        # Insert initial data
        temp_engine = Engine()
        insert_initial_data(temp_engine)
        print("✓ Initial data added")
        
        return True
        
    except SQLAlchemyError as e:
        print(f"✗ Database reset error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def backup_db(backup_file_path: str):
    """
    Creates a backup of the database
    
    Args:
        backup_file_path (str): Path to save backup file
    """
    try:
        # TODO: Implement database backup functionality
        # This could use SQLAlchemy's reflection to dump schema and data
        print(f"⚠️  Backup functionality not implemented yet")
        print(f"   Backup would be saved to: {backup_file_path}")
        return False
        
    except Exception as e:
        print(f"✗ Database backup error: {e}")
        return False


def restore_db(backup_file_path: str):
    """
    Restores database from backup
    
    Args:
        backup_file_path (str): Path to backup file
    """
    try:
        # TODO: Implement database restore functionality
        print(f"⚠️  Restore functionality not implemented yet")
        print(f"   Would restore from: {backup_file_path}")
        return False
        
    except Exception as e:
        print(f"✗ Database restore error: {e}")
        return False


def get_db_info():
    """
    Returns basic database information
    """
    try:
        temp_engine = Engine()
        with temp_engine.get_session() as session:
            # Get database version/info
            result = session.execute("SELECT 1")
            
            info = {
                "connection_status": "Connected",
                "database_url": str(temp_engine.engine.url),
                "dialect": temp_engine.engine.dialect.name,
                "driver": temp_engine.engine.dialect.driver
            }
            
            return info
            
    except Exception as e:
        return {
            "connection_status": "Failed",
            "error": str(e)
        }


def vacuum_db():
    """
    Performs database maintenance (VACUUM for SQLite)
    """
    try:
        temp_engine = Engine()
        
        # Check if it's SQLite
        if temp_engine.engine.dialect.name == 'sqlite':
            with temp_engine.get_session() as session:
                session.execute("VACUUM")
                session.commit()
                print("✓ Database vacuumed successfully")
                return True
        else:
            print("⚠️  VACUUM is only supported for SQLite databases")
            return False
            
    except Exception as e:
        print(f"✗ Database vacuum error: {e}")
        return False 