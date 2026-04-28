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

# Form #1 — LOGIN
# Provides both the form-row definition and its UI controls.

from data_layer.enums import FormName, ControlName, EventName
from data_layer.model.definition.form_control import FormControl


def get_form_data(cashier_id: str) -> list[dict]:
    """Return form-row definitions for the LOGIN form (form_no=1)."""
    return [
        {
            'form_no': 1,
            'name': FormName.LOGIN.name,
            'function': FormName.LOGIN.name,
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
            'fk_cashier_create_id': cashier_id,
        },
    ]


def get_form_controls(login_form, cashier_id: str) -> list:
    """Return FormControl instances for the LOGIN form."""
    return [
        FormControl(
            fk_form_id=login_form.id,
            fk_parent_id=None,
            name=ControlName.CASHIER_NAME_LIST.value,
            form_control_function1=EventName.LOGIN.value,
            form_control_function2=None,
            type_no=3,
            type="COMBOBOX",
            width=300,
            height=50,
            location_x=362,
            location_y=150,
            start_position=None,
            caption1="Select Cashier",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="LEFT",
            character_casing="NORMAL",
            font="Tahoma",
            icon=None,
            tool_tip="Select your name from the list",
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=14,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0xFFFFFF",
            fore_color="0x000000",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        ),
        FormControl(
            fk_form_id=login_form.id,
            fk_parent_id=None,
            name=ControlName.PASSWORD.value,
            form_control_function1=EventName.LOGIN.value,
            form_control_function2=None,
            type_no=2,
            type="TEXTBOX",
            width=300,
            height=50,
            location_x=362,
            location_y=225,
            start_position=None,
            caption1="Password",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="NORMAL",
            font="Tahoma",
            icon=None,
            tool_tip="Enter your password",
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=14,
            input_type="PASSWORD",
            text_image_relation=None,
            back_color="0xFFFFFF",
            fore_color="0x000000",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        ),
        FormControl(
            fk_form_id=login_form.id,
            fk_parent_id=None,
            name=ControlName.LOGIN.value,
            form_control_function1=EventName.LOGIN.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=300,
            height=50,
            location_x=362,
            location_y=300,
            start_position=None,
            caption1="LOGIN",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            icon=None,
            tool_tip=None,
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=16,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0x003366",
            fore_color="0xFFFFFF",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        ),
        FormControl(
            fk_form_id=login_form.id,
            fk_parent_id=None,
            name=ControlName.EXIT.value,
            form_control_function1=EventName.EXIT_APPLICATION.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=300,
            height=50,
            location_x=362,
            location_y=375,
            start_position=None,
            caption1="EXIT",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            icon=None,
            tool_tip="Exit Application",
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=16,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0xFF0000",
            fore_color="0xFFFFFF",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        ),
    ]
