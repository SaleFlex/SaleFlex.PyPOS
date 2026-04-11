"""
Database form definitions for campaign list and detail (administrators).

Forms: #21 CAMPAIGN_LIST, #22 CAMPAIGN_DETAIL (see ``form_control.py``).
Opened from Main Menu → Settings → CAMPAIGN SETTINGS. Schema patches: ``ensure_campaign_management_forms``.
"""

from __future__ import annotations

from core.logger import get_logger
from data_layer.enums import FormName, ControlName, EventName
from data_layer.model.definition.form_control import FormControl
from data_layer.model.definition.form_control_tab import FormControlTab

logger = get_logger(__name__)


def get_form_data(cashier_id: str) -> list[dict]:
    """Return form rows for CAMPAIGN_LIST (#21) and CAMPAIGN_DETAIL (#22)."""
    return [
        {
            "form_no": 21,
            "name": FormName.CAMPAIGN_LIST.name,
            "function": FormName.CAMPAIGN_LIST.name,
            "need_login": True,
            "need_auth": False,
            "width": 1024,
            "height": 768,
            "form_border_style": "SINGLE",
            "start_position": "CENTERSCREEN",
            "caption": "SaleFlex - Campaigns",
            "back_color": "0x2F4F4F",
            "fore_color": "0xFFFFFF",
            "show_status_bar": True,
            "show_in_taskbar": False,
            "use_virtual_keyboard": True,
            "is_visible": True,
            "is_startup": False,
            "display_mode": "MAIN",
            "fk_cashier_create_id": cashier_id,
        },
        {
            "form_no": 22,
            "name": FormName.CAMPAIGN_DETAIL.name,
            "function": FormName.CAMPAIGN_DETAIL.name,
            "need_login": True,
            "need_auth": False,
            "width": 1024,
            "height": 768,
            "form_border_style": "SINGLE",
            "start_position": "CENTERSCREEN",
            "caption": "SaleFlex - Campaign Detail",
            "back_color": "0x1B2631",
            "fore_color": "0xECF0F1",
            "show_status_bar": False,
            "show_in_taskbar": False,
            "use_virtual_keyboard": False,
            "is_visible": True,
            "is_startup": False,
            "display_mode": "MODAL",
            "fk_cashier_create_id": cashier_id,
        },
    ]


def get_campaign_list_form_controls(campaign_list_form, cashier_id: str) -> list:
    """Controls for CAMPAIGN_LIST (#21)."""
    return [
        FormControl(
            fk_form_id=campaign_list_form.id,
            fk_parent_id=None,
            name=ControlName.CAMPAIGN_SEARCH_TEXTBOX.value,
            form_control_function1=EventName.NONE.value,
            form_control_function2=None,
            type_no=2,
            type="TEXTBOX",
            width=820,
            height=50,
            location_x=10,
            location_y=10,
            caption1="Search by code or name...",
            text_alignment="LEFT",
            character_casing="NORMAL",
            font="Tahoma",
            font_auto_height=False,
            font_size=14,
            input_type="ALPHANUMERIC",
            tool_tip="Filter campaigns by code or name",
            back_color="0xFFFFFF",
            fore_color="0x000000",
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        ),
        FormControl(
            fk_form_id=campaign_list_form.id,
            fk_parent_id=None,
            name="CAMPAIGN_SEARCH_BTN",
            form_control_function1=EventName.CAMPAIGN_SEARCH.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=170,
            height=50,
            location_x=840,
            location_y=10,
            caption1="SEARCH",
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            font_auto_height=False,
            font_size=14,
            input_type="ALPHANUMERIC",
            tool_tip="Search campaigns",
            back_color="0x228B22",
            fore_color="0xFFFFFF",
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        ),
        FormControl(
            fk_form_id=campaign_list_form.id,
            fk_parent_id=None,
            name=ControlName.CAMPAIGN_LIST_DATAGRID.value,
            form_control_function1=EventName.NONE.value,
            form_control_function2=None,
            type_no=9,
            type="DATAGRID",
            width=1000,
            height=555,
            location_x=10,
            location_y=75,
            caption1="Campaigns",
            text_alignment="CENTER",
            character_casing="NORMAL",
            font="Tahoma",
            font_auto_height=False,
            font_size=11,
            input_type="ALPHANUMERIC",
            tool_tip="Sample and live campaigns from the database",
            back_color="0xFFFFFF",
            fore_color="0x000000",
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        ),
        FormControl(
            fk_form_id=campaign_list_form.id,
            fk_parent_id=None,
            name="CAMPAIGN_DETAIL_BTN",
            form_control_function1=EventName.CAMPAIGN_DETAIL.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=150,
            height=65,
            location_x=10,
            location_y=650,
            caption1="DETAIL",
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            font_auto_height=False,
            font_size=14,
            input_type="ALPHANUMERIC",
            tool_tip="Edit selected campaign",
            back_color="0xC0392B",
            fore_color="0xFFFFFF",
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        ),
        FormControl(
            fk_form_id=campaign_list_form.id,
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
            caption1="BACK",
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            font_auto_height=False,
            font_size=14,
            input_type="ALPHANUMERIC",
            tool_tip="Return to previous screen",
            back_color="0x4682B4",
            fore_color="0xFFFFFF",
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        ),
    ]


def insert_campaign_detail_controls(session, campaign_detail_form, cashier_id: str) -> None:
    """TABCONTROL with one panel ``CAMPAIGN`` mapping to the ``Campaign`` model."""
    if not campaign_detail_form:
        return

    tab_ctrl = FormControl(
        fk_form_id=campaign_detail_form.id,
        fk_parent_id=None,
        name=ControlName.CAMPAIGN_DETAIL_TAB.value,
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
    session.add(tab_ctrl)
    session.flush()

    tab_rec = FormControlTab(
        fk_form_control_id=tab_ctrl.id,
        tab_index=0,
        tab_title="Campaign",
        tab_tooltip="Core fields; seed campaigns (e.g. WELCOME10, BASKET100) are safe to edit for testing",
        back_color="0x1B2631",
        fore_color="0xECF0F1",
        is_visible=True,
        fk_cashier_create_id=cashier_id,
        fk_cashier_update_id=cashier_id,
    )
    session.add(tab_rec)
    session.flush()

    campaign_panel = FormControl(
        fk_form_id=campaign_detail_form.id,
        fk_parent_id=tab_ctrl.id,
        fk_tab_id=tab_rec.id,
        name="CAMPAIGN",
        type_no=10,
        type="PANEL",
        width=980,
        height=1100,
        location_x=0,
        location_y=0,
        back_color="0x1B2631",
        fore_color="0xECF0F1",
        font_size=12,
        tool_tip="Campaign row",
        is_visible=True,
        fk_cashier_create_id=cashier_id,
        fk_cashier_update_id=cashier_id,
    )
    session.add(campaign_panel)
    session.flush()

    label_width = 220
    field_width = 520
    ctrl_height = 34
    row_height = ctrl_height + 6
    start_y = 12

    campaign_fields = [
        ("Code", "code", "ALPHANUMERIC"),
        ("Name", "name", "ALPHANUMERIC"),
        ("Description", "description", "ALPHANUMERIC"),
        ("Campaign type id (UUID)", "fk_campaign_type_id", "ALPHANUMERIC"),
        ("Discount type", "discount_type", "ALPHANUMERIC"),
        ("Discount value", "discount_value", "ALPHANUMERIC"),
        ("Discount %", "discount_percentage", "ALPHANUMERIC"),
        ("Max discount amount", "max_discount_amount", "ALPHANUMERIC"),
        ("Min purchase", "min_purchase_amount", "ALPHANUMERIC"),
        ("Max purchase", "max_purchase_amount", "ALPHANUMERIC"),
        ("Buy qty (X get Y)", "buy_quantity", "ALPHANUMERIC"),
        ("Get qty (X get Y)", "get_quantity", "ALPHANUMERIC"),
        ("Start date/time", "start_date", "ALPHANUMERIC"),
        ("End date/time", "end_date", "ALPHANUMERIC"),
        ("Start time (HH:MM)", "start_time", "ALPHANUMERIC"),
        ("End time (HH:MM)", "end_time", "ALPHANUMERIC"),
        ("Days of week (1-7 csv)", "days_of_week", "ALPHANUMERIC"),
        ("Priority", "priority", "ALPHANUMERIC"),
        ("Combinable with other promos", "is_combinable", "CHECKBOX"),
        ("Active", "is_active", "CHECKBOX"),
        ("Auto apply", "is_auto_apply", "CHECKBOX"),
        ("Requires coupon", "requires_coupon", "CHECKBOX"),
        ("Usage limit / customer (empty=none)", "usage_limit_per_customer", "ALPHANUMERIC"),
        ("Total usage limit (empty=none)", "total_usage_limit", "ALPHANUMERIC"),
        ("Total uses (counter)", "total_usage_count", "ALPHANUMERIC"),
        ("Notification message", "notification_message", "ALPHANUMERIC"),
    ]

    for i, (lbl_text, field_name, input_type) in enumerate(campaign_fields):
        y_pos = start_y + (i * row_height)
        session.add(
            FormControl(
                fk_form_id=campaign_detail_form.id,
                fk_parent_id=campaign_panel.id,
                parent_name="CAMPAIGN",
                name=f"LBL_{field_name.upper()}",
                form_control_function1=EventName.NONE.value,
                type_no=8,
                type="LABEL",
                width=label_width,
                height=ctrl_height,
                location_x=10,
                location_y=y_pos,
                caption1=lbl_text + ":",
                text_alignment="RIGHT",
                font="Tahoma",
                font_size=11,
                fore_color="0xECF0F1",
                is_visible=True,
                fk_cashier_create_id=cashier_id,
                fk_cashier_update_id=cashier_id,
            )
        )
        if input_type == "CHECKBOX":
            session.add(
                FormControl(
                    fk_form_id=campaign_detail_form.id,
                    fk_parent_id=campaign_panel.id,
                    parent_name="CAMPAIGN",
                    name=field_name.upper(),
                    form_control_function1=EventName.NONE.value,
                    type_no=11,
                    type="CHECKBOX",
                    width=200,
                    height=ctrl_height,
                    location_x=label_width + 16,
                    location_y=y_pos,
                    caption1="",
                    font="Tahoma",
                    font_size=11,
                    input_type="BOOLEAN",
                    back_color="0xFFFFFF",
                    fore_color="0x000000",
                    tool_tip=lbl_text,
                    is_visible=True,
                    fk_cashier_create_id=cashier_id,
                    fk_cashier_update_id=cashier_id,
                )
            )
        else:
            session.add(
                FormControl(
                    fk_form_id=campaign_detail_form.id,
                    fk_parent_id=campaign_panel.id,
                    parent_name="CAMPAIGN",
                    name=field_name.upper(),
                    form_control_function1=EventName.NONE.value,
                    type_no=2,
                    type="TEXTBOX",
                    width=field_width,
                    height=ctrl_height,
                    location_x=label_width + 16,
                    location_y=y_pos,
                    font="Tahoma",
                    font_size=11,
                    input_type=input_type,
                    back_color="0xFFFFFF",
                    fore_color="0x000000",
                    tool_tip=lbl_text,
                    is_visible=True,
                    fk_cashier_create_id=cashier_id,
                    fk_cashier_update_id=cashier_id,
                )
            )

    session.add(
        FormControl(
            fk_form_id=campaign_detail_form.id,
            fk_parent_id=None,
            name="SAVE_CAMPAIGN_DETAIL",
            form_control_function1=EventName.CAMPAIGN_DETAIL_SAVE.value,
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
            tool_tip="Save campaign and refresh evaluation cache",
            back_color="0x228B22",
            fore_color="0xFFFFFF",
            is_visible=True,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        )
    )
    session.add(
        FormControl(
            fk_form_id=campaign_detail_form.id,
            fk_parent_id=None,
            name="BACK_CAMPAIGN_DETAIL",
            form_control_function1=EventName.CLOSE_FORM.value,
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
        )
    )
    session.flush()


def ensure_campaign_management_forms(session, cashier_id: str) -> None:
    """Idempotent: add campaign list/detail forms and controls (open list from Settings → CAMPAIGN SETTINGS)."""
    from data_layer.model.definition.form import Form
    from data_layer.model.definition.form_control import FormControl as FC

    list_form = session.query(Form).filter(Form.name == FormName.CAMPAIGN_LIST.name).first()
    if not list_form:
        for row in get_form_data(cashier_id):
            session.add(Form(**row))
        session.flush()
        list_form = session.query(Form).filter(Form.name == FormName.CAMPAIGN_LIST.name).first()
        detail_form = session.query(Form).filter(Form.name == FormName.CAMPAIGN_DETAIL.name).first()
        if list_form and detail_form:
            for c in get_campaign_list_form_controls(list_form, cashier_id):
                session.add(c)
            session.flush()
            insert_campaign_detail_controls(session, detail_form, cashier_id)
        logger.info("Schema patch: inserted CAMPAIGN_LIST and CAMPAIGN_DETAIL forms")
    else:
        detail_form = session.query(Form).filter(Form.name == FormName.CAMPAIGN_DETAIL.name).first()
        if detail_form:
            has_tab = (
                session.query(FC)
                .filter(
                    FC.fk_form_id == detail_form.id,
                    FC.name == ControlName.CAMPAIGN_DETAIL_TAB.value,
                )
                .first()
            )
            if not has_tab:
                insert_campaign_detail_controls(session, detail_form, cashier_id)
                logger.info("Schema patch: inserted CAMPAIGN_DETAIL controls")

    session.commit()
