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
from sqlalchemy.sql import func

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin
from data_layer.model.definition.transaction_status import TransactionStatus, TransactionType, DeliveryStatus

from uuid import uuid4


class TransactionHeadTemp(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Temporary transaction header for in-progress transactions.
    Migrates to TransactionHead upon successful completion.
    """

    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "transaction_head_temp"

    # Primary key
    id = Column(UUID, primary_key=True, default=uuid4)

    # Unique transaction identifier
    transaction_unique_id = Column(String(50), nullable=False, unique=True, index=True)

    # POS identification
    pos_id = Column(Integer, nullable=False, index=True)

    # Transaction timing
    transaction_date_time = Column(DateTime, server_default=func.now(), nullable=False, index=True)

    # Document classification
    document_type = Column(String(50), nullable=False)
    transaction_type = Column(String(50), nullable=False, default=TransactionType.SALE.value)
    transaction_status = Column(String(50), nullable=False, default=TransactionStatus.ACTIVE.value, index=True)

    # Customer & location
    fk_customer_id = Column(UUID, ForeignKey("customer.id"), index=True)
    fk_table_id = Column(UUID, ForeignKey("table.id"), nullable=True)
    fk_store_id = Column(UUID, ForeignKey("store.id"), nullable=False)

    # Numbering sequences
    closure_number = Column(Integer, nullable=False, index=True)
    receipt_number = Column(Integer, nullable=False, index=True)
    batch_number = Column(Integer, nullable=False)

    # Core financial totals
    total_amount = Column(Numeric(precision=15, scale=4), nullable=False, default=0)
    total_vat_amount = Column(Numeric(precision=15, scale=4), nullable=False, default=0)
    total_discount_amount = Column(Numeric(precision=15, scale=4), nullable=False, default=0)
    total_surcharge_amount = Column(Numeric(precision=15, scale=4), nullable=False, default=0)
    total_payment_amount = Column(Numeric(precision=15, scale=4), nullable=False, default=0)
    total_change_amount = Column(Numeric(precision=15, scale=4), nullable=False, default=0)

    # Additional charges ***
    service_charge_amount = Column(Numeric(precision=15, scale=4), nullable=False, default=0)
    tip_amount = Column(Numeric(precision=15, scale=4), nullable=False, default=0)
    rounding_amount = Column(Numeric(precision=15, scale=4), nullable=False, default=0)

    # Multi-currency support
    base_currency = Column(String(3), nullable=False, default="USD")  # ISO 4217
    display_currency = Column(String(3), nullable=True)  # Display currency if different
    exchange_rate = Column(Numeric(precision=15, scale=6), nullable=True, default=1.0)

    # Tax jurisdiction (critical for US/Canada)
    tax_jurisdiction_code = Column(String(50), nullable=True)
    tax_calculation_method = Column(String(50), nullable=True)  # "inclusive" or "exclusive"

    # Delivery information
    delivery_status = Column(String(50), nullable=True)
    estimated_delivery_time = Column(DateTime, nullable=True)
    actual_delivery_time = Column(DateTime, nullable=True)

    # Order source tracking
    order_source = Column(String(50), nullable=True)  # "in_store", "online", "mobile_app", "kiosk"
    order_channel = Column(String(50), nullable=True)

    # Fiscal compliance
    fiscal_receipt_number = Column(String(50), nullable=True)
    fiscal_signature = Column(String(500), nullable=True)
    fiscal_qr_code = Column(String(1000), nullable=True)

    # Tax exemption
    tax_exemption_code = Column(String(50), nullable=True)
    tax_exemption_reason = Column(String(200), nullable=True)

    # Loyalty program
    loyalty_member_id = Column(UUID, ForeignKey("customer_loyalty.id"), nullable=True)
    loyalty_points_earned = Column(Integer, nullable=False, default=0)
    loyalty_points_redeemed = Column(Integer, nullable=False, default=0)

    # Campaign tracking
    campaign_id = Column(UUID, ForeignKey("campaign.id"), nullable=True)

    # Reference tracking ***
    external_reference_number = Column(String(100), nullable=True)
    original_transaction_id = Column(UUID, ForeignKey("transaction_head.id"), nullable=True)  # For returns
    parent_transaction_id = Column(UUID, ForeignKey("transaction_head.id"), nullable=True)  # For splits

    # General description
    description = Column(String(500), nullable=True)

    # Transaction flags
    is_closed = Column(Boolean, nullable=False, default=False)
    is_pending = Column(Boolean, nullable=False, default=False)
    is_cancel = Column(Boolean, nullable=False, default=False)
    cancel_reason = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<TransactionHeadTemp(id='{self.transaction_unique_id}', status='{self.transaction_status}', total='{self.total_amount}')>"

    __table_args__ = (
        Index('idx_temp_head_transaction_date', 'transaction_date_time'),
        Index('idx_temp_head_status', 'transaction_status'),
        Index('idx_temp_head_customer', 'fk_customer_id'),
    )