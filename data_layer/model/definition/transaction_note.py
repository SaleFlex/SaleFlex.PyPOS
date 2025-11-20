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
