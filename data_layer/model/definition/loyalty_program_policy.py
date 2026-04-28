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
