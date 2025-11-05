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

from sqlalchemy import (
    Column, Integer, BigInteger, Boolean, String,
    DateTime, Float, ForeignKey, UUID, Numeric, Index
)

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin

from uuid import uuid4


class TransactionSurcharge(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Surcharges and additional fees beyond product prices.
    Examples: service charges, delivery fees, convenience fees, bag fees
    """

    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "transaction_surcharge"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_transaction_head_id = Column(UUID, ForeignKey("transaction_head.id"), index=True)

    # Surcharge details
    surcharge_type = Column(String(50), nullable=False)  # "service_charge", "delivery_fee", "convenience_fee"
    surcharge_name = Column(String(100), nullable=False)
    surcharge_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    surcharge_rate = Column(Numeric(precision=5, scale=2), nullable=True)  # If percentage-based

    # Tax treatment
    is_taxable = Column(Boolean, nullable=False, default=True)
    tax_amount = Column(Numeric(precision=15, scale=4), nullable=False, default=0)

    # Application rules
    is_automatic = Column(Boolean, nullable=False, default=False)
    can_be_removed = Column(Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<TransactionSurcharge(type='{self.surcharge_type}', amount='{self.surcharge_amount}')>"

