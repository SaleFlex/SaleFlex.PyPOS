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


class ProductUnit(Model, CRUD):
    def __init__(self, name=None, no: int = None, description: str = None,
                 base_id: int = None, base_amount: float = None, symbol: str = None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.name = name
        self.no = no
        self.description = description
        self.base_id = base_id
        self.base_amount = base_amount
        self.symbol = symbol

    __tablename__ = "product_unit"

    id = Column(BigInteger, primary_key=True, autoincrement=True, default=1)
    name = Column(String(50), nullable=False)
    no = Column(Integer, nullable=False)
    description = Column(String(100), nullable=False)
    base_id = Column(Integer, nullable=False)
    base_amount = Column(Float, nullable=False)
    symbol = Column(String(10), nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    fk_cashier_create_id = Column(BigInteger, ForeignKey("cashier.id"))
    fk_cashier_update_id = Column(BigInteger, ForeignKey("cashier.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<ProductUnit(name='{self.name}', no='{self.no}', description='{self.description}')>"
