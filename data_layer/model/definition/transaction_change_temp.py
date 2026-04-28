"""
SaleFlex.PyPOS - Point of Sale Application
Copyright (C) 2025-2026 Mousavi.Tech

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from sqlalchemy import (
    Column, Integer, Boolean, String,
    DateTime, ForeignKey, UUID, Numeric, Index
)
from sqlalchemy.sql import func

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin
from uuid import uuid4


class TransactionChangeTemp(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """Temporary transaction change records"""

    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "transaction_change_temp"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_transaction_head_id = Column(UUID, ForeignKey("transaction_head_temp.id"), index=True)
    line_no = Column(Integer, nullable=False)

    # Change details
    change_amount = Column(Numeric(precision=10, scale=2), nullable=False)
    currency = Column(String(3), nullable=False, default="GBP")  # ISO 4217 currency code

    # Status flags
    is_cancel = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"<TransactionChangeTemp(amount='{self.change_amount}', currency='{self.currency}')>"

    __table_args__ = (
        Index('idx_temp_change_transaction', 'fk_transaction_head_id'),
    )

