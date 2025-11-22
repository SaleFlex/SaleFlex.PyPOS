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

from sqlalchemy import Column, Integer, BigInteger, Boolean, String, DateTime, Float, ForeignKey, UUID, Numeric
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class TransactionDiscount(Model, CRUD, AuditMixin, SoftDeleteMixin):
    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "transaction_discount"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_transaction_head_id = Column(UUID, ForeignKey("transaction_head.id"))
    fk_transaction_product_id = Column(UUID, ForeignKey("transaction_product.id"), nullable=True)
    fk_transaction_payment_id = Column(UUID, ForeignKey("transaction_payment.id"), nullable=True)
    fk_transaction_department_id = Column(UUID, ForeignKey("transaction_department.id"), nullable=True)
    line_no = Column(Integer, nullable=False)
    fk_discount_type_id = Column(UUID, ForeignKey("transaction_discount_type.id"), nullable=False)
    discount_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    discount_rate = Column(Numeric(precision=2, scale=2), nullable=True)
    discount_code = Column(String(15), nullable=True)
    is_cancel = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"<TransactionDiscount(fk_discount_type_id='{self.fk_discount_type_id}', discount_amount='{self.discount_amount}')>"
