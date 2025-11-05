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

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, UUID, Numeric
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class Currency(Model, CRUD, AuditMixin, SoftDeleteMixin):
    def __init__(self, name=None, no=None, rate=None, currency_code=None, 
                 sign=None, sign_direction=None, currency_symbol=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.name = name
        self.no = no
        self.rate = rate
        self.currency_code = currency_code
        self.sign = sign
        self.sign_direction = sign_direction
        self.currency_symbol = currency_symbol

    __tablename__ = "currency"

    id = Column(UUID, primary_key=True, default=uuid4)
    no = Column(Integer, nullable=False, unique=True)
    name = Column(String(50), nullable=False)
    rate = Column(Numeric(precision=15, scale=4), nullable=False, default=1.0)
    currency_code = Column(Integer, nullable=True)
    sign = Column(String(10), nullable=True)
    sign_direction = Column(String(10), nullable=True)  # LEFT, RIGHT
    currency_symbol = Column(String(10), nullable=True)

    def __repr__(self):
        return f"<Currency(name='{self.name}', no='{self.no}', rate='{self.rate}')>" 