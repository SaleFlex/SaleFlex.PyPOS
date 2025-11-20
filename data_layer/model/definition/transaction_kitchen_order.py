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

from sqlalchemy import Column, Integer, BigInteger, Boolean, String, DateTime, Float, ForeignKey, UUID
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.definition.transaction_status import KitchenOrderStatus
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class TransactionKitchenOrder(Model, CRUD, AuditMixin, SoftDeleteMixin):
    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "transaction_kitchen_order"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_transaction_head_id = Column(UUID, ForeignKey("transaction_head.id"))
    fk_transaction_product_id = Column(UUID, ForeignKey("transaction_product.id"))
    fk_table_id = Column(UUID, ForeignKey("table.id"), nullable=True)
    order_number = Column(String(50), nullable=False)
    kitchen_order_status = Column(String(50), nullable=False, default=KitchenOrderStatus.WAITING.value)
    quantity = Column(Float, nullable=False)
    special_instructions = Column(String(500), nullable=True)
    priority = Column(Integer, nullable=False, default=1)  # 1=Normal, 2=High, 3=Urgent
    estimated_preparation_time = Column(Integer, nullable=True)  # in minutes
    actual_preparation_time = Column(Integer, nullable=True)  # in minutes
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    served_at = Column(DateTime, nullable=True)
    is_cancelled = Column(Boolean, nullable=False, default=False)
    cancel_reason = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<TransactionKitchenOrder(order_number='{self.order_number}', kitchen_order_status='{self.kitchen_order_status}', quantity='{self.quantity}')>" 