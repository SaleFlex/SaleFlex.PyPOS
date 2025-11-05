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