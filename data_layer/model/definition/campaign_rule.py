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

from sqlalchemy import Column, String, Boolean, DateTime, UUID, Text, ForeignKey
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class CampaignRule(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Defines inclusion/exclusion rules for campaign applicability
    Rules can filter by product, category, department, brand, payment type, etc.
    """
    def __init__(self, fk_campaign_id=None, rule_type=None, rule_value=None,
                 fk_product_id=None, fk_department_id=None, fk_payment_type_id=None,
                 fk_product_manufacturer_id=None, is_include=True, description=None,
                 settings_json=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.fk_campaign_id = fk_campaign_id
        self.rule_type = rule_type
        self.rule_value = rule_value
        self.fk_product_id = fk_product_id
        self.fk_department_id = fk_department_id
        self.fk_payment_type_id = fk_payment_type_id
        self.fk_product_manufacturer_id = fk_product_manufacturer_id
        self.is_include = is_include
        self.description = description
        self.settings_json = settings_json

    __tablename__ = "campaign_rule"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_campaign_id = Column(UUID, ForeignKey('campaign.id'), nullable=False)
    
    # Rule classification
    rule_type = Column(String(50), nullable=False)  # PRODUCT, DEPARTMENT, CATEGORY, BRAND, PAYMENT_TYPE, BARCODE_PATTERN
    rule_value = Column(String(250), nullable=True)  # For pattern-based rules (e.g., barcode prefix)
    
    # Entity-specific filters
    fk_product_id = Column(UUID, ForeignKey('product.id'), nullable=True)
    fk_department_id = Column(UUID, ForeignKey('department_main_group.id'), nullable=True)
    fk_payment_type_id = Column(UUID, ForeignKey('payment_type.id'), nullable=True)
    fk_product_manufacturer_id = Column(UUID, ForeignKey('product_manufacturer.id'), nullable=True)
    
    # Include/Exclude flag
    is_include = Column(Boolean, nullable=False, default=True)  # True = include in campaign, False = exclude from campaign
    
    description = Column(Text, nullable=True)
    
    # Additional rule settings stored as JSON
    settings_json = Column(Text, nullable=True)

    def __repr__(self):
        return f"<CampaignRule(campaign_id='{self.fk_campaign_id}', rule_type='{self.rule_type}')>"

