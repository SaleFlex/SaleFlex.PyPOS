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

from sqlalchemy import Column, Integer, String, Boolean, DateTime, UUID, ForeignKey
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD


class City(Model, CRUD):
    def __init__(self, name=None, code=None, short_name=None, numeric_code=None, fk_country_id=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.name = name
        self.code = code
        self.short_name = short_name
        self.numeric_code = numeric_code
        self.fk_country_id = fk_country_id

    __tablename__ = "city"

    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=False, unique=True)
    short_name = Column(String(10), nullable=True)
    numeric_code = Column(Integer, nullable=True)
    fk_country_id = Column(UUID, ForeignKey("country.id"), nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<City(name='{self.name}', code='{self.code}')>" 