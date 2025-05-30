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

from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, Float, ForeignKey, UUID
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD


class DepartmentSubGroup(Model, CRUD):
    def __init__(self, main_group_id=None, code=None, name=None, description=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.main_group_id = main_group_id
        self.code = code
        self.name = name
        self.description = description

    __tablename__ = "department_sub_group"

    id = Column(UUID, primary_key=True, default=uuid4)
    code = Column(String(10), nullable=False)
    name = Column(String(50), nullable=False)
    main_group_id = Column(UUID, nullable=True)  # Removed ForeignKey constraint
    description = Column(String(100), nullable=True)
    max_price = Column(Float, nullable=True)
    discount_rate = Column(Float, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    fk_cashier_create_id = Column(UUID, nullable=True)  # Removed ForeignKey constraint
    fk_cashier_update_id = Column(UUID, nullable=True)  # Removed ForeignKey constraint
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<DepartmentSubGroup(name='{self.name}', code='{self.code}', description='{self.description}')>"
