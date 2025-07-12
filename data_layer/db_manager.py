"""
SaleFlex.PyPOS - Database Manager

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

from data_layer.model import Cashier
from data_layer.model import Customer
from data_layer.model import Store
from data_layer.model import Vat
from data_layer.model import ProductUnit
from data_layer.model import DepartmentMainGroup
from data_layer.model import DepartmentSubGroup

from sqlalchemy.exc import SQLAlchemyError


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
        _insert_initial_data(temp_engine)
        print("✓ Initial data inserted successfully")
        
        return True
        
    except SQLAlchemyError as e:
        print(f"✗ Database initialization error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def _insert_initial_data(engine: Engine):
    """
    Inserts initial data (only if tables are empty)
    """
    try:
        with engine.get_session() as session:
            
            # Add admin user (if not exists)
            admin_exists = session.query(Cashier).filter_by(user_name="admin").first()
            if not admin_exists:
                admin_cashier = Cashier(
                    user_name="admin",
                    name="System",
                    last_name="Administrator", 
                    password="admin",  # Should be hashed in real application
                    identity_number="00000000000",
                    description="System administrator",
                    is_administrator=True,
                    is_active=True
                )
                session.add(admin_cashier)
                print("✓ Admin user added")
            
            # Add default store (if not exists)
            store_exists = session.query(Store).first()
            if not store_exists:
                default_store = Store(
                    name="Main Store",
                    brand_name="SaleFlex",
                    company_name="SaleFlex PyPOS",
                    web_page_url="https://saleflex.com",
                    description="Default store"
                )
                session.add(default_store)
                print("✓ Default store added")
            
            # Add default VAT rates (if not exists)
            vat_exists = session.query(Vat).first()
            if not vat_exists:
                vat_rates = [
                    {"name": "VAT Free", "no": 0, "rate": 0, "description": "VAT Free"},
                    {"name": "VAT 1%", "no": 1, "rate": 1, "description": "1% VAT"},
                    {"name": "VAT 8%", "no": 2, "rate": 8, "description": "8% VAT"},
                    {"name": "VAT 18%", "no": 3, "rate": 18, "description": "18% VAT"},
                    {"name": "VAT 20%", "no": 4, "rate": 20, "description": "20% VAT"}
                ]
                
                for vat_data in vat_rates:
                    vat = Vat(
                        name=vat_data["name"],
                        no=vat_data["no"],
                        rate=vat_data["rate"],
                        description=vat_data["description"]
                    )
                    session.add(vat)
                print("✓ Default VAT rates added")
            
            # Add default product units (if not exists)
            unit_exists = session.query(ProductUnit).first()
            if not unit_exists:
                units = [
                    {"code": "PCS", "name": "Pieces", "description": "Pieces unit"},
                    {"code": "KG", "name": "Kilogram", "description": "Kilogram unit"},
                    {"code": "GR", "name": "Gram", "description": "Gram unit"},
                    {"code": "LT", "name": "Liter", "description": "Liter unit"},
                    {"code": "M", "name": "Meter", "description": "Meter unit"},
                    {"code": "M2", "name": "Square Meter", "description": "Square meter unit"},
                    {"code": "PKT", "name": "Package", "description": "Package unit"}
                ]
                
                for unit_data in units:
                    unit = ProductUnit(
                        code=unit_data["code"],
                        name=unit_data["name"],
                        description=unit_data["description"]
                    )
                    session.add(unit)
                print("✓ Default product units added")
            
            # Add default main group (if not exists)
            main_group_exists = session.query(DepartmentMainGroup).first()
            if not main_group_exists:
                main_group = DepartmentMainGroup(
                    code="001",
                    name="General",
                    description="General product group"
                )
                session.add(main_group)
                session.flush()  # To get the ID
                print("✓ Default main group added")
                
                # Add default sub group
                sub_group = DepartmentSubGroup(
                    main_group_id=main_group.id,
                    code="001",
                    name="General",
                    description="General product sub group"
                )
                session.add(sub_group)
                print("✓ Default sub group added")
    
    except SQLAlchemyError as e:
        print(f"✗ Initial data insertion error: {e}")
        raise
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        raise


def reset_db():
    """
    Completely resets database (WARNING: All data will be deleted!)
    """
    try:
        temp_engine = Engine()
        
        print("⚠️  Resetting database... (All data will be deleted)")
        
        # Drop tables
        metadata.drop_all(bind=temp_engine.engine)
        print("✓ Tables dropped")
        
        # Recreate tables
        metadata.create_all(bind=temp_engine.engine)
        print("✓ Tables recreated")
        
        # Insert initial data
        _insert_initial_data(temp_engine)
        print("✓ Initial data added")
        
        return True
        
    except SQLAlchemyError as e:
        print(f"✗ Database reset error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


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