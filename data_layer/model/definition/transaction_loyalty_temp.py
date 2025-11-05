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