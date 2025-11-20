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

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, UUID, Numeric, ForeignKey, UniqueConstraint, Index
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class CurrencyTable(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Currency exchange rate table for converting between different currencies.
    
    This table stores exchange rates between currency pairs, allowing flexible
    conversion from any base currency to any target currency. For example, if
    base_currency_id points to GBP and target_currency_id points to TRY, the
    rate field indicates how many Turkish Lira equal one British Pound.
    
    The advantage of this approach is that it allows conversion between any
    currency pair without being limited to a single base currency.
    
    Example:
        base_currency_id = GBP (British Pound)
        target_currency_id = TRY (Turkish Lira)
        rate = 35.21
        Meaning: 1 GBP = 35.21 TRY
    """
    
    def __init__(self, fk_base_currency_id=None, fk_target_currency_id=None, rate=None):
        Model.__init__(self)
        CRUD.__init__(self)
        
        self.fk_base_currency_id = fk_base_currency_id
        self.fk_target_currency_id = fk_target_currency_id
        self.rate = rate

    __tablename__ = "currency_table"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_base_currency_id = Column(UUID, ForeignKey("currency.id"), nullable=False)  # Base currency (from)
    fk_target_currency_id = Column(UUID, ForeignKey("currency.id"), nullable=False)  # Target currency (to)
    rate = Column(Numeric(precision=15, scale=4), nullable=False)  # Exchange rate: 1 base_currency = rate target_currency

    def __repr__(self):
        return f"<CurrencyTable(base_currency_id='{self.fk_base_currency_id}', target_currency_id='{self.fk_target_currency_id}', rate='{self.rate}')>"
    
    __table_args__ = (
        UniqueConstraint('fk_base_currency_id', 'fk_target_currency_id', name='uq_currency_pair'),
        Index('idx_currency_base', 'fk_base_currency_id'),
        Index('idx_currency_target', 'fk_target_currency_id'),
    )

