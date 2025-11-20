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

from sqlalchemy import Column, String, Boolean, DateTime, UUID, Text, ForeignKey, Numeric, Integer, Date
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class LoyaltyPointTransaction(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Records all loyalty point movements (earned, redeemed, expired, adjusted)
    Provides complete audit trail of customer point balance changes
    """
    def __init__(self, fk_customer_loyalty_id=None, fk_customer_id=None, transaction_type=None,
                 points_amount=None, balance_after=None, fk_transaction_head_id=None,
                 fk_store_id=None, fk_cashier_id=None, transaction_date=None,
                 expiry_date=None, reference_number=None, description=None, notes=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.fk_customer_loyalty_id = fk_customer_loyalty_id
        self.fk_customer_id = fk_customer_id
        self.transaction_type = transaction_type
        self.points_amount = points_amount
        self.balance_after = balance_after
        self.fk_transaction_head_id = fk_transaction_head_id
        self.fk_store_id = fk_store_id
        self.fk_cashier_id = fk_cashier_id
        self.transaction_date = transaction_date
        self.expiry_date = expiry_date
        self.reference_number = reference_number
        self.description = description
        self.notes = notes

    __tablename__ = "loyalty_point_transaction"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_customer_loyalty_id = Column(UUID, ForeignKey('customer_loyalty.id'), nullable=False)
    fk_customer_id = Column(UUID, ForeignKey('customer.id'), nullable=False)
    
    # Transaction classification
    transaction_type = Column(String(50), nullable=False)  
    # EARNED, REDEEMED, EXPIRED, ADJUSTED, BONUS, WELCOME, BIRTHDAY, REFUND
    
    # Points movement (positive = earned/added, negative = redeemed/expired)
    points_amount = Column(Integer, nullable=False)
    balance_after = Column(Integer, nullable=False)  # Points balance after this transaction
    
    # Related entities
    fk_transaction_head_id = Column(UUID, ForeignKey('transaction_head.id'), nullable=True)  # Sale transaction if applicable
    fk_store_id = Column(UUID, ForeignKey('store.id'), nullable=True)
    fk_cashier_id = Column(UUID, ForeignKey('cashier.id'), nullable=True)
    
    # Transaction details
    transaction_date = Column(DateTime, server_default=func.now())
    expiry_date = Column(Date, nullable=True)  # When these points will expire (for EARNED transactions)
    reference_number = Column(String(100), nullable=True)  # External reference (receipt number, etc.)
    description = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<LoyaltyPointTransaction(customer_id='{self.fk_customer_id}', type='{self.transaction_type}', points={self.points_amount})>"

