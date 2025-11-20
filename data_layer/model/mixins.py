"""
SaleFlex.PyPOS - Point of Sale Application
Corrected Transaction Models with International Support

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