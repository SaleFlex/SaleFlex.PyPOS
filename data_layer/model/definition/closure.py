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

from sqlalchemy import Column, Integer, BigInteger, Boolean, String, DateTime, Text, ForeignKey, Date, UUID, Numeric
from sqlalchemy.sql import func

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin    

from uuid import uuid4


class Closure(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Main closure record - stores high-level summary only.
    Detailed breakdowns moved to separate summary tables.
    """
    __tablename__ = "closure"

    id = Column(UUID, primary_key=True, default=uuid4)
    closure_unique_id = Column(String(50), unique=True, nullable=False, index=True)
    closure_number = Column(Integer, nullable=False)  # Daily sequence
    
    # Store & POS Info
    fk_store_id = Column(UUID, ForeignKey("store.id"), nullable=False)
    fk_pos_id = Column(UUID, ForeignKey("pos_settings.id"), nullable=False)
    
    # Closure Timing
    closure_date = Column(Date, nullable=False, index=True)
    closure_start_time = Column(DateTime, nullable=False)
    closure_end_time = Column(DateTime, nullable=False)
    
    # Currency Info
    fk_base_currency_id = Column(UUID, ForeignKey("currency.id"), nullable=False)
    
    # High-Level Totals (in base currency)
    total_document_count = Column(Integer, nullable=False, default=0)
    gross_sales_amount = Column(Numeric(15, 4), nullable=False, default=0)
    net_sales_amount = Column(Numeric(15, 4), nullable=False, default=0)
    total_tax_amount = Column(Numeric(15, 4), nullable=False, default=0)
    total_discount_amount = Column(Numeric(15, 4), nullable=False, default=0)
    total_tip_amount = Column(Numeric(15, 4), nullable=False, default=0)  # For restaurants
    
    # Transaction Counts
    valid_transaction_count = Column(Integer, nullable=False, default=0)
    canceled_transaction_count = Column(Integer, nullable=False, default=0)
    return_transaction_count = Column(Integer, nullable=False, default=0)
    
    # Cash Management
    opening_cash_amount = Column(Numeric(15, 4), nullable=False, default=0)
    closing_cash_amount = Column(Numeric(15, 4), nullable=False, default=0)
    expected_cash_amount = Column(Numeric(15, 4), nullable=False, default=0)
    cash_difference = Column(Numeric(15, 4), nullable=False, default=0)
    
    # Paid In/Out
    paid_in_count = Column(Integer, nullable=False, default=0)
    paid_in_total = Column(Numeric(15, 4), nullable=False, default=0)
    paid_out_count = Column(Integer, nullable=False, default=0)
    paid_out_total = Column(Numeric(15, 4), nullable=False, default=0)
    
    # Status
    is_canceled = Column(Boolean, nullable=False, default=False)
    is_modified = Column(Boolean, nullable=False, default=False)
    
    # Employee Info
    fk_cashier_opened_id = Column(UUID, ForeignKey("cashier.id"), nullable=False)
    fk_cashier_closed_id = Column(UUID, ForeignKey("cashier.id"), nullable=False)
    fk_cashier_modified_id = Column(UUID, ForeignKey("cashier.id"))
    
    # Notes
    description = Column(Text)
    modified_description = Column(Text)

    def __repr__(self):
        return f"<Closure(id='{self.closure_unique_id}', date='{self.closure_date}')>"

