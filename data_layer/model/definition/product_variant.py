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

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, UUID
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD


class ProductVariant(Model, CRUD):
    def __init__(self, fk_product_id=None, variant_name=None, variant_code=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.fk_product_id = fk_product_id
        self.variant_name = variant_name
        self.variant_code = variant_code

    __tablename__ = "product_variant"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_product_id = Column(UUID, ForeignKey("product.id"), nullable=False)
    variant_name = Column(String(100), nullable=False)  # Varyant adı
    variant_code = Column(String(50), nullable=False, unique=True)  # Varyant kodu
    
    # Clothing and Fashion variants
    color = Column(String(50), nullable=True)  # Renk
    color_hex = Column(String(7), nullable=True)  # Renk HEX kodu (#FFFFFF)
    size = Column(String(20), nullable=True)  # Beden (XS, S, M, L, XL, 38, 40, 42, etc.)
    fabric = Column(String(100), nullable=True)  # Kumaş tipi
    pattern = Column(String(50), nullable=True)  # Desen (solid, striped, dotted, etc.)
    
    # Shoe specific variants
    shoe_size_eu = Column(String(10), nullable=True)  # EU beden (38, 39, 40, etc.)
    shoe_size_us = Column(String(10), nullable=True)  # US beden (7, 8, 9, etc.)
    shoe_size_uk = Column(String(10), nullable=True)  # UK beden (5, 6, 7, etc.)
    shoe_width = Column(String(10), nullable=True)  # Ayakkabı genişliği (narrow, medium, wide)
    heel_height = Column(Float, nullable=True)  # Topuk yüksekliği (cm)
    sole_material = Column(String(50), nullable=True)  # Taban malzemesi
    upper_material = Column(String(50), nullable=True)  # Üst malzeme
    closure_type = Column(String(50), nullable=True)  # Kapanış tipi (lace, velcro, slip-on, etc.)
    
    # Electronics variants
    storage_capacity = Column(String(20), nullable=True)  # Depolama kapasitesi (64GB, 128GB, etc.)
    ram_capacity = Column(String(20), nullable=True)  # RAM kapasitesi (4GB, 8GB, etc.)
    processor_type = Column(String(50), nullable=True)  # İşlemci tipi
    screen_size = Column(String(20), nullable=True)  # Ekran boyutu (13", 15", etc.)
    connectivity = Column(String(100), nullable=True)  # Bağlantı seçenekleri (WiFi, Bluetooth, etc.)
    
    # Cosmetics variants
    shade = Column(String(50), nullable=True)  # Ton/gölge
    finish = Column(String(50), nullable=True)  # Finish tipi (matte, glossy, satin, etc.)
    skin_type = Column(String(50), nullable=True)  # Cilt tipi (oily, dry, combination, etc.)
    
    # Jewelry variants
    metal_type = Column(String(50), nullable=True)  # Metal tipi (gold, silver, platinum, etc.)
    stone_type = Column(String(50), nullable=True)  # Taş tipi (diamond, ruby, sapphire, etc.)
    carat_weight = Column(Float, nullable=True)  # Karat ağırlığı
    ring_size = Column(String(10), nullable=True)  # Yüzük ölçüsü
    chain_length = Column(Float, nullable=True)  # Zincir uzunluğu (cm)
    
    # Variant specific information
    weight = Column(Float, nullable=True)  # Varyant ağırlığı
    dimensions = Column(String(100), nullable=True)  # Boyutlar
    additional_info = Column(String(500), nullable=True)  # Ek bilgiler
    
    # Status fields
    is_active = Column(Boolean, nullable=False, default=True)
    is_default = Column(Boolean, nullable=False, default=False)  # Varsayılan varyant mı?
    sort_order = Column(Integer, nullable=False, default=0)  # Sıralama
    
    # Audit fields
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    fk_cashier_create_id = Column(UUID, ForeignKey("cashier.id"))
    fk_cashier_update_id = Column(UUID, ForeignKey("cashier.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<ProductVariant(variant_name='{self.variant_name}', variant_code='{self.variant_code}')>" 