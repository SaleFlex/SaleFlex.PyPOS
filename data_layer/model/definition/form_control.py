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

from sqlalchemy import Column, Integer, Boolean, String, DateTime, Float, ForeignKey, UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD


class FormControl(Model, CRUD):
    """Model representing a control element within a form."""
    def __init__(self, name="TMP_CONTROL_NAME", character_casing="NORMAL", text_alignment="LEFT", input_type="NUMERIC",
                 fk_form_id=None, fk_parent_id=None, parent_name=None, type_no=0, type="NOTYPE",
                 form_control_function1=None, form_control_function2=None, width=0, height=0,
                 location_x=0, location_y=0, start_position=None, caption1=None, caption2=None,
                 list_values=None, dock=None, alignment=None, font=None, icon=None, tool_tip=None,
                 image=None, image_selected=None, font_auto_height=True, font_size=0,
                 text_image_relation=None, back_color=None, fore_color=None, keyboard_value=None,
                 is_visible=True, fk_table_id=None, fk_target_form_id=None, form_transition_mode=None,
                 fk_cashier_create_id=None, fk_cashier_update_id=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.name = name
        self.character_casing = character_casing
        self.text_alignment = text_alignment
        self.input_type = input_type
        self.fk_form_id = fk_form_id
        self.fk_parent_id = fk_parent_id
        self.parent_name = parent_name
        self.type_no = type_no
        self.type = type
        self.form_control_function1 = form_control_function1
        self.form_control_function2 = form_control_function2
        self.width = width
        self.height = height
        self.location_x = location_x
        self.location_y = location_y
        self.start_position = start_position
        self.caption1 = caption1
        self.caption2 = caption2
        self.list_values = list_values
        self.dock = dock
        self.alignment = alignment
        self.font = font
        self.icon = icon
        self.tool_tip = tool_tip
        self.image = image
        self.image_selected = image_selected
        self.font_auto_height = font_auto_height
        self.font_size = font_size
        self.text_image_relation = text_image_relation
        self.back_color = back_color
        self.fore_color = fore_color
        self.keyboard_value = keyboard_value
        self.is_visible = is_visible
        self.fk_table_id = fk_table_id
        self.fk_target_form_id = fk_target_form_id
        self.form_transition_mode = form_transition_mode
        self.fk_cashier_create_id = fk_cashier_create_id
        self.fk_cashier_update_id = fk_cashier_update_id

    __tablename__ = "form_control"

    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    fk_form_id = Column(UUID, ForeignKey("form.id"), nullable=False)
    fk_parent_id = Column(UUID, ForeignKey("form_control.id"), nullable=True)
    parent_name = Column(String(100), nullable=True)
    type_no = Column(Integer, nullable=False)
    type = Column(String(50), nullable=False)
    form_control_function1 = Column(String(100), nullable=True)
    form_control_function2 = Column(String(100), nullable=True)
    width = Column(Integer, nullable=False, default=0)
    height = Column(Integer, nullable=False, default=0)
    location_x = Column(Integer, nullable=False, default=0)
    location_y = Column(Integer, nullable=False, default=0)
    start_position = Column(String(50), nullable=True)
    caption1 = Column(String(100), nullable=True)
    caption2 = Column(String(100), nullable=True)
    list_values = Column(String(1000), nullable=True)  # For combo boxes, list boxes etc.
    dock = Column(String(50), nullable=True)
    alignment = Column(String(50), nullable=True)
    text_alignment = Column(String(50), nullable=False, default="LEFT")
    character_casing = Column(String(50), nullable=False, default="NORMAL")
    font = Column(String(100), nullable=True)
    icon = Column(String(255), nullable=True)
    tool_tip = Column(String(255), nullable=True)
    image = Column(String(255), nullable=True)
    image_selected = Column(String(255), nullable=True)
    font_auto_height = Column(Boolean, nullable=False, default=True)
    font_size = Column(Float, nullable=False, default=0)
    input_type = Column(String(50), nullable=False, default="NUMERIC")
    text_image_relation = Column(String(50), nullable=True)
    back_color = Column(String(50), nullable=True)
    fore_color = Column(String(50), nullable=True)
    keyboard_value = Column(String(50), nullable=True)
    fk_table_id = Column(UUID, ForeignKey("table.id"), nullable=True)  # Link to Table model
    fk_target_form_id = Column(UUID, ForeignKey("form.id"), nullable=True)  # Target form for navigation
    form_transition_mode = Column(String(50), nullable=True)  # MODAL, REPLACE
    is_visible = Column(Boolean, nullable=False, default=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    fk_cashier_create_id = Column(UUID, ForeignKey("cashier.id"))
    fk_cashier_update_id = Column(UUID, ForeignKey("cashier.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    # Relationships
    form = relationship("Form", back_populates="controls", foreign_keys=[fk_form_id])
    parent = relationship("FormControl", remote_side=[id], backref="children")
    table = relationship("Table")  # Link to Table model
    target_form = relationship("Form", foreign_keys=[fk_target_form_id])  # Target form for navigation

    def __repr__(self):
        return f"<FormControl(name='{self.name}', type='{self.type}')>" 