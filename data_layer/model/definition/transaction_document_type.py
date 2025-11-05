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
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class TransactionDocumentType(Model, CRUD, AuditMixin, SoftDeleteMixin):
    def __init__(self, no=None, name=None, display_name=None, description=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.no = no
        self.name = name
        self.display_name = display_name
        self.description = description

    __tablename__ = "transaction_document_type"

    id = Column(UUID, primary_key=True, default=uuid4)
    no = Column(Integer, nullable=False, unique=True)
    name = Column(String(50), nullable=False)
    display_name = Column(String(50), nullable=True)
    description = Column(String(150), nullable=True)

    def __repr__(self):
        return f"<TransactionDocumentType(name='{self.name}', display_name='{self.display_name}', no='{self.no}')>" 