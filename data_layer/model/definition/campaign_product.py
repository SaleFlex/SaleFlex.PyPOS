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

from sqlalchemy import Column, String, Boolean, DateTime, UUID, ForeignKey, Numeric, Integer
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class CampaignProduct(Model, CRUD, AuditMixin, SoftDeleteMixin):
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

    def __repr__(self):
        return f"<CampaignProduct(campaign_id='{self.fk_campaign_id}', product_id='{self.fk_product_id}')>"

