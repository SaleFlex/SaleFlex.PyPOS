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
import enum

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD


class FormType(enum.Enum):
    """Enum representing different types of forms used in the system."""
    NONE = 0           # No form selected.
    SALE = 1           # Sale transaction form.
    LOGIN = 2          # Login form.
    LOGIN_EXT = 3      # Extended login form.
    LOGIN_SERVICE = 4  # Service login form.
    SERVICE = 5        # Service-related form.
    SETTING = 6        # Settings configuration form.
    PARAMETER = 7      # Parameter configuration form.
    REPORT = 8         # Report form.
    FUNCTION = 9       # Function selection form.
    CUSTOMER = 10      # Customer-related form.
    VOID = 11          # Form for voiding a transaction.
    REFUND = 12        # Refund transaction form.
    STOCK = 13         # Stock management form.
    END_OF_DAY = 14    # End-of-day process form.
    TABLE = 15         # Table management form (e.g., for restaurants).
    ORDER = 16         # Order management form.
    CHECK = 17         # Check payment form.
    EMPLOYEE = 18      # Employee management form.
    RESERVATION = 19   # Reservation form.
    WAREHOUSE = 20     # Warehouse form.


class ControlType(enum.Enum):
    """Enum representing different types of form controls."""
    NONE = 0
    BUTTON = 1
    PICTURE = 2
    LABEL = 3
    TEXT_BOX = 4
    COMBO_BOX = 5
    TOOL_BAR = 6
    MENU = 7
    MENU_ITEM = 8
    MENU_SUB_ITEM = 9
    TAB_PAGE = 10
    TAB_PAGE_ITEM = 11
    PANEL = 12
    WEB_BROWSER = 13
    GROUP = 14
    DATA_VIEW = 15
    POP_UP = 16
    LIST_BOX = 17
    CHECK_BOX = 18


class Form(Model, CRUD):
    """Model representing a form in the application."""
    def __init__(self, name=None, form_no=None, function=None, need_login=False, need_auth=False,
                 width=None, height=None, start_position=None, form_border_style=None, caption=None,
                 icon=None, image=None, back_color=None, show_status_bar=False, show_in_taskbar=False,
                 use_virtual_keyboard=False, is_visible=True):
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
        self.show_status_bar = show_status_bar
        self.show_in_taskbar = show_in_taskbar
        self.use_virtual_keyboard = use_virtual_keyboard
        self.is_visible = is_visible

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
    show_status_bar = Column(Boolean, nullable=False, default=True)
    show_in_taskbar = Column(Boolean, nullable=False, default=True)
    use_virtual_keyboard = Column(Boolean, nullable=False, default=False)
    is_visible = Column(Boolean, nullable=False, default=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    fk_cashier_create_id = Column(UUID, ForeignKey("cashier.id"))
    fk_cashier_update_id = Column(UUID, ForeignKey("cashier.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    # Relationship to form controls
    controls = relationship("FormControl", back_populates="form")

    def __repr__(self):
        return f"<Form(name='{self.name}', form_no='{self.form_no}')>"


class FormFunction(Model, CRUD):
    """Model representing a function that can be associated with a form."""
    def __init__(self, name=None, no=None, need_login=False, need_auth=False):
        Model.__init__(self)
        CRUD.__init__(self)

        self.name = name
        self.no = no
        self.need_login = need_login
        self.need_auth = need_auth

    __tablename__ = "form_function"

    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    no = Column(Integer, nullable=False)
    need_login = Column(Boolean, nullable=False, default=False)
    need_auth = Column(Boolean, nullable=False, default=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    fk_cashier_create_id = Column(UUID, ForeignKey("cashier.id"))
    fk_cashier_update_id = Column(UUID, ForeignKey("cashier.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<FormFunction(name='{self.name}', no='{self.no}')>"


class FormControlFunction(Model, CRUD):
    """Model representing a function that can be associated with a form control."""
    def __init__(self, name=None, no=None, description=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.name = name
        self.no = no
        self.description = description

    __tablename__ = "form_control_function"

    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    no = Column(Integer, nullable=False)
    description = Column(String(255), nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    fk_cashier_create_id = Column(UUID, ForeignKey("cashier.id"))
    fk_cashier_update_id = Column(UUID, ForeignKey("cashier.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<FormControlFunction(name='{self.name}', no='{self.no}')>"


class FormControl(Model, CRUD):
    """Model representing a control element within a form."""
    def __init__(self, name="TMP_CONTROL_NAME", character_casing="NORMAL", text_alignment="LEFT", input_type="NUMERIC"):
        Model.__init__(self)
        CRUD.__init__(self)

        self.name = name
        self.character_casing = character_casing
        self.text_alignment = text_alignment
        self.input_type = input_type
        self.height = 0
        self.width = 0
        self.type = "NOTYPE"
        self.font = ""
        self.image = ""
        self.font_auto_height = True
        self.font_size = 0
        self.caption1 = ""

    __tablename__ = "form_control"

    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    fk_form_id = Column(UUID, ForeignKey("form.id"), nullable=False)
    fk_parent_id = Column(UUID, ForeignKey("form_control.id"), nullable=True)
    parent_name = Column(String(100), nullable=True)
    type_no = Column(Integer, nullable=False)
    type = Column(String(50), nullable=False)
    fk_control_function1_id = Column(UUID, ForeignKey("form_control_function.id"), nullable=True)
    fk_control_function2_id = Column(UUID, ForeignKey("form_control_function.id"), nullable=True)
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
    is_visible = Column(Boolean, nullable=False, default=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    fk_cashier_create_id = Column(UUID, ForeignKey("cashier.id"))
    fk_cashier_update_id = Column(UUID, ForeignKey("cashier.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    # Relationships
    form = relationship("Form", back_populates="controls")
    parent = relationship("FormControl", remote_side=[id], backref="children")
    control_function1 = relationship("FormControlFunction", foreign_keys=[fk_control_function1_id])
    control_function2 = relationship("FormControlFunction", foreign_keys=[fk_control_function2_id])

    def __repr__(self):
        return f"<FormControl(name='{self.name}', type='{self.type}')>" 