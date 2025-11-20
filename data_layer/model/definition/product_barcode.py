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

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UUID, Numeric
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class ProductBarcode(Model, CRUD, AuditMixin, SoftDeleteMixin):
    def __init__(self, fk_product_id=None, barcode=None, old_barcode=None, 
                 purchase_price=None, sale_price=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.fk_product_id = fk_product_id
        self.barcode = barcode
        self.old_barcode = old_barcode
        self.purchase_price = purchase_price
        self.sale_price = sale_price

    __tablename__ = "product_barcode"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_server_id = Column(Integer, nullable=True)  # For server synchronization
    fk_product_id = Column(UUID, ForeignKey("product.id"), nullable=False)
    barcode = Column(String(50), nullable=False, unique=True)
    old_barcode = Column(String(50), nullable=True)
    fk_barcode_mask_id = Column(UUID, ForeignKey("product_barcode_mask.id"), nullable=True)
    purchase_price = Column(Numeric(precision=15, scale=4), nullable=True, default=0)
    sale_price = Column(Numeric(precision=15, scale=4), nullable=True, default=0)

    def __repr__(self):
        return f"<ProductBarcode(barcode='{self.barcode}', sale_price='{self.sale_price}')>"
