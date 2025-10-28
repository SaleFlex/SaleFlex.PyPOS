"""
SaleFlex.PyPOS - Database Initializer

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

from data_layer.model import metadata
from data_layer.engine import Engine
from data_layer.db_init_data import insert_initial_data

from sqlalchemy.exc import SQLAlchemyError

# Import KeyboardSettingsLoader for initialization
try:
    from user_interface.control.virtual_keyboard.keyboard_settings_loader import KeyboardSettingsLoader
    KEYBOARD_LOADER_AVAILABLE = True
except ImportError:
    KEYBOARD_LOADER_AVAILABLE = False


def init_db():
    """
    Initializes database: creates tables and inserts initial data
    """
    try:
        temp_engine = Engine()
        
        print("Creating database tables...")
        
        # Create tables
        metadata.create_all(bind=temp_engine.engine)
        print("✓ Tables created successfully")
        
        # Insert initial data
        insert_initial_data(temp_engine)
        print("✓ Initial data inserted successfully")
        
        # Initialize keyboard settings loader
        if KEYBOARD_LOADER_AVAILABLE:
            KeyboardSettingsLoader.initialize(temp_engine)
            print("✓ Virtual keyboard settings loaded")
        
        return True
        
    except SQLAlchemyError as e:
        print(f"✗ Database initialization error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def create_tables():
    """
    Creates database tables only (without initial data)
    """
    try:
        temp_engine = Engine()
        
        print("Creating database tables...")
        metadata.create_all(bind=temp_engine.engine)
        print("✓ Tables created successfully")
        
        return True
        
    except SQLAlchemyError as e:
        print(f"✗ Table creation error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def drop_tables():
    """
    Drops all database tables
    """
    try:
        temp_engine = Engine()
        
        print("Dropping database tables...")
        metadata.drop_all(bind=temp_engine.engine)
        print("✓ Tables dropped successfully")
        
        return True
        
    except SQLAlchemyError as e:
        print(f"✗ Table drop error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False 