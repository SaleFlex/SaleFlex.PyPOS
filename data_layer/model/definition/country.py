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