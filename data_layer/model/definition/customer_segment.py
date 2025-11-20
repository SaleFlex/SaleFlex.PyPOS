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


class CustomerSegment(Model, CRUD, AuditMixin, SoftDeleteMixin):
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

    def __repr__(self):
        return f"<CustomerSegment(code='{self.code}', name='{self.name}', type='{self.segment_type}')>"

