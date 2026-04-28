"""
SaleFlex.PyPOS - Point of Sale Application
Copyright (C) 2025-2026 Mousavi.Tech

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from sqlalchemy import Column, String, UUID, Boolean, ForeignKey
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class Store(Model, CRUD, AuditMixin, SoftDeleteMixin):
    def __init__(self, brand_name=None, company_name=None,
                 web_page_url=None, description=None,
                 street=None, block_no=None, district=None, postal_code=None,
                 fk_city_id=None, fk_country_id=None,
                 phone_number=None, email=None, fax=None,
                 manager_name=None, manager_contact_number=None,
                 technician_name=None, technician_contact_number=None,
                 is_active=True):
        Model.__init__(self)
        CRUD.__init__(self)

        self.brand_name = brand_name
        self.company_name = company_name
        self.web_page_url = web_page_url
        self.description = description
        
        # Address fields
        self.street = street
        self.block_no = block_no
        self.district = district
        self.postal_code = postal_code
        self.fk_city_id = fk_city_id
        self.fk_country_id = fk_country_id
        
        # Contact information
        self.phone_number = phone_number
        self.email = email
        self.fax = fax
        
        # Manager information
        self.manager_name = manager_name
        self.manager_contact_number = manager_contact_number
        
        # Technician information
        self.technician_name = technician_name
        self.technician_contact_number = technician_contact_number
        
        # Status
        self.is_active = is_active

    __tablename__ = "store"

    id = Column(UUID, primary_key=True, default=uuid4)
    
    # Basic information
    brand_name = Column(String(50), nullable=True)
    company_name = Column(String(50), nullable=True)
    web_page_url = Column(String(250), nullable=True)
    description = Column(String(100), nullable=True)
    
    # Address fields
    street = Column(String(150), nullable=True)
    block_no = Column(String(20), nullable=True)
    district = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    fk_city_id = Column(UUID, ForeignKey('city.id'), nullable=True)
    fk_country_id = Column(UUID, ForeignKey('country.id'), nullable=True)
    
    # Contact information
    phone_number = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    fax = Column(String(20), nullable=True)
    
    # Manager information
    manager_name = Column(String(100), nullable=True)
    manager_contact_number = Column(String(20), nullable=True)
    
    # Technician information
    technician_name = Column(String(100), nullable=True)
    technician_contact_number = Column(String(20), nullable=True)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    
    def __repr__(self):
        return f"<Store(brand_name='{self.brand_name}', company_name='{self.company_name}', is_active={self.is_active})>"

