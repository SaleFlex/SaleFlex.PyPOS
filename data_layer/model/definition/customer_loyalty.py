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

from sqlalchemy import Column, String, Boolean, DateTime, UUID, ForeignKey, Numeric, Integer, Date
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class CustomerLoyalty(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Stores customer's loyalty program membership details
    Tracks points balance, tier, and program participation
    """
    def __init__(self, fk_customer_id=None, fk_loyalty_program_id=None, fk_loyalty_tier_id=None,
                 loyalty_card_number=None, total_points=0, available_points=0, lifetime_points=0,
                 points_to_expire=0, points_expiry_date=None, enrollment_date=None,
                 last_activity_date=None, total_purchases=0, total_spent=None,
                 annual_spent=None, is_active=True):
        Model.__init__(self)
        CRUD.__init__(self)

        self.fk_customer_id = fk_customer_id
        self.fk_loyalty_program_id = fk_loyalty_program_id
        self.fk_loyalty_tier_id = fk_loyalty_tier_id
        self.loyalty_card_number = loyalty_card_number
        self.total_points = total_points
        self.available_points = available_points
        self.lifetime_points = lifetime_points
        self.points_to_expire = points_to_expire
        self.points_expiry_date = points_expiry_date
        self.enrollment_date = enrollment_date
        self.last_activity_date = last_activity_date
        self.total_purchases = total_purchases
        self.total_spent = total_spent
        self.annual_spent = annual_spent
        self.is_active = is_active

    __tablename__ = "customer_loyalty"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_customer_id = Column(UUID, ForeignKey('customer.id'), nullable=False, unique=True)
    fk_loyalty_program_id = Column(UUID, ForeignKey('loyalty_program.id'), nullable=False)
    fk_loyalty_tier_id = Column(UUID, ForeignKey('loyalty_tier.id'), nullable=True)  # Current tier
    
    # Card identification
    loyalty_card_number = Column(String(100), nullable=True, unique=True)  # Physical/digital card number
    
    # Points tracking
    total_points = Column(Integer, nullable=False, default=0)  # Current total points (including reserved)
    available_points = Column(Integer, nullable=False, default=0)  # Points available for redemption
    lifetime_points = Column(Integer, nullable=False, default=0)  # All-time points earned
    points_to_expire = Column(Integer, nullable=False, default=0)  # Points expiring soon
    points_expiry_date = Column(Date, nullable=True)  # Date when next points batch expires
    
    # Program participation
    enrollment_date = Column(DateTime, server_default=func.now())
    last_activity_date = Column(DateTime, nullable=True)  # Last transaction date
    
    # Purchase statistics
    total_purchases = Column(Integer, nullable=False, default=0)  # Total number of purchases
    total_spent = Column(Numeric(18, 2), nullable=True, default=0)  # Lifetime spending
    annual_spent = Column(Numeric(18, 2), nullable=True, default=0)  # Current year spending
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<CustomerLoyalty(customer_id='{self.fk_customer_id}', available_points={self.available_points})>"

