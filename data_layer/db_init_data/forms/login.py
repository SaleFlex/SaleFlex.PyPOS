"""
SaleFlex.PyPOS - Point of Sale Application

Copyright (c) 2025-2026 Ferhat Mousavi

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
