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

from data_layer.model import Product, Vat, DepartmentSubGroup, ProductManufacturer, Store, ProductUnit, Warehouse



from core.logger import get_logger

logger = get_logger(__name__)

def _insert_products(session, admin_cashier_id: str):
    """Insert sample products if not exists"""
    product_exists = session.query(Product).first()
    if not product_exists:
        # Get required foreign key references
        vat_0_percent = session.query(Vat).filter_by(no=1).first()  # %0 VAT
        vat_1_percent = session.query(Vat).filter_by(no=2).first()  # %1 VAT
        vat_10_percent = session.query(Vat).filter_by(no=3).first()  # %10 VAT
        vat_20_percent = session.query(Vat).filter_by(no=4).first()  # %20 VAT
        default_manufacturer = session.query(ProductManufacturer).first()
        default_store = session.query(Store).first()
        
        # Get department sub groups
        fresh_food_sub_group = session.query(DepartmentSubGroup).filter_by(code="101").first()
        
        # Get product units
        pc_unit = session.query(ProductUnit).filter_by(code="PCS").first()
        kg_unit = session.query(ProductUnit).filter_by(code="KG").first()
        
        # Get primary warehouse (Sales Floor)
        sales_floor_warehouse = session.query(Warehouse).filter_by(code="SALES-001").first()
        
        if not vat_0_percent or not default_manufacturer or not default_store or not fresh_food_sub_group or not pc_unit or not kg_unit:
            logger.error("⚠ Required references not found. Cannot insert products.")
            return
        
        if not sales_floor_warehouse:
            logger.error("Sales Floor warehouse not found. Products will be created without primary warehouse.")
            # Continue anyway as primary warehouse is optional

        # Sample products based on C# TablePlu data
        products_data = [
            {
                "code": "1",
                "old_code": "1",
                "shelf_code": "",
                "purchase_price": 100.0,
                "sale_price": 110.0,
                "name": "Baguette",
                "short_name": "Baguette",
                "description": "Baguette",
                "description_on_screen": "Baguette",
                "description_on_shelf": "Baguette",
                "description_on_scale": "",
                "is_scalable": False,
                "is_allowed_discount": False,
                "discount_percent": 0,
                "is_allowed_negative_stock": True,
                "is_allowed_return": False,
                "stock": 100,
                "min_stock": 10,
                "max_stock": 100,
                "stock_unit": "PC",
                "unit": pc_unit
            },
            {
                "code": "2",
                "old_code": "2",
                "shelf_code": "",
                "purchase_price": 50.0,
                "sale_price": 55.0,
                "name": "Granny Smith Apple",
                "short_name": "Apple",
                "description": "Granny Smith Apple",
                "description_on_screen": "Granny Smith Apple",
                "description_on_shelf": "Granny Smith Apple",
                "description_on_scale": "Granny Smith Apple",
                "is_scalable": True,
                "is_allowed_discount": False,
                "discount_percent": 0,
                "is_allowed_negative_stock": False,
                "is_allowed_return": True,
                "stock": 100,
                "min_stock": 10,
                "max_stock": 100,
                "stock_unit": "KG",
                "unit": kg_unit
            },
            {
                "code": "3",
                "old_code": "3",
                "shelf_code": "",
                "purchase_price": 90.0,
                "sale_price": 95.0,
                "name": "Cavendish Banana",
                "short_name": "Banana",
                "description": "Cavendish Banana",
                "description_on_screen": "Cavendish Banana",
                "description_on_shelf": "Cavendish Banana",
                "description_on_scale": "Cavendish Banana",
                "is_scalable": True,
                "is_allowed_discount": False,
                "discount_percent": 0,
                "is_allowed_negative_stock": False,
                "is_allowed_return": True,
                "stock": 100,
                "min_stock": 10,
                "max_stock": 100,
                "stock_unit": "KG",
                "unit": kg_unit
            },
            {
                "code": "4",
                "old_code": "4",
                "shelf_code": "",
                "purchase_price": 100.0,
                "sale_price": 110.0,
                "name": "Heinz Tomato Ketchup",
                "short_name": "Heinz Ketchup",
                "description": "Heinz Tomato Ketchup (460g)",
                "description_on_screen": "Heinz Tomato Ketchup (460g)",
                "description_on_shelf": "Heinz Tomato Ketchup (460g)",
                "description_on_scale": "",
                "is_scalable": False,
                "is_allowed_discount": False,
                "discount_percent": 0,
                "is_allowed_negative_stock": True,
                "is_allowed_return": False,
                "stock": 1000,
                "min_stock": 10,
                "max_stock": 1000,
                "stock_unit": "PC",
                "unit": pc_unit
            },
            {
                "code": "5",
                "old_code": "5",
                "shelf_code": "",
                "purchase_price": 100.0,
                "sale_price": 110.0,
                "name": "Cadbury Dairy Milk Chocolate Bar",
                "short_name": "Chocolate Bar",
                "description": "Cadbury Dairy Milk Chocolate Bar (110g)",
                "description_on_screen": "Cadbury Dairy Milk Chocolate Bar (110g)",
                "description_on_shelf": "Cadbury Dairy Milk Chocolate Bar (110g)",
                "description_on_scale": "",
                "is_scalable": False,
                "is_allowed_discount": False,
                "discount_percent": 0,
                "is_allowed_negative_stock": True,
                "is_allowed_return": False,
                "stock": 1000,
                "min_stock": 10,
                "max_stock": 1000,
                "stock_unit": "PC",
                "unit": pc_unit
            },
            {
                "code": "6",
                "old_code": "6",
                "shelf_code": "",
                "purchase_price": 100.0,
                "sale_price": 110.0,
                "name": "Walkers Ready Salted Crisps",
                "short_name": "Walkers Crisps",
                "description": "Walkers Ready Salted Crisps (25g x 6 pack)",
                "description_on_screen": "Walkers Ready Salted Crisps (25g x 6 pack)",
                "description_on_shelf": "Walkers Ready Salted Crisps (25g x 6 pack)",
                "description_on_scale": "",
                "is_scalable": False,
                "is_allowed_discount": False,
                "discount_percent": 0,
                "is_allowed_negative_stock": True,
                "is_allowed_return": False,
                "stock": 1000,
                "min_stock": 10,
                "max_stock": 1000,
                "stock_unit": "PC",
                "unit": pc_unit
            },
            {
                "code": "7",
                "old_code": "7",
                "shelf_code": "",
                "purchase_price": 100.0,
                "sale_price": 110.0,
                "name": "PG Tips Tea Bags",
                "short_name": "PG Tea Bags",
                "description": "PG Tips Tea Bags (80 Bags)",
                "description_on_screen": "PG Tips Tea Bags (80 Bags)",
                "description_on_shelf": "PG Tips Tea Bags (80 Bags)",
                "description_on_scale": "",
                "is_scalable": False,
                "is_allowed_discount": False,
                "discount_percent": 0,
                "is_allowed_negative_stock": True,
                "is_allowed_return": False,
                "stock": 1000,
                "min_stock": 10,
                "max_stock": 1000,
                "stock_unit": "PC",
                "unit": pc_unit
            },
            {
                "code": "8",
                "old_code": "8",
                "shelf_code": "",
                "purchase_price": 100.0,
                "sale_price": 110.0,
                "name": "Coca-Cola Original Taste",
                "short_name": "Coca-Cola",
                "description": "Coca-Cola Original Taste (1.5L Bottle)",
                "description_on_screen": "Coca-Cola Original Taste (1.5L Bottle)",
                "description_on_shelf": "Coca-Cola Original Taste (1.5L Bottle)",
                "description_on_scale": "",
                "is_scalable": False,
                "is_allowed_discount": False,
                "discount_percent": 0,
                "is_allowed_negative_stock": True,
                "is_allowed_return": False,
                "stock": 1000,
                "min_stock": 10,
                "max_stock": 1000,
                "stock_unit": "PC",
                "unit": pc_unit
            },
            {
                "code": "9",
                "old_code": "9",
                "shelf_code": "",
                "purchase_price": 100.0,
                "sale_price": 110.0,
                "name": "Beard Butter Original",
                "short_name": "Beard Butter",
                "description": "Beard Butter Original Formula",
                "description_on_screen": "Beard Butter Original Formula",
                "description_on_shelf": "Beard Butter Original Formula",
                "description_on_scale": "",
                "is_scalable": False,
                "is_allowed_discount": False,
                "discount_percent": 0,
                "is_allowed_negative_stock": True,
                "is_allowed_return": False,
                "stock": 1000,
                "min_stock": 10,
                "max_stock": 1000,
                "stock_unit": "PC",
                "unit": pc_unit
            },
            {
                "code": "10",
                "old_code": "10",
                "shelf_code": "",
                "purchase_price": 100.0,
                "sale_price": 110.0,
                "name": "Cadbury Dairy Milk Chocolate",
                "short_name": "Milk Chocolate",
                "description": "Cadbury Dairy Milk Chocolate 180g",
                "description_on_screen": "Cadbury Dairy Milk Chocolate 180g",
                "description_on_shelf": "Cadbury Dairy Milk Chocolate 180g",
                "description_on_scale": "",
                "is_scalable": False,
                "is_allowed_discount": False,
                "discount_percent": 0,
                "is_allowed_negative_stock": True,
                "is_allowed_return": False,
                "stock": 1000,
                "min_stock": 10,
                "max_stock": 1000,
                "stock_unit": "PC",
                "unit": pc_unit
            },
            {
                "code": "11",
                "old_code": "11",
                "shelf_code": "",
                "purchase_price": 100.0,
                "sale_price": 110.0,
                "name": "Walkers Ready Salted Crisps",
                "short_name": "Salted Crisps",
                "description": "Walkers Ready Salted Crisps 6 Pack",
                "description_on_screen": "Walkers Ready Salted Crisps 6 Pack",
                "description_on_shelf": "Walkers Ready Salted Crisps 6 Pack",
                "description_on_scale": "",
                "is_scalable": False,
                "is_allowed_discount": False,
                "discount_percent": 0,
                "is_allowed_negative_stock": True,
                "is_allowed_return": False,
                "stock": 1000,
                "min_stock": 10,
                "max_stock": 1000,
                "stock_unit": "PC",
                "unit": pc_unit
            },
            {
                "code": "12",
                "old_code": "12",
                "shelf_code": "",
                "purchase_price": 100.0,
                "sale_price": 110.0,
                "name": "Heinz Baked Beans",
                "short_name": "Baked Beans",
                "description": "Heinz Baked Beans 415g",
                "description_on_screen": "Heinz Baked Beans 415g",
                "description_on_shelf": "Heinz Baked Beans 415g",
                "description_on_scale": "",
                "is_scalable": False,
                "is_allowed_discount": False,
                "discount_percent": 0,
                "is_allowed_negative_stock": True,
                "is_allowed_return": False,
                "stock": 1000,
                "min_stock": 10,
                "max_stock": 1000,
                "stock_unit": "PC",
                "unit": pc_unit
            },
            {
                "code": "13",
                "old_code": "13",
                "shelf_code": "",
                "purchase_price": 100.0,
                "sale_price": 110.0,
                "name": "Warburtons Sliced White Bread",
                "short_name": "Sliced White Bread",
                "description": "Warburtons Medium Sliced White Bread 800g",
                "description_on_screen": "Warburtons Medium Sliced White Bread 800g",
                "description_on_shelf": "Warburtons Medium Sliced White Bread 800g",
                "description_on_scale": "",
                "is_scalable": False,
                "is_allowed_discount": False,
                "discount_percent": 0,
                "is_allowed_negative_stock": True,
                "is_allowed_return": False,
                "stock": 1000,
                "min_stock": 10,
                "max_stock": 1000,
                "stock_unit": "PC",
                "unit": pc_unit
            },
            {
                "code": "14",
                "old_code": "14",
                "shelf_code": "",
                "purchase_price": 100.0,
                "sale_price": 110.0,
                "name": "Lurpak Butter Spreadable",
                "short_name": "Butter Spreadable",
                "description": "Lurpak Butter Spreadable 500g",
                "description_on_screen": "Lurpak Butter Spreadable 500g",
                "description_on_shelf": "Lurpak Butter Spreadable 500g",
                "description_on_scale": "",
                "is_scalable": False,
                "is_allowed_discount": False,
                "discount_percent": 0,
                "is_allowed_negative_stock": True,
                "is_allowed_return": False,
                "stock": 1000,
                "min_stock": 10,
                "max_stock": 1000,
                "stock_unit": "PC",
                "unit": pc_unit
            },
            {
                "code": "15",
                "old_code": "15",
                "shelf_code": "",
                "purchase_price": 100.0,
                "sale_price": 110.0,
                "name": "Ariel Washing Powder",
                "short_name": "Washing Powder",
                "description": "Ariel Washing Powder 40 Washes",
                "description_on_screen": "Ariel Washing Powder 40 Washes",
                "description_on_shelf": "Ariel Washing Powder 40 Washes",
                "description_on_scale": "",
                "is_scalable": False,
                "is_allowed_discount": False,
                "discount_percent": 0,
                "is_allowed_negative_stock": True,
                "is_allowed_return": False,
                "stock": 1000,
                "min_stock": 10,
                "max_stock": 1000,
                "stock_unit": "PC",
                "unit": pc_unit
            },
            {
                "code": "16",
                "old_code": "16",
                "shelf_code": "",
                "purchase_price": 100.0,
                "sale_price": 110.0,
                "name": "Domestos Thick Bleach",
                "short_name": "Thick Bleach",
                "description": "Domestos Thick Bleach 750ml",
                "description_on_screen": "Domestos Thick Bleach 750ml",
                "description_on_shelf": "Domestos Thick Bleach 750ml",
                "description_on_scale": "",
                "is_scalable": False,
                "is_allowed_discount": False,
                "discount_percent": 0,
                "is_allowed_negative_stock": True,
                "is_allowed_return": False,
                "stock": 1000,
                "min_stock": 10,
                "max_stock": 1000,
                "stock_unit": "PC",
                "unit": pc_unit
            },
            {
                "code": "17",
                "old_code": "17",
                "shelf_code": "",
                "purchase_price": 100.0,
                "sale_price": 110.0,
                "name": "Tropicana Orange Juice",
                "short_name": "Orange Juice",
                "description": "Tropicana Smooth Orange Juice 1L",
                "description_on_screen": "Tropicana Smooth Orange Juice 1L",
                "description_on_shelf": "Tropicana Smooth Orange Juice 1L",
                "description_on_scale": "",
                "is_scalable": False,
                "is_allowed_discount": False,
                "discount_percent": 0,
                "is_allowed_negative_stock": True,
                "is_allowed_return": False,
                "stock": 1000,
                "min_stock": 10,
                "max_stock": 1000,
                "stock_unit": "PC",
                "unit": pc_unit
            }
        ]

        # Create products
        for product_data in products_data:
            product = Product(
                name=product_data["name"],
                short_name=product_data["short_name"],
                code=product_data["code"],
                old_code=product_data["old_code"],
                shelf_code=product_data["shelf_code"]
            )
            
            # Set all other properties
            product.purchase_price = product_data["purchase_price"]
            product.sale_price = product_data["sale_price"]
            product.description = product_data["description"]
            product.description_on_screen = product_data["description_on_screen"]
            product.description_on_shelf = product_data["description_on_shelf"]
            product.description_on_scale = product_data["description_on_scale"]
            product.is_scalable = product_data["is_scalable"]
            product.is_allowed_discount = product_data["is_allowed_discount"]
            product.discount_percent = product_data["discount_percent"]
            product.is_allowed_negative_stock = product_data["is_allowed_negative_stock"]
            product.is_allowed_return = product_data["is_allowed_return"]
            product.stock = product_data["stock"]
            product.min_stock = product_data["min_stock"]
            product.max_stock = product_data["max_stock"]
            product.stock_unit = product_data["stock_unit"]
            product.stock_unit_no = 1
            product.vat_no = 1
            
            # Set foreign keys
            product.fk_vat_id = vat_0_percent.id
            product.fk_product_unit_id = product_data["unit"].id
            product.fk_department_main_group_id = fresh_food_sub_group.main_group_id
            product.fk_department_sub_group_id = fresh_food_sub_group.id
            product.fk_manufacturer_id = default_manufacturer.id
            product.fk_store_id = default_store.id
            product.fk_cashier_create_id = admin_cashier_id
            product.fk_cashier_update_id = admin_cashier_id
            
            # Set primary warehouse (Sales Floor)
            if sales_floor_warehouse:
                product.fk_primary_warehouse_id = sales_floor_warehouse.id
            
            session.add(product)

        logger.info("✓ Inserted %s sample products", len(products_data)) 