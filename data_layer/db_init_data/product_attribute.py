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
from data_layer.model.definition.product_attribute import ProductAttribute

# Example product attributes - these would be linked to actual products
PRODUCT_ATTRIBUTES = [
    # Shoe attributes
    {
        "id": str(uuid4()),
        "fk_product_id": None,  # Will be set when products are created
        "attribute_name": "waterproof",
        "attribute_value": "true",
        "attribute_type": "boolean",
        "boolean_value": True,
        "category": "technical",
        "display_name": "Waterproof",
        "display_order": 1,
        "is_searchable": True,
        "is_filterable": True,
        "is_visible_on_product": True,
        "language": "en",
    },
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "attribute_name": "breathable",
        "attribute_value": "true",
        "attribute_type": "boolean",
        "boolean_value": True,
        "category": "technical",
        "display_name": "Breathable",
        "display_order": 2,
        "is_searchable": True,
        "is_filterable": True,
        "is_visible_on_product": True,
        "language": "en",
    },
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "attribute_name": "heel_type",
        "attribute_value": "flat",
        "attribute_type": "text",
        "text_value": "Flat",
        "category": "physical",
        "display_name": "Heel Type",
        "display_order": 3,
        "is_searchable": True,
        "is_filterable": True,
        "is_visible_on_product": True,
        "language": "en",
    },
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "attribute_name": "orthopedic_support",
        "attribute_value": "true",
        "attribute_type": "boolean",
        "boolean_value": True,
        "category": "health",
        "display_name": "Orthopedic Support",
        "display_order": 4,
        "is_searchable": True,
        "is_filterable": True,
        "is_visible_on_product": True,
        "language": "en",
    },
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "attribute_name": "slip_resistant",
        "attribute_value": "true",
        "attribute_type": "boolean",
        "boolean_value": True,
        "category": "safety",
        "display_name": "Slip Resistant",
        "display_order": 5,
        "is_searchable": True,
        "is_filterable": True,
        "is_visible_on_product": True,
        "language": "en",
    },
    
    # Food product attributes
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "attribute_name": "organic",
        "attribute_value": "true",
        "attribute_type": "boolean",
        "boolean_value": True,
        "category": "marketing",
        "display_name": "Organic",
        "display_order": 1,
        "is_searchable": True,
        "is_filterable": True,
        "is_visible_on_product": True,
        "language": "en",
    },
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "attribute_name": "gluten_free",
        "attribute_value": "true",
        "attribute_type": "boolean",
        "boolean_value": True,
        "category": "health",
        "display_name": "Gluten Free",
        "display_order": 2,
        "is_searchable": True,
        "is_filterable": True,
        "is_visible_on_product": True,
        "language": "en",
    },
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "attribute_name": "shelf_life",
        "attribute_value": "365",
        "attribute_type": "number",
        "number_value": 365,
        "category": "technical",
        "display_name": "Shelf Life",
        "display_order": 3,
        "is_searchable": False,
        "is_filterable": False,
        "is_visible_on_product": True,
        "unit": "days",
        "language": "en",
    },
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "attribute_name": "non_gmo",
        "attribute_value": "true",
        "attribute_type": "boolean",
        "boolean_value": True,
        "category": "health",
        "display_name": "Non-GMO",
        "display_order": 4,
        "is_searchable": True,
        "is_filterable": True,
        "is_visible_on_product": True,
        "language": "en",
    },
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "attribute_name": "sugar_free",
        "attribute_value": "true",
        "attribute_type": "boolean",
        "boolean_value": True,
        "category": "health",
        "display_name": "Sugar Free",
        "display_order": 5,
        "is_searchable": True,
        "is_filterable": True,
        "is_visible_on_product": True,
        "language": "en",
    },
    
    # Clothing attributes
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "attribute_name": "stretch",
        "attribute_value": "true",
        "attribute_type": "boolean",
        "boolean_value": True,
        "category": "technical",
        "display_name": "Stretch",
        "display_order": 1,
        "is_searchable": True,
        "is_filterable": True,
        "is_visible_on_product": True,
        "language": "en",
    },
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "attribute_name": "fit_type",
        "attribute_value": "regular",
        "attribute_type": "text",
        "text_value": "Regular Fit",
        "category": "physical",
        "display_name": "Fit Type",
        "display_order": 2,
        "is_searchable": True,
        "is_filterable": True,
        "is_visible_on_product": True,
        "language": "en",
    },
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "attribute_name": "fabric_weight",
        "attribute_value": "180",
        "attribute_type": "number",
        "number_value": 180,
        "category": "technical",
        "display_name": "Fabric Weight",
        "display_order": 3,
        "is_searchable": False,
        "is_filterable": True,
        "is_visible_on_product": True,
        "unit": "g/m²",
        "language": "en",
    },
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "attribute_name": "wrinkle_free",
        "attribute_value": "true",
        "attribute_type": "boolean",
        "boolean_value": True,
        "category": "care",
        "display_name": "Wrinkle Free",
        "display_order": 4,
        "is_searchable": True,
        "is_filterable": True,
        "is_visible_on_product": True,
        "language": "en",
    },
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "attribute_name": "moisture_wicking",
        "attribute_value": "true",
        "attribute_type": "boolean",
        "boolean_value": True,
        "category": "technical",
        "display_name": "Moisture Wicking",
        "display_order": 5,
        "is_searchable": True,
        "is_filterable": True,
        "is_visible_on_product": True,
        "language": "en",
    },
    
    # Electronics attributes
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "attribute_name": "battery_life",
        "attribute_value": "24",
        "attribute_type": "number",
        "number_value": 24,
        "category": "technical",
        "display_name": "Battery Life",
        "display_order": 1,
        "is_searchable": False,
        "is_filterable": True,
        "is_visible_on_product": True,
        "unit": "hours",
        "language": "en",
    },
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "attribute_name": "water_resistant",
        "attribute_value": "IP68",
        "attribute_type": "text",
        "text_value": "IP68",
        "category": "technical",
        "display_name": "Water Resistance",
        "display_order": 2,
        "is_searchable": True,
        "is_filterable": True,
        "is_visible_on_product": True,
        "language": "en",
    },
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "attribute_name": "wireless_charging",
        "attribute_value": "true",
        "attribute_type": "boolean",
        "boolean_value": True,
        "category": "feature",
        "display_name": "Wireless Charging",
        "display_order": 3,
        "is_searchable": True,
        "is_filterable": True,
        "is_visible_on_product": True,
        "language": "en",
    },
    
    # Jewelry attributes
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "attribute_name": "hypoallergenic",
        "attribute_value": "true",
        "attribute_type": "boolean",
        "boolean_value": True,
        "category": "health",
        "display_name": "Hypoallergenic",
        "display_order": 1,
        "is_searchable": True,
        "is_filterable": True,
        "is_visible_on_product": True,
        "language": "en",
    },
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "attribute_name": "tarnish_resistant",
        "attribute_value": "true",
        "attribute_type": "boolean",
        "boolean_value": True,
        "category": "care",
        "display_name": "Tarnish Resistant",
        "display_order": 2,
        "is_searchable": True,
        "is_filterable": True,
        "is_visible_on_product": True,
        "language": "en",
    },
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "attribute_name": "handcrafted",
        "attribute_value": "true",
        "attribute_type": "boolean",
        "boolean_value": True,
        "category": "craftsmanship",
        "display_name": "Handcrafted",
        "display_order": 3,
        "is_searchable": True,
        "is_filterable": True,
        "is_visible_on_product": True,
        "language": "en",
    },
    
    # Cosmetics attributes
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "attribute_name": "cruelty_free",
        "attribute_value": "true",
        "attribute_type": "boolean",
        "boolean_value": True,
        "category": "ethics",
        "display_name": "Cruelty Free",
        "display_order": 1,
        "is_searchable": True,
        "is_filterable": True,
        "is_visible_on_product": True,
        "language": "en",
    },
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "attribute_name": "long_lasting",
        "attribute_value": "12",
        "attribute_type": "number",
        "number_value": 12,
        "category": "performance",
        "display_name": "Long Lasting",
        "display_order": 2,
        "is_searchable": False,
        "is_filterable": True,
        "is_visible_on_product": True,
        "unit": "hours",
        "language": "en",
    },
    {
        "id": str(uuid4()),
        "fk_product_id": None,
        "attribute_name": "paraben_free",
        "attribute_value": "true",
        "attribute_type": "boolean",
        "boolean_value": True,
        "category": "health",
        "display_name": "Paraben Free",
        "display_order": 3,
        "is_searchable": True,
        "is_filterable": True,
        "is_visible_on_product": True,
        "language": "en",
    },
]


def _insert_product_attributes(session: Session, cashier_id: str):
    """
    Inserts initial product attributes into the database
    """
    # Check if ProductAttribute table already has data
    existing_attributes = session.query(ProductAttribute).first()
    if existing_attributes:
        print("✓ ProductAttribute table already has data, skipping insert")
        return

    # Get first product to link attributes to (for demo purposes)
    from data_layer.model.definition.product import Product
    first_product = session.query(Product).first()
    
    if not first_product:
        print("✗ No products found, skipping ProductAttribute insert")
        return

    try:
        attributes_to_insert = []
        for attr_data in PRODUCT_ATTRIBUTES:
            # Create ProductAttribute instance
            attribute = ProductAttribute()
            
            # Set product ID for demo (in real app, this would be properly mapped)
            attribute.fk_product_id = first_product.id
            attribute.attribute_name = attr_data["attribute_name"]
            attribute.attribute_value = attr_data["attribute_value"]
            attribute.attribute_type = attr_data["attribute_type"]
            
            # Set all other fields
            for key, value in attr_data.items():
                if key not in ["id", "fk_product_id"] and hasattr(attribute, key):
                    setattr(attribute, key, value)
            
            # Set audit fields
            attribute.fk_cashier_create_id = cashier_id
            attribute.fk_cashier_update_id = cashier_id
            
            attributes_to_insert.append(attribute)

        # Insert all attributes
        session.add_all(attributes_to_insert)
        session.commit()
        print(f"✓ Inserted {len(attributes_to_insert)} product attributes")
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error inserting product attributes: {e}")
        raise 