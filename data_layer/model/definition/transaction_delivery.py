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

from sqlalchemy import Column, Integer, BigInteger, Boolean, String, DateTime, Float, ForeignKey, UUID, Numeric
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin
from data_layer.model.definition.transaction_status import DeliveryStatus


class TransactionDelivery(Model, CRUD, AuditMixin, SoftDeleteMixin):
    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "transaction_delivery"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_transaction_head_id = Column(UUID, ForeignKey("transaction_head.id"))
    delivery_number = Column(String(50), nullable=False)
    delivery_status = Column(String(50), nullable=False, default=DeliveryStatus.PENDING.value)
    delivery_type = Column(String(50), nullable=False)  # home_delivery, pickup, in_store
    delivery_address = Column(String(1000), nullable=True)
    delivery_phone = Column(String(20), nullable=True)
    delivery_contact_person = Column(String(100), nullable=True)
    delivery_notes = Column(String(500), nullable=True)
    estimated_delivery_date = Column(DateTime, nullable=True)
    actual_delivery_date = Column(DateTime, nullable=True)
    delivery_fee = Column(Numeric(precision=15, scale=4), nullable=False, default=0.0)
    courier_name = Column(String(100), nullable=True)
    courier_phone = Column(String(20), nullable=True)
    tracking_number = Column(String(100), nullable=True)
    delivery_attempts = Column(Integer, nullable=False, default=0)
    max_delivery_attempts = Column(Integer, nullable=False, default=3)
    is_paid_delivery = Column(Boolean, nullable=False, default=False)
    is_urgent = Column(Boolean, nullable=False, default=False)
    is_cancelled = Column(Boolean, nullable=False, default=False)
    cancel_reason = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<TransactionDelivery(delivery_number='{self.delivery_number}', delivery_status='{self.delivery_status}', delivery_type='{self.delivery_type}')>" 