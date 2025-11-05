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

from sqlalchemy import Column, Integer, BigInteger, Boolean, String, DateTime, ForeignKey, UUID
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class Table(Model, CRUD, AuditMixin, SoftDeleteMixin):
    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "table"

    id = Column(UUID, primary_key=True, default=uuid4)
    table_number = Column(String(20), nullable=False)
    table_name = Column(String(100), nullable=True)
    capacity = Column(Integer, nullable=False, default=1)
    location = Column(String(100), nullable=True)  # hall, garden, upper floor etc.
    is_active = Column(Boolean, nullable=False, default=True)
    is_occupied = Column(Boolean, nullable=False, default=False)
    description = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<Table(table_number='{self.table_number}', table_name='{self.table_name}', is_occupied='{self.is_occupied}')>" 