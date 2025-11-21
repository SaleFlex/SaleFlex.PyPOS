from sqlalchemy import Column, Integer, BigInteger, Boolean, String, DateTime, Text, ForeignKey, UUID, Numeric
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class ClosureDiscountSummary(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Discount breakdown by type - useful for all sectors.
    """
    __tablename__ = "closure_discount_summary"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_closure_id = Column(UUID, ForeignKey("closure.id"), nullable=False, index=True)
    fk_discount_type_id = Column(UUID, nullable=False)  # TODO: Add ForeignKey("discount_type.id") when discount_type table is created
    
    # Discount Details
    discount_count = Column(Integer, nullable=False, default=0)
    total_discount_amount = Column(Numeric(15, 4), nullable=False, default=0)
    affected_amount = Column(Numeric(15, 4), nullable=False, default=0)  # Original amount before discount
    
    # Modification tracking
    is_modified = Column(Boolean, nullable=False, default=False)
    fk_cashier_modified_id = Column(UUID, ForeignKey("cashier.id"))
    modified_description = Column(Text)

    def __repr__(self):
        return f"<ClosureDiscountSummary(type='{self.fk_discount_type_id}', amount='{self.total_discount_amount}')>"
