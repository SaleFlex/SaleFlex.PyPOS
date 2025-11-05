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