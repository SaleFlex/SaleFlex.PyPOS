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
    fk_vat_id = Column(UUID, ForeignKey("vat.id"))
    fk_product_unit_id = Column(UUID, ForeignKey("product_unit.id"))
    fk_department_main_group_id = Column(UUID, ForeignKey("department_main_group.id"))
    fk_department_sub_group_id = Column(UUID, ForeignKey("department_sub_group.id"))
    fk_manufacturer_id = Column(UUID, ForeignKey("manufacturer.id"))
    fk_store_id = Column(UUID, ForeignKey("store.id"))
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    fk_cashier_create_id = Column(UUID, ForeignKey("cashier.id"))
    fk_cashier_update_id = Column(UUID, ForeignKey("cashier.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Product(name='{self.name}', code='{self.code}', sale_price='{self.sale_price}')>"
