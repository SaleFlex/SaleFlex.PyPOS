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

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, UUID, Text
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class Warehouse(Model, CRUD, AuditMixin, SoftDeleteMixin):
    def __init__(self, name=None, code=None, warehouse_type=None, fk_store_id=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.name = name
        self.code = code
        self.warehouse_type = warehouse_type
        self.fk_store_id = fk_store_id

    __tablename__ = "warehouse"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_server_id = Column(Integer, nullable=True)  # For server synchronization
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=False, unique=True)
    description = Column(String(500), nullable=True)
    
    # Warehouse type classification for retail stores
    warehouse_type = Column(String(50), nullable=False)  # MAIN, BACKROOM, SALES_FLOOR, COLD_STORAGE, SECURITY, TEMPORARY
    
    # Physical information
    address = Column(String(500), nullable=True)
    total_area = Column(Float, nullable=True)  # Total area in square meters
    usable_area = Column(Float, nullable=True)  # Usable storage area in square meters
    height = Column(Float, nullable=True)  # Height in meters
    max_capacity = Column(Float, nullable=True)  # Maximum capacity in cubic meters
    
    # Environmental conditions
    temperature_controlled = Column(Boolean, nullable=False, default=False)
    min_temperature = Column(Float, nullable=True)  # Minimum temperature in Celsius
    max_temperature = Column(Float, nullable=True)  # Maximum temperature in Celsius
    humidity_controlled = Column(Boolean, nullable=False, default=False)
    min_humidity = Column(Float, nullable=True)  # Minimum humidity percentage
    max_humidity = Column(Float, nullable=True)  # Maximum humidity percentage
    
    # Security and access
    requires_security_access = Column(Boolean, nullable=False, default=False)
    access_code = Column(String(20), nullable=True)  # Access code for restricted areas
    security_level = Column(String(20), nullable=True)  # LOW, MEDIUM, HIGH
    
    # Operational information
    is_active = Column(Boolean, nullable=False, default=True)
    is_receiving_enabled = Column(Boolean, nullable=False, default=True)
    is_shipping_enabled = Column(Boolean, nullable=False, default=True)
    is_cycle_count_enabled = Column(Boolean, nullable=False, default=True)
    
    # Contact information
    manager_name = Column(String(100), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    contact_email = Column(String(100), nullable=True)
    
    # Operating hours
    operating_hours = Column(String(200), nullable=True)  # JSON format for weekly schedule
    
    # Special handling capabilities
    hazardous_material_allowed = Column(Boolean, nullable=False, default=False)
    fragile_items_area = Column(Boolean, nullable=False, default=False)
    high_value_items_area = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    fk_store_id = Column(UUID, ForeignKey("store.id"), nullable=False)
    fk_city_id = Column(UUID, ForeignKey("city.id"), nullable=True)
    fk_district_id = Column(UUID, ForeignKey("district.id"), nullable=True)
    
    def __repr__(self):
        return f"<Warehouse(name='{self.name}', code='{self.code}', type='{self.warehouse_type}')>" 