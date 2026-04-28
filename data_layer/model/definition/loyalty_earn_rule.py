"""
SaleFlex.PyPOS - Point of Sale Application
Copyright (C) 2025-2026 Mousavi.Tech

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from sqlalchemy import Column, String, Boolean, UUID, Text, ForeignKey, Integer
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class LoyaltyEarnRule(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Configurable earning rule placeholder. Evaluation order and JSON schema
    will be consumed by the earning engine (document total, line, bundle, etc.).
    """

    __tablename__ = "loyalty_earn_rule"

    def __init__(
        self,
        fk_loyalty_program_id=None,
        rule_code=None,
        rule_type=None,
        priority=None,
        is_active=None,
        config_json=None,
        description=None,
    ):
        Model.__init__(self)
        CRUD.__init__(self)
        self.fk_loyalty_program_id = fk_loyalty_program_id
        self.rule_code = rule_code
        self.rule_type = rule_type
        self.priority = priority
        self.is_active = is_active
        self.config_json = config_json
        self.description = description

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_loyalty_program_id = Column(UUID, ForeignKey("loyalty_program.id"), nullable=False, index=True)

    rule_code = Column(String(64), nullable=False)
    # DOCUMENT_TOTAL | LINE_ITEM | PRODUCT_SET | CATEGORY (extensible string)
    rule_type = Column(String(32), nullable=False, default="DOCUMENT_TOTAL")
    priority = Column(Integer, nullable=False, default=100)
    is_active = Column(Boolean, nullable=False, default=True)
    config_json = Column(Text, nullable=True)
    description = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<LoyaltyEarnRule(code={self.rule_code!r}, type={self.rule_type!r})>"
