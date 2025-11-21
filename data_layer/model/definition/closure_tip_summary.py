from sqlalchemy import Column, Integer, BigInteger, Boolean, String, DateTime, Text, ForeignKey, UUID, Numeric
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class ClosureTipSummary(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Tip tracking by payment method - essential for restaurant operations.
    North America requires detailed tip tracking.
    """
    __tablename__ = "closure_tip_summary"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_closure_id = Column(UUID, ForeignKey("closure.id"), nullable=False, index=True)
    fk_payment_type_id = Column(UUID, ForeignKey("payment_type.id"), nullable=False)
    
    # Tip Details
    tip_count = Column(Integer, nullable=False, default=0)
    total_tip_amount = Column(Numeric(15, 4), nullable=False, default=0)
    average_tip_amount = Column(Numeric(15, 4), nullable=False, default=0)
    average_tip_percentage = Column(Numeric(5, 2), nullable=False, default=0)
    
    # Employee Distribution (if tips are pooled/distributed)
    distributed_amount = Column(Numeric(15, 4), nullable=False, default=0)
    undistributed_amount = Column(Numeric(15, 4), nullable=False, default=0)
    
    # Modification tracking
    is_modified = Column(Boolean, nullable=False, default=False)
    fk_cashier_modified_id = Column(UUID, ForeignKey("cashier.id"))
    modified_description = Column(Text)

    def __repr__(self):
        return f"<ClosureTipSummary(count='{self.tip_count}', total='{self.total_tip_amount}')>"
