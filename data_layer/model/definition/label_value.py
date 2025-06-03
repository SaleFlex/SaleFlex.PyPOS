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

from sqlalchemy import Column, String, Boolean, DateTime, UUID
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD


class LabelValue(Model, CRUD):
    def __init__(self, key=None, value=None, culture_info=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.key = key
        self.value = value
        self.culture_info = culture_info

    __tablename__ = "label_value"

    id = Column(UUID, primary_key=True, default=uuid4)
    key = Column(String(100), nullable=False)
    value = Column(String(500), nullable=False)
    culture_info = Column(String(10), nullable=False, default='tr-TR')
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<LabelValue(key='{self.key}', value='{self.value}', culture='{self.culture_info}')>" 