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

from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, UUID, Integer, ForeignKey
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class Store(Model, CRUD, AuditMixin, SoftDeleteMixin):
    def __init__(self, name=None, brand_name=None, company_name=None,
                 web_page_url=None, description=None, serial_number=None,
                 model=None, operating_system_version=None, owner_national_id_number=None,
                 owner_tax_id_number=None, owner_mersis_id_number=None,
                 owner_commercial_record_no=None, owner_registration_number=None,
                 mac_address=None, cashier_screen_type=None, customer_screen_type=None,
                 customer_display_type=None, customer_display_port=None,
                 receipt_printer_type=None, receipt_printer_port_name=None,
                 invoice_printer_type=None, invoice_printer_port_name=None,
                 scale_type=None, scale_port_name=None, barcode_reader_port=None,
                 server_ip1=None, server_port1=None, server_ip2=None, server_port2=None,
                 force_to_work_online=False, fk_default_country_id=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.name = name
        self.brand_name = brand_name
        self.company_name = company_name
        self.web_page_url = web_page_url
        self.description = description
        self.serial_number = serial_number
        self.model = model
        self.operating_system_version = operating_system_version
        self.owner_national_id_number = owner_national_id_number
        self.owner_tax_id_number = owner_tax_id_number
        self.owner_mersis_id_number = owner_mersis_id_number
        self.owner_commercial_record_no = owner_commercial_record_no
        self.owner_registration_number = owner_registration_number
        self.mac_address = mac_address
        self.cashier_screen_type = cashier_screen_type
        self.customer_screen_type = customer_screen_type
        self.customer_display_type = customer_display_type
        self.customer_display_port = customer_display_port
        self.receipt_printer_type = receipt_printer_type
        self.receipt_printer_port_name = receipt_printer_port_name
        self.invoice_printer_type = invoice_printer_type
        self.invoice_printer_port_name = invoice_printer_port_name
        self.scale_type = scale_type
        self.scale_port_name = scale_port_name
        self.barcode_reader_port = barcode_reader_port
        self.server_ip1 = server_ip1
        self.server_port1 = server_port1
        self.server_ip2 = server_ip2
        self.server_port2 = server_port2
        self.force_to_work_online = force_to_work_online
        self.fk_default_country_id = fk_default_country_id

    __tablename__ = "store"

    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(String(250), nullable=False)
    brand_name = Column(String(50), nullable=True)
    company_name = Column(String(50), nullable=True)
    web_page_url = Column(String(250), nullable=True)
    description = Column(String(100), nullable=True)
    
    # Hardware and system information
    serial_number = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    operating_system_version = Column(String(100), nullable=True)
    mac_address = Column(String(17), nullable=True)  # MAC address format: XX:XX:XX:XX:XX:XX
    
    # Owner information
    owner_national_id_number = Column(String(20), nullable=True)
    owner_tax_id_number = Column(String(20), nullable=True)
    owner_mersis_id_number = Column(String(20), nullable=True)
    owner_commercial_record_no = Column(String(50), nullable=True)
    owner_registration_number = Column(String(50), nullable=True)
    
    # Screen and display settings
    cashier_screen_type = Column(String(50), nullable=True)
    customer_screen_type = Column(String(50), nullable=True)
    customer_display_type = Column(String(50), nullable=True)
    customer_display_port = Column(String(50), nullable=True)
    
    # Printer settings
    receipt_printer_type = Column(String(50), nullable=True)
    receipt_printer_port_name = Column(String(50), nullable=True)
    invoice_printer_type = Column(String(50), nullable=True)
    invoice_printer_port_name = Column(String(50), nullable=True)
    
    # Scale settings
    scale_type = Column(String(50), nullable=True)
    scale_port_name = Column(String(50), nullable=True)
    
    # Barcode reader settings
    barcode_reader_port = Column(String(50), nullable=True)
    
    # Server settings
    server_ip1 = Column(String(15), nullable=True)  # IPv4 address
    server_port1 = Column(String(10), nullable=True)
    server_ip2 = Column(String(15), nullable=True)  # IPv4 address
    server_port2 = Column(String(10), nullable=True)
    
    # System settings
    force_to_work_online = Column(Boolean, nullable=False, default=False)
    fk_default_country_id = Column(UUID, ForeignKey('country.id'), nullable=True)
    
    def __repr__(self):
        return f"<Store(name='{self.name}', brand_name='{self.brand_name}', company_name='{self.company_name}', serial_number='{self.serial_number}')>"

