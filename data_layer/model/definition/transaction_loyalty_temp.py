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


class TransactionLoyaltyTemp(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """Temporary version of TransactionLoyalty"""

    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "transaction_loyalty_temp"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_transaction_head_id = Column(UUID, ForeignKey("transaction_head_temp.id"), index=True)
    fk_loyalty_member_id = Column(UUID, ForeignKey("customer_loyalty.id"), index=True)
    points_earned = Column(Integer, nullable=False, default=0)
    points_redeemed = Column(Integer, nullable=False, default=0)
    points_balance_before = Column(Integer, nullable=False)
    points_balance_after = Column(Integer, nullable=False)
    points_monetary_value = Column(Numeric(precision=15, scale=4), nullable=True)
    redemption_amount = Column(Numeric(precision=15, scale=4), nullable=False, default=0)
    loyalty_tier = Column(String(50), nullable=True)
    bonus_multiplier = Column(Numeric(precision=5, scale=2), nullable=False, default=1.0)
    campaign_bonus = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<TransactionLoyalty(earned={self.points_earned}, redeemed={self.points_redeemed})>"