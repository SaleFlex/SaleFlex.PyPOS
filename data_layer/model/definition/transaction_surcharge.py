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
    DateTime, Float, ForeignKey, UUID, Numeric, Index
)

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin

from uuid import uuid4


class TransactionSurcharge(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Surcharges and additional fees beyond product prices.
    Examples: service charges, delivery fees, convenience fees, bag fees
    """

    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "transaction_surcharge"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_transaction_head_id = Column(UUID, ForeignKey("transaction_head.id"), index=True)

    # Surcharge details
    surcharge_type = Column(String(50), nullable=False)  # "service_charge", "delivery_fee", "convenience_fee"
    surcharge_name = Column(String(100), nullable=False)
    surcharge_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    surcharge_rate = Column(Numeric(precision=5, scale=2), nullable=True)  # If percentage-based

    # Tax treatment
    is_taxable = Column(Boolean, nullable=False, default=True)
    tax_amount = Column(Numeric(precision=15, scale=4), nullable=False, default=0)

    # Application rules
    is_automatic = Column(Boolean, nullable=False, default=False)
    can_be_removed = Column(Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<TransactionSurcharge(type='{self.surcharge_type}', amount='{self.surcharge_amount}')>"

