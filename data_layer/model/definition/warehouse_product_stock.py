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

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, UUID, Date, Numeric
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class WarehouseProductStock(Model, CRUD, AuditMixin, SoftDeleteMixin):
    def __init__(self, fk_product_id=None, fk_warehouse_location_id=None, quantity=0):
        Model.__init__(self)
        CRUD.__init__(self)

        self.fk_product_id = fk_product_id
        self.fk_warehouse_location_id = fk_warehouse_location_id
        self.quantity = quantity

    __tablename__ = "warehouse_product_stock"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_server_id = Column(Integer, nullable=True)  # For server synchronization
    
    # Core relationships
    fk_product_id = Column(UUID, ForeignKey("product.id"), nullable=False)
    fk_product_variant_id = Column(UUID, ForeignKey("product_variant.id"), nullable=True)
    fk_warehouse_location_id = Column(UUID, ForeignKey("warehouse_location.id"), nullable=False)
    
    # Stock quantities
    quantity = Column(Integer, nullable=False, default=0)  # Current stock quantity
    available_quantity = Column(Integer, nullable=False, default=0)  # Available for sale
    reserved_quantity = Column(Integer, nullable=False, default=0)  # Reserved for orders
    damaged_quantity = Column(Integer, nullable=False, default=0)  # Damaged items
    expired_quantity = Column(Integer, nullable=False, default=0)  # Expired items
    
    # Replenishment levels
    min_stock_level = Column(Integer, nullable=False, default=0)  # Minimum stock level
    max_stock_level = Column(Integer, nullable=False, default=0)  # Maximum stock level
    reorder_point = Column(Integer, nullable=False, default=0)  # Reorder point
    reorder_quantity = Column(Integer, nullable=False, default=0)  # Reorder quantity
    
    # Cost information
    average_cost = Column(Numeric(precision=15, scale=4), nullable=True, default=0.0)  # Average cost per unit
    last_cost = Column(Numeric(precision=15, scale=4), nullable=True, default=0.0)  # Last purchase cost
    total_value = Column(Numeric(precision=15, scale=4), nullable=True, default=0.0)  # Total stock value
    
    # Lot and expiration tracking
    lot_number = Column(String(50), nullable=True)  # Lot number
    expiration_date = Column(Date, nullable=True)  # Expiration date
    production_date = Column(Date, nullable=True)  # Production date
    
    # Physical properties
    weight_per_unit = Column(Float, nullable=True)  # Weight per unit in kg
    volume_per_unit = Column(Float, nullable=True)  # Volume per unit in cubic meters
    total_weight = Column(Float, nullable=True)  # Total weight
    total_volume = Column(Float, nullable=True)  # Total volume
    
    # Last movement tracking
    last_received_date = Column(DateTime, nullable=True)  # Last received date
    last_sold_date = Column(DateTime, nullable=True)  # Last sold date
    last_movement_date = Column(DateTime, nullable=True)  # Last movement date
    last_count_date = Column(DateTime, nullable=True)  # Last physical count date
    
    # Movement statistics
    total_received = Column(Integer, nullable=False, default=0)  # Total units received
    total_sold = Column(Integer, nullable=False, default=0)  # Total units sold
    total_adjusted = Column(Integer, nullable=False, default=0)  # Total units adjusted
    
    # Velocity and turnover
    avg_daily_sales = Column(Float, nullable=True, default=0.0)  # Average daily sales
    days_of_supply = Column(Float, nullable=True, default=0.0)  # Days of supply
    turnover_rate = Column(Float, nullable=True, default=0.0)  # Inventory turnover rate
    
    # Retail specific fields
    display_quantity = Column(Integer, nullable=False, default=0)  # Units on display
    backroom_quantity = Column(Integer, nullable=False, default=0)  # Units in backroom
    facing_quantity = Column(Integer, nullable=False, default=0)  # Units facing customers
    
    # Alerts and notifications
    low_stock_alert = Column(Boolean, nullable=False, default=False)  # Low stock alert
    overstock_alert = Column(Boolean, nullable=False, default=False)  # Overstock alert
    expiry_alert = Column(Boolean, nullable=False, default=False)  # Expiry alert
    slow_moving_alert = Column(Boolean, nullable=False, default=False)  # Slow moving alert
    
    # Seasonal and promotional
    is_seasonal_item = Column(Boolean, nullable=False, default=False)  # Is seasonal item
    is_promotional = Column(Boolean, nullable=False, default=False)  # Is promotional item
    promotional_start_date = Column(Date, nullable=True)  # Promotion start date
    promotional_end_date = Column(Date, nullable=True)  # Promotion end date
    
    # Status flags
    is_active = Column(Boolean, nullable=False, default=True)  # Is active
    is_discontinued = Column(Boolean, nullable=False, default=False)  # Is discontinued
    is_blocked = Column(Boolean, nullable=False, default=False)  # Is blocked for sales
    block_reason = Column(String(200), nullable=True)  # Block reason
    
    # Unique constraint to prevent duplicate entries
    __table_args__ = (
        {'extend_existing': True}
    )
    
    def __repr__(self):
        return f"<WarehouseProductStock(product_id='{self.fk_product_id}', location_id='{self.fk_warehouse_location_id}', quantity='{self.quantity}')>" 