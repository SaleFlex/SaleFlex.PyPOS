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

from sqlalchemy import Column, Integer, String, Boolean, DateTime, UUID
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD


class Country(Model, CRUD):
    def __init__(self, name=None, iso_alpha2=None, iso_alpha3=None, iso_numeric=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.name = name
        self.iso_alpha2 = iso_alpha2
        self.iso_alpha3 = iso_alpha3
        self.iso_numeric = iso_numeric

    __tablename__ = "country"

    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    # ISO 3166-1 alpha-2: 2-letter country code (e.g., "US", "TR", "CA")
    iso_alpha2 = Column(String(2), nullable=False, unique=True)
    # ISO 3166-1 alpha-3: 3-letter country code (e.g., "USA", "TUR", "CAN")
    iso_alpha3 = Column(String(3), nullable=True)
    # ISO 3166-1 numeric: 3-digit numeric country code (e.g., 840 for US, 792 for TR)
    iso_numeric = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<Country(name='{self.name}', iso_alpha2='{self.iso_alpha2}')>" 