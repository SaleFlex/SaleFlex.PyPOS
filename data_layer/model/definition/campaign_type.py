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

from sqlalchemy import Column, String, Boolean, DateTime, UUID, Text, Integer
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD


class CampaignType(Model, CRUD):
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
    
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<CampaignType(code='{self.code}', name='{self.name}')>"

