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


class ProductAttribute(Model, CRUD):
    def __init__(self, fk_product_id=None, attribute_name=None, attribute_value=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.fk_product_id = fk_product_id
        self.attribute_name = attribute_name
        self.attribute_value = attribute_value

    __tablename__ = "product_attribute"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_product_id = Column(UUID, ForeignKey("product.id"), nullable=False)
    fk_product_variant_id = Column(UUID, ForeignKey("product_variant.id"), nullable=True)  # Varyanta özel özellikler
    
    attribute_name = Column(String(100), nullable=False)  # Özellik adı
    attribute_value = Column(String(500), nullable=True)  # Özellik değeri
    attribute_type = Column(String(20), nullable=False, default='text')  # text, number, boolean, date
    
    # Değer tipleri için ayrı kolonlar
    text_value = Column(Text, nullable=True)
    number_value = Column(Float, nullable=True)
    boolean_value = Column(Boolean, nullable=True)
    date_value = Column(DateTime, nullable=True)
    
    # Özellik kategorisi
    category = Column(String(50), nullable=True)  # technical, physical, marketing, etc.
    
    # Gösterim bilgileri
    display_name = Column(String(100), nullable=True)  # Gösterim adı
    display_order = Column(Integer, nullable=False, default=0)  # Sıralama
    is_searchable = Column(Boolean, nullable=False, default=True)  # Aranabilir mi?
    is_filterable = Column(Boolean, nullable=False, default=True)  # Filtrelenebilir mi?
    is_visible_on_product = Column(Boolean, nullable=False, default=True)  # Ürün sayfasında görünür mü?
    
    # Birim bilgisi
    unit = Column(String(20), nullable=True)  # cm, kg, ml, etc.
    
    # Dil desteği
    language = Column(String(5), nullable=False, default='tr')  # tr, en, etc.
    
    # Audit fields
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    fk_cashier_create_id = Column(UUID, ForeignKey("cashier.id"))
    fk_cashier_update_id = Column(UUID, ForeignKey("cashier.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<ProductAttribute(attribute_name='{self.attribute_name}', attribute_value='{self.attribute_value}')>" 