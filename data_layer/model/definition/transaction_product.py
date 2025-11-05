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

from sqlalchemy import (
    Column, Integer, BigInteger, Boolean, String,
    DateTime, Float, ForeignKey, UUID, Numeric, Index
)

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin

from uuid import uuid4


class TransactionProduct(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """Permanent transaction product line items"""

    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "transaction_product"

    # Same structure as TransactionProductTemp
    id = Column(UUID, primary_key=True, default=uuid4)
    fk_transaction_head_id = Column(UUID, ForeignKey("transaction_head.id"), index=True)
    line_no = Column(Integer, nullable=False)
    fk_department_main_group_id = Column(UUID, ForeignKey("department_main_group.id"), nullable=False)
    fk_department_sub_group_id = Column(UUID, ForeignKey("department_sub_group.id"), nullable=True)
    fk_product_id = Column(UUID, ForeignKey("product.id"), nullable=True, index=True)
    fk_product_barcode_id = Column(UUID, ForeignKey("product_barcode.id"), nullable=True)
    fk_product_barcode_mask_id = Column(UUID, ForeignKey("product_barcode_mask.id"), nullable=True)
    product_code = Column(String(50), nullable=True)
    product_name = Column(String(200), nullable=True)
    product_description = Column(String(500), nullable=True)
    vat_rate = Column(Numeric(precision=5, scale=2), nullable=False)
    tax_category = Column(String(50), nullable=True)
    tax_exemption_reason = Column(String(200), nullable=True)
    tax_inclusive = Column(Boolean, nullable=False, default=True)
    cost_price = Column(Numeric(precision=15, scale=4), nullable=True)
    list_price = Column(Numeric(precision=15, scale=4), nullable=True)
    unit_price = Column(Numeric(precision=15, scale=4), nullable=False)
    unit_discount = Column(Numeric(precision=15, scale=4), nullable=False, default=0)
    discount_rate = Column(Numeric(precision=5, scale=2), nullable=True)
    discount_reason = Column(String(200), nullable=True)
    quantity = Column(Numeric(precision=15, scale=4), nullable=False)
    unit_of_measure = Column(String(20), nullable=False, default="EA")
    base_unit_quantity = Column(Numeric(precision=15, scale=4), nullable=True)
    weight = Column(Numeric(precision=15, scale=4), nullable=True)
    weight_unit = Column(String(10), nullable=True)
    total_price = Column(Numeric(precision=15, scale=4), nullable=False)
    total_vat = Column(Numeric(precision=15, scale=4), nullable=False)
    total_discount = Column(Numeric(precision=15, scale=4), nullable=True)
    serial_number = Column(String(100), nullable=True)
    lot_number = Column(String(100), nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    modifiers_json = Column(String(2000), nullable=True)
    special_instructions = Column(String(500), nullable=True)
    warranty_months = Column(Integer, nullable=True)
    return_period_days = Column(Integer, nullable=True)
    is_returnable = Column(Boolean, nullable=False, default=True)
    is_cancel = Column(Boolean, nullable=False, default=False)
    is_voided = Column(Boolean, nullable=False, default=False)
    void_reason = Column(String(200), nullable=True)

    def __repr__(self):
        return f"<TransactionProduct(product='{self.product_name}', qty='{self.quantity}', total='{self.total_price}')>"

    __table_args__ = (
        Index('idx_product_transaction', 'fk_transaction_head_id'),
        Index('idx_product_id', 'fk_product_id'),
    )