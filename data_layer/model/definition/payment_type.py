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

from sqlalchemy import Column, Integer, String, Boolean, DateTime, UUID
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class PaymentType(Model, CRUD, AuditMixin, SoftDeleteMixin):
    def __init__(self, type_no=None, type_name=None, type_description=None, culture_info=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.type_no = type_no
        self.type_name = type_name
        self.type_description = type_description
        self.culture_info = culture_info

        if culture_info is None:
            self.culture_info = 'en-GB'

    __tablename__ = "payment_type"

    id = Column(UUID, primary_key=True, default=uuid4)
    type_no = Column(Integer, nullable=False, unique=True)
    type_name = Column(String(50), nullable=False)
    type_description = Column(String(150), nullable=True)
    culture_info = Column(String(10), nullable=False, default='en-GB')

    def __repr__(self):
        return f"<PaymentType(type_name='{self.type_name}', type_no='{self.type_no}')>" 