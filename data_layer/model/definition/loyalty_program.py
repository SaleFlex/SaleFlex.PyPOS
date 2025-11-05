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

from sqlalchemy import Column, String, Boolean, DateTime, UUID, Text, ForeignKey, Numeric, Integer
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class LoyaltyProgram(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Defines loyalty program configuration
    Typically one active program per store or entire POS system
    """
    def __init__(self, name=None, description=None, fk_store_id=None, 
                 points_per_currency=None, currency_per_point=None,
                 min_purchase_for_points=None, point_expiry_days=None,
                 is_active=True, start_date=None, end_date=None,
                 welcome_points=None, birthday_points=None, terms_conditions=None,
                 settings_json=None, fk_created_by=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.name = name
        self.description = description
        self.fk_store_id = fk_store_id
        self.points_per_currency = points_per_currency
        self.currency_per_point = currency_per_point
        self.min_purchase_for_points = min_purchase_for_points
        self.point_expiry_days = point_expiry_days
        self.is_active = is_active
        self.start_date = start_date
        self.end_date = end_date
        self.welcome_points = welcome_points
        self.birthday_points = birthday_points
        self.terms_conditions = terms_conditions
        self.settings_json = settings_json
        self.fk_created_by = fk_created_by

    __tablename__ = "loyalty_program"

    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(String(250), nullable=False)
    description = Column(Text, nullable=True)
    fk_store_id = Column(UUID, ForeignKey('store.id'), nullable=True)  # NULL = applies to all stores
    
    # Point earning configuration
    points_per_currency = Column(Numeric(10, 2), nullable=False, default=1.0)  # Example: 1 point per 10 TL = 0.1
    currency_per_point = Column(Numeric(10, 2), nullable=True)  # Example: 1 point = 0.5 TL discount
    min_purchase_for_points = Column(Numeric(18, 2), nullable=True)  # Minimum purchase amount to earn points
    
    # Point expiry
    point_expiry_days = Column(Integer, nullable=True)  # NULL = points never expire
    
    # Program status
    is_active = Column(Boolean, nullable=False, default=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    
    # Bonus points
    welcome_points = Column(Integer, nullable=True, default=0)  # Points awarded to new customers
    birthday_points = Column(Integer, nullable=True, default=0)  # Points awarded on customer birthday
    
    # Terms and conditions
    terms_conditions = Column(Text, nullable=True)
    
    # Additional custom settings stored as JSON
    settings_json = Column(Text, nullable=True)
    
    # Additional audit trail (AuditMixin already provides fk_cashier_create_id, fk_cashier_update_id)
    # fk_created_by is now handled by AuditMixin as fk_cashier_create_id

    def __repr__(self):
        return f"<LoyaltyProgram(name='{self.name}', is_active={self.is_active})>"

