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
    DateTime, Float, ForeignKey, UUID, Numeric, Index
)

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin
from uuid import uuid4


class TransactionPayment(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """Permanent transaction payment records"""

    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "transaction_payment"

    # Same structure as TransactionPaymentTemp
    id = Column(UUID, primary_key=True, default=uuid4)
    fk_transaction_head_id = Column(UUID, ForeignKey("transaction_head.id"), index=True)
    line_no = Column(Integer, nullable=False)
    payment_type = Column(String(50), nullable=False, index=True)
    payment_total = Column(Numeric(precision=15, scale=4), nullable=False)
    currency_code = Column(String(3), nullable=False)
    currency_total = Column(Numeric(precision=15, scale=4), nullable=False)
    currency_exchange_rate = Column(Numeric(precision=15, scale=6), nullable=False, default=1.0)
    installment_count = Column(Integer, nullable=False, default=1)
    payment_provider = Column(String(50), nullable=True)
    payment_gateway_transaction_id = Column(String(100), nullable=True, index=True)
    authorization_code = Column(String(50), nullable=True)
    approval_code = Column(String(50), nullable=True)
    card_number_masked = Column(String(20), nullable=True)
    card_type = Column(String(20), nullable=True)
    card_holder_name = Column(String(100), nullable=True)
    card_expiry_month = Column(Integer, nullable=True)
    card_expiry_year = Column(Integer, nullable=True)
    terminal_id = Column(String(50), nullable=True)
    merchant_id = Column(String(50), nullable=True)
    batch_number = Column(String(50), nullable=True)
    payment_status = Column(String(50), nullable=False, default="approved", index=True)
    payment_status_message = Column(String(500), nullable=True)
    payment_processed_at = Column(DateTime, nullable=True)
    gift_card_number = Column(String(50), nullable=True)
    gift_card_balance_before = Column(Numeric(precision=15, scale=4), nullable=True)
    gift_card_balance_after = Column(Numeric(precision=15, scale=4), nullable=True)
    voucher_code = Column(String(50), nullable=True)
    voucher_amount = Column(Numeric(precision=15, scale=4), nullable=True)
    wallet_type = Column(String(50), nullable=True)
    wallet_transaction_id = Column(String(100), nullable=True)
    bank_name = Column(String(100), nullable=True)
    bank_account_last4 = Column(String(4), nullable=True)
    bank_reference_number = Column(String(100), nullable=True)
    is_split_payment = Column(Boolean, nullable=False, default=False)
    split_payment_sequence = Column(Integer, nullable=True)
    tip_amount = Column(Numeric(precision=15, scale=4), nullable=False, default=0)
    tip_type = Column(String(20), nullable=True)
    refunded_amount = Column(Numeric(precision=15, scale=4), nullable=False, default=0)
    refunded_at = Column(DateTime, nullable=True)
    refund_reference = Column(String(100), nullable=True)
    is_cancel = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"<TransactionPayment(type='{self.payment_type}', amount='{self.payment_total}', status='{self.payment_status}')>"

    __table_args__ = (
        Index('idx_payment_transaction', 'fk_transaction_head_id'),
        Index('idx_payment_type', 'payment_type'),
        Index('idx_payment_status', 'payment_status'),
        Index('idx_payment_gateway_id', 'payment_gateway_transaction_id'),
    )