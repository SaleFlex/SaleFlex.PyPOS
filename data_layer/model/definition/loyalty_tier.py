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


class LoyaltyTier(Model, CRUD):
    """
    Defines loyalty membership tiers (e.g., Bronze, Silver, Gold, Platinum)
    Each tier offers different benefits and requires different thresholds
    """
    def __init__(self, fk_loyalty_program_id=None, name=None, code=None, description=None,
                 min_points_required=None, min_annual_spending=None, tier_level=None,
                 points_multiplier=None, discount_percentage=None, special_benefits=None,
                 color_code=None, icon=None, is_active=True, display_order=0):
        Model.__init__(self)
        CRUD.__init__(self)

        self.fk_loyalty_program_id = fk_loyalty_program_id
        self.name = name
        self.code = code
        self.description = description
        self.min_points_required = min_points_required
        self.min_annual_spending = min_annual_spending
        self.tier_level = tier_level
        self.points_multiplier = points_multiplier
        self.discount_percentage = discount_percentage
        self.special_benefits = special_benefits
        self.color_code = color_code
        self.icon = icon
        self.is_active = is_active
        self.display_order = display_order

    __tablename__ = "loyalty_tier"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_loyalty_program_id = Column(UUID, ForeignKey('loyalty_program.id'), nullable=False)
    
    # Tier identification
    name = Column(String(100), nullable=False)  # Bronze, Silver, Gold, Platinum
    code = Column(String(50), nullable=False)  # BRONZE, SILVER, GOLD, PLATINUM
    description = Column(Text, nullable=True)
    
    # Tier requirements (customer meets ANY of these criteria)
    min_points_required = Column(Integer, nullable=True)  # Minimum lifetime points to reach this tier
    min_annual_spending = Column(Numeric(18, 2), nullable=True)  # Minimum annual spending amount
    
    # Tier hierarchy
    tier_level = Column(Integer, nullable=False, default=1)  # 1 = lowest tier, higher = better tier
    
    # Tier benefits
    points_multiplier = Column(Numeric(5, 2), nullable=True, default=1.0)  # Example: 1.5 = earn 50% more points
    discount_percentage = Column(Numeric(5, 2), nullable=True)  # Additional discount percentage for tier members
    special_benefits = Column(Text, nullable=True)  # Description of special benefits (free shipping, priority support, etc.)
    
    # Visual customization
    color_code = Column(String(20), nullable=True)  # Hex color code for UI display
    icon = Column(String(100), nullable=True)  # Icon name or path
    
    # Status and ordering
    is_active = Column(Boolean, nullable=False, default=True)
    display_order = Column(Integer, nullable=False, default=0)
    
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<LoyaltyTier(name='{self.name}', level={self.tier_level})>"

