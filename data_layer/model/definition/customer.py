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

from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, Integer, UUID, Date, Text
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import SoftDeleteMixin


class Customer(Model, CRUD, SoftDeleteMixin):
    """
    Stores customer information including personal details and preferences
    Extended to support loyalty programs and customer segmentation
    """
    def __init__(self, name=None, last_name=None, address_line_1=None, address_line_2=None, address_line_3=None,
                 email_address=None, phone_number=None, zip_code=None, description=None,
                 date_of_birth=None, gender=None, national_id=None, tax_id=None,
                 registration_source=None, marketing_consent=False, sms_consent=False,
                 email_consent=False, preferences_json=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.name = name
        self.last_name = last_name
        self.address_line_1 = address_line_1
        self.address_line_2 = address_line_2
        self.address_line_3 = address_line_3
        self.email_address = email_address
        self.phone_number = phone_number
        self.zip_code = zip_code
        self.description = description
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.national_id = national_id
        self.tax_id = tax_id
        self.registration_source = registration_source
        self.marketing_consent = marketing_consent
        self.sms_consent = sms_consent
        self.email_consent = email_consent
        self.preferences_json = preferences_json

    __tablename__ = "customer"

    id = Column(UUID, primary_key=True, default=uuid4)
    
    # Basic information
    name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    
    # Contact information
    address_line_1 = Column(String(100), nullable=True)
    address_line_2 = Column(String(100), nullable=True)
    address_line_3 = Column(String(100), nullable=True)
    email_address = Column(String(100), nullable=True)
    phone_number = Column(String(100), nullable=True)
    zip_code = Column(String(50), nullable=True)
    
    # Additional personal information
    date_of_birth = Column(Date, nullable=True)  # For birthday campaigns and age segmentation
    gender = Column(String(20), nullable=True)  # MALE, FEMALE, OTHER, PREFER_NOT_TO_SAY
    national_id = Column(String(50), nullable=True)  # National ID number
    tax_id = Column(String(50), nullable=True)  # Tax ID for invoicing
    
    # Registration tracking
    registration_source = Column(String(50), nullable=True)  # POS, MOBILE_APP, WEBSITE, SOCIAL_MEDIA, REFERRAL
    
    # Marketing preferences (GDPR/KVKK compliance)
    marketing_consent = Column(Boolean, nullable=False, default=False)
    sms_consent = Column(Boolean, nullable=False, default=False)
    email_consent = Column(Boolean, nullable=False, default=False)
    
    # Customer preferences stored as JSON
    # Example: {"favorite_products": [], "preferred_payment": "CREDIT_CARD", "language": "TR"}
    preferences_json = Column(Text, nullable=True)
    
    description = Column(String(100))
    
    # Legacy loyalty points field (consider migrating to customer_loyalty table)
    total_bonus_point = Column(Integer, nullable=False, default=0)
    
    # Status flags
    is_administrator = Column(Boolean(False), default=False)
    is_active = Column(Boolean(False), default=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    login_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Customer(name='{self.name}', last_name='{self.last_name}')>"

