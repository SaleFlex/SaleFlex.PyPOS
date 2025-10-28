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

from sqlalchemy import Column, String, Boolean, DateTime, UUID, ForeignKey, Numeric, Text
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD


class CampaignUsage(Model, CRUD):
    """
    Tracks campaign usage history for analytics and usage limit enforcement
    Records each time a campaign is applied to a transaction
    """
    def __init__(self, fk_campaign_id=None, fk_customer_id=None, fk_transaction_head_id=None,
                 fk_store_id=None, fk_cashier_id=None, discount_amount=None,
                 usage_date=None, coupon_code=None, notes=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.fk_campaign_id = fk_campaign_id
        self.fk_customer_id = fk_customer_id
        self.fk_transaction_head_id = fk_transaction_head_id
        self.fk_store_id = fk_store_id
        self.fk_cashier_id = fk_cashier_id
        self.discount_amount = discount_amount
        self.usage_date = usage_date
        self.coupon_code = coupon_code
        self.notes = notes

    __tablename__ = "campaign_usage"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_campaign_id = Column(UUID, ForeignKey('campaign.id'), nullable=False)
    fk_customer_id = Column(UUID, ForeignKey('customer.id'), nullable=True)  # NULL for anonymous purchases
    fk_transaction_head_id = Column(UUID, ForeignKey('transaction_head.id'), nullable=True)
    fk_store_id = Column(UUID, ForeignKey('store.id'), nullable=True)
    fk_cashier_id = Column(UUID, ForeignKey('cashier.id'), nullable=True)
    
    # Usage details
    discount_amount = Column(Numeric(18, 2), nullable=False)  # Total discount amount applied
    usage_date = Column(DateTime, server_default=func.now())
    coupon_code = Column(String(100), nullable=True)  # If campaign was activated via coupon
    notes = Column(Text, nullable=True)
    
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<CampaignUsage(campaign_id='{self.fk_campaign_id}', customer_id='{self.fk_customer_id}', amount={self.discount_amount})>"

