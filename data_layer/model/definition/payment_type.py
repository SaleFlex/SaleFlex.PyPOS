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


class PaymentType(Model, CRUD):
    def __init__(self, type_no=None, type_name=None, type_description=None, culture_info=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.type_no = type_no
        self.type_name = type_name
        self.type_description = type_description
        self.culture_info = culture_info

        if culture_info is None:
            self.culture_info = 'en-GB'

    __tablename__ = "payment_type"

    id = Column(UUID, primary_key=True, default=uuid4)
    type_no = Column(Integer, nullable=False, unique=True)
    type_name = Column(String(50), nullable=False)
    type_description = Column(String(150), nullable=True)
    culture_info = Column(String(10), nullable=False, default='en-GB')
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<PaymentType(type_name='{self.type_name}', type_no='{self.type_no}')>" 