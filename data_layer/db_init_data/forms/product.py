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

# Forms #8 (PRODUCT_LIST) and #9 (PRODUCT_DETAIL)
# PRODUCT_LIST has simple controls.
# PRODUCT_DETAIL uses a TABCONTROL with tab pages and requires a session flush
# to obtain UUIDs before child controls can be created.

from data_layer.enums import FormName, ControlName, EventName
from data_layer.model.definition.form_control import FormControl
from data_layer.model.definition.form_control_tab import FormControlTab


def get_form_data(cashier_id: str) -> list[dict]:
    """Return form-row definitions for PRODUCT_LIST (#8) and PRODUCT_DETAIL (#9)."""
    return [
        {
            'form_no': 8,
            'name': FormName.PRODUCT_LIST.name,
            'function': FormName.PRODUCT_LIST.name,
            'need_login': True,
            'need_auth': False,
            'width': 1024,
            'height': 768,
            'form_border_style': 'SINGLE',
            'start_position': 'CENTERSCREEN',
            'caption': 'SaleFlex - Product List',
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
            'form_no': 9,
            'name': FormName.PRODUCT_DETAIL.name,
            'function': FormName.PRODUCT_DETAIL.name,
            'need_login': True,
            'need_auth': False,
            'width': 1024,
            'height': 768,
            'form_border_style': 'SINGLE',
            'start_position': 'CENTERSCREEN',
            'caption': 'SaleFlex - Product Detail',
            'back_color': '0x1C2833',
            'fore_color': '0xECF0F1',
            'show_status_bar': False,
            'show_in_taskbar': False,
            'use_virtual_keyboard': False,
            'is_visible': True,
            'is_startup': False,
            'display_mode': 'MODAL',
            'fk_cashier_create_id': cashier_id,
        },
    ]


def get_product_list_form_controls(product_list_form, cashier_id: str) -> list:
    """Return FormControl instances for the PRODUCT_LIST form (#8).

    Layout (1024x768):
      y=10   Search textbox  (x=10, w=820, h=50)
      y=10   Search button   (x=840, w=170, h=50)
      y=75   DataGrid        (x=10, w=1000, h=570)
      y=660  Back button     (x=860, w=150, h=65)
      y=660  Detail button   (x=10, w=150, h=65)
    """
    return [
        FormControl(
            fk_form_id=product_list_form.id,
            fk_parent_id=None,
            name=ControlName.PRODUCT_SEARCH_TEXTBOX.value,
            form_control_function1=EventName.NONE.value,
            form_control_function2=None,
            type_no=2,
            type="TEXTBOX",
            width=820,
            height=50,
            location_x=10,
            location_y=10,
            start_position=None,
            caption1="Search by name or short name...",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="LEFT",
            character_casing="NORMAL",
            font="Tahoma",
            icon=None,
            tool_tip="Type product name or short name to search",
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
            fk_form_id=product_list_form.id,
            fk_parent_id=None,
            name="PRODUCT_SEARCH_BTN",
            form_control_function1=EventName.PRODUCT_SEARCH.value,
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
            tool_tip="Search products",
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
            fk_form_id=product_list_form.id,
            fk_parent_id=None,
            name=ControlName.PRODUCT_LIST_DATAGRID.value,
            form_control_function1=EventName.NONE.value,
            form_control_function2=None,
            type_no=9,
            type="DATAGRID",
            width=1000,
            height=570,
            location_x=10,
            location_y=75,
            start_position=None,
            caption1="Product List",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="NORMAL",
            font="Tahoma",
            icon=None,
            tool_tip="Product search results",
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
        FormControl(
            fk_form_id=product_list_form.id,
            fk_parent_id=None,
            name=ControlName.BACK.value,
            form_control_function1=EventName.BACK.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=150,
            height=65,
            location_x=860,
            location_y=660,
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
            tool_tip="Return to previous screen",
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
        FormControl(
            fk_form_id=product_list_form.id,
            fk_parent_id=None,
            name="PRODUCT_DETAIL_BTN",
            form_control_function1=EventName.PRODUCT_DETAIL.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=150,
            height=65,
            location_x=10,
            location_y=660,
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
            tool_tip="View detail of selected product",
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=14,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0x8B4513",
            fore_color="0xFFFFFF",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        ),
    ]


def insert_product_detail_controls(session, product_detail_form, cashier_id: str):
    """Insert tab-based controls for PRODUCT_DETAIL (#9).

    Must be called AFTER the first session.flush() (so that the enclosing form
    has a valid id).  This function issues its own flush/flush calls internally.

    Tab layout:
      Tab 0 – Product Info   : PANEL "PRODUCT" with label/textbox pairs
      Tab 1 – Barcodes       : DATAGRID
      Tab 2 – Attributes     : DATAGRID
      Tab 3 – Variants       : DATAGRID
    SAVE + BACK buttons are placed outside the tab control.
    """
    if not product_detail_form:
        return

    # 1. TABCONTROL
    pd_tab_control = FormControl(
        fk_form_id=product_detail_form.id,
        fk_parent_id=None,
        name=ControlName.PRODUCT_DETAIL_TAB.value,
        type_no=1,
        type="TABCONTROL",
        width=1004,
        height=694,
        location_x=10,
        location_y=10,
        back_color="0x1C2833",
        fore_color="0xECF0F1",
        font_size=13,
        is_visible=True,
        fk_cashier_create_id=cashier_id,
        fk_cashier_update_id=cashier_id,
    )
    session.add(pd_tab_control)
    session.flush()

    # 2. Tab page records
    tab_defs = [
        (0, "Product Info",  "Basic product information, unit and manufacturer"),
        (1, "Barcodes",      "Barcodes assigned to this product"),
        (2, "Attributes",    "Custom attributes / features of this product"),
        (3, "Variants",      "Product variants (colour, size, etc.)"),
    ]
    tab_records = []
    for tab_index, tab_title, tab_tooltip in tab_defs:
        tab_rec = FormControlTab(
            fk_form_control_id=pd_tab_control.id,
            tab_index=tab_index,
            tab_title=tab_title,
            tab_tooltip=tab_tooltip,
            back_color="0x1C2833",
            fore_color="0xECF0F1",
            is_visible=True,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        )
        session.add(tab_rec)
        tab_records.append(tab_rec)
    session.flush()

    # 3a. PANEL inside Tab 0 — name "PRODUCT" maps to the Product model
    product_panel = FormControl(
        fk_form_id=product_detail_form.id,
        fk_parent_id=pd_tab_control.id,
        fk_tab_id=tab_records[0].id,
        name="PRODUCT",
        type_no=10,
        type="PANEL",
        width=980,
        height=500,
        location_x=0,
        location_y=0,
        back_color="0x1C2833",
        fore_color="0xECF0F1",
        font_size=12,
        tool_tip="Product information panel",
        is_visible=True,
        fk_cashier_create_id=cashier_id,
        fk_cashier_update_id=cashier_id,
    )
    session.add(product_panel)
    session.flush()

    # 3b. Label/textbox pairs inside PRODUCT panel
    product_info_fields = [
        ("Code",           "code",           "ALPHANUMERIC"),
        ("Name",           "name",           "ALPHANUMERIC"),
        ("Short Name",     "short_name",     "ALPHANUMERIC"),
        ("Sale Price",     "sale_price",     "NUMERIC"),
        ("Purchase Price", "purchase_price", "NUMERIC"),
        ("Stock",          "stock",          "NUMERIC"),
        ("Min Stock",      "min_stock",      "NUMERIC"),
        ("Max Stock",      "max_stock",      "NUMERIC"),
        ("Description",    "description",    "ALPHANUMERIC"),
    ]

    label_width  = 200
    field_width  = 560
    ctrl_height  = 40
    row_height   = ctrl_height + 10
    start_y      = 20

    for i, (lbl_text, field_name, input_type) in enumerate(product_info_fields):
        y_pos = start_y + (i * row_height)

        session.add(FormControl(
            fk_form_id=product_detail_form.id,
            fk_parent_id=product_panel.id,
            parent_name="PRODUCT",
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
            fk_form_id=product_detail_form.id,
            fk_parent_id=product_panel.id,
            parent_name="PRODUCT",
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

    # 3c. DATAGRIDs for tabs 1–3 (Barcodes, Attributes, Variants)
    grid_defs = [
        (ControlName.PRODUCT_BARCODE_GRID.value,   tab_records[1], "Product barcodes"),
        (ControlName.PRODUCT_ATTRIBUTE_GRID.value, tab_records[2], "Product attributes"),
        (ControlName.PRODUCT_VARIANT_GRID.value,   tab_records[3], "Product variants"),
    ]
    for grid_name, tab_rec, tooltip in grid_defs:
        session.add(FormControl(
            fk_form_id=product_detail_form.id,
            fk_parent_id=pd_tab_control.id,
            fk_tab_id=tab_rec.id,
            name=grid_name,
            type_no=1,
            type="DATAGRID",
            width=1002,
            height=647,
            location_x=1,
            location_y=1,
            back_color="0x1C2833",
            fore_color="0xECF0F1",
            font_size=11,
            tool_tip=tooltip,
            is_visible=True,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        ))

    # 4. SAVE button (outside tab control)
    session.add(FormControl(
        fk_form_id=product_detail_form.id,
        fk_parent_id=None,
        name="SAVE_DETAIL",
        form_control_function1=EventName.PRODUCT_DETAIL_SAVE.value,
        type_no=1,
        type="BUTTON",
        width=150,
        height=48,
        location_x=680,
        location_y=710,
        caption1="SAVE",
        text_alignment="CENTER",
        character_casing="UPPER",
        font="Tahoma",
        font_auto_height=False,
        font_size=14,
        tool_tip="Save product changes",
        back_color="0x228B22",
        fore_color="0xFFFFFF",
        is_visible=True,
        fk_cashier_create_id=cashier_id,
        fk_cashier_update_id=cashier_id,
    ))

    # 5. BACK button (outside tab control)
    session.add(FormControl(
        fk_form_id=product_detail_form.id,
        fk_parent_id=None,
        name="BACK_DETAIL",
        form_control_function1="CLOSE_FORM",
        type_no=1,
        type="BUTTON",
        width=150,
        height=48,
        location_x=840,
        location_y=710,
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
