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

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, UUID
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class WarehouseLocation(Model, CRUD, AuditMixin, SoftDeleteMixin):
    def __init__(self, name=None, code=None, location_type=None, fk_warehouse_id=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.name = name
        self.code = code
        self.location_type = location_type
        self.fk_warehouse_id = fk_warehouse_id

    __tablename__ = "warehouse_location"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_server_id = Column(Integer, nullable=True)  # For server synchronization
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False, unique=True)
    description = Column(String(500), nullable=True)
    
    # Location type for retail organization
    location_type = Column(String(50), nullable=False)  # AISLE, SHELF, RACK, ZONE, BAY, LEVEL, DISPLAY, COUNTER, GONDOLA
    
    # Hierarchical structure
    parent_location_id = Column(UUID, ForeignKey("warehouse_location.id"), nullable=True)
    level = Column(Integer, nullable=False, default=1)  # 1=Zone, 2=Aisle, 3=Shelf, 4=Position
    
    # Physical dimensions and positioning
    x_coordinate = Column(Float, nullable=True)  # X position in warehouse layout
    y_coordinate = Column(Float, nullable=True)  # Y position in warehouse layout
    z_coordinate = Column(Float, nullable=True)  # Z position (height level)
    
    # Size information
    length = Column(Float, nullable=True)  # Length in meters
    width = Column(Float, nullable=True)  # Width in meters
    height = Column(Float, nullable=True)  # Height in meters
    volume = Column(Float, nullable=True)  # Volume in cubic meters
    max_weight = Column(Float, nullable=True)  # Maximum weight capacity in kg
    
    # Retail specific properties
    aisle_number = Column(String(10), nullable=True)  # Aisle number (A1, A2, etc.)
    shelf_level = Column(Integer, nullable=True)  # Shelf level (1=bottom, 2=middle, 3=top, etc.)
    bay_position = Column(String(10), nullable=True)  # Position within aisle (01, 02, etc.)
    facing_count = Column(Integer, nullable=True)  # Number of product facings
    
    # Display properties
    is_display_location = Column(Boolean, nullable=False, default=False)  # Is this a customer-facing display?
    is_customer_accessible = Column(Boolean, nullable=False, default=False)  # Can customers access this location?
    is_promotional_area = Column(Boolean, nullable=False, default=False)  # Is this a promotional display area?
    
    # Capacity and utilization
    max_items = Column(Integer, nullable=True)  # Maximum number of items
    current_utilization = Column(Float, nullable=True)  # Current utilization percentage
    
    # Special handling requirements
    requires_refrigeration = Column(Boolean, nullable=False, default=False)
    requires_freezing = Column(Boolean, nullable=False, default=False)
    fragile_items_only = Column(Boolean, nullable=False, default=False)
    high_value_items_only = Column(Boolean, nullable=False, default=False)
    restricted_access = Column(Boolean, nullable=False, default=False)
    
    # Picking and replenishment
    is_pick_location = Column(Boolean, nullable=False, default=True)  # Can items be picked from here?
    is_replenishment_location = Column(Boolean, nullable=False, default=True)  # Can items be replenished here?
    pick_sequence = Column(Integer, nullable=True)  # Sequence for picking optimization
    replenishment_priority = Column(Integer, nullable=True)  # Priority for replenishment
    
    # Cycle counting
    last_cycle_count_date = Column(DateTime, nullable=True)
    cycle_count_frequency = Column(Integer, nullable=True)  # Days between cycle counts
    
    # Status and operational info
    is_active = Column(Boolean, nullable=False, default=True)
    is_blocked = Column(Boolean, nullable=False, default=False)  # Temporarily blocked for maintenance
    block_reason = Column(String(200), nullable=True)  # Reason for blocking
    
    # Relationships
    fk_warehouse_id = Column(UUID, ForeignKey("warehouse.id"), nullable=False)
    
    def __repr__(self):
        return f"<WarehouseLocation(name='{self.name}', code='{self.code}', type='{self.location_type}')>" 