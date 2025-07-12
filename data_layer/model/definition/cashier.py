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


class Cashier(Model, CRUD):
    def __init__(self, no=None, user_name=None, name=None, last_name=None, password=None,
                 identity_number=None, description=None, is_administrator=False, is_active=False):
        Model.__init__(self)
        CRUD.__init__(self)

        self.no = no
        self.user_name = user_name
        self.name = name
        self.last_name = last_name
        self.password = password
        self.identity_number = identity_number
        self.description = description
        self.is_administrator = is_administrator
        self.is_active = is_active

    __tablename__ = "cashier"

    id = Column(UUID, primary_key=True, default=uuid4)
    no = Column(Integer, nullable=False, unique=True)
    user_name = Column(String(50), unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)
    identity_number = Column(String(24), nullable=False)
    description = Column(String(100), nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    is_administrator = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    login_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Cashier(name='{self.name}', last_name='{self.last_name}', user_name='{self.user_name}', no='{self.no}')>"

