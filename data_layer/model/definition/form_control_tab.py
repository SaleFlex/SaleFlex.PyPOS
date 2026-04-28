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
