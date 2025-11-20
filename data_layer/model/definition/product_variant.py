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

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, UUID
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class ProductVariant(Model, CRUD, AuditMixin, SoftDeleteMixin):
    def __init__(self, fk_product_id=None, variant_name=None, variant_code=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.fk_product_id = fk_product_id
        self.variant_name = variant_name
        self.variant_code = variant_code

    __tablename__ = "product_variant"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_product_id = Column(UUID, ForeignKey("product.id"), nullable=False)
    variant_name = Column(String(100), nullable=False)  # Variant name
    variant_code = Column(String(50), nullable=False, unique=True)  # Variant code
    
    # Clothing and Fashion variants
    color = Column(String(50), nullable=True)  # Color
    color_hex = Column(String(7), nullable=True)  # Color HEX code (#FFFFFF)
    size = Column(String(20), nullable=True)  # Size (XS, S, M, L, XL, 38, 40, 42, etc.)
    fabric = Column(String(100), nullable=True)  # Fabric type
    pattern = Column(String(50), nullable=True)  # Pattern (solid, striped, dotted, etc.)
    
    # Shoe specific variants
    shoe_size_eu = Column(String(10), nullable=True)  # EU size (38, 39, 40, etc.)
    shoe_size_us = Column(String(10), nullable=True)  # US size (7, 8, 9, etc.)
    shoe_size_uk = Column(String(10), nullable=True)  # UK size (5, 6, 7, etc.)
    shoe_width = Column(String(10), nullable=True)  # Shoe width (narrow, medium, wide)
    heel_height = Column(Float, nullable=True)  # Heel height (cm)
    sole_material = Column(String(50), nullable=True)  # Sole material
    upper_material = Column(String(50), nullable=True)  # Upper material
    closure_type = Column(String(50), nullable=True)  # Closure type (lace, velcro, slip-on, etc.)
    
    # Electronics variants
    storage_capacity = Column(String(20), nullable=True)  # Storage capacity (64GB, 128GB, etc.)
    ram_capacity = Column(String(20), nullable=True)  # RAM capacity (4GB, 8GB, etc.)
    processor_type = Column(String(50), nullable=True)  # Processor type
    screen_size = Column(String(20), nullable=True)  # Screen size (13", 15", etc.)
    connectivity = Column(String(100), nullable=True)  # Connectivity options (WiFi, Bluetooth, etc.)
    
    # Cosmetics variants
    shade = Column(String(50), nullable=True)  # Shade/tone
    finish = Column(String(50), nullable=True)  # Finish type (matte, glossy, satin, etc.)
    skin_type = Column(String(50), nullable=True)  # Skin type (oily, dry, combination, etc.)
    
    # Jewelry variants
    metal_type = Column(String(50), nullable=True)  # Metal type (gold, silver, platinum, etc.)
    stone_type = Column(String(50), nullable=True)  # Stone type (diamond, ruby, sapphire, etc.)
    carat_weight = Column(Float, nullable=True)  # Carat weight
    ring_size = Column(String(10), nullable=True)  # Ring size
    chain_length = Column(Float, nullable=True)  # Chain length (cm)
    
    # Variant specific information
    weight = Column(Float, nullable=True)  # Variant weight
    dimensions = Column(String(100), nullable=True)  # Dimensions
    additional_info = Column(String(500), nullable=True)  # Additional information
    
    # Status fields
    is_active = Column(Boolean, nullable=False, default=True)
    is_default = Column(Boolean, nullable=False, default=False)  # Is default variant?
    sort_order = Column(Integer, nullable=False, default=0)  # Sort order
    
    def __repr__(self):
        return f"<ProductVariant(variant_name='{self.variant_name}', variant_code='{self.variant_code}')>" 