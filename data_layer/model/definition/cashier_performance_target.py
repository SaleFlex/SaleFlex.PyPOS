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

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, UUID, Date
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD


class CashierPerformanceTarget(Model, CRUD):
    def __init__(self, fk_cashier_id=None, fk_store_id=None, target_type=None, 
                 target_period=None, target_start_date=None, target_end_date=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.fk_cashier_id = fk_cashier_id
        self.fk_store_id = fk_store_id
        self.target_type = target_type
        self.target_period = target_period
        self.target_start_date = target_start_date
        self.target_end_date = target_end_date

    __tablename__ = "cashier_performance_target"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_cashier_id = Column(UUID, ForeignKey("cashier.id"), nullable=False)
    fk_store_id = Column(UUID, ForeignKey("store.id"), nullable=False)
    fk_supervisor_id = Column(UUID, ForeignKey("cashier.id"), nullable=True)
    
    # Target period information
    target_type = Column(String(20), nullable=False)  # INDIVIDUAL, TEAM, STORE, COMPANY
    target_period = Column(String(20), nullable=False)  # DAILY, WEEKLY, MONTHLY, QUARTERLY, YEARLY
    target_start_date = Column(Date, nullable=False)
    target_end_date = Column(Date, nullable=False)
    target_year = Column(Integer, nullable=False)
    target_month = Column(Integer, nullable=True)  # 1-12
    target_week = Column(Integer, nullable=True)  # 1-52
    
    # Sales performance targets
    target_total_sales = Column(Integer, nullable=True)  # In cents
    target_daily_sales = Column(Integer, nullable=True)  # In cents
    target_transactions_count = Column(Integer, nullable=True)
    target_items_sold = Column(Integer, nullable=True)
    target_customers_served = Column(Integer, nullable=True)
    target_average_transaction_amount = Column(Integer, nullable=True)  # In cents
    
    # Efficiency targets
    target_transactions_per_hour = Column(Float, nullable=True)
    target_sales_per_hour = Column(Integer, nullable=True)  # In cents
    target_items_per_hour = Column(Float, nullable=True)
    target_customers_per_hour = Column(Float, nullable=True)
    target_average_transaction_time = Column(Float, nullable=True)  # In seconds
    target_working_hours = Column(Float, nullable=True)
    
    # Quality and accuracy targets
    target_void_rate = Column(Float, nullable=True)  # Maximum percentage
    target_return_rate = Column(Float, nullable=True)  # Maximum percentage
    target_error_rate = Column(Float, nullable=True)  # Maximum percentage
    target_accuracy_score = Column(Float, nullable=True)  # Minimum score (0-100)
    target_customer_satisfaction = Column(Float, nullable=True)  # Minimum score (1-5)
    
    # Productivity and scoring targets
    target_productivity_score = Column(Float, nullable=True)  # Minimum score (0-100)
    target_efficiency_score = Column(Float, nullable=True)  # Minimum score (0-100)
    target_service_quality_score = Column(Float, nullable=True)  # Minimum score (0-100)
    
    # Behavioral targets
    target_punctuality_score = Column(Float, nullable=True)  # Minimum score (0-100)
    target_attendance_rate = Column(Float, nullable=True)  # Minimum percentage
    target_break_compliance = Column(Float, nullable=True)  # Minimum percentage
    max_late_arrivals = Column(Integer, nullable=True)  # Maximum allowed late arrivals
    max_early_departures = Column(Integer, nullable=True)  # Maximum allowed early departures
    
    # Training and development targets
    target_training_hours = Column(Float, nullable=True)
    target_skill_assessments = Column(Integer, nullable=True)
    target_certification_completion = Column(Float, nullable=True)  # Percentage
    
    # Team collaboration targets
    target_team_support_score = Column(Float, nullable=True)  # Minimum score (0-100)
    target_knowledge_sharing = Column(Integer, nullable=True)  # Number of sessions
    target_mentoring_hours = Column(Float, nullable=True)
    
    # Payment method targets
    target_cash_handling_accuracy = Column(Float, nullable=True)  # Minimum percentage
    target_card_payment_processing = Column(Float, nullable=True)  # Minimum percentage
    target_digital_payment_adoption = Column(Float, nullable=True)  # Minimum percentage
    
    # Target difficulty and priority
    target_difficulty_level = Column(String(20), nullable=False, default='MEDIUM')  # EASY, MEDIUM, HARD, CHALLENGING
    target_priority = Column(String(20), nullable=False, default='MEDIUM')  # LOW, MEDIUM, HIGH, CRITICAL
    is_mandatory = Column(Boolean, nullable=False, default=False)
    is_achievable = Column(Boolean, nullable=False, default=True)
    
    # Incentive and reward information
    incentive_type = Column(String(30), nullable=True)  # BONUS, COMMISSION, RECOGNITION, PROMOTION, GIFT
    incentive_amount = Column(Integer, nullable=True)  # In cents
    incentive_description = Column(String(500), nullable=True)
    penalty_type = Column(String(30), nullable=True)  # WARNING, TRAINING, COUNSELING, REVIEW
    penalty_description = Column(String(500), nullable=True)
    
    # Progress tracking
    current_achievement_percentage = Column(Float, nullable=False, default=0.0)
    last_measurement_date = Column(Date, nullable=True)
    is_on_track = Column(Boolean, nullable=False, default=True)
    projected_completion_date = Column(Date, nullable=True)
    
    # Target adjustment information
    is_adjusted = Column(Boolean, nullable=False, default=False)
    adjustment_reason = Column(String(1000), nullable=True)
    adjustment_date = Column(Date, nullable=True)
    adjusted_by = Column(UUID, ForeignKey("cashier.id"), nullable=True)
    original_target_value = Column(String(100), nullable=True)  # JSON string of original targets
    
    # Status and lifecycle
    target_status = Column(String(20), nullable=False, default='ACTIVE')  # ACTIVE, COMPLETED, CANCELLED, SUSPENDED, EXPIRED
    is_completed = Column(Boolean, nullable=False, default=False)
    completion_date = Column(Date, nullable=True)
    completion_percentage = Column(Float, nullable=True)
    
    # Review and feedback
    review_frequency = Column(String(20), nullable=False, default='WEEKLY')  # DAILY, WEEKLY, MONTHLY
    next_review_date = Column(Date, nullable=True)
    supervisor_feedback = Column(String(2000), nullable=True)
    cashier_feedback = Column(String(2000), nullable=True)
    
    # Context and environment
    market_conditions = Column(String(500), nullable=True)
    seasonal_factors = Column(String(500), nullable=True)
    special_events = Column(String(500), nullable=True)
    
    # Notes and comments
    target_description = Column(String(1000), nullable=True)
    target_rationale = Column(String(1000), nullable=True)
    success_criteria = Column(String(1000), nullable=True)
    measurement_method = Column(String(500), nullable=True)
    
    # Audit fields
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    fk_cashier_create_id = Column(UUID, ForeignKey("cashier.id"), nullable=True)
    fk_cashier_update_id = Column(UUID, ForeignKey("cashier.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<CashierPerformanceTarget(cashier_id='{self.fk_cashier_id}', target_type='{self.target_type}', period='{self.target_period}')>" 