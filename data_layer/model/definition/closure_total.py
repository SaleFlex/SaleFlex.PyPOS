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

from sqlalchemy import Column, Integer, BigInteger, Boolean, String, DateTime, Float, ForeignKey, UUID
from sqlalchemy.sql import func

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD


class ClosureTotal(Model, CRUD):
    def __init__(self):
        Model.__init__(self)
        CRUD.__init__(self)

    __tablename__ = "closure_total"

    id = Column(BigInteger, primary_key=True, autoincrement=True, default=1)
    fk_closure_id = Column(BigInteger, ForeignKey("closure.id"))
    fk_department_main_group_id = Column(BigInteger, ForeignKey("department_main_group.id"), nullable=False)
    department_count = Column(Integer, nullable=False)
    total_department = Column(Float, nullable=False)
    total_department_vat = Column(Float, nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    is_modified = Column(Boolean, nullable=False, default=False)
    fk_cashier_modified_id = Column(BigInteger, ForeignKey("cashier.id"))
    modified_description = Column(String(1000), nullable=True)
    fk_cashier_create_id = Column(BigInteger, ForeignKey("cashier.id"))
    fk_cashier_update_id = Column(BigInteger, ForeignKey("cashier.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<ClosureTotal(total_department='{self.total_department}', total_department_vat='{self.total_department_vat}')>"
