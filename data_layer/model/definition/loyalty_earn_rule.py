"""
SaleFlex.PyPOS - Point of Sale Application

Copyright (c) 2025-2026 Ferhat Mousavi

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
