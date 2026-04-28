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

from sqlalchemy import Column, Integer, BigInteger, Boolean, String, DateTime, Text, ForeignKey, UUID, Numeric
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class ClosureCurrency(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Currency breakdown for multi-currency operations.
    Fixed: Now has FK to currency table.
    """
    __tablename__ = "closure_currency"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_closure_id = Column(UUID, ForeignKey("closure.id"), nullable=False, index=True)
    fk_currency_id = Column(UUID, ForeignKey("currency.id"), nullable=False)
    
    # Amounts in this currency
    currency_amount = Column(Numeric(15, 4), nullable=False)
    
    # Exchange Rate (to base currency)
    exchange_rate = Column(Numeric(12, 6), nullable=False)
    
    # Converted amount (in base currency)
    base_currency_amount = Column(Numeric(15, 4), nullable=False)
    
    # Modification tracking
    is_modified = Column(Boolean, nullable=False, default=False)
    fk_cashier_modified_id = Column(UUID, ForeignKey("cashier.id"))
    modified_description = Column(Text)

    def __repr__(self):
        return f"<ClosureCurrency(closure='{self.fk_closure_id}', amount='{self.currency_amount}')>"
