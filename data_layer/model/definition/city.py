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

    def __repr__(self):
        return f"<City(name='{self.name}', code='{self.code}')>" 