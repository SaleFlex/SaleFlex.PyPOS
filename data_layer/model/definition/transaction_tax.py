"""
SaleFlex.PyPOS - Point of Sale Application

Copyright (c) 2025 Ferhat Mousavi

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

from sqlalchemy import (
    Column, Integer, BigInteger, Boolean, String,
    DateTime, Float, ForeignKey, UUID, Numeric, Index
)

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin

from uuid import uuid4


class TransactionTax(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Detailed tax breakdown for multi-tax jurisdictions.
    Essential for US (state+county+city), Canada (GST+PST), and compound tax systems.
    """

    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "transaction_tax"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_transaction_head_id = Column(UUID, ForeignKey("transaction_head.id"), index=True)
    fk_transaction_product_id = Column(UUID, ForeignKey("transaction_product.id"), nullable=True, index=True)

    # Tax identification
    tax_type = Column(String(50), nullable=False)  # "VAT", "GST", "PST", "Sales Tax", "Service Tax"
    tax_name = Column(String(100), nullable=False)
    tax_code = Column(String(20), nullable=False)

    # Tax calculation
    taxable_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    tax_rate = Column(Numeric(precision=5, scale=2), nullable=False)
    tax_amount = Column(Numeric(precision=15, scale=4), nullable=False)

    # Jurisdiction (critical for US/Canada)
    jurisdiction_level = Column(String(20), nullable=True)  # "federal", "state", "county", "city"
    jurisdiction_code = Column(String(50), nullable=True, index=True)
    jurisdiction_name = Column(String(100), nullable=True)

    # Exemption handling
    is_exempt = Column(Boolean, nullable=False, default=False)
    exemption_certificate = Column(String(100), nullable=True)
    exemption_reason = Column(String(200), nullable=True)

    # Calculation method
    tax_calculation_method = Column(String(50), nullable=True)  # "compound", "simple", "exclusive", "inclusive"

    def __repr__(self):
        return f"<TransactionTax(type='{self.tax_type}', rate='{self.tax_rate}', amount='{self.tax_amount}')>"

    __table_args__ = (
        Index('idx_tax_transaction', 'fk_transaction_head_id'),
        Index('idx_tax_product', 'fk_transaction_product_id'),
        Index('idx_tax_jurisdiction', 'jurisdiction_code'),
    )