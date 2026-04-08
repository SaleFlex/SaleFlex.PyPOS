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

# Forms #3 (SETTING) and #4 (CASHIER)
# Each form has a scrollable panel containing label/field pairs for configuration.
# After the first session.flush() the caller must invoke update_*_panel_parents()
# so that child controls get the correct fk_parent_id for their enclosing panel.

from data_layer.enums import FormName, ControlName, EventName
from data_layer.model.definition.form_control import FormControl


def get_form_data(cashier_id: str) -> list[dict]:
    """Return form-row definitions for SETTING (#3) and CASHIER (#4)."""
    return [
        {
            'form_no': 3,
            'name': FormName.SETTING.name,
            'function': FormName.SETTING.name,
            'need_login': True,
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
    ]


# ---------------------------------------------------------------------------
# SETTING / Configuration form
# ---------------------------------------------------------------------------

def get_config_form_controls(config_form, cashier_id: str):
    """Return (config_form_controls, pos_settings_controls).

    config_form_controls  – full list ready to be added to the session.
    pos_settings_controls – subset of controls that are children of the
                            POS_SETTINGS panel; the caller must call
                            update_config_panel_parents() after the first
                            session.flush() to wire up fk_parent_id.
    """
    config_panel = FormControl(
        fk_form_id=config_form.id,
        fk_parent_id=None,
        name="POS_SETTINGS",
        form_control_function1=None,
        form_control_function2=None,
        type_no=10,
        type="PANEL",
        width=900,
        height=550,
        location_x=62,
        location_y=50,
        start_position=None,
        caption1="POS Settings",
        caption2=None,
        list_values=None,
        dock=None,
        alignment=None,
        text_alignment="CENTER",
        character_casing="NORMAL",
        font="Tahoma",
        icon=None,
        tool_tip="POS Settings Configuration Panel",
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

    pos_settings_fields = [
        ("POS No in Store",       "pos_no_in_store",          "NUMERIC"),
        ("Name",                  "name",                     "ALPHANUMERIC"),
        ("Owner National ID",     "owner_national_id",        "ALPHANUMERIC"),
        ("Owner Tax ID",          "owner_tax_id",             "ALPHANUMERIC"),
        ("Owner Web Address",     "owner_web_address",        "ALPHANUMERIC"),
        ("MAC Address",           "mac_address",              "ALPHANUMERIC"),
        ("Customer Display Type", "customer_display_type",    "ALPHANUMERIC"),
        ("Customer Display Port", "customer_display_port",    "ALPHANUMERIC"),
        ("Receipt Printer Type",  "receipt_printer_type",     "ALPHANUMERIC"),
        ("Receipt Printer Port",  "receipt_printer_port",     "ALPHANUMERIC"),
        ("Invoice Printer Type",  "invoice_printer_type",     "ALPHANUMERIC"),
        ("Invoice Printer Port",  "invoice_printer_port",     "ALPHANUMERIC"),
        ("Scale Type",            "scale_type",               "ALPHANUMERIC"),
        ("Scale Port",            "scale_port",               "ALPHANUMERIC"),
        ("Barcode Reader Port",   "barcode_reader_port",      "ALPHANUMERIC"),
        ("Backend IP 1",          "backend_ip1",              "ALPHANUMERIC"),
        ("Backend Port 1",        "backend_port1",            "NUMERIC"),
        ("Backend IP 2",          "backend_ip2",              "ALPHANUMERIC"),
        ("Backend Port 2",        "backend_port2",            "NUMERIC"),
        ("Backend Type",          "backend_type",             "ALPHANUMERIC"),
        ("Device Serial Number",  "device_serial_number",     "ALPHANUMERIC"),
        ("Device OS",             "device_operation_system",  "ALPHANUMERIC"),
        ("Force Online",          "force_to_work_online",     "CHECKBOX"),
        ("PLU Update No",         "plu_update_no",            "NUMERIC"),
    ]

    label_width    = 200
    textbox_width  = 400
    control_height = 40
    row_height     = control_height + 10
    start_y        = 20

    pos_settings_controls = []
    for i, (label_text, field_name, input_type) in enumerate(pos_settings_fields):
        y_pos = start_y + (i * row_height)

        pos_settings_controls.append(FormControl(
            fk_form_id=config_form.id,
            fk_parent_id=None,
            parent_name="POS_SETTINGS",
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
            pos_settings_controls.append(FormControl(
                fk_form_id=config_form.id,
                fk_parent_id=None,
                parent_name="POS_SETTINGS",
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
            pos_settings_controls.append(FormControl(
                fk_form_id=config_form.id,
                fk_parent_id=None,
                parent_name="POS_SETTINGS",
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
        fk_form_id=config_form.id,
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
        tool_tip="Save POS Settings",
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
        fk_form_id=config_form.id,
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

    config_form_controls = [config_panel] + pos_settings_controls + [save_button, back_button]
    return config_form_controls, pos_settings_controls


def update_config_panel_parents(config_form_controls: list, pos_settings_controls: list):
    """Wire fk_parent_id for panel children after the first session.flush()."""
    config_panel_control = next(
        (c for c in config_form_controls if c.type == "PANEL" and c.name == "POS_SETTINGS"),
        None,
    )
    if config_panel_control:
        for control in pos_settings_controls:
            if control.parent_name == "POS_SETTINGS":
                control.fk_parent_id = config_panel_control.id


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
