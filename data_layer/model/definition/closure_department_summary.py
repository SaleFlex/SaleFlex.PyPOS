from sqlalchemy import Column, Integer, BigInteger, Boolean, String, DateTime, Text, ForeignKey, UUID, Numeric
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class ClosureDepartmentSummary(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Department/category breakdown.
    Renamed from ClosureTotal for clarity.
    """
    __tablename__ = "closure_department_summary"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_closure_id = Column(UUID, ForeignKey("closure.id"), nullable=False, index=True)
    fk_department_main_group_id = Column(UUID, ForeignKey("department_main_group.id"), nullable=False)
    
    transaction_count = Column(Integer, nullable=False, default=0)
    gross_amount = Column(Numeric(15, 4), nullable=False, default=0)
    tax_amount = Column(Numeric(15, 4), nullable=False, default=0)
    net_amount = Column(Numeric(15, 4), nullable=False, default=0)
    discount_amount = Column(Numeric(15, 4), nullable=False, default=0)
    
    # Modification tracking
    is_modified = Column(Boolean, nullable=False, default=False)
    fk_cashier_modified_id = Column(UUID, ForeignKey("cashier.id"))
    modified_description = Column(Text)

    def __repr__(self):
        return f"<ClosureDepartmentSummary(dept='{self.fk_department_main_group_id}', amount='{self.gross_amount}')>"
