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

from sqlalchemy import Column, Integer, BigInteger, Boolean, String, DateTime, Float, ForeignKey, Date, UUID
from sqlalchemy.sql import func

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD

from uuid import uuid4


class Closure(Model, CRUD):
    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "closure"

    id = Column(UUID, primary_key=True, default=uuid4)
    closure_unique_id = Column(String(50), nullable=False, default=uuid4())
    closure_number = Column(Integer, nullable=False)
    pos_id = Column(Integer, nullable=False)
    fk_store_id = Column(BigInteger, ForeignKey("store.id"))
    closure_date = Column(Date, server_default=func.now(), nullable=False)
    total_document_count = Column(Integer, nullable=False)
    gross_total_amount = Column(Float, nullable=False)
    gross_total_vat_amount = Column(Float, nullable=False)
    daily_total_amount = Column(Float, nullable=False)
    daily_total_vat_amount = Column(Float, nullable=False)
    valid_receipt_count = Column(Integer, nullable=False)
    valid_invoice_count = Column(Integer, nullable=False)
    canceled_receipt_count = Column(Integer, nullable=False)
    canceled_invoice_count = Column(Integer, nullable=False)
    canceled_total_amount = Column(Float, nullable=False)
    valid_receipt_total_amount = Column(Float, nullable=False)
    valid_invoice_total_amount = Column(Float, nullable=False)
    valid_receipt_vat_total_amount = Column(Float, nullable=False)
    valid_invoice_vat_total_amount = Column(Float, nullable=False)
    bonus_point_total_amount = Column(Float, nullable=False)
    discount_total_amount = Column(Float, nullable=False)
    waybill_count = Column(Integer, nullable=False)
    canceled_waybill_count = Column(Integer, nullable=False)
    waybill_total_amount = Column(Float, nullable=False)
    canceled_waybill_total_amount = Column(Float, nullable=False)
    return_count = Column(Integer, nullable=False)
    canceled_return_count = Column(Integer, nullable=False)
    return_total_amount = Column(Float, nullable=False)
    canceled_return_total_amount = Column(Float, nullable=False)
    diplomatic_invoice_count = Column(Integer, nullable=False)
    canceled_diplomatic_invoice_count = Column(Integer, nullable=False)
    diplomatic_invoice_total_amount = Column(Float, nullable=False)
    canceled_diplomatic_invoice_total_amount = Column(Float, nullable=False)
    electronic_receipt_count = Column(Integer, nullable=False)
    canceled_electronic_receipt_count = Column(Integer, nullable=False)
    electronic_receipt_total_amount = Column(Float, nullable=False)
    canceled_electronic_receipt_total_amount = Column(Float, nullable=False)
    electronic_invoice_count = Column(Integer, nullable=False)
    canceled_electronic_invoice_count = Column(Integer, nullable=False)
    electronic_invoice_total_amount = Column(Float, nullable=False)
    canceled_electronic_invoice_total_amount = Column(Float, nullable=False)
    electronic_corporate_invoice_count = Column(Integer, nullable=False)
    canceled_electronic_corporate_invoice_count = Column(Integer, nullable=False)
    electronic_corporate_invoice_total_amount = Column(Float, nullable=False)
    canceled_electronic_corporate_invoice_total_amount = Column(Float, nullable=False)
    electronic_individual_invoice_count = Column(Integer, nullable=False)
    canceled_electronic_individual_invoice_count = Column(Integer, nullable=False)
    electronic_individual_invoice_total_amount = Column(Float, nullable=False)
    canceled_electronic_individual_invoice_total_amount = Column(Float, nullable=False)
    expanse_count = Column(Integer, nullable=False)
    canceled_expanse_count = Column(Integer, nullable=False)
    expanse_total_amount = Column(Float, nullable=False)
    canceled_expanse_total_amount = Column(Float, nullable=False)
    paid_out_count = Column(Integer, nullable=False)
    canceled_paid_out_count = Column(Integer, nullable=False)
    paid_out_total_amount = Column(Float, nullable=False)
    canceled_paid_out_total_amount = Column(Float, nullable=False)
    paid_in_count = Column(Integer, nullable=False)
    canceled_paid_in_count = Column(Integer, nullable=False)
    paid_in_total_amount = Column(Float, nullable=False)
    canceled_paid_in_total_amount = Column(Float, nullable=False)
    description = Column(String(100))
    is_canceled = Column(Boolean, nullable=False, default=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    is_modified = Column(Boolean, nullable=False, default=False)
    fk_cashier_modified_id = Column(BigInteger, ForeignKey("cashier.id"))
    modified_description = Column(String(1000), nullable=True)
    fk_cashier_create_id = Column(BigInteger, ForeignKey("cashier.id"))
    fk_cashier_update_id = Column(BigInteger, ForeignKey("cashier.id"))
    modified_at = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Closure(closure_unique_id='{self.closure_unique_id}', closure_date='{self.closure_date}')>"
