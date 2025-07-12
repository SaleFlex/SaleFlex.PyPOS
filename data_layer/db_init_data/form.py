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

from sqlalchemy.orm import Session
from data_layer.model.definition.form import Form


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

    # Default forms data based on C# code
    forms_data = [
        {
            'form_no': 1,
            'name': 'LOGIN',
            'function': 'LOGIN',
            'need_login': False,
            'need_auth': False,
            'width': 1024,
            'height': 768,
            'form_border_style': 'SINGLE',
            'start_position': 'CENTERSCREEN',
            'caption': 'LOGIN',
            'back_color': 'MidnightBlue',
            'show_status_bar': True,
            'show_in_taskbar': False,
            'use_virtual_keyboard': False,
            'is_visible': True,
            'fk_cashier_create_id': cashier_id
        },
        {
            'form_no': 2,
            'name': 'SALE',
            'function': 'SALE',
            'need_login': True,
            'need_auth': False,
            'width': 1024,
            'height': 768,
            'form_border_style': 'SINGLE',
            'start_position': 'CENTERSCREEN',
            'caption': 'SALE',
            'back_color': 'MidnightBlue',
            'show_status_bar': True,
            'show_in_taskbar': False,
            'use_virtual_keyboard': False,
            'is_visible': True,
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