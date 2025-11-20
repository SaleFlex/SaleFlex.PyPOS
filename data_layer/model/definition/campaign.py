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

from sqlalchemy import Column, String, Boolean, DateTime, UUID, Text, ForeignKey, Numeric, Integer, Time
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class Campaign(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Defines promotional campaigns with various discount types and complex rules
    Supports store-specific, time-based, and customer-targeted campaigns
    """
    def __init__(self, code=None, name=None, description=None, fk_campaign_type_id=None,
                 fk_store_id=None, discount_type=None, discount_value=None, 
                 discount_percentage=None, max_discount_amount=None, min_purchase_amount=None,
                 max_purchase_amount=None, buy_quantity=None, get_quantity=None,
                 start_date=None, end_date=None, start_time=None, end_time=None, 
                 days_of_week=None, priority=1, is_combinable=False, 
                 usage_limit_per_customer=None, total_usage_limit=None, 
                 total_usage_count=0, is_active=True, is_auto_apply=False, 
                 requires_coupon=False, fk_customer_segment_id=None, image_url=None, 
                 terms_conditions=None, notification_message=None, settings_json=None,
                 fk_created_by=None, fk_updated_by=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.code = code
        self.name = name
        self.description = description
        self.fk_campaign_type_id = fk_campaign_type_id
        self.fk_store_id = fk_store_id
        self.discount_type = discount_type
        self.discount_value = discount_value
        self.discount_percentage = discount_percentage
        self.max_discount_amount = max_discount_amount
        self.min_purchase_amount = min_purchase_amount
        self.max_purchase_amount = max_purchase_amount
        self.buy_quantity = buy_quantity
        self.get_quantity = get_quantity
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.end_time = end_time
        self.days_of_week = days_of_week
        self.priority = priority
        self.is_combinable = is_combinable
        self.usage_limit_per_customer = usage_limit_per_customer
        self.total_usage_limit = total_usage_limit
        self.total_usage_count = total_usage_count
        self.is_active = is_active
        self.is_auto_apply = is_auto_apply
        self.requires_coupon = requires_coupon
        self.fk_customer_segment_id = fk_customer_segment_id
        self.image_url = image_url
        self.terms_conditions = terms_conditions
        self.notification_message = notification_message
        self.settings_json = settings_json
        self.fk_created_by = fk_created_by
        self.fk_updated_by = fk_updated_by

    __tablename__ = "campaign"

    id = Column(UUID, primary_key=True, default=uuid4)
    code = Column(String(50), nullable=False, unique=True)
    name = Column(String(250), nullable=False)
    description = Column(Text, nullable=True)
    
    fk_campaign_type_id = Column(UUID, ForeignKey('campaign_type.id'), nullable=False)
    fk_store_id = Column(UUID, ForeignKey('store.id'), nullable=True)  # NULL = applies to all stores
    
    # Discount configuration
    discount_type = Column(String(50), nullable=True)  # PERCENTAGE, FIXED_AMOUNT, FREE_PRODUCT, BUY_X_GET_Y, CHEAPEST_FREE
    discount_value = Column(Numeric(18, 2), nullable=True)
    discount_percentage = Column(Numeric(5, 2), nullable=True)  # Range: 0-100
    max_discount_amount = Column(Numeric(18, 2), nullable=True)
    
    # Purchase requirements
    min_purchase_amount = Column(Numeric(18, 2), nullable=True)
    max_purchase_amount = Column(Numeric(18, 2), nullable=True)
    buy_quantity = Column(Integer, nullable=True)  # For "Buy X Get Y" campaigns
    get_quantity = Column(Integer, nullable=True)  # For "Buy X Get Y" campaigns
    
    # Time-based restrictions
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    start_time = Column(Time, nullable=True)  # Daily start time (e.g., 15:00 for happy hour)
    end_time = Column(Time, nullable=True)  # Daily end time (e.g., 18:00)
    days_of_week = Column(String(50), nullable=True)  # Comma-separated: 1,2,3,4,5,6,7 (Monday-Sunday)
    
    # Application rules
    priority = Column(Integer, nullable=False, default=1)  # Higher value = applied first
    is_combinable = Column(Boolean, nullable=False, default=False)  # Can be combined with other campaigns
    
    # Usage restrictions
    usage_limit_per_customer = Column(Integer, nullable=True)  # NULL = unlimited per customer
    total_usage_limit = Column(Integer, nullable=True)  # NULL = unlimited total usage
    total_usage_count = Column(Integer, nullable=False, default=0)  # Current usage counter
    
    # Activation settings
    is_active = Column(Boolean, nullable=False, default=True)
    is_auto_apply = Column(Boolean, nullable=False, default=False)  # Auto-apply without requiring coupon
    requires_coupon = Column(Boolean, nullable=False, default=False)  # Requires coupon code to activate
    
    # Customer targeting
    fk_customer_segment_id = Column(UUID, ForeignKey('customer_segment.id'), nullable=True)  # NULL = all customers
    
    # Marketing assets
    image_url = Column(String(500), nullable=True)
    terms_conditions = Column(Text, nullable=True)
    notification_message = Column(Text, nullable=True)  # Message for SMS/Email/Push notifications
    
    # Additional custom settings stored as JSON
    settings_json = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Campaign(code='{self.code}', name='{self.name}', is_active={self.is_active})>"

