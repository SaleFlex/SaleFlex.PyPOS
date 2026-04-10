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

from sqlalchemy import Column, String, Boolean, UUID, Text, ForeignKey, UniqueConstraint
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class LoyaltyProgramPolicy(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Operational policy for a loyalty program (one row per program).
    Drives customer identification (phone vs legacy card), void/refund behaviour flags,
    and which integration backend will own balances later (LOCAL only for now).
    """

    __tablename__ = "loyalty_program_policy"
    __table_args__ = (UniqueConstraint("fk_loyalty_program_id", name="uq_loyalty_program_policy_program"),)

    def __init__(
        self,
        fk_loyalty_program_id=None,
        customer_identifier_type=None,
        require_customer_phone_for_enrollment=None,
        default_phone_country_calling_code=None,
        void_loyalty_points_policy=None,
        integration_provider=None,
        integration_settings_json=None,
    ):
        Model.__init__(self)
        CRUD.__init__(self)
        self.fk_loyalty_program_id = fk_loyalty_program_id
        self.customer_identifier_type = customer_identifier_type
        self.require_customer_phone_for_enrollment = require_customer_phone_for_enrollment
        self.default_phone_country_calling_code = default_phone_country_calling_code
        self.void_loyalty_points_policy = void_loyalty_points_policy
        self.integration_provider = integration_provider
        self.integration_settings_json = integration_settings_json

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_loyalty_program_id = Column(UUID, ForeignKey("loyalty_program.id"), nullable=False)

    # PHONE (default) | LOYALTY_CARD — POS lookup priority for loyalty
    customer_identifier_type = Column(String(20), nullable=False, default="PHONE")
    require_customer_phone_for_enrollment = Column(Boolean, nullable=False, default=True)
    # E.g. "90" for TR mobiles when cashier enters local 0-prefixed numbers
    default_phone_country_calling_code = Column(String(5), nullable=True)

    # NONE | CLAWBACK_FULL | CLAWBACK_PROPORTIONAL (reserved for later sale-completion logic)
    void_loyalty_points_policy = Column(String(50), nullable=False, default="NONE")

    # LOCAL | GATE | EXTERNAL — only LOCAL is implemented; others are placeholders
    integration_provider = Column(String(20), nullable=False, default="LOCAL")
    integration_settings_json = Column(Text, nullable=True)

    def __repr__(self):
        return f"<LoyaltyProgramPolicy(program_id={self.fk_loyalty_program_id}, id_type={self.customer_identifier_type})>"
