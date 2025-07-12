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
from data_layer.model.definition.transaction_status import DeliveryStatus


class TransactionDelivery(Model, CRUD):
    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "transaction_delivery"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_transaction_head_id = Column(BigInteger, ForeignKey("transaction_head.id"))
    delivery_number = Column(String(50), nullable=False)
    delivery_status = Column(String(50), nullable=False, default=DeliveryStatus.PENDING.value)
    delivery_type = Column(String(50), nullable=False)  # home_delivery, pickup, in_store
    delivery_address = Column(String(1000), nullable=True)
    delivery_phone = Column(String(20), nullable=True)
    delivery_contact_person = Column(String(100), nullable=True)
    delivery_notes = Column(String(500), nullable=True)
    estimated_delivery_date = Column(DateTime, nullable=True)
    actual_delivery_date = Column(DateTime, nullable=True)
    delivery_fee = Column(Float, nullable=False, default=0.0)
    courier_name = Column(String(100), nullable=True)
    courier_phone = Column(String(20), nullable=True)
    tracking_number = Column(String(100), nullable=True)
    delivery_attempts = Column(Integer, nullable=False, default=0)
    max_delivery_attempts = Column(Integer, nullable=False, default=3)
    is_paid_delivery = Column(Boolean, nullable=False, default=False)
    is_urgent = Column(Boolean, nullable=False, default=False)
    is_cancelled = Column(Boolean, nullable=False, default=False)
    cancel_reason = Column(String(500), nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    fk_cashier_create_id = Column(BigInteger, ForeignKey("cashier.id"))
    fk_cashier_update_id = Column(BigInteger, ForeignKey("cashier.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<TransactionDelivery(delivery_number='{self.delivery_number}', delivery_status='{self.delivery_status}', delivery_type='{self.delivery_type}')>" 