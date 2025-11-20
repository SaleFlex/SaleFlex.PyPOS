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

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, UUID, Date, Text, Numeric
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class Product(Model, CRUD, AuditMixin, SoftDeleteMixin):
    def __init__(self, name=None, short_name=None, code=None, old_code=None, shelf_code=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.name = name
        self.short_name = short_name
        self.code = code
        self.old_code = old_code
        self.shelf_code = shelf_code

    __tablename__ = "product"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_server_id = Column(Integer, nullable=True)  # For server synchronization
    name = Column(String(100), nullable=False)
    short_name = Column(String(50), nullable=True)
    code = Column(String(20), nullable=False, unique=True)
    old_code = Column(String(20), nullable=True)
    shelf_code = Column(String(20), nullable=True)
    keyboard_value = Column(String(10), nullable=True)
    description = Column(String(150), nullable=True)
    description_on_screen = Column(String(150), nullable=True)
    description_on_shelf = Column(String(150), nullable=True)
    description_on_scale = Column(String(150), nullable=True)
    is_scalable = Column(Boolean, nullable=False, default=False)
    is_allowed_discount = Column(Boolean, nullable=False, default=True)
    discount_percent = Column(Integer, nullable=False, default=0)
    is_allowed_negative_stock = Column(Boolean, nullable=False, default=False)
    is_allowed_return = Column(Boolean, nullable=False, default=True)
    purchase_price = Column(Numeric(precision=15, scale=4), nullable=True, default=0)
    sale_price = Column(Numeric(precision=15, scale=4), nullable=False, default=0)
    stock = Column(Integer, nullable=False, default=0)
    min_stock = Column(Integer, nullable=False, default=0)
    max_stock = Column(Integer, nullable=False, default=0)
    stock_unit = Column(String(10), nullable=True)
    stock_unit_no = Column(Integer, nullable=False, default=1)
    vat_no = Column(Integer, nullable=False, default=1)
    
    # Expiration and dating fields (for markets/grocery stores)
    expiration_date = Column(Date, nullable=True)  # Expiration date
    production_date = Column(Date, nullable=True)  # Production date
    shelf_life_days = Column(Integer, nullable=True)  # Shelf life (days)
    lot_number = Column(String(50), nullable=True)  # Lot number
    
    # Nutritional information (for food products)
    calories_per_100g = Column(Float, nullable=True)  # Calories per 100g
    protein_per_100g = Column(Float, nullable=True)  # Protein per 100g
    carb_per_100g = Column(Float, nullable=True)  # Carbohydrates per 100g
    fat_per_100g = Column(Float, nullable=True)  # Fat per 100g
    fiber_per_100g = Column(Float, nullable=True)  # Fiber per 100g
    sodium_per_100g = Column(Float, nullable=True)  # Sodium per 100g
    allergen_info = Column(String(500), nullable=True)  # Allergen information
    
    # Restaurant specific fields
    ingredients = Column(Text, nullable=True)  # Ingredients/components
    recipe_instructions = Column(Text, nullable=True)  # Recipe instructions
    preparation_time = Column(Integer, nullable=True)  # Preparation time (minutes)
    cooking_time = Column(Integer, nullable=True)  # Cooking time (minutes)
    serving_size = Column(String(50), nullable=True)  # Serving size
    spice_level = Column(Integer, nullable=True)  # Spice level (1-5)
    is_vegetarian = Column(Boolean, nullable=False, default=False)
    is_vegan = Column(Boolean, nullable=False, default=False)
    is_halal = Column(Boolean, nullable=False, default=False)
    is_kosher = Column(Boolean, nullable=False, default=False)
    
    # Physical dimensions and weight (for clothing, shoes, etc.)
    weight = Column(Float, nullable=True)  # Weight (grams)
    length = Column(Float, nullable=True)  # Length (cm)
    width = Column(Float, nullable=True)  # Width (cm)
    height = Column(Float, nullable=True)  # Height (cm)
    
    # Season and style information (for fashion items)
    season = Column(String(20), nullable=True)  # Season (spring, summer, autumn, winter)
    style = Column(String(100), nullable=True)  # Style (casual, formal, sporty, etc.)
    gender = Column(String(10), nullable=True)  # Gender (male, female, unisex, kids)
    age_group = Column(String(20), nullable=True)  # Age group (baby, child, teen, adult, senior)
    
    # Care instructions (for clothing and textiles)
    care_instructions = Column(Text, nullable=True)  # Care instructions
    washing_temperature = Column(Integer, nullable=True)  # Washing temperature
    
    # Brand and collection information
    brand = Column(String(100), nullable=True)  # Brand
    collection = Column(String(100), nullable=True)  # Collection
    model_year = Column(Integer, nullable=True)  # Model year
    
    # Special flags
    is_gift_wrappable = Column(Boolean, nullable=False, default=False)
    is_fragile = Column(Boolean, nullable=False, default=False)
    is_hazardous = Column(Boolean, nullable=False, default=False)
    requires_age_verification = Column(Boolean, nullable=False, default=False)
    
    # Additional product information
    origin_country = Column(String(100), nullable=True)  # Country of origin
    warranty_period = Column(Integer, nullable=True)  # Warranty period (months)
    warranty_description = Column(String(500), nullable=True)  # Warranty description
    
    fk_vat_id = Column(UUID, ForeignKey("vat.id"))
    fk_product_unit_id = Column(UUID, ForeignKey("product_unit.id"))
    fk_department_main_group_id = Column(UUID, ForeignKey("department_main_group.id"), nullable=False,)
    fk_department_sub_group_id = Column(UUID, ForeignKey("department_sub_group.id"), nullable=False,)
    fk_manufacturer_id = Column(UUID, ForeignKey("product_manufacturer.id"))
    fk_store_id = Column(UUID, ForeignKey("store.id"))
    fk_primary_warehouse_id = Column(UUID, ForeignKey("warehouse.id"), nullable=True)  # Primary warehouse for this product

    def __repr__(self):
        return f"<Product(name='{self.name}', code='{self.code}', sale_price='{self.sale_price}')>"
