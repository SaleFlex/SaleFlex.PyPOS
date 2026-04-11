"""
SETTING form (#3) — tabbed POS + loyalty configuration.

Replaces the legacy single PANEL layout with a TABCONTROL:
  Tab 0: POS_SETTINGS  → PosSettings
  Tab 1: LOYALTY_PROGRAM → LoyaltyProgram
  Tab 2: LOYALTY_PROGRAM_POLICY → LoyaltyProgramPolicy
  Tab 3: LOYALTY_REDEMPTION_POLICY → LoyaltyRedemptionPolicy
"""

from __future__ import annotations

from data_layer.enums import ControlName, EventName
from data_layer.model.definition.form_control import FormControl
from data_layer.model.definition.form_control_tab import FormControlTab


def get_config_form_controls(config_form, cashier_id: str):
    """Legacy signature: rows are inserted by ``insert_setting_form_controls``."""
    return [], []


def update_config_panel_parents(config_form_controls: list, pos_settings_controls: list) -> None:
    """No-op: parents are wired inside ``insert_setting_form_controls``."""
    return


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


def insert_setting_form_controls(session, config_form, cashier_id: str) -> None:
    if not config_form:
        return

    tab_ctrl = FormControl(
        fk_form_id=config_form.id,
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
        (0, "POS", "Hardware, backend, and store identity"),
        (1, "Loyalty program", "Earn rates, welcome points, program JSON"),
        (2, "Loyalty policy", "Phone ID, enrollment, integration"),
        (3, "Loyalty redemption", "Basket caps and point steps"),
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
            fk_form_id=config_form.id,
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

    pos_fields = [
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
    pid = add_tab_panel(0, "POS_SETTINGS", "POS settings")
    _add_fields_to_panel(session, config_form.id, pid, cashier_id, pos_fields)

    loyalty_program_fields = [
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
    pid = add_tab_panel(1, "LOYALTY_PROGRAM", "Loyalty program")
    _add_fields_to_panel(session, config_form.id, pid, cashier_id, loyalty_program_fields)

    policy_fields = [
        ("Customer ID type (PHONE / LOYALTY_CARD)", "customer_identifier_type", "ALPHANUMERIC"),
        ("Require phone for enrollment", "require_customer_phone_for_enrollment", "CHECKBOX"),
        ("Default phone country code", "default_phone_country_calling_code", "ALPHANUMERIC"),
        ("Void points policy", "void_loyalty_points_policy", "ALPHANUMERIC"),
        ("Integration (LOCAL / GATE / EXTERNAL)", "integration_provider", "ALPHANUMERIC"),
        ("integration_settings_json", "integration_settings_json", "ALPHANUMERIC"),
    ]
    pid = add_tab_panel(2, "LOYALTY_PROGRAM_POLICY", "Loyalty policy")
    _add_fields_to_panel(session, config_form.id, pid, cashier_id, policy_fields)

    redemption_fields = [
        ("Max basket share from points (0–1)", "max_basket_amount_share_from_points", "ALPHANUMERIC"),
        ("Minimum points to redeem", "minimum_points_to_redeem", "NUMERIC"),
        ("Points redemption step", "points_redemption_step", "NUMERIC"),
        ("Allow partial redemption", "allow_partial_redemption", "CHECKBOX"),
    ]
    pid = add_tab_panel(3, "LOYALTY_REDEMPTION_POLICY", "Redemption policy")
    _add_fields_to_panel(session, config_form.id, pid, cashier_id, redemption_fields)

    session.add(
        FormControl(
            fk_form_id=config_form.id,
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
            tool_tip="Save POS and loyalty settings",
            back_color="0x228B22",
            fore_color="0xFFFFFF",
            is_visible=True,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        )
    )
    session.add(
        FormControl(
            fk_form_id=config_form.id,
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
            tool_tip="Back to Main Menu",
            back_color="0x4682B4",
            fore_color="0xFFFFFF",
            is_visible=True,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id,
        )
    )
    session.flush()


def ensure_setting_form_tabs(session, cashier_id: str) -> None:
    """Replace legacy flat SETTING form with tabbed layout if needed (idempotent)."""
    from core.logger import get_logger
    from data_layer.model.definition.form import Form
    from data_layer.model.definition.form_control import FormControl
    from data_layer.model.definition.form_control_tab import FormControlTab

    logger = get_logger(__name__)
    cfg = session.query(Form).filter(Form.form_no == 3).first()
    if not cfg:
        return
    has_tab = (
        session.query(FormControl)
        .filter(
            FormControl.fk_form_id == cfg.id,
            FormControl.name == ControlName.SETTING_TAB_CONTROL.value,
        )
        .first()
    )
    if has_tab:
        return

    logger.info("Schema patch: migrating SETTING form to tabbed POS + loyalty layout")
    tab_ctrl_ids = [
        r.id
        for r in session.query(FormControl)
        .filter(
            FormControl.fk_form_id == cfg.id,
            FormControl.type == "TABCONTROL",
        )
        .all()
    ]
    for tid in tab_ctrl_ids:
        session.query(FormControlTab).filter(FormControlTab.fk_form_control_id == tid).delete(
            synchronize_session=False
        )
    session.query(FormControl).filter(FormControl.fk_form_id == cfg.id).delete(synchronize_session=False)
    session.flush()
    insert_setting_form_controls(session, cfg, cashier_id)
