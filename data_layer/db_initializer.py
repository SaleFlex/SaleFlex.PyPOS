"""
SaleFlex.PyPOS - Database Initializer

Copyright (c) 2025 Ferhat Mousavi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
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