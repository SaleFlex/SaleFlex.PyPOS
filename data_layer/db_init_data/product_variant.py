"""
SaleFlex.PyPOS - Point of Sale Application

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

from uuid import uuid4
from sqlalchemy.orm import Session
from data_layer.model.definition.product_variant import ProductVariant

# Example product variants - these would be linked to actual products
PRODUCT_VARIANTS = [
    # Clothing variants
    {
        "id": str(uuid4()),
        "fk_product_id": None,  # Will be set when products are created
        "variant_name": "Red - Medium",
        "variant_code": "T-SHIRT-RED-M",
        "color": "Red",
        "color_hex": "#FF0000",
        "size": "M",
        "fabric": "Cotton",
        "pattern": "Solid",
        "is_active": True,
        "is_default": True,
        "sort_order": 1,
    },
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "variant_name": "Blue - Large",
        "variant_code": "T-SHIRT-BLUE-L",
        "color": "Blue",
        "color_hex": "#0000FF",
        "size": "L",
        "fabric": "Cotton",
        "pattern": "Solid",
        "is_active": True,
        "is_default": False,
        "sort_order": 2,
    },
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "variant_name": "Green - Small",
        "variant_code": "T-SHIRT-GREEN-S",
        "color": "Green",
        "color_hex": "#00FF00",
        "size": "S",
        "fabric": "Cotton Blend",
        "pattern": "Striped",
        "is_active": True,
        "is_default": False,
        "sort_order": 3,
    },
    
    # Shoe variants
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "variant_name": "Black Leather - 42",
        "variant_code": "SHOE-BLK-42",
        "color": "Black",
        "color_hex": "#000000",
        "shoe_size_eu": "42",
        "shoe_size_us": "9",
        "shoe_size_uk": "8",
        "shoe_width": "Medium",
        "heel_height": 0.0,
        "upper_material": "Leather",
        "sole_material": "Rubber",
        "closure_type": "Lace",
        "is_active": True,
        "is_default": True,
        "sort_order": 1,
    },
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "variant_name": "Brown Suede - 43",
        "variant_code": "SHOE-BRN-43",
        "color": "Brown",
        "color_hex": "#8B4513",
        "shoe_size_eu": "43",
        "shoe_size_us": "9.5",
        "shoe_size_uk": "8.5",
        "shoe_width": "Medium",
        "heel_height": 0.0,
        "upper_material": "Suede",
        "sole_material": "Rubber",
        "closure_type": "Lace",
        "is_active": True,
        "is_default": False,
        "sort_order": 2,
    },
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "variant_name": "White Leather - 41",
        "variant_code": "SHOE-WHT-41",
        "color": "White",
        "color_hex": "#FFFFFF",
        "shoe_size_eu": "41",
        "shoe_size_us": "8.5",
        "shoe_size_uk": "7.5",
        "shoe_width": "Medium",
        "heel_height": 0.0,
        "upper_material": "Leather",
        "sole_material": "Rubber",
        "closure_type": "Slip-on",
        "is_active": True,
        "is_default": False,
        "sort_order": 3,
    },
    
    # Electronics variants
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "variant_name": "64GB - Silver",
        "variant_code": "PHONE-64GB-SLV",
        "color": "Silver",
        "color_hex": "#C0C0C0",
        "storage_capacity": "64GB",
        "ram_capacity": "4GB",
        "screen_size": "6.1 inch",
        "connectivity": "WiFi, Bluetooth 5.0, 5G",
        "is_active": True,
        "is_default": True,
        "sort_order": 1,
    },
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "variant_name": "128GB - Black",
        "variant_code": "PHONE-128GB-BLK",
        "color": "Black",
        "color_hex": "#000000",
        "storage_capacity": "128GB",
        "ram_capacity": "6GB",
        "screen_size": "6.1 inch",
        "connectivity": "WiFi, Bluetooth 5.0, 5G",
        "is_active": True,
        "is_default": False,
        "sort_order": 2,
    },
    
    # Jewelry variants
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "variant_name": "Gold - Size 7",
        "variant_code": "RING-GOLD-7",
        "color": "Gold",
        "color_hex": "#FFD700",
        "metal_type": "Gold",
        "stone_type": "Diamond",
        "carat_weight": 0.5,
        "ring_size": "7",
        "is_active": True,
        "is_default": True,
        "sort_order": 1,
    },
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "variant_name": "Silver - Size 6",
        "variant_code": "RING-SILVER-6",
        "color": "Silver",
        "color_hex": "#C0C0C0",
        "metal_type": "Silver",
        "stone_type": "Ruby",
        "carat_weight": 0.3,
        "ring_size": "6",
        "is_active": True,
        "is_default": False,
        "sort_order": 2,
    },
    
    # Cosmetics variants
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "variant_name": "Matte Red",
        "variant_code": "LIPSTICK-MATTE-RED",
        "color": "Red",
        "color_hex": "#DC143C",
        "shade": "Cherry Red",
        "finish": "Matte",
        "skin_type": "All",
        "is_active": True,
        "is_default": True,
        "sort_order": 1,
    },
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "variant_name": "Glossy Pink",
        "variant_code": "LIPSTICK-GLOSSY-PINK",
        "color": "Pink",
        "color_hex": "#FFC0CB",
        "shade": "Rose Pink",
        "finish": "Glossy",
        "skin_type": "All",
        "is_active": True,
        "is_default": False,
        "sort_order": 2,
    },
]


def _insert_product_variants(session: Session, cashier_id: str):
    """
    Inserts initial product variants into the database
    """
    # Check if ProductVariant table already has data
    existing_variants = session.query(ProductVariant).first()
    if existing_variants:
        print("✓ ProductVariant table already has data, skipping insert")
        return

    # Get first product to link variants to (for demo purposes)
    from data_layer.model.definition.product import Product
    first_product = session.query(Product).first()
    
    if not first_product:
        print("✗ No products found, skipping ProductVariant insert")
        return

    try:
        variants_to_insert = []
        for variant_data in PRODUCT_VARIANTS:
            # Create ProductVariant instance
            variant = ProductVariant()
            
            # Set product ID for demo (in real app, this would be properly mapped)
            variant.fk_product_id = first_product.id
            variant.variant_name = variant_data["variant_name"]
            variant.variant_code = variant_data["variant_code"]
            
            # Set all other fields
            for key, value in variant_data.items():
                if key not in ["id", "fk_product_id"] and hasattr(variant, key):
                    setattr(variant, key, value)
            
            # Set audit fields
            variant.fk_cashier_create_id = cashier_id
            variant.fk_cashier_update_id = cashier_id
            
            variants_to_insert.append(variant)

        # Insert all variants
        session.add_all(variants_to_insert)
        session.commit()
        print(f"✓ Inserted {len(variants_to_insert)} product variants")
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error inserting product variants: {e}")
        raise 