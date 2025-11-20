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

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, UUID, Text
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class ProductAttribute(Model, CRUD, AuditMixin, SoftDeleteMixin):
    def __init__(self, fk_product_id=None, attribute_name=None, attribute_value=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.fk_product_id = fk_product_id
        self.attribute_name = attribute_name
        self.attribute_value = attribute_value

    __tablename__ = "product_attribute"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_product_id = Column(UUID, ForeignKey("product.id"), nullable=False)
    fk_product_variant_id = Column(UUID, ForeignKey("product_variant.id"), nullable=True)  # Variant-specific features
    
    attribute_name = Column(String(100), nullable=False)  # Feature name
    attribute_value = Column(String(500), nullable=True)  # Property value
    attribute_type = Column(String(20), nullable=False, default='text')  # text, number, boolean, date
    
    # Separate columns for value types
    text_value = Column(Text, nullable=True)
    number_value = Column(Float, nullable=True)
    boolean_value = Column(Boolean, nullable=True)
    date_value = Column(DateTime, nullable=True)
    
    # Feature category
    category = Column(String(50), nullable=True)  # technical, physical, marketing, etc.
    
    # Display information
    display_name = Column(String(100), nullable=True)  # Display name
    display_order = Column(Integer, nullable=False, default=0)  # Arrangement
    is_searchable = Column(Boolean, nullable=False, default=True)  # Is it searchable?
    is_filterable = Column(Boolean, nullable=False, default=True)  # Can it be filtered?
    is_visible_on_product = Column(Boolean, nullable=False, default=True)  # Is it visible on the product page?
    
    # Unit information
    unit = Column(String(20), nullable=True)  # cm, kg, ml, etc.
    
    # Language support
    language = Column(String(5), nullable=False, default='tr')  # tr, en, etc.

    def __repr__(self):
        return f"<ProductAttribute(attribute_name='{self.attribute_name}', attribute_value='{self.attribute_value}')>" 