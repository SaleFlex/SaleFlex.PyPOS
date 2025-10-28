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

from sqlalchemy import Column, Integer, BigInteger, Boolean, String, DateTime, Float, ForeignKey, UUID, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD

class Form(Model, CRUD):
    """Model representing a form in the application."""
    def __init__(self, name=None, form_no=None, function=None, need_login=False, need_auth=False,
                 width=None, height=None, start_position=None, form_border_style=None, caption=None,
                 icon=None, image=None, back_color=None, fore_color=None, show_status_bar=False, 
                 show_in_taskbar=False, use_virtual_keyboard=False, is_visible=True, is_startup=False,
                 display_mode=None, fk_cashier_create_id=None, fk_cashier_update_id=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.name = name
        self.form_no = form_no
        self.function = function
        self.need_login = need_login
        self.need_auth = need_auth
        self.width = width
        self.height = height
        self.start_position = start_position
        self.form_border_style = form_border_style
        self.caption = caption
        self.icon = icon
        self.image = image
        self.back_color = back_color
        self.fore_color = fore_color
        self.show_status_bar = show_status_bar
        self.show_in_taskbar = show_in_taskbar
        self.use_virtual_keyboard = use_virtual_keyboard
        self.is_visible = is_visible
        self.is_startup = is_startup
        self.display_mode = display_mode
        self.fk_cashier_create_id = fk_cashier_create_id
        self.fk_cashier_update_id = fk_cashier_update_id

    __tablename__ = "form"

    id = Column(UUID, primary_key=True, default=uuid4)
    form_no = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    function = Column(String(100), nullable=True)
    need_login = Column(Boolean, nullable=False, default=False)
    need_auth = Column(Boolean, nullable=False, default=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    start_position = Column(String(50), nullable=True)
    form_border_style = Column(String(50), nullable=True)
    caption = Column(String(100), nullable=True)
    icon = Column(String(255), nullable=True)
    image = Column(String(255), nullable=True)
    back_color = Column(String(50), nullable=True)
    fore_color = Column(String(50), nullable=True)
    show_status_bar = Column(Boolean, nullable=False, default=True)
    show_in_taskbar = Column(Boolean, nullable=False, default=True)
    use_virtual_keyboard = Column(Boolean, nullable=False, default=False)
    is_visible = Column(Boolean, nullable=False, default=True)
    is_startup = Column(Boolean, nullable=False, default=False)
    display_mode = Column(String(50), nullable=True)  # MAIN, CUSTOMER, BOTH
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    fk_cashier_create_id = Column(UUID, ForeignKey("cashier.id"))
    fk_cashier_update_id = Column(UUID, ForeignKey("cashier.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    # Relationship to form controls
    controls = relationship("FormControl", back_populates="form", foreign_keys="[FormControl.fk_form_id]")

    def __repr__(self):
        return f"<Form(name='{self.name}', form_no='{self.form_no}')>"


