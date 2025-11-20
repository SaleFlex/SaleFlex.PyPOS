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

from sqlalchemy import (
    Column, Integer, BigInteger, Boolean, String,
    DateTime, Float, ForeignKey, UUID, Numeric, Index, func
)

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin

from uuid import uuid4


class TransactionTipTemp(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """Temporary version of TransactionTip"""

    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "transaction_tip_temp"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_transaction_head_id = Column(UUID, ForeignKey("transaction_head_temp.id"), index=True)
    fk_transaction_payment_id = Column(UUID, ForeignKey("transaction_payment_temp.id"), nullable=True)
    tip_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    tip_percentage = Column(Numeric(precision=5, scale=2), nullable=True)
    tip_type = Column(String(50), nullable=False)
    is_pooled = Column(Boolean, nullable=False, default=False)
    fk_server_id = Column(UUID, ForeignKey("cashier.id"), nullable=True)
    is_taxable = Column(Boolean, nullable=False, default=True)
    tax_amount = Column(Numeric(precision=15, scale=4), nullable=False, default=0)
    suggested_tip_percentage = Column(Numeric(precision=5, scale=2), nullable=True)

    def __repr__(self):
        return f"<TransactionTip(amount='{self.tip_amount}', type='{self.tip_type}')>"