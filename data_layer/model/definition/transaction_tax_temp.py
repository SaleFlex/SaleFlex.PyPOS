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


class TransactionTaxTemp(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """Temporary version of TransactionTax"""

    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "transaction_tax_temp"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_transaction_head_id = Column(UUID, ForeignKey("transaction_head_temp.id"), index=True)
    fk_transaction_product_id = Column(UUID, ForeignKey("transaction_product_temp.id"), nullable=True, index=True)
    tax_type = Column(String(50), nullable=False)
    tax_name = Column(String(100), nullable=False)
    tax_code = Column(String(20), nullable=False)
    taxable_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    tax_rate = Column(Numeric(precision=5, scale=2), nullable=False)
    tax_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    jurisdiction_level = Column(String(20), nullable=True)
    jurisdiction_code = Column(String(50), nullable=True, index=True)
    jurisdiction_name = Column(String(100), nullable=True)
    is_exempt = Column(Boolean, nullable=False, default=False)
    exemption_certificate = Column(String(100), nullable=True)
    exemption_reason = Column(String(200), nullable=True)
    tax_calculation_method = Column(String(50), nullable=True)

    def __repr__(self):
        return f"<TransactionTax(type='{self.tax_type}', rate='{self.tax_rate}', amount='{self.tax_amount}')>"

    __table_args__ = (
        Index('idx_tax_transaction_temp', 'fk_transaction_head_id'),
        Index('idx_tax_product_temp', 'fk_transaction_product_id'),
        Index('idx_tax_jurisdiction_temp', 'jurisdiction_code'),
    )