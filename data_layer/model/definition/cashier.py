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
from data_layer.model.mixins import SoftDeleteMixin


class Cashier(Model, CRUD, SoftDeleteMixin):
    def __init__(self, no=None, user_name=None, name=None, last_name=None, password=None,
                 identity_number=None, description=None, is_administrator=False, is_active=False):
        Model.__init__(self)
        CRUD.__init__(self)

        self.no = no
        self.user_name = user_name
        self.name = name
        self.last_name = last_name
        self.password = password
        self.identity_number = identity_number
        self.description = description
        self.is_administrator = is_administrator
        self.is_active = is_active

    __tablename__ = "cashier"

    id = Column(UUID, primary_key=True, default=uuid4)
    no = Column(Integer, nullable=False, unique=True)
    user_name = Column(String(50), unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)
    identity_number = Column(String(24), nullable=False)
    description = Column(String(100), nullable=False)
    is_administrator = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    login_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Cashier(name='{self.name}', last_name='{self.last_name}', user_name='{self.user_name}', no='{self.no}')>"

