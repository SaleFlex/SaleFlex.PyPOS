from sqlalchemy import Column, Integer, BigInteger, Boolean, String, DateTime, Text, ForeignKey, UUID, Numeric
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class ClosureVATSummary(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Tax rate breakdown - essential for multi-tax jurisdictions.
    Supports both simple VAT (Turkey) and complex tax systems (US).
    """
    __tablename__ = "closure_vat_summary"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_closure_id = Column(UUID, ForeignKey("closure.id"), nullable=False, index=True)
    
    # Tax Configuration
    fk_tax_rate_id = Column(UUID, ForeignKey("vat.id"), nullable=True)
    tax_rate_percentage = Column(Numeric(5, 2), nullable=False)  # e.g., 18.00, 8.50
    tax_jurisdiction = Column(String(100))  # e.g., "Federal", "California", "Sales Tax"
    
    # Amounts
    taxable_amount = Column(Numeric(15, 4), nullable=False, default=0)
    tax_amount = Column(Numeric(15, 4), nullable=False, default=0)
    transaction_count = Column(Integer, nullable=False, default=0)
    
    # Tax Exemptions
    exempt_amount = Column(Numeric(15, 4), nullable=False, default=0)
    exempt_count = Column(Integer, nullable=False, default=0)
    
    # Modification tracking
    is_modified = Column(Boolean, nullable=False, default=False)
    fk_cashier_modified_id = Column(UUID, ForeignKey("cashier.id"))
    modified_description = Column(Text)

    def __repr__(self):
        return f"<ClosureVATSummary(rate='{self.tax_rate_percentage}%', tax='{self.tax_amount}')>"
