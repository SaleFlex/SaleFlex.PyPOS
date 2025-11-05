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

from sqlalchemy import Column, Integer, BigInteger, Boolean, String, DateTime, Float, ForeignKey, UUID, Numeric
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class TransactionDiscountTemp(Model, CRUD, AuditMixin, SoftDeleteMixin):
    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "transaction_discount_temp"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_transaction_head_id = Column(UUID, ForeignKey("transaction_head_temp.id"))
    fk_transaction_product_id = Column(UUID, ForeignKey("transaction_product_temp.id"), nullable=True)
    fk_transaction_payment_id = Column(UUID, ForeignKey("transaction_payment_temp.id"), nullable=True)
    fk_transaction_total_id = Column(UUID, ForeignKey("transaction_total_temp.id"), nullable=True)
    line_no = Column(Integer, nullable=False)
    discount_type = Column(String(50), nullable=False)
    discount_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    discount_rate = Column(Numeric(precision=2, scale=2), nullable=True)
    discount_code = Column(String(15), nullable=True)
    is_cancel = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"<TransactionDiscountTemp(discount_type='{self.discount_type}', discount_amount='{self.discount_amount}')>"
