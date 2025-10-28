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

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, UUID
from sqlalchemy.sql import func
from uuid import uuid4

from data_layer.model.crud_model import Model
from data_layer.model.crud_model import CRUD


class PosVirtualKeyboard(Model, CRUD):
    """Model representing virtual keyboard settings and appearance."""
    def __init__(self, name="DEFAULT_VIRTUAL_KEYBOARD", is_active=True, 
                 keyboard_width=970, keyboard_height=315, x_position=0, y_position=0,
                 # Font settings
                 font_family="Noto Sans CJK JP", font_size=20,
                 # Regular button settings
                 button_width=80, button_height=40, button_min_width=80, button_max_width=80,
                 button_min_height=40, button_max_height=40,
                 button_background_color="qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #f6f7fa, stop: 1 #dadbde)",
                 button_pressed_color="rgb(29, 150, 255)",
                 button_border_color="#8f8f91", button_border_width=3, button_border_radius=8,
                 # Space button settings
                 space_button_min_width=450, space_button_max_width=550,
                 # Backspace/Enter button settings
                 special_button_min_width=100, special_button_max_width=200,
                 # Caps/Symbol/Close button settings
                 control_button_width=120,
                 control_button_active_color="rgb(29, 150, 255)",
                 # Text colors
                 button_text_color=None, button_text_color_pressed=None):
        Model.__init__(self)
        CRUD.__init__(self)

        self.name = name
        self.is_active = is_active
        self.keyboard_width = keyboard_width
        self.keyboard_height = keyboard_height
        self.x_position = x_position
        self.y_position = y_position
        
        # Font settings
        self.font_family = font_family
        self.font_size = font_size
        
        # Regular button settings
        self.button_width = button_width
        self.button_height = button_height
        self.button_min_width = button_min_width
        self.button_max_width = button_max_width
        self.button_min_height = button_min_height
        self.button_max_height = button_max_height
        self.button_background_color = button_background_color
        self.button_pressed_color = button_pressed_color
        self.button_border_color = button_border_color
        self.button_border_width = button_border_width
        self.button_border_radius = button_border_radius
        
        # Space button settings
        self.space_button_min_width = space_button_min_width
        self.space_button_max_width = space_button_max_width
        
        # Backspace/Enter button settings
        self.special_button_min_width = special_button_min_width
        self.special_button_max_width = special_button_max_width
        
        # Caps/Symbol/Close button settings
        self.control_button_width = control_button_width
        self.control_button_active_color = control_button_active_color
        
        # Text colors
        self.button_text_color = button_text_color
        self.button_text_color_pressed = button_text_color_pressed

    __tablename__ = "pos_virtual_keyboard"

    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Keyboard dimensions and position
    keyboard_width = Column(Integer, nullable=False, default=970)
    keyboard_height = Column(Integer, nullable=False, default=315)
    x_position = Column(Integer, nullable=False, default=0)
    y_position = Column(Integer, nullable=False, default=0)
    
    # Font settings
    font_family = Column(String(100), nullable=False, default="Noto Sans CJK JP")
    font_size = Column(Integer, nullable=False, default=20)
    
    # Regular button dimensions
    button_width = Column(Integer, nullable=False, default=80)
    button_height = Column(Integer, nullable=False, default=40)
    button_min_width = Column(Integer, nullable=False, default=80)
    button_max_width = Column(Integer, nullable=False, default=80)
    button_min_height = Column(Integer, nullable=False, default=40)
    button_max_height = Column(Integer, nullable=False, default=40)
    
    # Button colors
    button_background_color = Column(String(500), nullable=False, 
                                     default="qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #f6f7fa, stop: 1 #dadbde)")
    button_pressed_color = Column(String(100), nullable=False, default="rgb(29, 150, 255)")
    button_border_color = Column(String(50), nullable=False, default="#8f8f91")
    button_border_width = Column(Integer, nullable=False, default=3)
    button_border_radius = Column(Integer, nullable=False, default=8)
    
    # Space button dimensions
    space_button_min_width = Column(Integer, nullable=False, default=450)
    space_button_max_width = Column(Integer, nullable=False, default=550)
    
    # Backspace/Enter button dimensions
    special_button_min_width = Column(Integer, nullable=False, default=100)
    special_button_max_width = Column(Integer, nullable=False, default=200)
    
    # Caps/Symbol/Close button dimensions
    control_button_width = Column(Integer, nullable=False, default=120)
    control_button_active_color = Column(String(100), nullable=False, default="rgb(29, 150, 255)")
    
    # Text colors
    button_text_color = Column(String(50), nullable=True)
    button_text_color_pressed = Column(String(50), nullable=True)
    
    # Standard fields
    is_deleted = Column(Boolean, nullable=False, default=False)
    delete_description = Column(String(1000), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<PosVirtualKeyboard(name='{self.name}', is_active={self.is_active})>"

