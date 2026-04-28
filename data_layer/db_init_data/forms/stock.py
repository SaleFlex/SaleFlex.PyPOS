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

# Forms #13 (STOCK_INQUIRY), #14 (STOCK_IN), #15 (STOCK_ADJUSTMENT),
#         #16 (STOCK_MOVEMENT)
# All four forms share the same layout built by _make_inventory_controls().

from data_layer.enums import FormName, ControlName, EventName
from data_layer.model.definition.form_control import FormControl


def get_form_data(cashier_id: str) -> list[dict]:
    """Return form-row definitions for all stock / inventory forms (#13–#16)."""
    return [
        {
            'form_no': 13,
            'name': FormName.STOCK_INQUIRY.name,
            'function': FormName.STOCK_INQUIRY.name,
            'need_login': True,
            'need_auth': False,
            'width': 1024,
            'height': 768,
            'form_border_style': 'SINGLE',
            'start_position': 'CENTERSCREEN',
            'caption': 'SaleFlex - Stock Inquiry',
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
            'form_no': 14,
            'name': FormName.STOCK_IN.name,
            'function': FormName.STOCK_IN.name,
            'need_login': True,
            'need_auth': False,
            'width': 1024,
            'height': 768,
            'form_border_style': 'SINGLE',
            'start_position': 'CENTERSCREEN',
            'caption': 'SaleFlex - Goods Receipt (Stock In)',
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
            'form_no': 15,
            'name': FormName.STOCK_ADJUSTMENT.name,
            'function': FormName.STOCK_ADJUSTMENT.name,
            'need_login': True,
            'need_auth': False,
            'width': 1024,
            'height': 768,
            'form_border_style': 'SINGLE',
            'start_position': 'CENTERSCREEN',
            'caption': 'SaleFlex - Stock Adjustment',
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
            'form_no': 16,
            'name': FormName.STOCK_MOVEMENT.name,
            'function': FormName.STOCK_MOVEMENT.name,
            'need_login': True,
            'need_auth': False,
            'width': 1024,
            'height': 768,
            'form_border_style': 'SINGLE',
            'start_position': 'CENTERSCREEN',
            'caption': 'SaleFlex - Stock Movement History',
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


def _make_inventory_controls(
    form, cashier_id: str,
    confirm_event, confirm_caption, confirm_color,
    grid_name, search_event,
    has_secondary_grid=False, secondary_grid_name=None,
    show_qty=False, show_reason=False,
) -> list:
    """Build the standard control set for an inventory form.

    All four inventory forms share this template:
      - Search textbox + SEARCH button
      - Primary DataGrid
      - Optional secondary DataGrid (STOCK_INQUIRY only)
      - Optional Quantity textbox (STOCK_IN / STOCK_ADJUSTMENT)
      - Optional Reason textbox   (STOCK_IN / STOCK_ADJUSTMENT)
      - BACK button
      - Optional CONFIRM button
    """
    controls = [
        FormControl(
            fk_form_id=form.id, fk_parent_id=None,
            name=ControlName.STOCK_SEARCH_TEXTBOX.value,
            form_control_function1=EventName.NONE.value,
            type_no=2, type="TEXTBOX",
            width=820, height=50, location_x=10, location_y=10,
            caption1="Search by product name or code...",
            text_alignment="LEFT", character_casing="NORMAL",
            font="Tahoma", font_auto_height=False, font_size=14,
            input_type="ALPHANUMERIC",
            back_color="0xFFFFFF", fore_color="0x000000",
            fk_cashier_create_id=cashier_id, fk_cashier_update_id=cashier_id,
        ),
        FormControl(
            fk_form_id=form.id, fk_parent_id=None,
            name="INV_SEARCH_BTN",
            form_control_function1=search_event,
            type_no=1, type="BUTTON",
            width=170, height=50, location_x=840, location_y=10,
            caption1="SEARCH",
            text_alignment="CENTER", character_casing="UPPER",
            font="Tahoma", font_auto_height=False, font_size=14,
            input_type="ALPHANUMERIC",
            back_color="0x228B22", fore_color="0xFFFFFF",
            fk_cashier_create_id=cashier_id, fk_cashier_update_id=cashier_id,
        ),
    ]

    main_grid_height = 390 if (show_qty or has_secondary_grid) else 570
    controls.append(FormControl(
        fk_form_id=form.id, fk_parent_id=None,
        name=grid_name,
        form_control_function1=EventName.NONE.value,
        type_no=9, type="DATAGRID",
        width=1000, height=main_grid_height, location_x=10, location_y=75,
        caption1="", text_alignment="CENTER", character_casing="NORMAL",
        font="Tahoma", font_auto_height=False, font_size=11,
        input_type="ALPHANUMERIC",
        back_color="0xFFFFFF", fore_color="0x000000",
        fk_cashier_create_id=cashier_id, fk_cashier_update_id=cashier_id,
    ))

    current_y = 75 + main_grid_height + 10

    if has_secondary_grid and secondary_grid_name:
        controls.append(FormControl(
            fk_form_id=form.id, fk_parent_id=None,
            name=secondary_grid_name,
            form_control_function1=EventName.NONE.value,
            type_no=9, type="DATAGRID",
            width=1000, height=160, location_x=10, location_y=current_y,
            caption1="", text_alignment="CENTER", character_casing="NORMAL",
            font="Tahoma", font_auto_height=False, font_size=11,
            input_type="ALPHANUMERIC",
            back_color="0xF0F0F0", fore_color="0x000000",
            fk_cashier_create_id=cashier_id, fk_cashier_update_id=cashier_id,
        ))
        current_y += 170

    if show_qty:
        controls.append(FormControl(
            fk_form_id=form.id, fk_parent_id=None,
            name=ControlName.STOCK_QUANTITY_TEXTBOX.value,
            form_control_function1=EventName.NONE.value,
            type_no=2, type="TEXTBOX",
            width=220, height=50, location_x=10, location_y=current_y,
            caption1="Quantity...",
            text_alignment="LEFT", character_casing="NORMAL",
            font="Tahoma", font_auto_height=False, font_size=14,
            input_type="NUMERIC",
            back_color="0xFFFFFF", fore_color="0x000000",
            fk_cashier_create_id=cashier_id, fk_cashier_update_id=cashier_id,
        ))

    if show_reason:
        x_reason = 240 if show_qty else 10
        w_reason = 760 if show_qty else 1000
        controls.append(FormControl(
            fk_form_id=form.id, fk_parent_id=None,
            name=ControlName.STOCK_REASON_TEXTBOX.value,
            form_control_function1=EventName.NONE.value,
            type_no=2, type="TEXTBOX",
            width=w_reason, height=50, location_x=x_reason, location_y=current_y,
            caption1="Reason / note (optional)...",
            text_alignment="LEFT", character_casing="NORMAL",
            font="Tahoma", font_auto_height=False, font_size=14,
            input_type="ALPHANUMERIC",
            back_color="0xFFFFFF", fore_color="0x000000",
            fk_cashier_create_id=cashier_id, fk_cashier_update_id=cashier_id,
        ))

    controls.append(FormControl(
        fk_form_id=form.id, fk_parent_id=None,
        name=ControlName.BACK.value,
        form_control_function1=EventName.BACK.value,
        type_no=1, type="BUTTON",
        width=150, height=65, location_x=860, location_y=650,
        caption1="BACK",
        text_alignment="CENTER", character_casing="UPPER",
        font="Tahoma", font_auto_height=False, font_size=14,
        input_type="ALPHANUMERIC",
        back_color="0x4682B4", fore_color="0xFFFFFF",
        fk_cashier_create_id=cashier_id, fk_cashier_update_id=cashier_id,
    ))

    if confirm_event and confirm_caption:
        controls.append(FormControl(
            fk_form_id=form.id, fk_parent_id=None,
            name="INV_CONFIRM_BTN",
            form_control_function1=confirm_event,
            type_no=1, type="BUTTON",
            width=180, height=65, location_x=10, location_y=650,
            caption1=confirm_caption,
            text_alignment="CENTER", character_casing="UPPER",
            font="Tahoma", font_auto_height=False, font_size=14,
            input_type="ALPHANUMERIC",
            back_color=confirm_color, fore_color="0xFFFFFF",
            fk_cashier_create_id=cashier_id, fk_cashier_update_id=cashier_id,
        ))

    return controls


def insert_stock_form_controls(session, stock_forms: dict, cashier_id: str):
    """Insert controls for all inventory forms.

    Must be called AFTER the first session.flush().

    stock_forms keys: 'inquiry', 'stock_in', 'adjustment', 'movement'
    Each value is the Form ORM object (or None if the form does not exist).
    """
    stock_inquiry_form    = stock_forms.get('inquiry')
    stock_in_form         = stock_forms.get('stock_in')
    stock_adjustment_form = stock_forms.get('adjustment')
    stock_movement_form   = stock_forms.get('movement')

    if stock_inquiry_form:
        for ctrl in _make_inventory_controls(
            form=stock_inquiry_form,
            cashier_id=cashier_id,
            confirm_event=EventName.STOCK_DETAIL.value,
            confirm_caption="DETAIL",
            confirm_color="0x8B4513",
            grid_name=ControlName.STOCK_INQUIRY_DATAGRID.value,
            search_event=EventName.STOCK_SEARCH.value,
            has_secondary_grid=True,
            secondary_grid_name=ControlName.STOCK_DETAIL_DATAGRID.value,
        ):
            session.add(ctrl)

        # Navigation buttons to sibling inventory forms
        nav_buttons = [
            ("STOCK_IN_NAV_BTN",  "STOCK IN",   EventName.STOCK_IN.value,         205, "0x1E8449", "Go to Goods Receipt (Stock-In) form"),
            ("STOCK_ADJ_NAV_BTN", "ADJUSTMENT", EventName.STOCK_ADJUSTMENT.value, 400, "0xB7950B", "Go to Manual Stock Adjustment form"),
            ("STOCK_MOV_NAV_BTN", "HISTORY",    EventName.STOCK_MOVEMENT.value,   595, "0x1A7A7A", "Go to Stock Movement History form"),
        ]
        for btn_name, caption, event, loc_x, color, tip in nav_buttons:
            session.add(FormControl(
                fk_form_id=stock_inquiry_form.id, fk_parent_id=None,
                name=btn_name,
                form_control_function1=event,
                type_no=1, type="BUTTON",
                width=180, height=65, location_x=loc_x, location_y=650,
                caption1=caption,
                text_alignment="CENTER", character_casing="UPPER",
                font="Tahoma", font_auto_height=False, font_size=13,
                input_type="ALPHANUMERIC",
                back_color=color, fore_color="0xFFFFFF",
                tool_tip=tip,
                fk_cashier_create_id=cashier_id, fk_cashier_update_id=cashier_id,
            ))

    if stock_in_form:
        for ctrl in _make_inventory_controls(
            form=stock_in_form,
            cashier_id=cashier_id,
            confirm_event=EventName.STOCK_IN_CONFIRM.value,
            confirm_caption="RECEIVE",
            confirm_color="0x1E8449",
            grid_name=ControlName.STOCK_IN_PRODUCT_DATAGRID.value,
            search_event=EventName.STOCK_IN_SEARCH.value,
            show_qty=True,
            show_reason=True,
        ):
            session.add(ctrl)

    if stock_adjustment_form:
        for ctrl in _make_inventory_controls(
            form=stock_adjustment_form,
            cashier_id=cashier_id,
            confirm_event=EventName.STOCK_ADJUSTMENT_CONFIRM.value,
            confirm_caption="ADJUST",
            confirm_color="0xB7950B",
            grid_name=ControlName.STOCK_ADJUSTMENT_DATAGRID.value,
            search_event=EventName.STOCK_ADJUSTMENT_SEARCH.value,
            show_qty=True,
            show_reason=True,
        ):
            session.add(ctrl)

    if stock_movement_form:
        for ctrl in _make_inventory_controls(
            form=stock_movement_form,
            cashier_id=cashier_id,
            confirm_event=None,
            confirm_caption=None,
            confirm_color=None,
            grid_name=ControlName.STOCK_MOVEMENT_DATAGRID.value,
            search_event=EventName.STOCK_MOVEMENT_SEARCH.value,
        ):
            session.add(ctrl)
