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

