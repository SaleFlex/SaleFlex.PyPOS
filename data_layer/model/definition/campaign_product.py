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

from sqlalchemy import Column, String, Boolean, DateTime, UUID, ForeignKey, Numeric, Integer
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD


class CampaignProduct(Model, CRUD):
    """
    Links specific products to campaigns
    Allows product-specific discount configurations or identifies gift products
    """
    def __init__(self, fk_campaign_id=None, fk_product_id=None, is_gift_product=False,
                 min_quantity=None, max_quantity=None, discount_value=None,
                 discount_percentage=None, is_active=True, display_order=0):
        Model.__init__(self)
        CRUD.__init__(self)

        self.fk_campaign_id = fk_campaign_id
        self.fk_product_id = fk_product_id
        self.is_gift_product = is_gift_product
        self.min_quantity = min_quantity
        self.max_quantity = max_quantity
        self.discount_value = discount_value
        self.discount_percentage = discount_percentage
        self.is_active = is_active
        self.display_order = display_order

    __tablename__ = "campaign_product"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_campaign_id = Column(UUID, ForeignKey('campaign.id'), nullable=False)
    fk_product_id = Column(UUID, ForeignKey('product.id'), nullable=False)
    
    # Product role in the campaign
    is_gift_product = Column(Boolean, nullable=False, default=False)  # True if this product is the free gift
    
    # Quantity constraints
    min_quantity = Column(Integer, nullable=True)  # Minimum quantity required for campaign
    max_quantity = Column(Integer, nullable=True)  # Maximum quantity eligible for discount
    
    # Product-specific discount (overrides campaign's default discount)
    discount_value = Column(Numeric(18, 2), nullable=True)
    discount_percentage = Column(Numeric(5, 2), nullable=True)
    
    # Status and display
    is_active = Column(Boolean, nullable=False, default=True)
    display_order = Column(Integer, nullable=False, default=0)
    
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<CampaignProduct(campaign_id='{self.fk_campaign_id}', product_id='{self.fk_product_id}')>"

