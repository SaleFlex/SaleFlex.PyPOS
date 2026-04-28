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
    closure_end_time = Column(DateTime, nullable=True)  # None for open closures
    
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
    suspended_transaction_count = Column(Integer, nullable=False, default=0)
    
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

