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

from sqlalchemy.orm import Session
from data_layer.model.definition import PosVirtualKeyboard


def _insert_virtual_keyboard_settings(session: Session):
    """
    Inserts default virtual keyboard settings if not exists
    
    Args:
        session: Database session
    """
    # Check if virtual keyboard settings already exist
    existing = session.query(PosVirtualKeyboard).first()
    if existing:
        print("✓ Virtual keyboard settings already exist")
        return existing

    # Create default virtual keyboard settings
    default_keyboard = PosVirtualKeyboard(
        name="DEFAULT_VIRTUAL_KEYBOARD",
        is_active=True,
        
        # Keyboard dimensions and position
        keyboard_width=970,
        keyboard_height=315,
        x_position=0,
        y_position=0,
        
        # Font settings
        font_family="Noto Sans CJK JP",
        font_size=20,
        
        # Regular button dimensions
        button_width=80,
        button_height=40,
        button_min_width=80,
        button_max_width=80,
        button_min_height=40,
        button_max_height=40,
        
        # Button colors
        button_background_color="qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #f6f7fa, stop: 1 #dadbde)",
        button_pressed_color="rgb(29, 150, 255)",
        button_border_color="#8f8f91",
        button_border_width=3,
        button_border_radius=8,
        
        # Space button dimensions
        space_button_min_width=450,
        space_button_max_width=550,
        
        # Backspace/Enter button dimensions
        special_button_min_width=100,
        special_button_max_width=200,
        
        # Caps/Symbol/Close button dimensions
        control_button_width=120,
        control_button_active_color="rgb(29, 150, 255)",
        
        # Text colors (optional, defaults to None)
        button_text_color="#000000",
        button_text_color_pressed="#000000"
    )

    session.add(default_keyboard)
    session.commit()
    
    print(f"✓ Virtual keyboard settings created: {default_keyboard.name}")
    return default_keyboard


def _insert_alternative_keyboard_themes(session: Session):
    """
    Inserts alternative virtual keyboard themes/settings
    
    Args:
        session: Database session
    """
    # Check if dark theme already exists
    dark_theme = session.query(PosVirtualKeyboard).filter_by(name="DARK_THEME_KEYBOARD").first()
    if not dark_theme:
        dark_theme_keyboard = PosVirtualKeyboard(
            name="DARK_THEME_KEYBOARD",
            is_active=False,  # Not active by default
            
            # Keyboard dimensions and position
            keyboard_width=970,
            keyboard_height=315,
            x_position=0,
            y_position=0,
            
            # Font settings
            font_family="Noto Sans CJK JP",
            font_size=20,
            
            # Regular button dimensions
            button_width=80,
            button_height=40,
            button_min_width=80,
            button_max_width=80,
            button_min_height=40,
            button_max_height=40,
            
            # Button colors - Dark theme
            button_background_color="qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #2d2d2d, stop: 1 #1a1a1a)",
            button_pressed_color="rgb(64, 128, 255)",
            button_border_color="#555555",
            button_border_width=3,
            button_border_radius=8,
            
            # Space button dimensions
            space_button_min_width=450,
            space_button_max_width=550,
            
            # Backspace/Enter button dimensions
            special_button_min_width=100,
            special_button_max_width=200,
            
            # Caps/Symbol/Close button dimensions
            control_button_width=120,
            control_button_active_color="rgb(64, 128, 255)",
            
            # Text colors for dark theme
            button_text_color="#ffffff",
            button_text_color_pressed="#ffffff"
        )
        session.add(dark_theme_keyboard)
        print(f"✓ Virtual keyboard theme created: {dark_theme_keyboard.name}")
    
    # Check if compact theme already exists
    compact_theme = session.query(PosVirtualKeyboard).filter_by(name="COMPACT_KEYBOARD").first()
    if not compact_theme:
        compact_keyboard = PosVirtualKeyboard(
            name="COMPACT_KEYBOARD",
            is_active=False,  # Not active by default
            
            # Keyboard dimensions and position - smaller
            keyboard_width=750,
            keyboard_height=250,
            x_position=0,
            y_position=0,
            
            # Font settings - smaller
            font_family="Noto Sans CJK JP",
            font_size=16,
            
            # Regular button dimensions - smaller
            button_width=65,
            button_height=35,
            button_min_width=65,
            button_max_width=65,
            button_min_height=35,
            button_max_height=35,
            
            # Button colors
            button_background_color="qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #f6f7fa, stop: 1 #dadbde)",
            button_pressed_color="rgb(29, 150, 255)",
            button_border_color="#8f8f91",
            button_border_width=2,
            button_border_radius=6,
            
            # Space button dimensions - smaller
            space_button_min_width=350,
            space_button_max_width=450,
            
            # Backspace/Enter button dimensions - smaller
            special_button_min_width=80,
            special_button_max_width=150,
            
            # Caps/Symbol/Close button dimensions - smaller
            control_button_width=100,
            control_button_active_color="rgb(29, 150, 255)",
            
            # Text colors
            button_text_color=None,
            button_text_color_pressed=None
        )
        session.add(compact_keyboard)
        print(f"✓ Virtual keyboard theme created: {compact_keyboard.name}")
    
    session.commit()

