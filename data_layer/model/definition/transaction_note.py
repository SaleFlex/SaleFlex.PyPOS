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


class TransactionNote(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Free-form notes and special instructions for transactions.
    """

    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "transaction_note"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_transaction_head_id = Column(UUID, ForeignKey("transaction_head.id"), index=True)

    # Note details
    note_type = Column(String(50), nullable=False)  # "general", "kitchen", "delivery", "internal"
    note_text = Column(String(2000), nullable=False)

    # Visibility controls
    is_visible_to_customer = Column(Boolean, nullable=False, default=False)
    is_visible_on_receipt = Column(Boolean, nullable=False, default=False)
    is_visible_to_kitchen = Column(Boolean, nullable=False, default=False)

    # Priority
    priority = Column(Integer, nullable=False, default=1)

    def __repr__(self):
        return f"<TransactionNote(type='{self.note_type}', priority={self.priority})>"
