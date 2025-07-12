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

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UUID
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD


class ProductBarcode(Model, CRUD):
    def __init__(self, fk_product_id=None, barcode=None, old_barcode=None, 
                 purchase_price=None, sale_price=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.fk_product_id = fk_product_id
        self.barcode = barcode
        self.old_barcode = old_barcode
        self.purchase_price = purchase_price
        self.sale_price = sale_price

    __tablename__ = "product_barcode"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_server_id = Column(Integer, nullable=True)  # For server synchronization
    fk_product_id = Column(UUID, ForeignKey("product.id"), nullable=False)
    barcode = Column(String(50), nullable=False, unique=True)
    old_barcode = Column(String(50), nullable=True)
    fk_barcode_mask_id = Column(UUID, ForeignKey("product_barcode_mask.id"), nullable=True)
    purchase_price = Column(Integer, nullable=True, default=0)  # In cents
    sale_price = Column(Integer, nullable=True, default=0)  # In cents
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    fk_cashier_create_id = Column(UUID, ForeignKey("cashier.id"))
    fk_cashier_update_id = Column(UUID, ForeignKey("cashier.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<ProductBarcode(barcode='{self.barcode}', sale_price='{self.sale_price}')>"
