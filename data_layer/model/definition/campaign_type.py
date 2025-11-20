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

from sqlalchemy import Column, String, Boolean, DateTime, UUID, Text, Integer
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class CampaignType(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Defines types of promotional campaigns
    Examples: PRODUCT_DISCOUNT, BASKET_DISCOUNT, TIME_BASED, BUY_X_GET_Y, WELCOME_BONUS
    """
    def __init__(self, code=None, name=None, description=None, icon=None, 
                 is_active=True, display_order=0, settings_json=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.code = code
        self.name = name
        self.description = description
        self.icon = icon
        self.is_active = is_active
        self.display_order = display_order
        self.settings_json = settings_json

    __tablename__ = "campaign_type"

    id = Column(UUID, primary_key=True, default=uuid4)
    code = Column(String(50), nullable=False, unique=True)  
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)
    
    is_active = Column(Boolean, nullable=False, default=True)
    display_order = Column(Integer, nullable=False, default=0)
    
    # Type-specific settings stored as JSON
    settings_json = Column(Text, nullable=True)

    def __repr__(self):
        return f"<CampaignType(code='{self.code}', name='{self.name}')>"

