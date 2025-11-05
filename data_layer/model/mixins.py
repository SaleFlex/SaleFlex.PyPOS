"""
SaleFlex.PyPOS - Point of Sale Application
Corrected Transaction Models with International Support

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
from sqlalchemy import (Column, Boolean, String, DateTime, ForeignKey, UUID)
from sqlalchemy.sql import func

# ====================================================================================
# MIXINS FOR REUSABLE PATTERNS
# ====================================================================================

class AuditMixin:
    """Mixin for standard audit fields"""
    fk_cashier_create_id = Column(UUID, ForeignKey("cashier.id"))
    fk_cashier_update_id = Column(UUID, ForeignKey("cashier.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class SoftDeleteMixin:
    """Mixin for soft delete functionality"""
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(UUID, ForeignKey("cashier.id"), nullable=True)