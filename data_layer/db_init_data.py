"""
SaleFlex.PyPOS - Database Initial Data

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

from data_layer.model import (
    Cashier, Customer, Store, Vat, ProductUnit, ProductManufacturer,
    DepartmentMainGroup, DepartmentSubGroup, TransactionDocumentType,
    TransactionSequence
)
from data_layer.engine import Engine
from sqlalchemy.exc import SQLAlchemyError


def insert_initial_data(engine: Engine):
    """
    Inserts initial data (only if tables are empty)
    """
    try:
        with engine.get_session() as session:
            # Insert admin cashier
            admin_cashier = _insert_admin_cashier(session)
            
            # Insert default store
            _insert_default_store(session)
            
            # Insert VAT rates
            _insert_vat_rates(session, admin_cashier.id)
            
            # Insert product units
            _insert_product_units(session, admin_cashier.id)
            
            # Insert product manufacturers
            _insert_product_manufacturers(session)
            
            # Insert department groups
            _insert_department_groups(session, admin_cashier.id)
            
            # Insert transaction document types
            _insert_transaction_document_types(session)
            
            # Insert transaction sequences
            _insert_transaction_sequences(session, admin_cashier.id)
    
    except SQLAlchemyError as e:
        print(f"✗ Initial data insertion error: {e}")
        raise
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        raise


def _insert_admin_cashier(session) -> Cashier:
    """Insert admin user if not exists"""
    admin_exists = session.query(Cashier).filter_by(user_name="admin").first()
    if not admin_exists:
        admin_cashier = Cashier(
            no=1,
            user_name="admin",
            name="Ferhat", 
            last_name="Mousavi",
            password="admin",  # TODO: Should be hashed in real application
            identity_number="A00001",
            description="System administrator",
            is_administrator=True,
            is_active=True
        )
        session.add(admin_cashier)
        session.flush()  # To get the ID
        print("✓ Admin user added")
        return admin_cashier
    else:
        return admin_exists


def _insert_default_store(session):
    """Insert default store if not exists"""
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


def _insert_vat_rates(session, admin_cashier_id: int):
    """Insert default VAT rates if not exists"""
    vat_exists = session.query(Vat).first()
    if not vat_exists:
        vat_rates = [
            {"name": "%0", "no": 1, "rate": 0, "description": "Zero VAT Rate (0%)"},
            {"name": "%5", "no": 2, "rate": 5, "description": "Reduced VAT Rate (5%)"},
            {"name": "%20", "no": 3, "rate": 20, "description": "Standard VAT Rate (20%)"}
        ]
        
        for vat_data in vat_rates:
            vat = Vat(
                name=vat_data["name"],
                no=vat_data["no"],
                rate=vat_data["rate"],
                description=vat_data["description"]
            )
            vat.fk_cashier_create_id = admin_cashier_id
            vat.fk_cashier_update_id = admin_cashier_id
            session.add(vat)
        print("✓ Default VAT rates added")


def _insert_product_units(session, admin_cashier_id: int):
    """Insert default product units if not exists"""
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
            unit.fk_cashier_create_id = admin_cashier_id
            unit.fk_cashier_update_id = admin_cashier_id
            session.add(unit)
        print("✓ Default product units added")


def _insert_product_manufacturers(session):
    """Insert default product manufacturers if not exists"""
    manufacturer_exists = session.query(ProductManufacturer).first()
    if not manufacturer_exists:
        default_manufacturer = ProductManufacturer(
            name="General Manufacturer",
            description="Default manufacturer for products without specific manufacturer"
        )
        session.add(default_manufacturer)
        print("✓ Default product manufacturer added")


def _insert_department_groups(session, admin_cashier_id: int):
    """Insert default department groups if not exists"""
    main_group_exists = session.query(DepartmentMainGroup).first()
    if not main_group_exists:
        # First get VAT IDs by their no values
        vat_0_percent = session.query(Vat).filter_by(no=1).first()  # %0 VAT
        vat_20_percent = session.query(Vat).filter_by(no=3).first()  # %20 VAT
        
        main_groups = [
            {
                "code": "1",
                "name": "FOOD",
                "description": "Food products department",
                "max_price": 100.0,
                "vat_id": vat_0_percent.id if vat_0_percent else None
            },
            {
                "code": "2", 
                "name": "TOBACCO",
                "description": "Tobacco products department",
                "max_price": 200.0,
                "vat_id": vat_20_percent.id if vat_20_percent else None
            },
            {
                "code": "3",
                "name": "INDIVIDUAL",
                "description": "Individual products department", 
                "max_price": 300.0,
                "vat_id": vat_20_percent.id if vat_20_percent else None
            }
        ]
        
        # Create main groups and store them for sub group creation
        created_main_groups = []
        for group_data in main_groups:
            main_group = DepartmentMainGroup(
                code=group_data["code"],
                name=group_data["name"],
                description=group_data["description"]
            )
            main_group.max_price = group_data["max_price"]
            main_group.fk_vat_id = group_data["vat_id"]
            main_group.fk_cashier_create_id = admin_cashier_id
            main_group.fk_cashier_update_id = admin_cashier_id
            session.add(main_group)
            session.flush()  # To get the ID
            created_main_groups.append(main_group)
        
        # Create sub groups for each main group
        _insert_department_sub_groups(session, admin_cashier_id, created_main_groups)
        
        print("✓ Default main groups added: FOOD, TOBACCO, INDIVIDUAL")
        print("✓ Default sub groups added")


def _insert_department_sub_groups(session, admin_cashier_id: int, main_groups):
    """Insert default department sub groups"""
    sub_groups_data = [
        # FOOD sub groups
        {"main_group_code": "1", "code": "101", "name": "FRESH FOOD", "description": "Fresh food products"},
        {"main_group_code": "1", "code": "102", "name": "CANNED FOOD", "description": "Canned and preserved food"},
        {"main_group_code": "1", "code": "103", "name": "BEVERAGES", "description": "Drinks and beverages"},
        
        # TOBACCO sub groups
        {"main_group_code": "2", "code": "201", "name": "CIGARETTES", "description": "Cigarette products"},
        {"main_group_code": "2", "code": "202", "name": "TOBACCO PRODUCTS", "description": "Other tobacco products"},
        
        # INDIVIDUAL sub groups
        {"main_group_code": "3", "code": "301", "name": "PERSONAL CARE", "description": "Personal care items"},
        {"main_group_code": "3", "code": "302", "name": "HOUSEHOLD ITEMS", "description": "Household products"},
        {"main_group_code": "3", "code": "303", "name": "ACCESSORIES", "description": "General accessories"}
    ]
    
    for sub_group_data in sub_groups_data:
        # Find the corresponding main group
        main_group = next((mg for mg in main_groups if mg.code == sub_group_data["main_group_code"]), None)
        if main_group:
            sub_group = DepartmentSubGroup(
                main_group_id=main_group.id,
                code=sub_group_data["code"],
                name=sub_group_data["name"],
                description=sub_group_data["description"]
            )
            sub_group.fk_cashier_create_id = admin_cashier_id
            sub_group.fk_cashier_update_id = admin_cashier_id
            session.add(sub_group)


def _insert_transaction_document_types(session):
    """Insert default transaction document types if not exists"""
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


def _insert_transaction_sequences(session, admin_cashier_id: int):
    """Insert default transaction sequences if not exists"""
    sequence_exists = session.query(TransactionSequence).first()
    if not sequence_exists:
        sequences = [
            {"name": "ReceiptNumber", "value": 1, "description": "Receipt sequence number"},
            {"name": "ZNumber", "value": 1, "description": "Z report sequence number"}
        ]
        
        for seq_data in sequences:
            sequence = TransactionSequence(
                name=seq_data["name"],
                value=seq_data["value"],
                description=seq_data["description"]
            )
            sequence.fk_cashier_create_id = admin_cashier_id
            sequence.fk_cashier_update_id = admin_cashier_id
            session.add(sequence)
        print("✓ Default transaction sequences added") 