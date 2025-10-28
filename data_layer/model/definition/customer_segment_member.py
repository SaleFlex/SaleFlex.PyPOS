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

from sqlalchemy import Column, String, Boolean, DateTime, UUID, ForeignKey, Text
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD


class CustomerSegmentMember(Model, CRUD):
    """
    Links customers to segments
    A customer can belong to multiple segments simultaneously
    """
    def __init__(self, fk_customer_id=None, fk_customer_segment_id=None,
                 assigned_date=None, assigned_by=None, assignment_reason=None,
                 is_active=True):
        Model.__init__(self)
        CRUD.__init__(self)

        self.fk_customer_id = fk_customer_id
        self.fk_customer_segment_id = fk_customer_segment_id
        self.assigned_date = assigned_date
        self.assigned_by = assigned_by
        self.assignment_reason = assignment_reason
        self.is_active = is_active

    __tablename__ = "customer_segment_member"

    id = Column(UUID, primary_key=True, default=uuid4)
    fk_customer_id = Column(UUID, ForeignKey('customer.id'), nullable=False)
    fk_customer_segment_id = Column(UUID, ForeignKey('customer_segment.id'), nullable=False)
    
    # Assignment tracking
    assigned_date = Column(DateTime, server_default=func.now())
    assigned_by = Column(String(50), nullable=True)  # MANUAL, AUTO, SYSTEM
    assignment_reason = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<CustomerSegmentMember(customer_id='{self.fk_customer_id}', segment_id='{self.fk_customer_segment_id}')>"

