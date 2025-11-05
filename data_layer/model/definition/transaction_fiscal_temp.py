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
    DateTime, Float, ForeignKey, UUID, Numeric, Index, func
)

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin

from uuid import uuid4


class TransactionFiscalTemp(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """Temporary version of TransactionFiscal"""

    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "transaction_fiscal_temp"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_transaction_head_id = Column(UUID, ForeignKey("transaction_head_temp.id"), index=True)

    # Country-specific
    country_code = Column(String(2), nullable=False, index=True)  # ISO 3166-1

    # Fiscal device
    fiscal_device_id = Column(String(100), nullable=True)
    fiscal_device_serial = Column(String(100), nullable=True)

    # Receipt/Invoice numbers
    fiscal_receipt_number = Column(String(50), nullable=True, index=True)
    fiscal_invoice_number = Column(String(50), nullable=True)
    fiscal_document_type = Column(String(50), nullable=True)

    # Digital signatures
    fiscal_signature = Column(String(500), nullable=True)
    fiscal_hash = Column(String(500), nullable=True)
    qr_code_data = Column(String(2000), nullable=True)
    verification_code = Column(String(100), nullable=True)

    # E-invoice/E-archive (Turkey, Italy)
    e_invoice_id = Column(String(100), nullable=True)
    e_invoice_uuid = Column(UUID, nullable=True)
    e_archive_id = Column(String(100), nullable=True)

    # Government reporting
    reporting_status = Column(String(50), nullable=True)  # "pending", "submitted", "accepted"
    reported_at = Column(DateTime, nullable=True)
    government_response = Column(String(2000), nullable=True)

    # Tax authority
    tax_authority_code = Column(String(50), nullable=True)

    def __repr__(self):
        return f"<TransactionFiscalTemp(country='{self.country_code}', receipt='{self.fiscal_receipt_number}')>"

    __table_args__ = (
        Index('idx_fiscal_transaction_temp', 'fk_transaction_head_id'),
        Index('idx_fiscal_country_temp', 'country_code'),
        Index('idx_fiscal_receipt_temp', 'fiscal_receipt_number'),
    )