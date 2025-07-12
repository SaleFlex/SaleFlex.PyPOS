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

from sqlalchemy import Column, Integer, BigInteger, Boolean, String, DateTime, Float, ForeignKey, UUID
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.definition.transaction_status import KitchenOrderStatus


class TransactionKitchenOrderTemp(Model, CRUD):
    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "transaction_kitchen_order_temp"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_transaction_head_id = Column(BigInteger, ForeignKey("transaction_head_temp.id"))
    fk_transaction_product_id = Column(BigInteger, ForeignKey("transaction_product_temp.id"))
    fk_table_id = Column(BigInteger, ForeignKey("table.id"), nullable=True)
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
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    fk_cashier_create_id = Column(BigInteger, ForeignKey("cashier.id"))
    fk_cashier_update_id = Column(BigInteger, ForeignKey("cashier.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<TransactionKitchenOrderTemp(order_number='{self.order_number}', kitchen_order_status='{self.kitchen_order_status}', quantity='{self.quantity}')>" 