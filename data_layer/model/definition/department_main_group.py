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

from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, Float, ForeignKey, UUID, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class DepartmentMainGroup(Model, CRUD, AuditMixin, SoftDeleteMixin):
    def __init__(self, code=None, name=None, description=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.code = code
        self.name = name
        self.description = description

    __tablename__ = "department_main_group"

    id = Column(UUID, primary_key=True, default=uuid4)
    code = Column(String(10), nullable=False)
    name = Column(String(50), nullable=False)
    fk_vat_id = Column(UUID, nullable=True)
    description = Column(String(100), nullable=True)
    max_price = Column(Numeric(precision=15, scale=4), nullable=True)
    discount_rate = Column(Numeric(precision=15, scale=4), nullable=True)

    def __repr__(self):
        return f"<DepartmentMainGroup(name='{self.name}', code='{self.code}', description='{self.description}')>"
