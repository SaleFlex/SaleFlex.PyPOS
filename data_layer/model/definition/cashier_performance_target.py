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
    def __init__(self, fk_cashier_id=None, fk_store_id=None, fk_supervisor_id=None,
                 target_type=None, target_period=None, target_start_date=None, target_end_date=None,
                 target_year=None, target_month=None, target_week=None,
                 target_total_sales=None, target_daily_sales=None, target_transactions_count=None,
                 target_items_sold=None, target_customers_served=None, target_average_transaction_amount=None,
                 target_transactions_per_hour=None, target_sales_per_hour=None, target_items_per_hour=None,
                 target_customers_per_hour=None, target_average_transaction_time=None, target_working_hours=None,
                 target_void_rate=None, target_return_rate=None, target_error_rate=None,
                 target_accuracy_score=None, target_customer_satisfaction=None,
                 target_productivity_score=None, target_efficiency_score=None, target_service_quality_score=None,
                 target_punctuality_score=None, target_attendance_rate=None, target_break_compliance=None,
                 max_late_arrivals=None, max_early_departures=None,
                 target_training_hours=None, target_skill_assessments=None, target_certification_completion=None,
                 target_team_support_score=None, target_knowledge_sharing=None, target_mentoring_hours=None,
                 target_cash_handling_accuracy=None, target_card_payment_processing=None, target_digital_payment_adoption=None,
                 target_difficulty_level='MEDIUM', target_priority='MEDIUM', is_mandatory=False, is_achievable=True,
                 incentive_type=None, incentive_amount=None, incentive_description=None,
                 penalty_type=None, penalty_description=None,
                 current_achievement_percentage=0.0, last_measurement_date=None, is_on_track=True, projected_completion_date=None,
                 is_adjusted=False, adjustment_reason=None, adjustment_date=None, adjusted_by=None, original_target_value=None,
                 target_status='ACTIVE', is_completed=False, completion_date=None, completion_percentage=None,
                 review_frequency='WEEKLY', next_review_date=None, supervisor_feedback=None, cashier_feedback=None,
                 market_conditions=None, seasonal_factors=None, special_events=None,
                 target_description=None, target_rationale=None, success_criteria=None, measurement_method=None,
                 fk_cashier_create_id=None, fk_cashier_update_id=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.fk_cashier_id = fk_cashier_id
        self.fk_store_id = fk_store_id
        self.fk_supervisor_id = fk_supervisor_id
        self.target_type = target_type
        self.target_period = target_period
        self.target_start_date = target_start_date
        self.target_end_date = target_end_date
        self.target_year = target_year
        self.target_month = target_month
        self.target_week = target_week
        self.target_total_sales = target_total_sales
        self.target_daily_sales = target_daily_sales
        self.target_transactions_count = target_transactions_count
        self.target_items_sold = target_items_sold
        self.target_customers_served = target_customers_served
        self.target_average_transaction_amount = target_average_transaction_amount
        self.target_transactions_per_hour = target_transactions_per_hour
        self.target_sales_per_hour = target_sales_per_hour
        self.target_items_per_hour = target_items_per_hour
        self.target_customers_per_hour = target_customers_per_hour
        self.target_average_transaction_time = target_average_transaction_time
        self.target_working_hours = target_working_hours
        self.target_void_rate = target_void_rate
        self.target_return_rate = target_return_rate
        self.target_error_rate = target_error_rate
        self.target_accuracy_score = target_accuracy_score
        self.target_customer_satisfaction = target_customer_satisfaction
        self.target_productivity_score = target_productivity_score
        self.target_efficiency_score = target_efficiency_score
        self.target_service_quality_score = target_service_quality_score
        self.target_punctuality_score = target_punctuality_score
        self.target_attendance_rate = target_attendance_rate
        self.target_break_compliance = target_break_compliance
        self.max_late_arrivals = max_late_arrivals
        self.max_early_departures = max_early_departures
        self.target_training_hours = target_training_hours
        self.target_skill_assessments = target_skill_assessments
        self.target_certification_completion = target_certification_completion
        self.target_team_support_score = target_team_support_score
        self.target_knowledge_sharing = target_knowledge_sharing
        self.target_mentoring_hours = target_mentoring_hours
        self.target_cash_handling_accuracy = target_cash_handling_accuracy
        self.target_card_payment_processing = target_card_payment_processing
        self.target_digital_payment_adoption = target_digital_payment_adoption
        self.target_difficulty_level = target_difficulty_level
        self.target_priority = target_priority
        self.is_mandatory = is_mandatory
        self.is_achievable = is_achievable
        self.incentive_type = incentive_type
        self.incentive_amount = incentive_amount
        self.incentive_description = incentive_description
        self.penalty_type = penalty_type
        self.penalty_description = penalty_description
        self.current_achievement_percentage = current_achievement_percentage
        self.last_measurement_date = last_measurement_date
        self.is_on_track = is_on_track
        self.projected_completion_date = projected_completion_date
        self.is_adjusted = is_adjusted
        self.adjustment_reason = adjustment_reason
        self.adjustment_date = adjustment_date
        self.adjusted_by = adjusted_by
        self.original_target_value = original_target_value
        self.target_status = target_status
        self.is_completed = is_completed
        self.completion_date = completion_date
        self.completion_percentage = completion_percentage
        self.review_frequency = review_frequency
        self.next_review_date = next_review_date
        self.supervisor_feedback = supervisor_feedback
        self.cashier_feedback = cashier_feedback
        self.market_conditions = market_conditions
        self.seasonal_factors = seasonal_factors
        self.special_events = special_events
        self.target_description = target_description
        self.target_rationale = target_rationale
        self.success_criteria = success_criteria
        self.measurement_method = measurement_method
        self.fk_cashier_create_id = fk_cashier_create_id
        self.fk_cashier_update_id = fk_cashier_update_id

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