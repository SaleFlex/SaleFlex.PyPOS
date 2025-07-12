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
from data_layer.model import TransactionDocumentType

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
            
            # Add default transaction document types (if not exists)
            doc_type_exists = session.query(TransactionDocumentType).first()
            if not doc_type_exists:
                document_types = [
                    {"no": 1, "name": "FISCAL_RECEIPT", "display_name": "Receipt", "description": "Fiscal Receipt"},
                    {"no": 2, "name": "NONE_FISCAL_RECEIPT", "display_name": "Receipt", "description": "Non Fiscal Receipt"},
                    {"no": 3, "name": "NONE_FISCAL_INVOICE", "display_name": "Invoice", "description": "Printed Invoice"},
                    {"no": 4, "name": "NONE_FISCAL_E_INVOICE", "display_name": "E Invoice", "description": "Electronic Invoice"},
                    {"no": 5, "name": "NONE_FISCAL_E_ARCHIVE_INVOICE", "display_name": "E Archive Invoice", "description": "Electronic Archive Invoice"},
                    {"no": 6, "name": "NONE_FISCAL_DIPLOMATIC_RECEIPT", "display_name": "Diplomatic Invoice", "description": "Diplomatic Invoice"},
                    {"no": 7, "name": "NONE_FISCAL_WAYBILL", "display_name": "Waybill", "description": "Waybill"},
                    {"no": 8, "name": "NONE_FISCAL_DELIVERY_NOTE", "display_name": "Delivery Note", "description": "Delivery Note"},
                    {"no": 9, "name": "NONE_FISCAL_CASH_OUT_FLOW", "display_name": "Cash Out flow", "description": "Cash Out flow"},
                    {"no": 10, "name": "NONE_FISCAL_CASH_IN_FLOW", "display_name": "Cash In flow", "description": "Cash In flow"},
                    {"no": 11, "name": "NONE_FISCAL_RETURN", "display_name": "Return", "description": "Return"},
                    {"no": 12, "name": "NONE_FISCAL_SELF_BILLING_INVOICE", "display_name": "Self Billing Invoice", "description": "Self Billing Invoice"}
                ]
                
                for doc_type_data in document_types:
                    doc_type = TransactionDocumentType(
                        no=doc_type_data["no"],
                        name=doc_type_data["name"],
                        display_name=doc_type_data["display_name"],
                        description=doc_type_data["description"]
                    )
                    session.add(doc_type)
                print("✓ Default transaction document types added")
    
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