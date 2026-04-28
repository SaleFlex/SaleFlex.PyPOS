"""
SaleFlex.PyPOS - Point of Sale Application
Copyright (C) 2025-2026 Mousavi.Tech

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from sqlalchemy import Column, Integer, BigInteger, Boolean, String, DateTime, Float, ForeignKey, UUID, Numeric
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class Vat(Model, CRUD, AuditMixin, SoftDeleteMixin):
    def __init__(self, name=None, no: int = None, rate: float = None, description=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.name = name
        self.no = no
        self.rate = rate
        self.description = description

    __tablename__ = "vat"

    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(String(50), nullable=False)
    no = Column(Integer, nullable=False)
    rate = Column(Numeric(precision=5, scale=2), nullable=False)
    description = Column(String(100))

    def __repr__(self):
        return f"<Vat(name='{self.name}', no='{self.no}', rate='{self.rate}')>"
