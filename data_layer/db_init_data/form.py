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
from data_layer.model.definition.form import Form
from data_layer.enums import FormName


def _insert_default_forms(session: Session, cashier_id: str):
    """
    Insert default forms (LOGIN and SALE) if they don't exist.
    This corresponds to the C# TableForm initialization.
    """
    # Check if any forms exist
    existing_forms = session.query(Form).first()
    
    if existing_forms:
        print("✓ Forms already exist, skipping insertion")
        return

    # Default forms data with new dynamic rendering fields
    # Using FormName enum to ensure consistency with the rest of the application
    forms_data = [
        {
            'form_no': 1,
            'name': FormName.LOGIN.name,  # Using enum for form name
            'function': FormName.LOGIN.name,  # Using enum for function name
            'need_login': False,
            'need_auth': False,
            'width': 1024,
            'height': 768,
            'form_border_style': 'SINGLE',
            'start_position': 'CENTERSCREEN',
            'caption': 'SaleFlex - Login',
            'back_color': '0x191970',  # MidnightBlue
            'fore_color': '0xFFFFFF',  # White
            'show_status_bar': False,
            'show_in_taskbar': False,
            'use_virtual_keyboard': True,
            'is_visible': True,
            'is_startup': False,
            'display_mode': 'MAIN',
            'fk_cashier_create_id': cashier_id
        },
        {
            'form_no': 2,
            'name': FormName.MAIN_MENU.name,
            'function': FormName.MAIN_MENU.name,
            'need_login': True,  # Requires login
            'need_auth': False,
            'width': 1024,
            'height': 768,
            'form_border_style': 'SINGLE',
            'start_position': 'CENTERSCREEN',
            'caption': 'SaleFlex - Main Menu',
            'back_color': '0x2F4F4F',  # DarkSlateGray
            'fore_color': '0xFFFFFF',  # White
            'show_status_bar': True,
            'show_in_taskbar': False,
            'use_virtual_keyboard': False,
            'is_visible': True,
            'is_startup': True,  # MAIN_MENU is the startup form
            'display_mode': 'MAIN',
            'fk_cashier_create_id': cashier_id
        },
        {
            'form_no': 3,
            'name': FormName.SETTING.name,
            'function': FormName.SETTING.name,
            'need_login': True,  # Requires login
            'need_auth': False,
            'width': 1024,
            'height': 768,
            'form_border_style': 'SINGLE',
            'start_position': 'CENTERSCREEN',
            'caption': 'SaleFlex - Configuration',
            'back_color': '0x2F4F4F',  # DarkSlateGray
            'fore_color': '0xFFFFFF',  # White
            'show_status_bar': True,
            'show_in_taskbar': False,
            'use_virtual_keyboard': False,
            'is_visible': True,
            'is_startup': False,
            'display_mode': 'MAIN',
            'fk_cashier_create_id': cashier_id
        },
        {
            'form_no': 4,
            'name': FormName.CASHIER.name,
            'function': FormName.CASHIER.name,
            'need_login': True,  # Requires login
            'need_auth': False,
            'width': 1024,
            'height': 768,
            'form_border_style': 'SINGLE',
            'start_position': 'CENTERSCREEN',
            'caption': 'SaleFlex - Cashier Management',
            'back_color': '0x2F4F4F',  # DarkSlateGray
            'fore_color': '0xFFFFFF',  # White
            'show_status_bar': True,
            'show_in_taskbar': False,
            'use_virtual_keyboard': True,
            'is_visible': True,
            'is_startup': False,
            'display_mode': 'MAIN',
            'fk_cashier_create_id': cashier_id
        },
        {
            'form_no': 5,
            'name': FormName.SALE.name,  # Using enum for form name
            'function': FormName.SALE.name,  # Using enum for function name
            'need_login': True,  # Requires login
            'need_auth': False,
            'width': 1024,
            'height': 768,
            'form_border_style': 'SINGLE',
            'start_position': 'CENTERSCREEN',
            'caption': 'SaleFlex - Point of Sale',
            'back_color': '0x2F4F4F',  # DarkSlateGray
            'fore_color': '0xFFFFFF',  # White
            'show_status_bar': True,
            'show_in_taskbar': False,
            'use_virtual_keyboard': False,
            'is_visible': True,
            'is_startup': False,
            'display_mode': 'MAIN',
            'fk_cashier_create_id': cashier_id
        },
        {
            'form_no': 6,
            'name': FormName.CLOSURE.name,
            'function': FormName.CLOSURE.name,
            'need_login': True,  # Requires login
            'need_auth': True,  # Requires authorization
            'width': 1024,
            'height': 768,
            'form_border_style': 'SINGLE',
            'start_position': 'CENTERSCREEN',
            'caption': 'SaleFlex - Closure',
            'back_color': '0x2F4F4F',  # DarkSlateGray
            'fore_color': '0xFFFFFF',  # White
            'show_status_bar': True,
            'show_in_taskbar': False,
            'use_virtual_keyboard': False,
            'is_visible': True,
            'is_startup': False,
            'display_mode': 'MAIN',
            'fk_cashier_create_id': cashier_id
        }
    ]

    try:
        for form_data in forms_data:
            form = Form(**form_data)
            session.add(form)
        
        session.commit()
        print(f"✓ Inserted {len(forms_data)} default forms")
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error inserting forms: {e}")
        raise 