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

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UUID
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class PosSettings(Model, CRUD, AuditMixin, SoftDeleteMixin):
    def __init__(self, name=None, owner_national_id=None, owner_tax_id=None, 
                 mac_address=None, cashier_screen_type=None, customer_screen_type=None,
                 force_to_work_online=None, fk_current_currency_id=None, **kwargs):
        Model.__init__(self)
        CRUD.__init__(self)

        self.name = name
        self.owner_national_id = owner_national_id
        self.owner_tax_id = owner_tax_id
        self.mac_address = mac_address
        self.cashier_screen_type = cashier_screen_type
        self.customer_screen_type = customer_screen_type
        if force_to_work_online is not None:
            self.force_to_work_online = force_to_work_online
        if fk_current_currency_id is not None:
            self.fk_current_currency_id = fk_current_currency_id
        
        # Handle any additional kwargs (for audit fields, etc.)
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

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
    fk_current_currency_id = Column(UUID, ForeignKey("currency.id"), nullable=True)  # Foreign key to Currency

    def __repr__(self):
        return f"<PosSettings(name='{self.name}', mac_address='{self.mac_address}')>" 