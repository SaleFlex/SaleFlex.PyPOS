"""
Settings UI: hub form (#3 SETTINGS_MENU), POS_SETTINGS (#23), LOYALTY_SETTINGS (#24).

Former single tabbed SETTING form is split so Main Menu → SETTINGS opens the hub;
POS / Loyalty / Campaign open dedicated screens. Campaigns reuse CAMPAIGN_LIST (#21).
"""

from __future__ import annotations

from data_layer.enums import ControlName, EventName, FormName
from data_layer.model.definition.form_control import FormControl
from data_layer.model.definition.form_control_tab import FormControlTab


def get_config_form_controls(config_form, cashier_id: str):
    """Legacy signature: rows are inserted by dedicated insert_* functions."""
    return [], []


def update_config_panel_parents(config_form_controls: list, pos_settings_controls: list) -> None:
    """No-op: parents are wired inside insert_* helpers."""
    return


# --- Field definitions (shared by POS and loyalty screens) ---------------------------------

POS_SETTINGS_FIELDS: list[tuple[str, str, str]] = [
    ("POS No in Store", "pos_no_in_store", "NUMERIC"),
    ("Name", "name", "ALPHANUMERIC"),
    ("Owner National ID", "owner_national_id", "ALPHANUMERIC"),
    ("Owner Tax ID", "owner_tax_id", "ALPHANUMERIC"),
    ("Owner Web Address", "owner_web_address", "ALPHANUMERIC"),
    ("MAC Address", "mac_address", "ALPHANUMERIC"),
    ("Customer Display Type", "customer_display_type", "ALPHANUMERIC"),
    ("Customer Display Port", "customer_display_port", "ALPHANUMERIC"),
    ("Receipt Printer Type", "receipt_printer_type", "ALPHANUMERIC"),
    ("Receipt Printer Port", "receipt_printer_port", "ALPHANUMERIC"),
    ("Invoice Printer Type", "invoice_printer_type", "ALPHANUMERIC"),
    ("Invoice Printer Port", "invoice_printer_port", "ALPHANUMERIC"),
    ("Scale Type", "scale_type", "ALPHANUMERIC"),
    ("Scale Port", "scale_port", "ALPHANUMERIC"),
    ("Barcode Reader Port", "barcode_reader_port", "ALPHANUMERIC"),
    ("Backend IP 1", "backend_ip1", "ALPHANUMERIC"),
    ("Backend Port 1", "backend_port1", "NUMERIC"),
    ("Backend IP 2", "backend_ip2", "ALPHANUMERIC"),
    ("Backend Port 2", "backend_port2", "NUMERIC"),
    ("Backend Type", "backend_type", "ALPHANUMERIC"),
    ("Device Serial Number", "device_serial_number", "ALPHANUMERIC"),
    ("Device OS", "device_operation_system", "ALPHANUMERIC"),
    ("Force Online", "force_to_work_online", "CHECKBOX"),
    ("PLU Update No", "plu_update_no", "NUMERIC"),
]

LOYALTY_PROGRAM_FIELDS: list[tuple[str, str, str]] = [
    ("Program name", "name", "ALPHANUMERIC"),
    ("Description", "description", "ALPHANUMERIC"),
    ("Points per currency", "points_per_currency", "ALPHANUMERIC"),
    ("Currency per point", "currency_per_point", "ALPHANUMERIC"),
    ("Min purchase for points", "min_purchase_for_points", "ALPHANUMERIC"),
    ("Point expiry days (empty=none)", "point_expiry_days", "NUMERIC"),
    ("Welcome points", "welcome_points", "NUMERIC"),
    ("Birthday points", "birthday_points", "NUMERIC"),
    ("Program active", "is_active", "CHECKBOX"),
    ("settings_json (e.g. earn payment types)", "settings_json", "ALPHANUMERIC"),
]

LOYALTY_POLICY_FIELDS: list[tuple[str, str, str]] = [
    ("Customer ID type (PHONE / LOYALTY_CARD)", "customer_identifier_type", "ALPHANUMERIC"),
    ("Require phone for enrollment", "require_customer_phone_for_enrollment", "CHECKBOX"),
    ("Default phone country code", "default_phone_country_calling_code", "ALPHANUMERIC"),
    ("Void points policy", "void_loyalty_points_policy", "ALPHANUMERIC"),
    ("Integration (LOCAL / GATE / EXTERNAL)", "integration_provider", "ALPHANUMERIC"),
    ("integration_settings_json", "integration_settings_json", "ALPHANUMERIC"),
]

LOYALTY_REDEMPTION_FIELDS: list[tuple[str, str, str]] = [
    ("Max basket share from points (0–1)", "max_basket_amount_share_from_points", "ALPHANUMERIC"),
    ("Minimum points to redeem", "minimum_points_to_redeem", "NUMERIC"),
    ("Points redemption step", "points_redemption_step", "NUMERIC"),
    ("Allow partial redemption", "allow_partial_redemption", "CHECKBOX"),
]


def _add_fields_to_panel(
    session,
    form_id,
    panel_id: str,
    cashier_id: str,
    field_rows: list[tuple[str, str, str]],
    *,
    label_width: int = 220,
    textbox_width: int = 520,
    control_height: int = 36,
    row_gap: int = 8,
    start_y: int = 12,
) -> None:
    row_height = control_height + row_gap
    for i, (label_text, field_name, input_type) in enumerate(field_rows):
        y_pos = start_y + (i * row_height)
        session.add(
            FormControl(
                fk_form_id=form_id,
                fk_parent_id=panel_id,
                name=f"LBL_{field_name.upper()}",
                form_control_function1=EventName.NONE.value,
                type_no=8,
                type="LABEL",
                width=label_width,
                height=control_height,
                location_x=8,
                location_y=y_pos,
                caption1=label_text + ":",
                text_alignment="RIGHT",
                font="Tahoma",
                font_size=11,
                fore_color="0xFFFFFF",
                is_visible=True,
                fk_cashier_create_id=cashier_id,
                fk_cashier_update_id=cashier_id,
            )
        )
        if input_type == "CHECKBOX":
            session.add(
                FormControl(
                    fk_form_id=form_id,
                    fk_parent_id=panel_id,
                    name=field_name.upper(),
                    form_control_function1=EventName.NONE.value,
                    type_no=11,
                    type="CHECKBOX",
                    width=200,
                    height=control_height,
                    location_x=label_width + 16,
                    location_y=y_pos,
                    caption1="",
                    font="Tahoma",
                    font_size=11,
                    input_type="BOOLEAN",
                    back_color="0xFFFFFF",
                    fore_color="0x000000",
                    tool_tip=label_text,
                    is_visible=True,
                    fk_cashier_create_id=cashier_id,
                    fk_cashier_update_id=cashier_id,
                )
            )
        else:
            session.add(
                FormControl(
                    fk_form_id=form_id,
                    fk_parent_id=panel_id,
                    name=field_name.upper(),
                    form_control_function1=EventName.NONE.value,
                    type_no=2,
                    type="TEXTBOX",
                    width=textbox_width,
                    height=control_height,
                    location_x=label_width + 16,
                    location_y=y_pos,
                    font="Tahoma",
                    font_size=11,
                    input_type=input_type,
                    back_color="0xFFFFFF",
                    fore_color="0x000000",
                    tool_tip=f"Enter {label_text.lower()}",
                    is_visible=True,
                    fk_cashier_create_id=cashier_id,
                    fk_cashier_update_id=cashier_id,
                )
            )


def insert_settings_menu_controls(session, menu_form, cashier_id: str) -> None:
    """Hub: three centre navigation buttons + BACK (bottom-right)."""
    if not menu_form:
        return
    buttons = [
        (
            "GOTO_POS_SETTINGS",
            EventName.POS_SETTINGS_FORM.value,
            180,
            "POS SETTINGS",
            "0x4682B4",
            "Hardware, backend, and store identity",
        ),
        (
            "GOTO_LOYALTY_SETTINGS",
            EventName.LOYALTY_SETTINGS_FORM.value,
            280,
            "LOYALTY SETTINGS",
            "0xFF8C00",
            "Loyalty program and redemption policies",
        ),
        (
            "GOTO_CAMPAIGN_SETTINGS",
            EventName.CAMPAIGN_LIST_FORM.value,
            380,
            "CAMPAIGN SETTINGS",
            "0xC0392B",
            "Campaign definitions (administrators)",
        ),
    ]
    for name, fn1, y, caption, bg, tip in buttons:
        session.add(
            FormControl(
                fk_form_id=menu_form.id,
                fk_parent_id=None,
                name=name,
                form_control_function1=fn1,
                form_control_function2=None,
                type_no=1,
                type="BUTTON",
                width=400,
                height=80,
                location_x=312,
                location_y=y,
                caption1=caption,
                text_alignment="CENTER",
                character_casing="UPPER",
                font="Tahoma",
                font_auto_height=False,
                font_size=16,
                input_type="ALPHANUMERIC",
                tool_tip=tip,
                back_color=bg,
                fore_color="0xFFFFFF",
                fk_cashier_create_id=cashier_id,
                fk_cashier_update_id=cashier_id,
            )
        )
    session.add(
        FormControl(
            fk_form_id=menu_form.id,
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
            caption1="BACK",
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            font_auto_height=False,
            font_size=12,
            input_type="ALPHANUMERIC",
            tool_tip="Return to Main Menu",
            back_color="0x4682B4",
            fore_color="0xFFFFFF",
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        )
    )
    session.flush()


def insert_pos_settings_form_controls(session, target_form, cashier_id: str) -> None:
    """Single root panel POS_SETTINGS + SAVE + BACK."""
    if not target_form:
        return
    panel = FormControl(
        fk_form_id=target_form.id,
        fk_parent_id=None,
        name="POS_SETTINGS",
        type_no=10,
        type="PANEL",
        width=1000,
        height=618,
        location_x=12,
        location_y=8,
        caption1="POS settings",
        back_color="0x2F4F4F",
        fore_color="0xFFFFFF",
        font_size=11,
        tool_tip="POS settings",
        is_visible=True,
        fk_cashier_create_id=cashier_id,
        fk_cashier_update_id=cashier_id,
    )
    session.add(panel)
    session.flush()
    _add_fields_to_panel(session, target_form.id, panel.id, cashier_id, POS_SETTINGS_FIELDS)
    session.add(
        FormControl(
            fk_form_id=target_form.id,
            fk_parent_id=None,
            name=ControlName.SAVE.value,
            form_control_function1=EventName.SAVE_CHANGES.value,
            type_no=1,
            type="BUTTON",
            width=125,
            height=99,
            location_x=745,
            location_y=630,
            caption1="SAVE",
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            font_size=14,
            tool_tip="Save POS settings",
            back_color="0x228B22",
            fore_color="0xFFFFFF",
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        )
    )
    session.add(
        FormControl(
            fk_form_id=target_form.id,
            fk_parent_id=None,
            name=ControlName.BACK.value,
            form_control_function1=EventName.BACK.value,
            type_no=1,
            type="BUTTON",
            width=125,
            height=99,
            location_x=880,
            location_y=630,
            caption1="BACK",
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            font_size=14,
            tool_tip="Back to Settings menu",
            back_color="0x4682B4",
            fore_color="0xFFFFFF",
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        )
    )
    session.flush()


def insert_loyalty_settings_form_controls(session, target_form, cashier_id: str) -> None:
    """TABCONTROL with three loyalty tabs (same panels as former SETTING tabs 1–3)."""
    if not target_form:
        return
    tab_ctrl = FormControl(
        fk_form_id=target_form.id,
        fk_parent_id=None,
        name=ControlName.SETTING_TAB_CONTROL.value,
        type_no=1,
        type="TABCONTROL",
        width=1000,
        height=618,
        location_x=12,
        location_y=8,
        back_color="0x2F4F4F",
        fore_color="0xFFFFFF",
        font_size=12,
        is_visible=True,
        fk_cashier_create_id=cashier_id,
        fk_cashier_update_id=cashier_id,
    )
    session.add(tab_ctrl)
    session.flush()

    tab_defs = [
        (0, "Loyalty program", "Earn rates, welcome points, program JSON"),
        (1, "Loyalty policy", "Phone ID, enrollment, integration"),
        (2, "Loyalty redemption", "Basket caps and point steps"),
    ]
    tab_records: list[FormControlTab] = []
    for idx, title, tip in tab_defs:
        tr = FormControlTab(
            fk_form_control_id=tab_ctrl.id,
            tab_index=idx,
            tab_title=title,
            tab_tooltip=tip,
            back_color="0x2F4F4F",
            fore_color="0xFFFFFF",
            is_visible=True,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        )
        session.add(tr)
        tab_records.append(tr)
    session.flush()

    def add_tab_panel(tab_index: int, panel_name: str, caption: str) -> str:
        p = FormControl(
            fk_form_id=target_form.id,
            fk_parent_id=tab_ctrl.id,
            fk_tab_id=tab_records[tab_index].id,
            name=panel_name,
            type_no=10,
            type="PANEL",
            width=980,
            height=580,
            location_x=2,
            location_y=2,
            caption1=caption,
            back_color="0x2F4F4F",
            fore_color="0xFFFFFF",
            font_size=11,
            tool_tip=caption,
            is_visible=True,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        )
        session.add(p)
        session.flush()
        return p.id

    pid = add_tab_panel(0, "LOYALTY_PROGRAM", "Loyalty program")
    _add_fields_to_panel(session, target_form.id, pid, cashier_id, LOYALTY_PROGRAM_FIELDS)
    pid = add_tab_panel(1, "LOYALTY_PROGRAM_POLICY", "Loyalty policy")
    _add_fields_to_panel(session, target_form.id, pid, cashier_id, LOYALTY_POLICY_FIELDS)
    pid = add_tab_panel(2, "LOYALTY_REDEMPTION_POLICY", "Redemption policy")
    _add_fields_to_panel(session, target_form.id, pid, cashier_id, LOYALTY_REDEMPTION_FIELDS)

    session.add(
        FormControl(
            fk_form_id=target_form.id,
            fk_parent_id=None,
            name=ControlName.SAVE.value,
            form_control_function1=EventName.SAVE_CHANGES.value,
            type_no=1,
            type="BUTTON",
            width=125,
            height=99,
            location_x=745,
            location_y=630,
            caption1="SAVE",
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            font_size=14,
            tool_tip="Save loyalty settings",
            back_color="0x228B22",
            fore_color="0xFFFFFF",
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        )
    )
    session.add(
        FormControl(
            fk_form_id=target_form.id,
            fk_parent_id=None,
            name=ControlName.BACK.value,
            form_control_function1=EventName.BACK.value,
            type_no=1,
            type="BUTTON",
            width=125,
            height=99,
            location_x=880,
            location_y=630,
            caption1="BACK",
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            font_size=14,
            tool_tip="Back to Settings menu",
            back_color="0x4682B4",
            fore_color="0xFFFFFF",
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        )
    )
    session.flush()


def _delete_all_form_controls(session, form_id) -> None:
    from data_layer.model.definition.form_control import FormControl as FC

    tab_ctrl_ids = [
        r.id
        for r in session.query(FC)
        .filter(
            FC.fk_form_id == form_id,
            FC.type == "TABCONTROL",
        )
        .all()
    ]
    from data_layer.model.definition.form_control_tab import FormControlTab

    for tid in tab_ctrl_ids:
        session.query(FormControlTab).filter(FormControlTab.fk_form_control_id == tid).delete(
            synchronize_session=False
        )
    session.query(FC).filter(FC.fk_form_id == form_id).delete(synchronize_session=False)
    session.flush()


def _default_form_row(form_no: int, name: str, caption: str, cashier_id: str) -> dict:
    return {
        "form_no": form_no,
        "name": name,
        "function": name,
        "need_login": True,
        "need_auth": False,
        "width": 1024,
        "height": 768,
        "form_border_style": "SINGLE",
        "start_position": "CENTERSCREEN",
        "caption": caption,
        "back_color": "0x2F4F4F",
        "fore_color": "0xFFFFFF",
        "show_status_bar": True,
        "show_in_taskbar": False,
        "use_virtual_keyboard": False,
        "is_visible": True,
        "is_startup": False,
        "display_mode": "MAIN",
        "fk_cashier_create_id": cashier_id,
    }


def ensure_settings_hub_layout(session, cashier_id: str) -> None:
    """
    Idempotent migration:
    - Form #3 becomes SETTINGS_MENU with hub controls (replaces legacy tabbed SETTING).
    - Inserts forms #23 POS_SETTINGS and #24 LOYALTY_SETTINGS if missing.
    - Removes CAMPAIGNS shortcut from Main Menu and from old settings form.
    """
    from core.logger import get_logger
    from data_layer.model.definition.form import Form
    from data_layer.model.definition.form_control import FormControl as FC

    logger = get_logger(__name__)

    hub = session.query(Form).filter(Form.form_no == 3).first()
    if not hub:
        return

    has_hub_nav = (
        session.query(FC)
        .filter(
            FC.fk_form_id == hub.id,
            FC.name == "GOTO_POS_SETTINGS",
            FC.is_deleted.is_(False),
        )
        .first()
    )
    legacy_tab = (
        session.query(FC)
        .filter(
            FC.fk_form_id == hub.id,
            FC.name == ControlName.SETTING_TAB_CONTROL.value,
            FC.is_deleted.is_(False),
        )
        .first()
    )

    if hub.name != FormName.SETTINGS_MENU.name or legacy_tab or not has_hub_nav:
        hub.name = FormName.SETTINGS_MENU.name
        hub.function = FormName.SETTINGS_MENU.name
        hub.caption = "SaleFlex - Settings"
        _delete_all_form_controls(session, hub.id)
        insert_settings_menu_controls(session, hub, cashier_id)
        logger.info("Schema patch: form #3 is SETTINGS_MENU hub")

    # POS_SETTINGS #23
    pos_form = session.query(Form).filter(Form.form_no == 23).first()
    if not pos_form:
        session.add(Form(**_default_form_row(23, FormName.POS_SETTINGS.name, "SaleFlex - POS Settings", cashier_id)))
        session.flush()
        pos_form = session.query(Form).filter(Form.form_no == 23).first()
    else:
        if pos_form.name != FormName.POS_SETTINGS.name:
            pos_form.name = FormName.POS_SETTINGS.name
            pos_form.function = FormName.POS_SETTINGS.name
            pos_form.caption = "SaleFlex - POS Settings"

    has_pos_panel = (
        session.query(FC)
        .filter(
            FC.fk_form_id == pos_form.id,
            FC.name == "POS_SETTINGS",
            FC.type == "PANEL",
            FC.is_deleted.is_(False),
        )
        .first()
    )
    if pos_form and not has_pos_panel:
        _delete_all_form_controls(session, pos_form.id)
        insert_pos_settings_form_controls(session, pos_form, cashier_id)
        logger.info("Schema patch: inserted POS_SETTINGS form controls (#23)")

    # LOYALTY_SETTINGS #24
    loy_form = session.query(Form).filter(Form.form_no == 24).first()
    if not loy_form:
        session.add(
            Form(**_default_form_row(24, FormName.LOYALTY_SETTINGS.name, "SaleFlex - Loyalty Settings", cashier_id))
        )
        session.flush()
        loy_form = session.query(Form).filter(Form.form_no == 24).first()
    else:
        if loy_form.name != FormName.LOYALTY_SETTINGS.name:
            loy_form.name = FormName.LOYALTY_SETTINGS.name
            loy_form.function = FormName.LOYALTY_SETTINGS.name
            loy_form.caption = "SaleFlex - Loyalty Settings"

    has_loyalty_tab = (
        session.query(FC)
        .filter(
            FC.fk_form_id == loy_form.id,
            FC.name == ControlName.SETTING_TAB_CONTROL.value,
            FC.is_deleted.is_(False),
        )
        .first()
    )
    if loy_form and not has_loyalty_tab:
        _delete_all_form_controls(session, loy_form.id)
        insert_loyalty_settings_form_controls(session, loy_form, cashier_id)
        logger.info("Schema patch: inserted LOYALTY_SETTINGS form controls (#24)")

    main = session.query(Form).filter(Form.name == FormName.MAIN_MENU.name).first()
    if main:
        n = (
            session.query(FC)
            .filter(FC.fk_form_id == main.id, FC.name == "GOTO_CAMPAIGNS", FC.is_deleted.is_(False))
            .delete(synchronize_session=False)
        )
        if n:
            logger.info("Schema patch: removed GOTO_CAMPAIGNS from MAIN_MENU")

    session.query(FC).filter(
        FC.name == "GOTO_CAMPAIGNS_FROM_SETTINGS",
        FC.is_deleted.is_(False),
    ).delete(synchronize_session=False)

    session.commit()


def ensure_setting_form_tabs(session, cashier_id: str) -> None:
    """Backward-compatible name: delegate to settings hub migration."""
    ensure_settings_hub_layout(session, cashier_id)
