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

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.definition.transaction_status import TransactionStatus, TransactionType, DeliveryStatus

from uuid import uuid4


class TransactionHeadTemp(Model, CRUD):
    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "transaction_head_temp"

    id = Column(UUID, primary_key=True, default=uuid4)
    transaction_unique_id = Column(String(50), nullable=False, default=uuid4())
    pos_id = Column(Integer, nullable=False)
    transaction_date_time = Column(DateTime, server_default=func.now(), nullable=False)
    document_type = Column(String(50), nullable=False)
    transaction_type = Column(String(50), nullable=False, default=TransactionType.SALE.value)
    transaction_status = Column(String(50), nullable=False, default=TransactionStatus.ACTIVE.value)
    fk_customer_id = Column(UUID, ForeignKey("customer.id"))
    fk_table_id = Column(UUID, ForeignKey("table.id"), nullable=True)
    closure_number = Column(Integer, nullable=False)
    receipt_number = Column(Integer, nullable=False)
    batch_number = Column(Integer, nullable=False)
    total_amount = Column(Integer, nullable=False)
    total_vat_amount = Column(Integer, nullable=False)
    total_discount_amount = Column(Integer, nullable=False)
    total_surcharge_amount = Column(Integer, nullable=False)
    total_payment_amount = Column(Integer, nullable=False)
    total_change_amount = Column(Integer, nullable=False)
    delivery_status = Column(String(50), nullable=True)
    estimated_delivery_time = Column(DateTime, nullable=True)
    actual_delivery_time = Column(DateTime, nullable=True)
    description = Column(String(100))
    is_closed = Column(Boolean, nullable=False, default=False)
    is_pending = Column(Boolean, nullable=False, default=False)
    is_cancel = Column(Boolean, nullable=False, default=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    fk_cashier_create_id = Column(UUID, ForeignKey("cashier.id"))
    fk_cashier_update_id = Column(UUID, ForeignKey("cashier.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<TransactionHeadTemp(transaction_unique_id='{self.transaction_unique_id}', transaction_date_time='{self.transaction_date_time}')>"
