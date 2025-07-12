"""
SaleFlex.PyPOS - Point of Sale Application

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

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, UUID, Date, Text
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD


class Product(Model, CRUD):
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
    purchase_price = Column(Integer, nullable=True, default=0)  # In cents
    sale_price = Column(Integer, nullable=False, default=0)  # In cents
    stock = Column(Integer, nullable=False, default=0)
    min_stock = Column(Integer, nullable=False, default=0)
    max_stock = Column(Integer, nullable=False, default=0)
    stock_unit = Column(String(10), nullable=True)
    stock_unit_no = Column(Integer, nullable=False, default=1)
    vat_no = Column(Integer, nullable=False, default=1)
    
    # Expiration and dating fields (for markets/grocery stores)
    expiration_date = Column(Date, nullable=True)  # Son kullanma tarihi
    production_date = Column(Date, nullable=True)  # Üretim tarihi
    shelf_life_days = Column(Integer, nullable=True)  # Raf ömrü (gün)
    lot_number = Column(String(50), nullable=True)  # Lot numarası
    
    # Nutritional information (for food products)
    calories_per_100g = Column(Float, nullable=True)  # 100g başına kalori
    protein_per_100g = Column(Float, nullable=True)  # 100g başına protein
    carb_per_100g = Column(Float, nullable=True)  # 100g başına karbonhidrat
    fat_per_100g = Column(Float, nullable=True)  # 100g başına yağ
    fiber_per_100g = Column(Float, nullable=True)  # 100g başına lif
    sodium_per_100g = Column(Float, nullable=True)  # 100g başına sodyum
    allergen_info = Column(String(500), nullable=True)  # Alerjen bilgileri
    
    # Restaurant specific fields
    ingredients = Column(Text, nullable=True)  # İçerikler/malzemeler
    recipe_instructions = Column(Text, nullable=True)  # Tarif talimatları
    preparation_time = Column(Integer, nullable=True)  # Hazırlanma süresi (dakika)
    cooking_time = Column(Integer, nullable=True)  # Pişirme süresi (dakika)
    serving_size = Column(String(50), nullable=True)  # Porsiyon boyutu
    spice_level = Column(Integer, nullable=True)  # Acılık seviyesi (1-5)
    is_vegetarian = Column(Boolean, nullable=False, default=False)
    is_vegan = Column(Boolean, nullable=False, default=False)
    is_halal = Column(Boolean, nullable=False, default=False)
    is_kosher = Column(Boolean, nullable=False, default=False)
    
    # Physical dimensions and weight (for clothing, shoes, etc.)
    weight = Column(Float, nullable=True)  # Ağırlık (gram)
    length = Column(Float, nullable=True)  # Uzunluk (cm)
    width = Column(Float, nullable=True)  # Genişlik (cm)
    height = Column(Float, nullable=True)  # Yükseklik (cm)
    
    # Season and style information (for fashion items)
    season = Column(String(20), nullable=True)  # Mevsim (spring, summer, autumn, winter)
    style = Column(String(100), nullable=True)  # Stil (casual, formal, sporty, etc.)
    gender = Column(String(10), nullable=True)  # Cinsiyet (male, female, unisex, kids)
    age_group = Column(String(20), nullable=True)  # Yaş grubu (baby, child, teen, adult, senior)
    
    # Care instructions (for clothing and textiles)
    care_instructions = Column(Text, nullable=True)  # Bakım talimatları
    washing_temperature = Column(Integer, nullable=True)  # Yıkama sıcaklığı
    
    # Brand and collection information
    brand = Column(String(100), nullable=True)  # Marka
    collection = Column(String(100), nullable=True)  # Koleksiyon
    model_year = Column(Integer, nullable=True)  # Model yılı
    
    # Special flags
    is_gift_wrappable = Column(Boolean, nullable=False, default=False)
    is_fragile = Column(Boolean, nullable=False, default=False)
    is_hazardous = Column(Boolean, nullable=False, default=False)
    requires_age_verification = Column(Boolean, nullable=False, default=False)
    
    # Additional product information
    origin_country = Column(String(100), nullable=True)  # Menşei ülke
    warranty_period = Column(Integer, nullable=True)  # Garanti süresi (ay)
    warranty_description = Column(String(500), nullable=True)  # Garanti açıklaması
    
    fk_vat_id = Column(UUID, ForeignKey("vat.id"))
    fk_product_unit_id = Column(UUID, ForeignKey("product_unit.id"))
    fk_department_main_group_id = Column(UUID, ForeignKey("department_main_group.id"), nullable=False,)
    fk_department_sub_group_id = Column(UUID, ForeignKey("department_sub_group.id"), nullable=False,)
    fk_manufacturer_id = Column(UUID, ForeignKey("product_manufacturer.id"))
    fk_store_id = Column(UUID, ForeignKey("store.id"))
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    fk_cashier_create_id = Column(UUID, ForeignKey("cashier.id"))
    fk_cashier_update_id = Column(UUID, ForeignKey("cashier.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Product(name='{self.name}', code='{self.code}', sale_price='{self.sale_price}')>"
