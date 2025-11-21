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

from sqlalchemy import Column, Integer, BigInteger, Boolean, String, DateTime, Text, ForeignKey, UUID, Numeric
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class ClosurePaymentTypeSummary(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """Payment method breakdown - unchanged, already well structured."""
    __tablename__ = "closure_payment_type_summary"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_closure_id = Column(UUID, ForeignKey("closure.id"), nullable=False, index=True)
    fk_payment_type_id = Column(UUID, ForeignKey("payment_type.id"), nullable=False)
    
    total_count = Column(Integer, nullable=False, default=0)
    total_amount = Column(Numeric(15, 4), nullable=False, default=0)
    
    # Modification tracking
    is_modified = Column(Boolean, nullable=False, default=False)
    fk_cashier_modified_id = Column(UUID, ForeignKey("cashier.id"))
    modified_description = Column(Text)

    def __repr__(self):
        return f"<ClosurePaymentTypeSummary(count='{self.total_count}', amount='{self.total_amount}')>"