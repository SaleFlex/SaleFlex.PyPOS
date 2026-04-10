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

from sqlalchemy import Column, Boolean, UUID, ForeignKey, Integer, Numeric, UniqueConstraint
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class LoyaltyRedemptionPolicy(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Caps and steps for redeeming points at POS.
    PaymentService will apply these when point redemption is implemented.
    """

    __tablename__ = "loyalty_redemption_policy"
    __table_args__ = (UniqueConstraint("fk_loyalty_program_id", name="uq_loyalty_redemption_policy_program"),)

    def __init__(
        self,
        fk_loyalty_program_id=None,
        max_basket_amount_share_from_points=None,
        minimum_points_to_redeem=None,
        points_redemption_step=None,
        allow_partial_redemption=None,
    ):
        Model.__init__(self)
        CRUD.__init__(self)
        self.fk_loyalty_program_id = fk_loyalty_program_id
        self.max_basket_amount_share_from_points = max_basket_amount_share_from_points
        self.minimum_points_to_redeem = minimum_points_to_redeem
        self.points_redemption_step = points_redemption_step
        self.allow_partial_redemption = allow_partial_redemption

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_loyalty_program_id = Column(UUID, ForeignKey("loyalty_program.id"), nullable=False)

    # 0–1 fraction of basket total that may be covered by points (NULL = no extra cap)
    max_basket_amount_share_from_points = Column(Numeric(5, 4), nullable=True)
    minimum_points_to_redeem = Column(Integer, nullable=True)
    points_redemption_step = Column(Integer, nullable=False, default=1)
    allow_partial_redemption = Column(Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<LoyaltyRedemptionPolicy(program_id={self.fk_loyalty_program_id})>"
