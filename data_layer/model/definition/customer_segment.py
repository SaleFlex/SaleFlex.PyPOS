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


class CustomerSegment(Model, CRUD):
    """
    Defines customer segments for targeted marketing and campaigns
    Segments can be based on behavior, demographics, purchase patterns, etc.
    """
    def __init__(self, code=None, name=None, description=None, segment_type=None,
                 criteria_json=None, is_active=True, customer_count=0, 
                 display_order=0, color_code=None, icon=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.code = code
        self.name = name
        self.description = description
        self.segment_type = segment_type
        self.criteria_json = criteria_json
        self.is_active = is_active
        self.customer_count = customer_count
        self.display_order = display_order
        self.color_code = color_code
        self.icon = icon

    __tablename__ = "customer_segment"

    id = Column(UUID, primary_key=True, default=uuid4)
    code = Column(String(50), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Segment classification
    segment_type = Column(String(50), nullable=False)  
    # VIP, NEW_CUSTOMER, FREQUENT_BUYER, HIGH_VALUE, INACTIVE, BIRTHDAY, CUSTOM
    
    # Segment criteria stored as JSON
    # Example: {"min_annual_spending": 10000, "min_purchases": 50, "loyalty_tier": "GOLD"}
    criteria_json = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    customer_count = Column(Integer, nullable=False, default=0)  # Cached count of customers in segment
    
    # Display settings
    display_order = Column(Integer, nullable=False, default=0)
    color_code = Column(String(20), nullable=True)  # Hex color for UI
    icon = Column(String(100), nullable=True)
    
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<CustomerSegment(code='{self.code}', name='{self.name}', type='{self.segment_type}')>"

