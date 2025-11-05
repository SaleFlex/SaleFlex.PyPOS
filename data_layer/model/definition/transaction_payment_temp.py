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


class TransactionPaymentTemp(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """Temporary transaction payment records"""

    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "transaction_payment_temp"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_transaction_head_id = Column(UUID, ForeignKey("transaction_head_temp.id"), index=True)
    line_no = Column(Integer, nullable=False)

    # Payment details
    payment_type = Column(String(50), nullable=False, index=True)  # "cash", "card", "gift_card", "wallet"
    payment_total = Column(Numeric(precision=15, scale=4), nullable=False)

    # Currency code from Integer to String (ISO 4217)
    currency_code = Column(String(3), nullable=False)  # "USD", "EUR", "GBP"
    currency_total = Column(Numeric(precision=15, scale=4), nullable=False)
    currency_exchange_rate = Column(Numeric(precision=15, scale=6), nullable=False, default=1.0)

    # Installment info
    installment_count = Column(Integer, nullable=False, default=1)

    # Payment gateway integration
    payment_provider = Column(String(50), nullable=True)  # "stripe", "square", "adyen"
    payment_gateway_transaction_id = Column(String(100), nullable=True, index=True)
    authorization_code = Column(String(50), nullable=True)
    approval_code = Column(String(50), nullable=True)

    # Card payment details
    card_number_masked = Column(String(20), nullable=True)  # "****1234"
    card_type = Column(String(20), nullable=True)  # "visa", "mastercard", "amex"
    card_holder_name = Column(String(100), nullable=True)
    card_expiry_month = Column(Integer, nullable=True)
    card_expiry_year = Column(Integer, nullable=True)

    # Terminal information
    terminal_id = Column(String(50), nullable=True)
    merchant_id = Column(String(50), nullable=True)
    batch_number = Column(String(50), nullable=True)

    # Payment status
    payment_status = Column(String(50), nullable=False, default="pending", index=True)
    payment_status_message = Column(String(500), nullable=True)
    payment_processed_at = Column(DateTime, nullable=True)

    # Gift card details
    gift_card_number = Column(String(50), nullable=True)
    gift_card_balance_before = Column(Numeric(precision=15, scale=4), nullable=True)
    gift_card_balance_after = Column(Numeric(precision=15, scale=4), nullable=True)

    # Voucher/coupon
    voucher_code = Column(String(50), nullable=True)
    voucher_amount = Column(Numeric(precision=15, scale=4), nullable=True)

    # Digital wallets
    wallet_type = Column(String(50), nullable=True)  # "apple_pay", "google_pay"
    wallet_transaction_id = Column(String(100), nullable=True)

    # Bank transfer details
    bank_name = Column(String(100), nullable=True)
    bank_account_last4 = Column(String(4), nullable=True)
    bank_reference_number = Column(String(100), nullable=True)

    # Split payment
    is_split_payment = Column(Boolean, nullable=False, default=False)
    split_payment_sequence = Column(Integer, nullable=True)

    # Tip handling
    tip_amount = Column(Numeric(precision=15, scale=4), nullable=False, default=0)
    tip_type = Column(String(20), nullable=True)  # "cash", "card", "auto_gratuity"

    # Refund tracking
    refunded_amount = Column(Numeric(precision=15, scale=4), nullable=False, default=0)
    refunded_at = Column(DateTime, nullable=True)
    refund_reference = Column(String(100), nullable=True)

    # Status flags
    is_cancel = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"<TransactionPaymentTemp(type='{self.payment_type}', amount='{self.payment_total}', status='{self.payment_status}')>"

    __table_args__ = (
        Index('idx_temp_payment_transaction', 'fk_transaction_head_id'),
        Index('idx_temp_payment_type', 'payment_type'),
        Index('idx_temp_payment_status', 'payment_status'),
    )