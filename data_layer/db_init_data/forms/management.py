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

# Forms #3 (SETTINGS_MENU), #4 (CASHIER), #23 (POS_SETTINGS), #24 (LOYALTY_SETTINGS)
# Each form has a scrollable panel containing label/field pairs for configuration.
# After the first session.flush() the caller must invoke update_*_panel_parents()
# so that child controls get the correct fk_parent_id for their enclosing panel.

from data_layer.enums import FormName, ControlName, EventName
from data_layer.model.definition.form_control import FormControl


def get_form_data(cashier_id: str) -> list[dict]:
    """Return form rows for settings hub (#3), CASHIER (#4), POS_SETTINGS (#23), LOYALTY_SETTINGS (#24)."""
    return [
        {
            'form_no': 3,
            'name': FormName.SETTINGS_MENU.name,
            'function': FormName.SETTINGS_MENU.name,
            'need_login': True,
            'need_auth': False,
            'width': 1024,
            'height': 768,
            'form_border_style': 'SINGLE',
            'start_position': 'CENTERSCREEN',
            'caption': 'SaleFlex - Settings',
            'back_color': '0x2F4F4F',  # DarkSlateGray
            'fore_color': '0xFFFFFF',  # White
            'show_status_bar': True,
            'show_in_taskbar': False,
            'use_virtual_keyboard': False,
            'is_visible': True,
            'is_startup': False,
            'display_mode': 'MAIN',
            'fk_cashier_create_id': cashier_id,
        },
        {
            'form_no': 4,
            'name': FormName.CASHIER.name,
            'function': FormName.CASHIER.name,
            'need_login': True,
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
            'fk_cashier_create_id': cashier_id,
        },
        {
            'form_no': 23,
            'name': FormName.POS_SETTINGS.name,
            'function': FormName.POS_SETTINGS.name,
            'need_login': True,
            'need_auth': False,
            'width': 1024,
            'height': 768,
            'form_border_style': 'SINGLE',
            'start_position': 'CENTERSCREEN',
            'caption': 'SaleFlex - POS Settings',
            'back_color': '0x2F4F4F',
            'fore_color': '0xFFFFFF',
            'show_status_bar': True,
            'show_in_taskbar': False,
            'use_virtual_keyboard': False,
            'is_visible': True,
            'is_startup': False,
            'display_mode': 'MAIN',
            'fk_cashier_create_id': cashier_id,
        },
        {
            'form_no': 24,
            'name': FormName.LOYALTY_SETTINGS.name,
            'function': FormName.LOYALTY_SETTINGS.name,
            'need_login': True,
            'need_auth': False,
            'width': 1024,
            'height': 768,
            'form_border_style': 'SINGLE',
            'start_position': 'CENTERSCREEN',
            'caption': 'SaleFlex - Loyalty Settings',
            'back_color': '0x2F4F4F',
            'fore_color': '0xFFFFFF',
            'show_status_bar': True,
            'show_in_taskbar': False,
            'use_virtual_keyboard': False,
            'is_visible': True,
            'is_startup': False,
            'display_mode': 'MAIN',
            'fk_cashier_create_id': cashier_id,
        },
    ]


# ---------------------------------------------------------------------------
# Settings hub and sub-forms → ``forms/setting_form.py``
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# CASHIER management form
# ---------------------------------------------------------------------------

def get_cashier_form_controls(cashier_form, cashier_id: str):
    """Return (cashier_form_controls, cashier_panel_children).

    cashier_form_controls   – full list ready to be added to the session.
    cashier_panel_children  – subset that are children of the CASHIER panel;
                              the caller must call update_cashier_panel_parents()
                              after the first session.flush().
    """
    cashier_panel = FormControl(
        fk_form_id=cashier_form.id,
        fk_parent_id=None,
        name="CASHIER",
        form_control_function1=None,
        form_control_function2=None,
        type_no=10,
        type="PANEL",
        width=900,
        height=550,
        location_x=62,
        location_y=50,
        start_position=None,
        caption1="Cashier Information",
        caption2=None,
        list_values=None,
        dock=None,
        alignment=None,
        text_alignment="CENTER",
        character_casing="NORMAL",
        font="Tahoma",
        icon=None,
        tool_tip="Cashier Information Configuration Panel",
        image=None,
        image_selected=None,
        font_auto_height=False,
        font_size=0,
        input_type="ALPHANUMERIC",
        text_image_relation=None,
        back_color="0x2F4F4F",
        fore_color="0xFFFFFF",
        keyboard_value=None,
        fk_cashier_create_id=cashier_id,
        fk_cashier_update_id=cashier_id,
    )

    cashier_mgmt_list = FormControl(
        fk_form_id=cashier_form.id,
        fk_parent_id=None,
        parent_name="CASHIER",
        name=ControlName.CASHIER_MGMT_LIST.value,
        form_control_function1=EventName.SELECT_CASHIER.value,
        form_control_function2=None,
        type_no=3,
        type="COMBOBOX",
        width=400,
        height=50,
        location_x=220,
        location_y=10,
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
        tool_tip="Select cashier to view or edit",
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
    )

    add_new_cashier_button = FormControl(
        fk_form_id=cashier_form.id,
        fk_parent_id=None,
        parent_name=None,
        name=ControlName.ADD_NEW_CASHIER.value,
        form_control_function1=EventName.ADD_NEW_CASHIER.value,
        form_control_function2=None,
        type_no=1,
        type="BUTTON",
        width=300,
        height=99,
        location_x=20,
        location_y=630,
        start_position=None,
        caption1="ADD NEW CASHIER",
        caption2=None,
        list_values=None,
        dock=None,
        alignment=None,
        text_alignment="CENTER",
        character_casing="UPPER",
        font="Tahoma",
        icon=None,
        tool_tip="Add a new cashier account",
        image=None,
        image_selected=None,
        font_auto_height=False,
        font_size=14,
        input_type="ALPHANUMERIC",
        text_image_relation=None,
        back_color="0x8B4513",  # SaddleBrown
        fore_color="0xFFFFFF",
        keyboard_value=None,
        fk_cashier_create_id=cashier_id,
        fk_cashier_update_id=cashier_id,
    )

    cashier_fields = [
        ("No",               "no",               "NUMERIC"),
        ("Username",         "user_name",         "ALPHANUMERIC"),
        ("Name",             "name",              "ALPHANUMERIC"),
        ("Last Name",        "last_name",         "ALPHANUMERIC"),
        ("Password",         "password",          "PASSWORD"),
        ("Identity Number",  "identity_number",   "ALPHANUMERIC"),
        ("Description",      "description",       "ALPHANUMERIC"),
        ("Is Administrator", "is_administrator",  "CHECKBOX"),
        ("Is Active",        "is_active",         "CHECKBOX"),
    ]

    label_width    = 200
    textbox_width  = 400
    control_height = 40
    row_height     = control_height + 10
    start_y        = 70

    cashier_panel_children = [cashier_mgmt_list]
    for i, (label_text, field_name, input_type) in enumerate(cashier_fields):
        y_pos = start_y + (i * row_height)

        cashier_panel_children.append(FormControl(
            fk_form_id=cashier_form.id,
            fk_parent_id=None,
            parent_name="CASHIER",
            name=f"LBL_{field_name.upper()}",
            form_control_function1=EventName.NONE.value,
            form_control_function2=None,
            type_no=8,
            type="LABEL",
            width=label_width,
            height=control_height,
            location_x=10,
            location_y=y_pos,
            start_position=None,
            caption1=label_text + ":",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="RIGHT",
            character_casing="NORMAL",
            font="Tahoma",
            icon=None,
            tool_tip=None,
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=12,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color=None,
            fore_color="0xFFFFFF",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        ))

        if input_type == "CHECKBOX":
            cashier_panel_children.append(FormControl(
                fk_form_id=cashier_form.id,
                fk_parent_id=None,
                parent_name="CASHIER",
                name=field_name.upper(),
                form_control_function1=EventName.NONE.value,
                form_control_function2=None,
                type_no=11,
                type="CHECKBOX",
                width=80,
                height=control_height,
                location_x=label_width + 20,
                location_y=y_pos,
                start_position=None,
                caption1="",
                caption2=None,
                list_values=None,
                dock=None,
                alignment=None,
                text_alignment="LEFT",
                character_casing="NORMAL",
                font="Tahoma",
                icon=None,
                tool_tip=label_text,
                image=None,
                image_selected=None,
                font_auto_height=False,
                font_size=12,
                input_type="BOOLEAN",
                text_image_relation=None,
                back_color="0xFFFFFF",
                fore_color="0x000000",
                keyboard_value=None,
                fk_cashier_create_id=cashier_id,
                fk_cashier_update_id=cashier_id,
            ))
        else:
            cashier_panel_children.append(FormControl(
                fk_form_id=cashier_form.id,
                fk_parent_id=None,
                parent_name="CASHIER",
                name=field_name.upper(),
                form_control_function1=EventName.NONE.value,
                form_control_function2=None,
                type_no=2,
                type="TEXTBOX",
                width=textbox_width,
                height=control_height,
                location_x=label_width + 20,
                location_y=y_pos,
                start_position=None,
                caption1="",
                caption2=None,
                list_values=None,
                dock=None,
                alignment=None,
                text_alignment="LEFT",
                character_casing="NORMAL",
                font="Tahoma",
                icon=None,
                tool_tip=f"Enter {label_text.lower()}",
                image=None,
                image_selected=None,
                font_auto_height=False,
                font_size=12,
                input_type=input_type,
                text_image_relation=None,
                back_color="0xFFFFFF",
                fore_color="0x000000",
                keyboard_value=None,
                fk_cashier_create_id=cashier_id,
                fk_cashier_update_id=cashier_id,
            ))

    save_button = FormControl(
        fk_form_id=cashier_form.id,
        fk_parent_id=None,
        name=ControlName.SAVE.value,
        form_control_function1=EventName.SAVE_CHANGES.value,
        form_control_function2=None,
        type_no=1,
        type="BUTTON",
        width=125,
        height=99,
        location_x=745,
        location_y=630,
        start_position=None,
        caption1="SAVE",
        caption2=None,
        list_values=None,
        dock=None,
        alignment=None,
        text_alignment="CENTER",
        character_casing="UPPER",
        font="Tahoma",
        icon=None,
        tool_tip="Save Cashier Information",
        image=None,
        image_selected=None,
        font_auto_height=False,
        font_size=14,
        input_type="ALPHANUMERIC",
        text_image_relation=None,
        back_color="0x228B22",
        fore_color="0xFFFFFF",
        keyboard_value=None,
        fk_cashier_create_id=cashier_id,
        fk_cashier_update_id=cashier_id,
    )

    back_button = FormControl(
        fk_form_id=cashier_form.id,
        fk_parent_id=None,
        name=ControlName.BACK.value,
        form_control_function1=EventName.BACK.value,
        form_control_function2=None,
        type_no=1,
        type="BUTTON",
        width=125,
        height=99,
        location_x=880,
        location_y=630,
        start_position=None,
        caption1="BACK",
        caption2=None,
        list_values=None,
        dock=None,
        alignment=None,
        text_alignment="CENTER",
        character_casing="UPPER",
        font="Tahoma",
        icon=None,
        tool_tip="Back to Main Menu",
        image=None,
        image_selected=None,
        font_auto_height=False,
        font_size=14,
        input_type="ALPHANUMERIC",
        text_image_relation=None,
        back_color="0x4682B4",
        fore_color="0xFFFFFF",
        keyboard_value=None,
        fk_cashier_create_id=cashier_id,
        fk_cashier_update_id=cashier_id,
    )

    cashier_form_controls = (
        [cashier_mgmt_list, add_new_cashier_button, cashier_panel]
        + cashier_panel_children
        + [save_button, back_button]
    )
    return cashier_form_controls, cashier_panel_children


def update_cashier_panel_parents(cashier_form_controls: list, cashier_panel_children: list):
    """Wire fk_parent_id for panel children after the first session.flush()."""
    cashier_panel_control = next(
        (c for c in cashier_form_controls if c.type == "PANEL" and c.name == "CASHIER"),
        None,
    )
    if cashier_panel_control:
        for control in cashier_panel_children:
            if control.parent_name == "CASHIER":
                control.fk_parent_id = cashier_panel_control.id
