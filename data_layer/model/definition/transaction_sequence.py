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

from sqlalchemy import Column, Integer, String, Boolean, DateTime, UUID
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD


class TransactionSequence(Model, CRUD):
    def __init__(self, name=None, value: int = None, description=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.name = name
        self.value = value
        self.description = description

    __tablename__ = "transaction_sequence"

    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(String(50), nullable=False)
    value = Column(Integer, nullable=False)
    description = Column(String(100))
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    fk_cashier_create_id = Column(UUID, nullable=True)
    fk_cashier_update_id = Column(UUID, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<TransactionSequence(name='{self.name}', value='{self.value}')>" 