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

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, UUID, Text
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD


class WarehouseStockAdjustment(Model, CRUD):
    def __init__(self, fk_product_id=None, adjustment_type=None, quantity_difference=0):
        Model.__init__(self)
        CRUD.__init__(self)

        self.fk_product_id = fk_product_id
        self.adjustment_type = adjustment_type
        self.quantity_difference = quantity_difference

    __tablename__ = "warehouse_stock_adjustment"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_server_id = Column(Integer, nullable=True)  # For server synchronization
    adjustment_number = Column(String(50), nullable=False, unique=True)  # Adjustment reference number
    
    # Core relationships
    fk_product_id = Column(UUID, ForeignKey("product.id"), nullable=False)
    fk_product_variant_id = Column(UUID, ForeignKey("product_variant.id"), nullable=True)
    fk_warehouse_location_id = Column(UUID, ForeignKey("warehouse_location.id"), nullable=False)
    fk_warehouse_stock_movement_id = Column(UUID, ForeignKey("warehouse_stock_movement.id"), nullable=True)
    
    # Adjustment details
    adjustment_type = Column(String(50), nullable=False)  # CYCLE_COUNT, PHYSICAL_COUNT, LOSS, DAMAGE, FOUND, WRITE_OFF
    adjustment_reason = Column(String(100), nullable=True)  # THEFT, DAMAGE, EXPIRY, SYSTEM_ERROR, etc.
    
    # Quantities
    system_quantity = Column(Integer, nullable=False)  # Quantity according to system
    counted_quantity = Column(Integer, nullable=False)  # Quantity actually counted
    quantity_difference = Column(Integer, nullable=False)  # Difference (counted - system)
    
    # Cost impact
    unit_cost = Column(Float, nullable=True)  # Cost per unit
    total_cost_impact = Column(Float, nullable=True)  # Total cost impact of adjustment
    
    # Count details
    count_date = Column(DateTime, nullable=False, default=func.now())
    count_method = Column(String(50), nullable=True)  # MANUAL, BARCODE_SCAN, RFID, etc.
    is_blind_count = Column(Boolean, nullable=False, default=False)  # Was system quantity hidden during count?
    
    # Approval workflow
    status = Column(String(50), nullable=False, default='PENDING')  # PENDING, APPROVED, REJECTED, PROCESSED
    requires_approval = Column(Boolean, nullable=False, default=True)
    approved_by = Column(UUID, ForeignKey("cashier.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(String(200), nullable=True)
    
    # Variance analysis
    variance_percentage = Column(Float, nullable=True)  # Percentage variance
    is_significant_variance = Column(Boolean, nullable=False, default=False)
    variance_threshold = Column(Float, nullable=True)  # Threshold for significant variance
    
    # Cycle count information
    cycle_count_schedule_id = Column(UUID, nullable=True)  # Reference to cycle count schedule
    is_scheduled_count = Column(Boolean, nullable=False, default=False)
    count_frequency = Column(String(50), nullable=True)  # DAILY, WEEKLY, MONTHLY, QUARTERLY, etc.
    
    # Investigation and resolution
    investigation_required = Column(Boolean, nullable=False, default=False)
    investigation_notes = Column(Text, nullable=True)
    is_investigated = Column(Boolean, nullable=False, default=False)
    investigated_by = Column(UUID, ForeignKey("cashier.id"), nullable=True)
    investigated_at = Column(DateTime, nullable=True)
    
    # Root cause analysis
    root_cause = Column(String(200), nullable=True)  # Identified root cause
    corrective_action = Column(String(500), nullable=True)  # Corrective action taken
    preventive_action = Column(String(500), nullable=True)  # Preventive action to avoid recurrence
    
    # Batch and lot information
    lot_number = Column(String(50), nullable=True)
    batch_number = Column(String(50), nullable=True)
    expiration_date = Column(DateTime, nullable=True)
    
    # Quality information
    condition_code = Column(String(20), nullable=True)  # GOOD, DAMAGED, EXPIRED, etc.
    quality_notes = Column(String(500), nullable=True)
    
    # Retail specific fields
    location_accuracy = Column(Float, nullable=True)  # Accuracy of location count
    is_customer_visible_area = Column(Boolean, nullable=False, default=False)
    impact_on_sales = Column(Boolean, nullable=False, default=False)
    
    # Seasonal and promotional impact
    is_promotional_item = Column(Boolean, nullable=False, default=False)
    promotion_code = Column(String(50), nullable=True)
    seasonal_factor = Column(Float, nullable=True)  # Seasonal adjustment factor
    
    # Performance metrics
    count_accuracy = Column(Float, nullable=True)  # Accuracy of the count
    count_time = Column(Float, nullable=True)  # Time taken for count in minutes
    recount_required = Column(Boolean, nullable=False, default=False)
    recount_count = Column(Integer, nullable=False, default=0)
    
    # System integration
    is_system_generated = Column(Boolean, nullable=False, default=False)
    source_system = Column(String(50), nullable=True)  # Source system
    
    # Audit trail
    original_counted_quantity = Column(Integer, nullable=True)  # Original count before any recounts
    adjustment_history = Column(Text, nullable=True)  # JSON history of adjustments
    
    # Notification and alerts
    notification_sent = Column(Boolean, nullable=False, default=False)
    alert_level = Column(String(20), nullable=True)  # LOW, MEDIUM, HIGH, CRITICAL
    
    # Comments and notes
    counter_notes = Column(Text, nullable=True)  # Notes from the person who counted
    supervisor_notes = Column(Text, nullable=True)  # Notes from supervisor
    system_notes = Column(Text, nullable=True)  # System generated notes
    
    # Audit fields
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    fk_cashier_create_id = Column(UUID, ForeignKey("cashier.id"))
    fk_cashier_update_id = Column(UUID, ForeignKey("cashier.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<WarehouseStockAdjustment(adjustment_number='{self.adjustment_number}', type='{self.adjustment_type}', difference='{self.quantity_difference}')>" 