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

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, UUID, Numeric
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class Currency(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Currency model representing different currencies used in the POS system.
    
    This model stores basic currency information including name, code, sign,
    and decimal places. Exchange rates between currencies are stored in the
    CurrencyTable model, allowing flexible conversion between any currency pair.
    """
    
    def __init__(self, name=None, no=None, currency_code=None, 
                 sign=None, sign_direction=None, currency_symbol=None, decimal_places=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.name = name
        self.no = no
        self.currency_code = currency_code
        self.sign = sign
        self.sign_direction = sign_direction
        self.currency_symbol = currency_symbol
        self.decimal_places = decimal_places

    __tablename__ = "currency"

    id = Column(UUID, primary_key=True, default=uuid4)
    no = Column(Integer, nullable=False, unique=True)
    name = Column(String(50), nullable=False)
    currency_code = Column(Integer, nullable=True)
    sign = Column(String(10), nullable=True)
    sign_direction = Column(String(10), nullable=True)  # LEFT, RIGHT
    currency_symbol = Column(String(10), nullable=True)
    decimal_places = Column(Integer, nullable=False, default=2)  # Number of decimal places (0, 2, 3, etc.)

    def __repr__(self):
        return f"<Currency(name='{self.name}', no='{self.no}', sign='{self.sign}')>" 