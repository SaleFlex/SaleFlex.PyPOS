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

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, UUID, Text, Numeric
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class WarehouseStockMovement(Model, CRUD, AuditMixin, SoftDeleteMixin):
    def __init__(self, fk_product_id=None, movement_type=None, quantity=0):
        Model.__init__(self)
        CRUD.__init__(self)

        self.fk_product_id = fk_product_id
        self.movement_type = movement_type
        self.quantity = quantity

    __tablename__ = "warehouse_stock_movement"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_server_id = Column(Integer, nullable=True)  # For server synchronization
    movement_number = Column(String(50), nullable=False, unique=True)  # Movement reference number
    
    # Core relationships
    fk_product_id = Column(UUID, ForeignKey("product.id"), nullable=False)
    fk_product_variant_id = Column(UUID, ForeignKey("product_variant.id"), nullable=True)
    fk_warehouse_location_from = Column(UUID, ForeignKey("warehouse_location.id"), nullable=True)
    fk_warehouse_location_to = Column(UUID, ForeignKey("warehouse_location.id"), nullable=True)
    
    # Movement details
    movement_type = Column(String(50), nullable=False)  # RECEIPT, SALE, TRANSFER, ADJUSTMENT, RETURN, LOSS, DAMAGE
    movement_subtype = Column(String(50), nullable=True)  # PURCHASE, CUSTOMER_RETURN, SUPPLIER_RETURN, CYCLE_COUNT, etc.
    quantity = Column(Integer, nullable=False)  # Quantity moved (positive for increases, negative for decreases)
    unit_cost = Column(Numeric(precision=15, scale=4), nullable=True)  # Cost per unit
    total_cost = Column(Numeric(precision=15, scale=4), nullable=True)  # Total cost of movement
    
    # Transaction references
    fk_transaction_head_id = Column(UUID, ForeignKey("transaction_head.id"), nullable=True)
    fk_transaction_product_id = Column(UUID, ForeignKey("transaction_product.id"), nullable=True)
    reference_document = Column(String(100), nullable=True)  # PO number, invoice number, etc.
    
    # Timing
    movement_date = Column(DateTime, nullable=False, default=func.now())
    scheduled_date = Column(DateTime, nullable=True)  # Scheduled movement date
    
    # Status and tracking
    status = Column(String(50), nullable=False, default='PENDING')  # PENDING, COMPLETED, CANCELLED, REVERSED
    is_reversed = Column(Boolean, nullable=False, default=False)
    reversal_reason = Column(String(200), nullable=True)
    parent_movement_id = Column(UUID, ForeignKey("warehouse_stock_movement.id"), nullable=True)  # For reversals
    
    # Reason and description
    reason = Column(String(200), nullable=True)  # Reason for movement
    description = Column(Text, nullable=True)  # Detailed description
    
    # Batch and lot tracking
    lot_number = Column(String(50), nullable=True)
    batch_number = Column(String(50), nullable=True)
    expiration_date = Column(DateTime, nullable=True)
    
    # Supplier/Customer information
    supplier_name = Column(String(100), nullable=True)
    supplier_invoice = Column(String(50), nullable=True)
    fk_customer_id = Column(UUID, ForeignKey("customer.id"), nullable=True)
    
    # Physical properties
    weight_per_unit = Column(Float, nullable=True)  # Weight per unit in kg
    total_weight = Column(Float, nullable=True)  # Total weight moved
    
    # Before and after quantities (for audit trail)
    quantity_before = Column(Integer, nullable=True)  # Quantity before movement
    quantity_after = Column(Integer, nullable=True)  # Quantity after movement
    
    # Approval and authorization
    requires_approval = Column(Boolean, nullable=False, default=False)
    is_approved = Column(Boolean, nullable=False, default=False)
    approved_by = Column(UUID, ForeignKey("cashier.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Quality control
    quality_check_required = Column(Boolean, nullable=False, default=False)
    quality_check_passed = Column(Boolean, nullable=True)
    quality_check_notes = Column(String(500), nullable=True)
    
    # Retail specific fields
    movement_category = Column(String(50), nullable=True)  # DISPLAY_REPLENISHMENT, BACKROOM_RECEIPT, etc.
    is_customer_visible = Column(Boolean, nullable=False, default=False)  # Is movement visible to customers
    
    # Seasonal and promotional
    is_promotional_movement = Column(Boolean, nullable=False, default=False)
    promotion_code = Column(String(50), nullable=True)
    
    # System fields
    is_system_generated = Column(Boolean, nullable=False, default=False)  # System vs manual movement
    source_system = Column(String(50), nullable=True)  # Source system (POS, WMS, etc.)
    
    # Exception handling
    has_exception = Column(Boolean, nullable=False, default=False)
    exception_type = Column(String(50), nullable=True)  # OVERAGE, SHORTAGE, DAMAGE, etc.
    exception_notes = Column(String(500), nullable=True)
    
    # Performance metrics
    processing_time = Column(Float, nullable=True)  # Time taken to process movement
    
    def __repr__(self):
        return f"<WarehouseStockMovement(movement_number='{self.movement_number}', type='{self.movement_type}', quantity='{self.quantity}')>" 