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

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, UUID
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD


class CashierTransactionMetrics(Model, CRUD):
    def __init__(self, fk_cashier_id=None, fk_transaction_head_id=None, 
                 fk_work_session_id=None, transaction_start_time=None, transaction_end_time=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.fk_cashier_id = fk_cashier_id
        self.fk_transaction_head_id = fk_transaction_head_id
        self.fk_work_session_id = fk_work_session_id
        self.transaction_start_time = transaction_start_time
        self.transaction_end_time = transaction_end_time

    __tablename__ = "cashier_transaction_metrics"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_cashier_id = Column(UUID, ForeignKey("cashier.id"), nullable=False)
    fk_transaction_head_id = Column(UUID, ForeignKey("transaction_head.id"), nullable=False)
    fk_work_session_id = Column(UUID, ForeignKey("cashier_work_session.id"), nullable=False)
    fk_store_id = Column(UUID, ForeignKey("store.id"), nullable=False)
    fk_customer_id = Column(UUID, ForeignKey("customer.id"), nullable=True)
    
    # Transaction timing metrics
    transaction_start_time = Column(DateTime, nullable=False)
    transaction_end_time = Column(DateTime, nullable=True)
    total_transaction_time = Column(Float, nullable=True)  # Total time in seconds
    
    # Detailed timing breakdown
    item_scanning_time = Column(Float, nullable=True)  # Time spent scanning items (seconds)
    payment_processing_time = Column(Float, nullable=True)  # Time spent processing payment (seconds)
    customer_interaction_time = Column(Float, nullable=True)  # Time spent interacting with customer (seconds)
    system_processing_time = Column(Float, nullable=True)  # Time spent on system operations (seconds)
    idle_time_during_transaction = Column(Float, nullable=True)  # Idle time during transaction (seconds)
    
    # Transaction complexity metrics
    number_of_items = Column(Integer, nullable=False, default=0)
    unique_product_count = Column(Integer, nullable=False, default=0)
    total_item_quantity = Column(Integer, nullable=False, default=0)
    number_of_barcodes_scanned = Column(Integer, nullable=False, default=0)
    number_of_manual_entries = Column(Integer, nullable=False, default=0)
    
    # Transaction value metrics
    transaction_total_amount = Column(Integer, nullable=False, default=0)  # In cents
    transaction_subtotal = Column(Integer, nullable=False, default=0)  # In cents
    transaction_tax_amount = Column(Integer, nullable=False, default=0)  # In cents
    transaction_discount_amount = Column(Integer, nullable=False, default=0)  # In cents
    average_item_price = Column(Float, nullable=True)  # In cents
    
    # Payment method metrics
    payment_method_used = Column(String(50), nullable=True)  # CASH, CARD, MOBILE, GIFT_CARD, MIXED
    number_of_payment_methods = Column(Integer, nullable=False, default=1)
    cash_payment_amount = Column(Integer, nullable=False, default=0)  # In cents
    card_payment_amount = Column(Integer, nullable=False, default=0)  # In cents
    mobile_payment_amount = Column(Integer, nullable=False, default=0)  # In cents
    change_given = Column(Integer, nullable=False, default=0)  # In cents
    
    # Customer service metrics
    customer_queue_wait_time = Column(Float, nullable=True)  # Time customer waited in queue (seconds)
    greeting_time = Column(Float, nullable=True)  # Time spent greeting customer (seconds)
    farewell_time = Column(Float, nullable=True)  # Time spent saying goodbye (seconds)
    customer_questions_answered = Column(Integer, nullable=False, default=0)
    product_recommendations_made = Column(Integer, nullable=False, default=0)
    
    # Efficiency metrics
    items_per_minute = Column(Float, nullable=True)
    scanning_speed = Column(Float, nullable=True)  # Items scanned per minute
    transaction_efficiency_score = Column(Float, nullable=True)  # 0-100 scale
    
    # Quality and accuracy metrics
    number_of_voids = Column(Integer, nullable=False, default=0)
    number_of_price_overrides = Column(Integer, nullable=False, default=0)
    number_of_quantity_changes = Column(Integer, nullable=False, default=0)
    number_of_supervisor_calls = Column(Integer, nullable=False, default=0)
    number_of_rescans = Column(Integer, nullable=False, default=0)
    number_of_system_errors = Column(Integer, nullable=False, default=0)
    
    # Error tracking
    scan_errors = Column(Integer, nullable=False, default=0)
    price_errors = Column(Integer, nullable=False, default=0)
    payment_errors = Column(Integer, nullable=False, default=0)
    discount_errors = Column(Integer, nullable=False, default=0)
    transaction_cancelled = Column(Boolean, nullable=False, default=False)
    cancellation_reason = Column(String(200), nullable=True)
    
    # Product and discount handling
    number_of_promotions_applied = Column(Integer, nullable=False, default=0)
    number_of_coupons_used = Column(Integer, nullable=False, default=0)
    loyalty_points_earned = Column(Integer, nullable=False, default=0)
    loyalty_points_redeemed = Column(Integer, nullable=False, default=0)
    
    # Technology usage
    barcode_scanner_used = Column(Boolean, nullable=False, default=False)
    keyboard_manual_entry_used = Column(Boolean, nullable=False, default=False)
    touch_screen_used = Column(Boolean, nullable=False, default=False)
    receipt_printer_used = Column(Boolean, nullable=False, default=True)
    customer_display_used = Column(Boolean, nullable=False, default=False)
    
    # Transaction flow metrics
    transaction_sequence_number = Column(Integer, nullable=False, default=0)  # Transaction number in session
    time_since_last_transaction = Column(Float, nullable=True)  # Seconds since last transaction
    time_until_next_transaction = Column(Float, nullable=True)  # Seconds until next transaction
    
    # Peak time indicators
    is_peak_hour = Column(Boolean, nullable=False, default=False)
    is_rush_period = Column(Boolean, nullable=False, default=False)
    queue_length_when_started = Column(Integer, nullable=False, default=0)
    store_occupancy_level = Column(String(20), nullable=True)  # LOW, MEDIUM, HIGH, VERY_HIGH
    
    # Performance indicators
    exceeded_expected_time = Column(Boolean, nullable=False, default=False)
    transaction_complexity_level = Column(String(20), nullable=False, default='MEDIUM')  # SIMPLE, MEDIUM, COMPLEX, VERY_COMPLEX
    customer_satisfaction_rating = Column(Integer, nullable=True)  # 1-5 scale
    
    # Special circumstances
    senior_citizen_discount = Column(Boolean, nullable=False, default=False)
    employee_discount = Column(Boolean, nullable=False, default=False)
    bulk_purchase = Column(Boolean, nullable=False, default=False)
    special_handling_required = Column(Boolean, nullable=False, default=False)
    special_handling_reason = Column(String(200), nullable=True)
    
    # Environmental factors
    weather_condition = Column(String(50), nullable=True)  # Impact on customer flow
    day_of_week = Column(String(10), nullable=True)  # MONDAY, TUESDAY, etc.
    hour_of_day = Column(Integer, nullable=True)  # 0-23
    
    # Learning and improvement
    training_opportunity_identified = Column(Boolean, nullable=False, default=False)
    training_topic = Column(String(200), nullable=True)
    improvement_suggestion = Column(String(500), nullable=True)
    
    # Notes and comments
    transaction_notes = Column(String(1000), nullable=True)
    customer_feedback = Column(String(1000), nullable=True)
    supervisor_comments = Column(String(1000), nullable=True)
    
    # Audit fields
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<CashierTransactionMetrics(cashier_id='{self.fk_cashier_id}', transaction_id='{self.fk_transaction_head_id}', start_time='{self.transaction_start_time}')>" 