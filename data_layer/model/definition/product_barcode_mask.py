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

from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.sql import func

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD


class ProductBarcodeMask(Model, CRUD):
    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "product_barcode_mask"

    id = Column(BigInteger, primary_key=True, autoincrement=True, default=1)
    fk_product_id = Column(BigInteger, ForeignKey("product.id"))
    code_started_at = Column(Integer, nullable=True)
    code_length = Column(Integer, nullable=True)
    quantity_started_at = Column(Integer, nullable=True)
    quantity_length = Column(Integer, nullable=True)
    weight_started_at = Column(Integer, nullable=True)
    weight_length = Column(Integer, nullable=True)
    price_started_at = Column(Integer, nullable=True)
    price_length = Column(Integer, nullable=True)
    color_started_at = Column(Integer, nullable=True)
    color_length = Column(Integer, nullable=True)
    size_started_at = Column(Integer, nullable=True)
    size_length = Column(Integer, nullable=True)
    description = Column(String(150), nullable=True)
    fk_cashier_create_id = Column(BigInteger, ForeignKey("cashier.id"))
    fk_cashier_update_id = Column(BigInteger, ForeignKey("cashier.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<ProductBarcode(name='{self.name}', barcode='{self.barcode}'>"
