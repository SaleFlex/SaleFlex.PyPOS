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

from sqlalchemy import Column, Integer, BigInteger, Boolean, String, DateTime, Float, ForeignKey, Date, UUID, Numeric
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
    gross_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    gross_total_vat_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    daily_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    daily_total_vat_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    valid_receipt_count = Column(Integer, nullable=False)
    valid_invoice_count = Column(Integer, nullable=False)
    canceled_receipt_count = Column(Integer, nullable=False)
    canceled_invoice_count = Column(Integer, nullable=False)
    canceled_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    valid_receipt_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    valid_invoice_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    valid_receipt_vat_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    valid_invoice_vat_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    bonus_point_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    discount_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    waybill_count = Column(Integer, nullable=False)
    canceled_waybill_count = Column(Integer, nullable=False)
    waybill_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    canceled_waybill_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    return_count = Column(Integer, nullable=False)
    canceled_return_count = Column(Integer, nullable=False)
    return_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    canceled_return_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    diplomatic_invoice_count = Column(Integer, nullable=False)
    canceled_diplomatic_invoice_count = Column(Integer, nullable=False)
    diplomatic_invoice_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    canceled_diplomatic_invoice_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    electronic_receipt_count = Column(Integer, nullable=False)
    canceled_electronic_receipt_count = Column(Integer, nullable=False)
    electronic_receipt_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    canceled_electronic_receipt_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    electronic_invoice_count = Column(Integer, nullable=False)
    canceled_electronic_invoice_count = Column(Integer, nullable=False)
    electronic_invoice_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    canceled_electronic_invoice_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    electronic_corporate_invoice_count = Column(Integer, nullable=False)
    canceled_electronic_corporate_invoice_count = Column(Integer, nullable=False)
    electronic_corporate_invoice_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    canceled_electronic_corporate_invoice_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    electronic_individual_invoice_count = Column(Integer, nullable=False)
    canceled_electronic_individual_invoice_count = Column(Integer, nullable=False)
    electronic_individual_invoice_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    canceled_electronic_individual_invoice_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    expanse_count = Column(Integer, nullable=False)
    canceled_expanse_count = Column(Integer, nullable=False)
    expanse_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    canceled_expanse_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    paid_out_count = Column(Integer, nullable=False)
    canceled_paid_out_count = Column(Integer, nullable=False)
    paid_out_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    canceled_paid_out_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    paid_in_count = Column(Integer, nullable=False)
    canceled_paid_in_count = Column(Integer, nullable=False)
    paid_in_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    canceled_paid_in_total_amount = Column(Numeric(precision=15, scale=4), nullable=False)
    description = Column(String(100))
    is_canceled = Column(Boolean, nullable=False, default=False)
    is_modified = Column(Boolean, nullable=False, default=False)
    fk_cashier_modified_id = Column(BigInteger, ForeignKey("cashier.id"))
    modified_description = Column(String(1000), nullable=True)
    modified_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Closure(closure_unique_id='{self.closure_unique_id}', closure_date='{self.closure_date}')>"
