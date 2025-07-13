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


class CashierWorkSession(Model, CRUD):
    def __init__(self, fk_cashier_id=None, fk_store_id=None, session_start_time=None, 
                 session_end_time=None, session_status=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.fk_cashier_id = fk_cashier_id
        self.fk_store_id = fk_store_id
        self.session_start_time = session_start_time
        self.session_end_time = session_end_time
        self.session_status = session_status

    __tablename__ = "cashier_work_session"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_cashier_id = Column(UUID, ForeignKey("cashier.id"), nullable=False)
    fk_store_id = Column(UUID, ForeignKey("store.id"), nullable=False)
    
    # Session timing
    session_start_time = Column(DateTime, nullable=False)
    session_end_time = Column(DateTime, nullable=True)
    planned_session_duration = Column(Integer, nullable=True)  # Planned duration in minutes
    actual_session_duration = Column(Integer, nullable=True)  # Actual duration in minutes
    
    # Session status
    session_status = Column(String(20), nullable=False, default='ACTIVE')  # ACTIVE, COMPLETED, TERMINATED, BREAK
    
    # Work statistics
    total_transactions = Column(Integer, nullable=False, default=0)
    total_sales_amount = Column(Integer, nullable=False, default=0)  # In cents
    total_items_sold = Column(Integer, nullable=False, default=0)
    total_customers_served = Column(Integer, nullable=False, default=0)
    
    # Performance metrics
    average_transaction_time = Column(Float, nullable=True)  # In seconds
    fastest_transaction_time = Column(Float, nullable=True)  # In seconds
    slowest_transaction_time = Column(Float, nullable=True)  # In seconds
    
    # Error and void statistics
    total_voids = Column(Integer, nullable=False, default=0)
    total_returns = Column(Integer, nullable=False, default=0)
    total_price_overrides = Column(Integer, nullable=False, default=0)
    total_supervisor_calls = Column(Integer, nullable=False, default=0)
    
    # Break information
    total_break_time = Column(Integer, nullable=False, default=0)  # In minutes
    number_of_breaks = Column(Integer, nullable=False, default=0)
    
    # Idle time tracking
    total_idle_time = Column(Integer, nullable=False, default=0)  # In minutes
    longest_idle_period = Column(Integer, nullable=False, default=0)  # In minutes
    
    # Session notes and comments
    session_notes = Column(String(1000), nullable=True)
    supervisor_comments = Column(String(1000), nullable=True)
    
    # Login/logout information
    login_ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    logout_ip_address = Column(String(45), nullable=True)
    pos_terminal_id = Column(String(50), nullable=True)
    
    # Audit fields
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<CashierWorkSession(cashier_id='{self.fk_cashier_id}', start_time='{self.session_start_time}', status='{self.session_status}')>" 