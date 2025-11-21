from sqlalchemy import Column, Integer, BigInteger, Boolean, String, DateTime, Text, ForeignKey, UUID, Numeric
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class ClosureCashierSummary(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Cashier performance tracking - useful for all sectors.
    """
    __tablename__ = "closure_employee_summary"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_closure_id = Column(UUID, ForeignKey("closure.id"), nullable=False, index=True)
    fk_cashier_id = Column(UUID, ForeignKey("cashier.id"), nullable=False)
    
    # Transaction Stats
    transaction_count = Column(Integer, nullable=False, default=0)
    total_sales_amount = Column(Numeric(15, 4), nullable=False, default=0)
    average_transaction_amount = Column(Numeric(15, 4), nullable=False, default=0)
    
    # Error/Void Tracking
    void_count = Column(Integer, nullable=False, default=0)
    void_amount = Column(Numeric(15, 4), nullable=False, default=0)
    correction_count = Column(Integer, nullable=False, default=0)
    
    # Time Tracking
    clock_in_time = Column(DateTime)
    clock_out_time = Column(DateTime)
    hours_worked = Column(Numeric(5, 2))
    
    # Modification tracking
    is_modified = Column(Boolean, nullable=False, default=False)
    fk_cashier_modified_id = Column(UUID, ForeignKey("cashier.id"))
    modified_description = Column(Text)

    def __repr__(self):
        return f"<ClosureEmployeeSummary(cashier='{self.fk_cashier_id}', sales='{self.total_sales_amount}')>"
