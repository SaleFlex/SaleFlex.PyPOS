"""
SaleFlex.PyPOS - Point of Sale Application

Copyright (c) 2025-2026 Ferhat Mousavi

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

from sqlalchemy import Column, Integer, Boolean, String, ForeignKey, UUID
from sqlalchemy.orm import relationship
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin


class FormControlTab(Model, CRUD, AuditMixin, SoftDeleteMixin):
    """
    Defines a tab page within a TABCONTROL form control.

    Each row represents one tab page inside a specific TABCONTROL (identified by
    ``fk_form_control_id``).  Child ``FormControl`` records that belong to this tab
    reference it via the ``fk_tab_id`` column added to ``FormControl``.

    The relationship between ``FormControl`` (TABCONTROL type) and ``FormControlTab``
    is one-to-many: one TABCONTROL can have many tab pages.  The relationship between
    ``FormControlTab`` and child ``FormControl`` records is also one-to-many: one tab
    page can contain many controls.

    Using a separate table (rather than embedding tab data in ``FormControl``) keeps
    ``FormControl`` lean – the overwhelming majority of controls do not belong to a tab
    and would waste storage on nullable tab columns.
    """

    def __init__(self, fk_form_control_id=None, tab_index=0, tab_title="",
                 tab_tooltip=None, back_color=None, fore_color=None,
                 is_visible=True, fk_cashier_create_id=None, fk_cashier_update_id=None):
        Model.__init__(self)
        CRUD.__init__(self)
        self.fk_form_control_id = fk_form_control_id
        self.tab_index = tab_index
        self.tab_title = tab_title
        self.tab_tooltip = tab_tooltip
        self.back_color = back_color
        self.fore_color = fore_color
        self.is_visible = is_visible
        self.fk_cashier_create_id = fk_cashier_create_id
        self.fk_cashier_update_id = fk_cashier_update_id

    __tablename__ = "form_control_tab"

    id = Column(UUID, primary_key=True, default=uuid4)

    # FK to the parent TABCONTROL form_control record
    fk_form_control_id = Column(UUID, ForeignKey("form_control.id"), nullable=False)

    tab_index = Column(Integer, nullable=False, default=0)
    tab_title = Column(String(100), nullable=False)
    tab_tooltip = Column(String(200), nullable=True)
    back_color = Column(String(20), nullable=True)
    fore_color = Column(String(20), nullable=True)
    is_visible = Column(Boolean, nullable=False, default=True)

    # Relationship: back-reference to the parent TABCONTROL FormControl
    form_control = relationship(
        "FormControl",
        foreign_keys=[fk_form_control_id],
        back_populates="tab_pages",
    )

    def __repr__(self):
        return (
            f"<FormControlTab(tab_index={self.tab_index}, "
            f"tab_title='{self.tab_title}')>"
        )
