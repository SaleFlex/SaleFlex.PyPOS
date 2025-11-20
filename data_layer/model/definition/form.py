"""
SaleFlex.PyPOS - Point of Sale Application

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

from sqlalchemy import Column, Integer, BigInteger, Boolean, String, DateTime, Float, ForeignKey, UUID, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD
from data_layer.model.mixins import AuditMixin, SoftDeleteMixin

class Form(Model, CRUD, AuditMixin, SoftDeleteMixin):
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

    # Relationship to form controls
    controls = relationship("FormControl", back_populates="form", foreign_keys="[FormControl.fk_form_id]")

    def __repr__(self):
        return f"<Form(name='{self.name}', form_no='{self.form_no}')>"


