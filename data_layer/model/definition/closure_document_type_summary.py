from sqlalchemy import Column, Integer, BigInteger, Boolean, String, DateTime, Text, ForeignKey, UUID, Numeric
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class ClosureDocumentTypeSummary(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Flexible document type tracking instead of hardcoded fields.
    Supports any document type (receipt, invoice, waybill, etc.)
    """
    __tablename__ = "closure_document_type_summary"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_closure_id = Column(UUID, ForeignKey("closure.id"), nullable=False, index=True)
    fk_document_type_id = Column(UUID, ForeignKey("transaction_document_type.id"),nullable=False)
    
    # Valid Documents
    valid_count = Column(Integer, nullable=False, default=0)
    valid_amount = Column(Numeric(15, 4), nullable=False, default=0)
    valid_tax_amount = Column(Numeric(15, 4), nullable=False, default=0)
    
    # Canceled Documents
    canceled_count = Column(Integer, nullable=False, default=0)
    canceled_amount = Column(Numeric(15, 4), nullable=False, default=0)
    canceled_tax_amount = Column(Numeric(15, 4), nullable=False, default=0)
    
    # Modification tracking
    is_modified = Column(Boolean, nullable=False, default=False)
    fk_cashier_modified_id = Column(UUID, ForeignKey("cashier.id"))
    modified_description = Column(Text)

    def __repr__(self):
        return f"<ClosureDocumentTypeSummary(type='{self.fk_document_type_id}', count='{self.valid_count}')>"
