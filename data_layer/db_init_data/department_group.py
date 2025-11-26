"""
SaleFlex.PyPOS - Database Initial Data

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

from data_layer.model import DepartmentMainGroup, DepartmentSubGroup, Vat


def _insert_department_groups(session, admin_cashier_id: int):
    """Insert default department groups if not exists"""
    main_group_exists = session.query(DepartmentMainGroup).first()
    if not main_group_exists:
        # First get VAT IDs by their no values
        vat_0_percent = session.query(Vat).filter_by(no=1).first()  # %0 VAT
        vat_1_percent = session.query(Vat).filter_by(no=2).first()  # %1 VAT
        vat_10_percent = session.query(Vat).filter_by(no=3).first()  # %10 VAT
        vat_20_percent = session.query(Vat).filter_by(no=4).first()  # %20 VAT

        main_groups = [
            {
                "code": "1",
                "name": "BAKERY",
                "description": "Baked Goods department",
                "max_price": 5.0,
                "vat_id": vat_0_percent.id if vat_0_percent else None
            },
            {
                "code": "1",
                "name": "FOOD",
                "description": "Food products department",
                "max_price": 100.0,
                "vat_id": vat_1_percent.id if vat_1_percent else None
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

        print("✓ Default main groups added: BAKERY, FOOD, TOBACCO, INDIVIDUAL")
        print("✓ Default sub groups added")


def _insert_department_sub_groups(session, admin_cashier_id: int, main_groups):
    """Insert default department sub groups"""
    sub_groups_data = [
        # FOOD sub groups
        {"main_group_code": "2", "code": "101", "name": "FRESH FOOD", "description": "Fresh food products"},
        {"main_group_code": "2", "code": "102", "name": "CANNED FOOD", "description": "Canned and preserved food"},
        {"main_group_code": "2", "code": "103", "name": "BEVERAGES", "description": "Drinks and beverages"},

        # TOBACCO sub groups
        {"main_group_code": "3", "code": "201", "name": "CIGARETTES", "description": "Cigarette products"},
        {"main_group_code": "3", "code": "202", "name": "TOBACCO PRODUCTS", "description": "Other tobacco products"},

        # INDIVIDUAL sub groups
        {"main_group_code": "4", "code": "301", "name": "PERSONAL CARE", "description": "Personal care items"},
        {"main_group_code": "4", "code": "302", "name": "HOUSEHOLD ITEMS", "description": "Household products"},
        {"main_group_code": "4", "code": "303", "name": "ACCESSORIES", "description": "General accessories"}
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