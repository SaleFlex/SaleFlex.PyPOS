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


class CashierPerformanceMetrics(Model, CRUD):
    def __init__(self, fk_cashier_id=None, fk_store_id=None, period_type=None, 
                 period_start_date=None, period_end_date=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.fk_cashier_id = fk_cashier_id
        self.fk_store_id = fk_store_id
        self.period_type = period_type
        self.period_start_date = period_start_date
        self.period_end_date = period_end_date

    __tablename__ = "cashier_performance_metrics"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_cashier_id = Column(UUID, ForeignKey("cashier.id"), nullable=False)
    fk_store_id = Column(UUID, ForeignKey("store.id"), nullable=False)
    
    # Period information
    period_type = Column(String(20), nullable=False)  # DAILY, WEEKLY, MONTHLY, YEARLY
    period_start_date = Column(Date, nullable=False)
    period_end_date = Column(Date, nullable=False)
    period_year = Column(Integer, nullable=False)
    period_month = Column(Integer, nullable=True)  # 1-12
    period_week = Column(Integer, nullable=True)  # 1-52
    period_day = Column(Integer, nullable=True)  # 1-31
    
    # Working time metrics
    total_working_hours = Column(Float, nullable=False, default=0.0)  # In hours
    total_active_time = Column(Float, nullable=False, default=0.0)  # In hours
    total_idle_time = Column(Float, nullable=False, default=0.0)  # In hours
    total_break_time = Column(Float, nullable=False, default=0.0)  # In hours
    number_of_sessions = Column(Integer, nullable=False, default=0)
    
    # Sales performance metrics
    total_transactions = Column(Integer, nullable=False, default=0)
    total_sales_amount = Column(Integer, nullable=False, default=0)  # In cents
    total_items_sold = Column(Integer, nullable=False, default=0)
    total_customers_served = Column(Integer, nullable=False, default=0)
    
    # Efficiency metrics
    transactions_per_hour = Column(Float, nullable=True)
    sales_per_hour = Column(Float, nullable=True)  # In cents per hour
    items_per_hour = Column(Float, nullable=True)
    customers_per_hour = Column(Float, nullable=True)
    average_transaction_amount = Column(Float, nullable=True)  # In cents
    average_items_per_transaction = Column(Float, nullable=True)
    
    # Transaction timing metrics
    average_transaction_time = Column(Float, nullable=True)  # In seconds
    fastest_transaction_time = Column(Float, nullable=True)  # In seconds
    slowest_transaction_time = Column(Float, nullable=True)  # In seconds
    median_transaction_time = Column(Float, nullable=True)  # In seconds
    
    # Quality and accuracy metrics
    total_voids = Column(Integer, nullable=False, default=0)
    total_returns = Column(Integer, nullable=False, default=0)
    total_price_overrides = Column(Integer, nullable=False, default=0)
    total_supervisor_calls = Column(Integer, nullable=False, default=0)
    total_system_errors = Column(Integer, nullable=False, default=0)
    
    # Error rates (percentages)
    void_rate = Column(Float, nullable=True)  # Percentage
    return_rate = Column(Float, nullable=True)  # Percentage
    price_override_rate = Column(Float, nullable=True)  # Percentage
    error_rate = Column(Float, nullable=True)  # Percentage
    
    # Payment method distribution
    cash_transactions = Column(Integer, nullable=False, default=0)
    card_transactions = Column(Integer, nullable=False, default=0)
    mobile_payment_transactions = Column(Integer, nullable=False, default=0)
    gift_card_transactions = Column(Integer, nullable=False, default=0)
    other_payment_transactions = Column(Integer, nullable=False, default=0)
    
    # Productivity metrics
    productivity_score = Column(Float, nullable=True)  # Overall productivity score (0-100)
    efficiency_score = Column(Float, nullable=True)  # Efficiency score (0-100)
    accuracy_score = Column(Float, nullable=True)  # Accuracy score (0-100)
    customer_service_score = Column(Float, nullable=True)  # Customer service score (0-100)
    
    # Comparison metrics
    performance_rank = Column(Integer, nullable=True)  # Rank among all cashiers
    improvement_percentage = Column(Float, nullable=True)  # Improvement from previous period
    target_achievement_percentage = Column(Float, nullable=True)  # Target achievement percentage
    
    # Peak performance tracking
    peak_hour_start = Column(Integer, nullable=True)  # Hour of day (0-23)
    peak_hour_end = Column(Integer, nullable=True)  # Hour of day (0-23)
    peak_transactions_per_hour = Column(Float, nullable=True)
    peak_sales_per_hour = Column(Float, nullable=True)  # In cents
    
    # Customer satisfaction metrics
    customer_complaints = Column(Integer, nullable=False, default=0)
    positive_feedback_count = Column(Integer, nullable=False, default=0)
    average_service_rating = Column(Float, nullable=True)  # 1-5 scale
    
    # Notes and comments
    performance_notes = Column(String(2000), nullable=True)
    supervisor_feedback = Column(String(2000), nullable=True)
    improvement_suggestions = Column(String(2000), nullable=True)
    
    # Audit fields
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<CashierPerformanceMetrics(cashier_id='{self.fk_cashier_id}', period='{self.period_type}', start_date='{self.period_start_date}')>" 