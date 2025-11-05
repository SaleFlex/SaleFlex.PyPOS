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

from sqlalchemy import Column, String, Boolean, DateTime, UUID, Text, ForeignKey, Integer
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class Coupon(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Defines discount coupons linked to campaigns
    Supports single-use, multi-use, personal, and public coupons with various distribution methods
    """
    def __init__(self, code=None, name=None, description=None, fk_campaign_id=None,
                 coupon_type=None, fk_customer_id=None, start_date=None, end_date=None,
                 usage_limit=None, usage_count=0, is_active=True, barcode=None,
                 qr_code=None, is_sent=False, sent_date=None, sent_method=None,
                 fk_created_by=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.code = code
        self.name = name
        self.description = description
        self.fk_campaign_id = fk_campaign_id
        self.coupon_type = coupon_type
        self.fk_customer_id = fk_customer_id
        self.start_date = start_date
        self.end_date = end_date
        self.usage_limit = usage_limit
        self.usage_count = usage_count
        self.is_active = is_active
        self.barcode = barcode
        self.qr_code = qr_code
        self.is_sent = is_sent
        self.sent_date = sent_date
        self.sent_method = sent_method
        self.fk_created_by = fk_created_by

    __tablename__ = "coupon"

    id = Column(UUID, primary_key=True, default=uuid4)
    code = Column(String(100), nullable=False, unique=True)  # Unique coupon code for redemption
    name = Column(String(250), nullable=False)
    description = Column(Text, nullable=True)
    
    # Campaign association
    fk_campaign_id = Column(UUID, ForeignKey('campaign.id'), nullable=False)
    
    # Coupon classification
    coupon_type = Column(String(50), nullable=False)  # SINGLE_USE, MULTI_USE, PERSONAL, PUBLIC
    
    # Customer assignment (NULL = public coupon available to all)
    fk_customer_id = Column(UUID, ForeignKey('customer.id'), nullable=True)
    
    # Validity period
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    
    # Usage tracking
    usage_limit = Column(Integer, nullable=True)  # NULL = unlimited usage
    usage_count = Column(Integer, nullable=False, default=0)  # Current usage counter
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Digital formats for scanning
    barcode = Column(String(200), nullable=True)  # Barcode data
    qr_code = Column(Text, nullable=True)  # QR code data/URL
    
    # Distribution tracking
    is_sent = Column(Boolean, nullable=False, default=False)
    sent_date = Column(DateTime, nullable=True)
    sent_method = Column(String(50), nullable=True)  # SMS, EMAIL, PUSH, MANUAL
    
    # Note: created_by tracking is now handled by AuditMixin (fk_cashier_create_id)

    def __repr__(self):
        return f"<Coupon(code='{self.code}', name='{self.name}', type='{self.coupon_type}')>"

