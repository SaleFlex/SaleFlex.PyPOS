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

# Forms #17 (CUSTOMER_LIST), #18 (CUSTOMER_DETAIL), #19 (CUSTOMER_SELECT)
# CUSTOMER_LIST and CUSTOMER_SELECT have simple controls.
# CUSTOMER_DETAIL uses a TABCONTROL and requires session flushes.

from data_layer.enums import FormName, ControlName, EventName
from data_layer.model.definition.form_control import FormControl
from data_layer.model.definition.form_control_tab import FormControlTab


def get_form_data(cashier_id: str) -> list[dict]:
    """Return form-row definitions for customer-related forms (#17, #18, #19)."""
    return [
        {
            'form_no': 17,
            'name': FormName.CUSTOMER_LIST.name,
            'function': FormName.CUSTOMER_LIST.name,
            'need_login': True,
            'need_auth': False,
            'width': 1024,
            'height': 768,
            'form_border_style': 'SINGLE',
            'start_position': 'CENTERSCREEN',
            'caption': 'SaleFlex - Customer List',
            'back_color': '0x2F4F4F',
            'fore_color': '0xFFFFFF',
            'show_status_bar': True,
            'show_in_taskbar': False,
            'use_virtual_keyboard': True,
            'is_visible': True,
            'is_startup': False,
            'display_mode': 'MAIN',
            'fk_cashier_create_id': cashier_id,
        },
        {
            'form_no': 18,
            'name': FormName.CUSTOMER_DETAIL.name,
            'function': FormName.CUSTOMER_DETAIL.name,
            'need_login': True,
            'need_auth': False,
            'width': 1024,
            'height': 768,
            'form_border_style': 'SINGLE',
            'start_position': 'CENTERSCREEN',
            'caption': 'SaleFlex - Customer Detail',
            'back_color': '0x1B2631',
            'fore_color': '0xECF0F1',
            'show_status_bar': False,
            'show_in_taskbar': False,
            'use_virtual_keyboard': False,
            'is_visible': True,
            'is_startup': False,
            'display_mode': 'MODAL',
            'fk_cashier_create_id': cashier_id,
        },
        {
            'form_no': 19,
            'name': FormName.CUSTOMER_SELECT.name,
            'function': FormName.CUSTOMER_SELECT.name,
            'need_login': True,
            'need_auth': False,
            'width': 1024,
            'height': 768,
            'form_border_style': 'SINGLE',
            'start_position': 'CENTERSCREEN',
            'caption': 'SaleFlex - Select Customer',
            'back_color': '0x2F4F4F',
            'fore_color': '0xFFFFFF',
            'show_status_bar': True,
            'show_in_taskbar': False,
            'use_virtual_keyboard': True,
            'is_visible': True,
            'is_startup': False,
            'display_mode': 'MAIN',
            'fk_cashier_create_id': cashier_id,
        },
    ]


def get_customer_list_form_controls(customer_list_form, cashier_id: str) -> list:
    """Return FormControl instances for CUSTOMER_LIST (#17).

    Layout (1024x768):
      y=10   Search textbox  (x=10,  w=820, h=50)
      y=10   SEARCH button   (x=840, w=170, h=50)
      y=75   DataGrid        (x=10,  w=1000, h=555)
      y=650  DETAIL button   (x=10,  w=150, h=65)
      y=650  ADD button      (x=175, w=150, h=65)
      y=650  BACK button     (x=860, w=150, h=65)
    """
    return [
        FormControl(
            fk_form_id=customer_list_form.id,
            fk_parent_id=None,
            name=ControlName.CUSTOMER_SEARCH_TEXTBOX.value,
            form_control_function1=EventName.NONE.value,
            form_control_function2=None,
            type_no=2,
            type="TEXTBOX",
            width=820,
            height=50,
            location_x=10,
            location_y=10,
            start_position=None,
            caption1="Search by name, phone or e-mail...",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="LEFT",
            character_casing="NORMAL",
            font="Tahoma",
            icon=None,
            tool_tip="Type customer name, phone number or e-mail to search",
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
            fk_form_id=customer_list_form.id,
            fk_parent_id=None,
            name="CUSTOMER_SEARCH_BTN",
            form_control_function1=EventName.CUSTOMER_SEARCH.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=170,
            height=50,
            location_x=840,
            location_y=10,
            start_position=None,
            caption1="SEARCH",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            icon=None,
            tool_tip="Search customers",
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
        ),
        FormControl(
            fk_form_id=customer_list_form.id,
            fk_parent_id=None,
            name=ControlName.CUSTOMER_LIST_DATAGRID.value,
            form_control_function1=EventName.NONE.value,
            form_control_function2=None,
            type_no=9,
            type="DATAGRID",
            width=1000,
            height=555,
            location_x=10,
            location_y=75,
            start_position=None,
            caption1="Customer List",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="NORMAL",
            font="Tahoma",
            icon=None,
            tool_tip="Customer search results",
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=11,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0xFFFFFF",
            fore_color="0x000000",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        ),
        # DETAIL button – open Customer Detail modal for selected row
        FormControl(
            fk_form_id=customer_list_form.id,
            fk_parent_id=None,
            name="CUSTOMER_DETAIL_BTN",
            form_control_function1=EventName.CUSTOMER_DETAIL.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=150,
            height=65,
            location_x=10,
            location_y=650,
            start_position=None,
            caption1="DETAIL",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            icon=None,
            tool_tip="View and edit selected customer",
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=14,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0x7D3C98",
            fore_color="0xFFFFFF",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        ),
        # ADD button – open blank Customer Detail modal to create new customer
        FormControl(
            fk_form_id=customer_list_form.id,
            fk_parent_id=None,
            name="CUSTOMER_ADD_BTN",
            form_control_function1=EventName.CUSTOMER_ADD.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=150,
            height=65,
            location_x=175,
            location_y=650,
            start_position=None,
            caption1="ADD",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            icon=None,
            tool_tip="Add a new customer",
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=14,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0x228B22",  # Forest Green
            fore_color="0xFFFFFF",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        ),
        # BACK button – context-aware: returns to SALE or Main Menu
        FormControl(
            fk_form_id=customer_list_form.id,
            fk_parent_id=None,
            name="CUSTOMER_LIST_BACK_BTN",
            form_control_function1=EventName.CUSTOMER_LIST_BACK.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=150,
            height=65,
            location_x=860,
            location_y=650,
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
            tool_tip="Return to previous screen (assigns selected customer to sale if opened from SALE form)",
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
        ),
    ]


def get_customer_select_form_controls(customer_select_form, cashier_id: str) -> list:
    """Return FormControl instances for CUSTOMER_SELECT (#19). Returns [] if form is None.

    Layout identical to CUSTOMER_LIST but with SELECT instead of DETAIL.
    The SELECT button assigns the chosen customer to the active sale.
    """
    if not customer_select_form:
        return []
    return [
        FormControl(
            fk_form_id=customer_select_form.id,
            fk_parent_id=None,
            name=ControlName.CUSTOMER_SEARCH_TEXTBOX.value,
            form_control_function1=EventName.NONE.value,
            form_control_function2=None,
            type_no=2,
            type="TEXTBOX",
            width=820,
            height=50,
            location_x=10,
            location_y=10,
            start_position=None,
            caption1="Search by name, phone or e-mail...",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="LEFT",
            character_casing="NORMAL",
            font="Tahoma",
            icon=None,
            tool_tip="Type customer name, phone number or e-mail to search",
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
            fk_form_id=customer_select_form.id,
            fk_parent_id=None,
            name="CUSTOMER_SELECT_SEARCH_BTN",
            form_control_function1=EventName.CUSTOMER_SEARCH.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=170,
            height=50,
            location_x=840,
            location_y=10,
            start_position=None,
            caption1="SEARCH",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            icon=None,
            tool_tip="Search customers",
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
        ),
        FormControl(
            fk_form_id=customer_select_form.id,
            fk_parent_id=None,
            name=ControlName.CUSTOMER_LIST_DATAGRID.value,
            form_control_function1=EventName.NONE.value,
            form_control_function2=None,
            type_no=9,
            type="DATAGRID",
            width=1000,
            height=540,
            location_x=10,
            location_y=75,
            start_position=None,
            caption1="Customer List",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="NORMAL",
            font="Tahoma",
            icon=None,
            tool_tip="Customer search results — select a row then press SELECT",
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=11,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0xFFFFFF",
            fore_color="0x000000",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        ),
        # SELECT button – assign highlighted customer to active sale, return to SALE
        FormControl(
            fk_form_id=customer_select_form.id,
            fk_parent_id=None,
            name="CUSTOMER_SELECT_BTN",
            form_control_function1=EventName.CUSTOMER_SELECT.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=150,
            height=65,
            location_x=10,
            location_y=650,
            start_position=None,
            caption1="SELECT",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            icon=None,
            tool_tip="Assign selected customer to active sale and return to SALE form",
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=14,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0x7D3C98",  # Purple
            fore_color="0xFFFFFF",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        ),
        # ADD button – open blank Customer Detail modal
        FormControl(
            fk_form_id=customer_select_form.id,
            fk_parent_id=None,
            name="CUSTOMER_SELECT_ADD_BTN",
            form_control_function1=EventName.CUSTOMER_ADD.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=150,
            height=65,
            location_x=175,
            location_y=650,
            start_position=None,
            caption1="ADD",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            icon=None,
            tool_tip="Add a new customer, then press SELECT to assign",
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=14,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0x228B22",  # Forest Green
            fore_color="0xFFFFFF",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        ),
        # BACK button – return to SALE without assigning
        FormControl(
            fk_form_id=customer_select_form.id,
            fk_parent_id=None,
            name=ControlName.BACK.value,
            form_control_function1=EventName.BACK.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=150,
            height=65,
            location_x=860,
            location_y=650,
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
            tool_tip="Return to SALE form without assigning a customer",
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
        ),
    ]


def insert_customer_detail_controls(session, customer_detail_form, cashier_id: str):
    """Insert tab-based controls for CUSTOMER_DETAIL (#18).

    Must be called AFTER the first session.flush().  Issues its own flushes internally.

    Tab layout:
      Tab 0 – Customer Info     : PANEL "CUSTOMER" with label/textbox pairs
      Tab 1 – Activity History  : DATAGRID with transaction history
      Tab 2 – Point movements   : DATAGRID with loyalty ledger (LoyaltyPointTransaction)
    SAVE + BACK buttons are placed outside the tab control.
    """
    if not customer_detail_form:
        return

    # 1. TABCONTROL
    cd_tab_control = FormControl(
        fk_form_id=customer_detail_form.id,
        fk_parent_id=None,
        name=ControlName.CUSTOMER_DETAIL_TAB.value,
        type_no=1,
        type="TABCONTROL",
        width=1004,
        height=694,
        location_x=10,
        location_y=10,
        back_color="0x1B2631",
        fore_color="0xECF0F1",
        font_size=13,
        is_visible=True,
        fk_cashier_create_id=cashier_id,
        fk_cashier_update_id=cashier_id,
    )
    session.add(cd_tab_control)
    session.flush()

    # 2. Tab page records
    cd_tab_defs = [
        (0, "Customer Info",     "Personal details and contact information"),
        (1, "Activity History",  "Transaction history for this customer"),
        (2, "Point movements",   "Loyalty point ledger for this customer"),
    ]
    cd_tab_records = []
    for tab_index, tab_title, tab_tooltip in cd_tab_defs:
        tab_rec = FormControlTab(
            fk_form_control_id=cd_tab_control.id,
            tab_index=tab_index,
            tab_title=tab_title,
            tab_tooltip=tab_tooltip,
            back_color="0x1B2631",
            fore_color="0xECF0F1",
            is_visible=True,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        )
        session.add(tab_rec)
        cd_tab_records.append(tab_rec)
    session.flush()

    # 3. PANEL inside Tab 0 — name "CUSTOMER" maps to the Customer model
    customer_panel = FormControl(
        fk_form_id=customer_detail_form.id,
        fk_parent_id=cd_tab_control.id,
        fk_tab_id=cd_tab_records[0].id,
        name="CUSTOMER",
        type_no=10,
        type="PANEL",
        width=980,
        height=500,
        location_x=0,
        location_y=0,
        back_color="0x1B2631",
        fore_color="0xECF0F1",
        font_size=12,
        tool_tip="Customer information panel",
        is_visible=True,
        fk_cashier_create_id=cashier_id,
        fk_cashier_update_id=cashier_id,
    )
    session.add(customer_panel)
    session.flush()

    # 4. Label/textbox pairs inside CUSTOMER panel
    customer_info_fields = [
        ("First Name",  "name",           "ALPHANUMERIC"),
        ("Last Name",   "last_name",      "ALPHANUMERIC"),
        ("Phone",       "phone_number",   "ALPHANUMERIC"),
        ("E-mail",      "email_address",  "ALPHANUMERIC"),
        ("Address 1",   "address_line_1", "ALPHANUMERIC"),
        ("Address 2",   "address_line_2", "ALPHANUMERIC"),
        ("City / Area", "address_line_3", "ALPHANUMERIC"),
        ("Post Code",   "zip_code",       "ALPHANUMERIC"),
        ("Description", "description",    "ALPHANUMERIC"),
    ]

    label_width = 200
    field_width = 560
    ctrl_height = 40
    row_height  = ctrl_height + 8
    start_y     = 15

    for i, (lbl_text, field_name, input_type) in enumerate(customer_info_fields):
        y_pos = start_y + (i * row_height)

        session.add(FormControl(
            fk_form_id=customer_detail_form.id,
            fk_parent_id=customer_panel.id,
            parent_name="CUSTOMER",
            name=f"LBL_{field_name.upper()}",
            form_control_function1=EventName.NONE.value,
            form_control_function2=None,
            type_no=8,
            type="LABEL",
            width=label_width,
            height=ctrl_height,
            location_x=10,
            location_y=y_pos,
            caption1=lbl_text + ":",
            text_alignment="RIGHT",
            character_casing="NORMAL",
            font="Tahoma",
            font_auto_height=False,
            font_size=12,
            back_color=None,
            fore_color="0xECF0F1",
            is_visible=True,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        ))

        session.add(FormControl(
            fk_form_id=customer_detail_form.id,
            fk_parent_id=customer_panel.id,
            parent_name="CUSTOMER",
            name=field_name.upper(),
            form_control_function1=EventName.NONE.value,
            form_control_function2=None,
            type_no=2,
            type="TEXTBOX",
            width=field_width,
            height=ctrl_height,
            location_x=label_width + 20,
            location_y=y_pos,
            caption1="",
            text_alignment="LEFT",
            character_casing="NORMAL",
            font="Tahoma",
            font_auto_height=False,
            font_size=12,
            input_type=input_type,
            tool_tip=f"Enter {lbl_text.lower()}",
            back_color="0xFFFFFF",
            fore_color="0x000000",
            is_visible=True,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        ))

    # 5. Activity History DATAGRID in Tab 1
    session.add(FormControl(
        fk_form_id=customer_detail_form.id,
        fk_parent_id=cd_tab_control.id,
        fk_tab_id=cd_tab_records[1].id,
        name=ControlName.CUSTOMER_ACTIVITY_GRID.value,
        type_no=1,
        type="DATAGRID",
        width=1002,
        height=647,
        location_x=1,
        location_y=1,
        back_color="0x1B2631",
        fore_color="0xECF0F1",
        font_size=11,
        tool_tip="Transaction history for this customer",
        is_visible=True,
        fk_cashier_create_id=cashier_id,
        fk_cashier_update_id=cashier_id,
    ))

    # 5b. Loyalty point movements DATAGRID in Tab 2
    session.add(FormControl(
        fk_form_id=customer_detail_form.id,
        fk_parent_id=cd_tab_control.id,
        fk_tab_id=cd_tab_records[2].id,
        name=ControlName.CUSTOMER_LOYALTY_POINTS_GRID.value,
        type_no=1,
        type="DATAGRID",
        width=1002,
        height=647,
        location_x=1,
        location_y=1,
        back_color="0x1B2631",
        fore_color="0xECF0F1",
        font_size=11,
        tool_tip="Loyalty point movements (earned, redeemed, welcome, …)",
        is_visible=True,
        fk_cashier_create_id=cashier_id,
        fk_cashier_update_id=cashier_id,
    ))

    # 6. SAVE button (outside tab control)
    session.add(FormControl(
        fk_form_id=customer_detail_form.id,
        fk_parent_id=None,
        name="SAVE_CUSTOMER",
        form_control_function1=EventName.CUSTOMER_DETAIL_SAVE.value,
        type_no=1,
        type="BUTTON",
        width=150,
        height=48,
        location_x=680,
        location_y=716,
        caption1="SAVE",
        text_alignment="CENTER",
        character_casing="UPPER",
        font="Tahoma",
        font_auto_height=False,
        font_size=14,
        tool_tip="Save customer changes",
        back_color="0x228B22",
        fore_color="0xFFFFFF",
        is_visible=True,
        fk_cashier_create_id=cashier_id,
        fk_cashier_update_id=cashier_id,
    ))

    # 7. BACK / CLOSE button (outside tab control)
    session.add(FormControl(
        fk_form_id=customer_detail_form.id,
        fk_parent_id=None,
        name="BACK_CUSTOMER",
        form_control_function1="CLOSE_FORM",
        type_no=1,
        type="BUTTON",
        width=150,
        height=48,
        location_x=840,
        location_y=716,
        caption1="BACK",
        text_alignment="CENTER",
        character_casing="UPPER",
        font="Tahoma",
        font_auto_height=False,
        font_size=14,
        tool_tip="Close this dialog",
        back_color="0x4682B4",
        fore_color="0xFFFFFF",
        is_visible=True,
        fk_cashier_create_id=cashier_id,
        fk_cashier_update_id=cashier_id,
    ))

    session.flush()


def ensure_customer_loyalty_points_grid(session) -> None:
    """
    Idempotent schema patch: add ``Point movements`` tab and ``CUSTOMER_LOYALTY_POINTS_GRID``
    to existing CUSTOMER_DETAIL (#18) when form controls were seeded before this grid existed.
    """
    from sqlalchemy import func

    from core.logger import get_logger
    from data_layer.model.definition.cashier import Cashier
    from data_layer.model.definition.form import Form
    from data_layer.model.definition.form_control import FormControl

    logger = get_logger(__name__)

    if session.query(FormControl).filter(
        FormControl.name == ControlName.CUSTOMER_LOYALTY_POINTS_GRID.value
    ).first():
        return

    customer_form = session.query(Form).filter(Form.form_no == 18).first()
    if not customer_form:
        return

    tab_control = session.query(FormControl).filter(
        FormControl.fk_form_id == customer_form.id,
        FormControl.name == ControlName.CUSTOMER_DETAIL_TAB.value,
    ).first()
    if not tab_control:
        return

    admin = session.query(Cashier).filter(Cashier.username == "admin").first()
    if not admin:
        admin = session.query(Cashier).first()
    if not admin:
        logger.warning("ensure_customer_loyalty_points_grid: no cashier row; skipping patch")
        return
    cashier_id = admin.id

    max_idx = session.query(func.max(FormControlTab.tab_index)).filter(
        FormControlTab.fk_form_control_id == tab_control.id
    ).scalar()
    next_index = (max_idx + 1) if max_idx is not None else 0

    tab_rec = FormControlTab(
        fk_form_control_id=tab_control.id,
        tab_index=next_index,
        tab_title="Point movements",
        tab_tooltip="Loyalty point ledger for this customer",
        back_color="0x1B2631",
        fore_color="0xECF0F1",
        is_visible=True,
        fk_cashier_create_id=cashier_id,
        fk_cashier_update_id=cashier_id,
    )
    session.add(tab_rec)
    session.flush()

    session.add(FormControl(
        fk_form_id=customer_form.id,
        fk_parent_id=tab_control.id,
        fk_tab_id=tab_rec.id,
        name=ControlName.CUSTOMER_LOYALTY_POINTS_GRID.value,
        type_no=1,
        type="DATAGRID",
        width=1002,
        height=647,
        location_x=1,
        location_y=1,
        back_color="0x1B2631",
        fore_color="0xECF0F1",
        font_size=11,
        tool_tip="Loyalty point movements (earned, redeemed, welcome, …)",
        is_visible=True,
        fk_cashier_create_id=cashier_id,
        fk_cashier_update_id=cashier_id,
    ))
    logger.info("Schema patch: added CUSTOMER_LOYALTY_POINTS_GRID to CUSTOMER_DETAIL")
