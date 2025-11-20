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

from sqlalchemy import Column, String, Boolean, DateTime, UUID, ForeignKey, Numeric, Text
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class CouponUsage(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Tracks coupon redemption history
    Records each time a coupon is used in a transaction
    """
    def __init__(self, fk_coupon_id=None, fk_customer_id=None, fk_transaction_head_id=None,
                 fk_store_id=None, fk_cashier_id=None, discount_amount=None,
                 usage_date=None, notes=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.fk_coupon_id = fk_coupon_id
        self.fk_customer_id = fk_customer_id
        self.fk_transaction_head_id = fk_transaction_head_id
        self.fk_store_id = fk_store_id
        self.fk_cashier_id = fk_cashier_id
        self.discount_amount = discount_amount
        self.usage_date = usage_date
        self.notes = notes

    __tablename__ = "coupon_usage"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_coupon_id = Column(UUID, ForeignKey('coupon.id'), nullable=False)
    fk_customer_id = Column(UUID, ForeignKey('customer.id'), nullable=True)
    fk_transaction_head_id = Column(UUID, ForeignKey('transaction_head.id'), nullable=True)
    fk_store_id = Column(UUID, ForeignKey('store.id'), nullable=True)
    fk_cashier_id = Column(UUID, ForeignKey('cashier.id'), nullable=True)
    
    # Usage details
    discount_amount = Column(Numeric(18, 2), nullable=False)  # Discount amount applied
    usage_date = Column(DateTime, server_default=func.now())
    notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<CouponUsage(coupon_id='{self.fk_coupon_id}', customer_id='{self.fk_customer_id}', amount={self.discount_amount})>"

