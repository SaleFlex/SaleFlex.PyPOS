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

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UUID
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD


class PosSettings(Model, CRUD):
    def __init__(self, name=None, owner_national_id=None, owner_tax_id=None, 
                 mac_address=None, cashier_screen_type=None, customer_screen_type=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.name = name
        self.owner_national_id = owner_national_id
        self.owner_tax_id = owner_tax_id
        self.mac_address = mac_address
        self.cashier_screen_type = cashier_screen_type
        self.customer_screen_type = customer_screen_type

    __tablename__ = "pos_settings"

    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    owner_national_id = Column(String(20), nullable=True)
    owner_tax_id = Column(String(20), nullable=True)
    owner_mersis_id = Column(String(20), nullable=True)
    owner_commercial_record_no = Column(String(20), nullable=True)
    owner_web_address = Column(String(100), nullable=True)
    owner_registration_number = Column(String(20), nullable=True)
    mac_address = Column(String(50), nullable=True)
    cashier_screen_type = Column(String(20), nullable=True)
    customer_screen_type = Column(String(20), nullable=True)
    customer_display_type = Column(String(20), nullable=True)
    customer_display_port = Column(String(20), nullable=True)
    receipt_printer_type = Column(String(20), nullable=True)
    receipt_printer_port = Column(String(20), nullable=True)
    invoice_printer_type = Column(String(20), nullable=True)
    invoice_printer_port = Column(String(20), nullable=True)
    scale_type = Column(String(20), nullable=True)
    scale_port = Column(String(20), nullable=True)
    barcode_reader_port = Column(String(20), nullable=True)
    server_ip1 = Column(String(15), nullable=True)
    server_port1 = Column(Integer, nullable=True)
    server_ip2 = Column(String(15), nullable=True)
    server_port2 = Column(Integer, nullable=True)
    force_to_work_online = Column(Boolean, nullable=False, default=False)
    plu_update_no = Column(Integer, nullable=False, default=0)
    fk_default_country_id = Column(UUID, ForeignKey("country.id"), nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<PosSettings(name='{self.name}', mac_address='{self.mac_address}')>" 