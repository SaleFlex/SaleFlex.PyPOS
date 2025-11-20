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


class CashierWorkBreak(Model, CRUD, AuditMixin, SoftDeleteMixin):
    def __init__(self, fk_cashier_id=None, fk_work_session_id=None, break_type=None, 
                 break_start_time=None, break_end_time=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.fk_cashier_id = fk_cashier_id
        self.fk_work_session_id = fk_work_session_id
        self.break_type = break_type
        self.break_start_time = break_start_time
        self.break_end_time = break_end_time

    __tablename__ = "cashier_work_break"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_cashier_id = Column(UUID, ForeignKey("cashier.id"), nullable=False)
    fk_work_session_id = Column(UUID, ForeignKey("cashier_work_session.id"), nullable=False)
    fk_store_id = Column(UUID, ForeignKey("store.id"), nullable=False)
    
    # Break timing
    break_start_time = Column(DateTime, nullable=False)
    break_end_time = Column(DateTime, nullable=True)
    planned_break_duration = Column(Integer, nullable=True)  # Planned duration in minutes
    actual_break_duration = Column(Integer, nullable=True)  # Actual duration in minutes
    
    # Break type and classification
    break_type = Column(String(30), nullable=False)  # LUNCH, COFFEE, PRAYER, SMOKE, PERSONAL, EMERGENCY, SICK, SCHEDULED, UNSCHEDULED
    break_category = Column(String(20), nullable=False, default='REGULAR')  # REGULAR, MANDATORY, EMERGENCY, MEDICAL
    
    # Break approval and authorization
    is_approved = Column(Boolean, nullable=False, default=False)
    approved_by_supervisor = Column(Boolean, nullable=False, default=False)
    fk_supervisor_id = Column(UUID, ForeignKey("cashier.id"), nullable=True)
    approval_time = Column(DateTime, nullable=True)
    
    # Break status
    break_status = Column(String(20), nullable=False, default='IN_PROGRESS')  # IN_PROGRESS, COMPLETED, EXTENDED, CANCELLED
    
    # Location and replacement information
    break_location = Column(String(100), nullable=True)  # WHERE THE BREAK IS TAKEN
    replacement_cashier_id = Column(UUID, ForeignKey("cashier.id"), nullable=True)
    register_locked = Column(Boolean, nullable=False, default=True)
    
    # Break extension information
    is_extended = Column(Boolean, nullable=False, default=False)
    extension_duration = Column(Integer, nullable=False, default=0)  # In minutes
    extension_reason = Column(String(500), nullable=True)
    extension_approved = Column(Boolean, nullable=False, default=False)
    
    # Compliance and policy tracking
    is_mandatory_break = Column(Boolean, nullable=False, default=False)
    is_legal_requirement = Column(Boolean, nullable=False, default=False)
    policy_compliance = Column(Boolean, nullable=False, default=True)
    
    # Performance impact
    transactions_before_break = Column(Integer, nullable=False, default=0)
    transactions_after_break = Column(Integer, nullable=False, default=0)
    productivity_before_break = Column(Float, nullable=True)  # Transactions per hour
    productivity_after_break = Column(Float, nullable=True)  # Transactions per hour
    
    # Timing analysis
    time_since_last_break = Column(Integer, nullable=True)  # In minutes
    time_until_next_break = Column(Integer, nullable=True)  # In minutes
    break_frequency_today = Column(Integer, nullable=False, default=0)
    
    # Health and wellness metrics
    stress_level_before = Column(Integer, nullable=True)  # 1-10 scale
    stress_level_after = Column(Integer, nullable=True)  # 1-10 scale
    energy_level_before = Column(Integer, nullable=True)  # 1-10 scale
    energy_level_after = Column(Integer, nullable=True)  # 1-10 scale
    
    # Break quality assessment
    break_quality_rating = Column(Integer, nullable=True)  # 1-5 scale
    was_refreshing = Column(Boolean, nullable=True)
    was_interrupted = Column(Boolean, nullable=False, default=False)
    interruption_reason = Column(String(500), nullable=True)
    
    # Weather and environmental factors
    weather_condition = Column(String(50), nullable=True)  # SUNNY, RAINY, CLOUDY, SNOWY, etc.
    temperature = Column(Float, nullable=True)  # In Celsius
    break_area_condition = Column(String(100), nullable=True)  # CLEAN, CROWDED, QUIET, etc.
    
    # Notes and comments
    break_notes = Column(String(1000), nullable=True)
    supervisor_comments = Column(String(1000), nullable=True)
    reason_for_break = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<CashierWorkBreak(cashier_id='{self.fk_cashier_id}', break_type='{self.break_type}', start_time='{self.break_start_time}')>" 