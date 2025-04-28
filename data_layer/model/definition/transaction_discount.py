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

from sqlalchemy import Column, Integer, BigInteger, Boolean, String, DateTime, Float, ForeignKey, UUID
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD


class TransactionDiscount(Model, CRUD):
    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "transaction_discount"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_transaction_head_id = Column(BigInteger, ForeignKey("transaction_head.id"))
    fk_transaction_product_id = Column(BigInteger, ForeignKey("transaction_product.id"), nullable=True)
    fk_transaction_payment_id = Column(BigInteger, ForeignKey("transaction_payment.id"), nullable=True)
    fk_transaction_total_id = Column(BigInteger, ForeignKey("transaction_total.id"), nullable=True)
    line_no = Column(Integer, nullable=False)
    discount_type = Column(String(50), nullable=False)
    discount_amount = Column(Float, nullable=False)
    discount_rate = Column(Float, nullable=True)
    discount_code = Column(String(15), nullable=True)
    is_cancel = Column(Boolean, nullable=False, default=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    fk_cashier_create_id = Column(BigInteger, ForeignKey("cashier.id"))
    fk_cashier_update_id = Column(BigInteger, ForeignKey("cashier.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<TransactionDiscount(discount_type='{self.discount_type}', discount_amount='{self.discount_amount}')>"
