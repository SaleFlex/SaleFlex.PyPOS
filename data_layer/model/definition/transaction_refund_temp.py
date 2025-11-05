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


class TransactionRefundTemp(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """Temporary version of TransactionRefund"""

    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "transaction_refund_temp"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_transaction_head_id = Column(UUID, ForeignKey("transaction_head_temp.id"), index=True)
    fk_original_transaction_id = Column(UUID, ForeignKey("transaction_head.id"), index=True)
    fk_transaction_product_id = Column(UUID, ForeignKey("transaction_product_temp.id"), nullable=True)
    refund_type = Column(String(50), nullable=False)
    refund_reason = Column(String(50), nullable=False)
    refund_reason_detail = Column(String(500), nullable=True)
    refund_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    refund_quantity = Column(Numeric(precision=15, scale=4), nullable=True)
    restocking_fee = Column(Numeric(precision=15, scale=4), nullable=False, default=0)
    requires_approval = Column(Boolean, nullable=False, default=True)
    approved_by = Column(UUID, ForeignKey("cashier.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    item_condition = Column(String(50), nullable=True)
    is_restocked = Column(Boolean, nullable=False, default=False)
    restocked_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<TransactionRefund(type='{self.refund_type}', amount='{self.refund_amount}')>"

    __table_args__ = (
        Index('idx_refund_transaction_temp', 'fk_transaction_head_id'),
        Index('idx_refund_original_temp', 'fk_original_transaction_id'),
    )