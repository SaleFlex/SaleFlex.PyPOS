"""
SaleFlex.PyPOS - Point of Sale Application

Copyright (c) 2025-2026 Ferhat Mousavi

Form #20 PAYMENT — dedicated payment screen (opened from SALE via FUNC + dual CREDIT CARD).

Payment-type buttons map to existing EventName payment handlers and ``PaymentService``;
see module docstring on ``get_payment_form_controls`` for EventName ↔ business mapping.
"""

from data_layer.enums import FormName, EventName
from data_layer.model.definition.form_control import FormControl


def get_form_data(cashier_id: str) -> list[dict]:
    """Return form-row definition for PAYMENT (form_no=20)."""
    return [
        {
            "form_no": 20,
            "name": FormName.PAYMENT.name,
            "function": FormName.PAYMENT.name,
            "need_login": True,
            "need_auth": False,
            "width": 1024,
            "height": 768,
            "form_border_style": "SINGLE",
            "start_position": "CENTERSCREEN",
            "caption": "SaleFlex - Payment",
            "back_color": "0x2F4F4F",
            "fore_color": "0xFFFFFF",
            "show_status_bar": True,
            "show_in_taskbar": False,
            "use_virtual_keyboard": False,
            "is_visible": True,
            "is_startup": False,
            "display_mode": "MAIN",
            "fk_cashier_create_id": cashier_id,
        },
    ]


def _btn(
    form,
    cashier_id: str,
    *,
    name: str,
    caption: str,
    event: str,
    x: int,
    y: int,
    w: int,
    h: int,
    tip: str,
    back_color: str,
    fore_color: str = "0x000000",
    font_size: int = 11,
) -> FormControl:
    return FormControl(
        fk_form_id=form.id,
        fk_parent_id=None,
        name=name,
        form_control_function1=event,
        form_control_function2=None,
        type_no=1,
        type="BUTTON",
        width=w,
        height=h,
        location_x=x,
        location_y=y,
        start_position=None,
        caption1=caption,
        caption2=None,
        list_values=None,
        dock=None,
        alignment=None,
        text_alignment="CENTER",
        character_casing="UPPER",
        font="Tahoma",
        icon=None,
        tool_tip=tip,
        image=None,
        image_selected=None,
        font_auto_height=True,
        font_size=font_size,
        input_type="ALPHANUMERIC",
        text_image_relation=None,
        back_color=back_color,
        fore_color=fore_color,
        keyboard_value=None,
        fk_cashier_create_id=cashier_id,
        fk_cashier_update_id=cashier_id,
    )


def get_payment_form_controls(payment_form, cashier_id: str) -> list:
    """Return FormControl rows for PAYMENT (#20). Empty list if ``payment_form`` is None.

    ``PaymentType``-style labels map to existing ``EventName`` values processed by
    ``PaymentService``:

    - CASH → ``CASH_PAYMENT``
    - CREDIT_CARD → ``CREDIT_PAYMENT``
    - CHECK → ``CHECK_PAYMENT``
    - ON_CREDIT / CURRENT_ACCOUNT → ``CHARGE_SALE_PAYMENT``
    - PREPAID_CARD → ``PREPAID_PAYMENT``
    - MOBILE / BANK_TRANSFER → ``OTHER_PAYMENT`` (recorded as OTHER on receipt)
    - BONUS → ``BONUS_PAYMENT`` (loyalty points discount; enter whole points on numpad first)
    - EXCHANGE → ``EXCHANGE_PAYMENT``
    """
    if not payment_form:
        return []

    f = payment_form
    cid = cashier_id

    # Layout (1024×768): top band = AMOUNTSTABLE + payment grid; middle = PAYMENTLIST | NUMPAD;
    # bottom row = BACK + CHANGE, sized to sit above the status bar.
    form_w, form_h = 1024, 768
    margin = 6
    top_h = 292
    amt_w, amt_h = 382, top_h - margin  # enlarged summary table, top-left
    pay_x0 = amt_w + margin * 2
    pay_w_total = form_w - pay_x0 - margin
    pay_gap_x, pay_gap_y = 8, 10
    pay_cols = 5
    pay_btn_w = (pay_w_total - (pay_cols - 1) * pay_gap_x) // pay_cols
    pay_top_pad = 8
    pay_inner_h = top_h - pay_top_pad * 2
    pay_btn_h = (pay_inner_h - pay_gap_y) // 2

    mid_y = top_h + margin
    status_reserve = 42  # keep controls clear of the window status bar
    gap_above_status = 6
    bottom_btn_h = 86
    bottom_btn_y = form_h - status_reserve - gap_above_status - bottom_btn_h
    mid_bottom = bottom_btn_y - margin
    mid_h = max(200, mid_bottom - mid_y)
    list_w = 440
    list_x = margin
    numpad_x = list_x + list_w + margin
    numpad_w = form_w - numpad_x - margin

    controls: list = [
        FormControl(
            fk_form_id=f.id,
            fk_parent_id=None,
            name="AMOUNTSTABLE",
            form_control_function1="AMOUNTSTABLE",
            form_control_function2=None,
            type_no=7,
            type="AMOUNTSTABLE",
            width=amt_w,
            height=amt_h,
            location_x=margin,
            location_y=margin,
            start_position=None,
            caption1="",
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
            font_auto_height=True,
            font_size=0,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color=None,
            fore_color=None,
            keyboard_value=None,
            fk_cashier_create_id=cid,
            fk_cashier_update_id=cid,
        ),
        FormControl(
            fk_form_id=f.id,
            fk_parent_id=None,
            name="PAYMENTLIST",
            form_control_function1="PAYMENTLIST",
            form_control_function2=None,
            type_no=6,
            type="PAYMENTLIST",
            width=list_w,
            height=mid_h,
            location_x=list_x,
            location_y=mid_y,
            start_position=None,
            caption1="",
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
            font_auto_height=True,
            font_size=0,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color=None,
            fore_color=None,
            keyboard_value=None,
            fk_cashier_create_id=cid,
            fk_cashier_update_id=cid,
        ),
        FormControl(
            fk_form_id=f.id,
            fk_parent_id=None,
            name="NUMPAD",
            form_control_function1=EventName.NONE.value,
            form_control_function2=None,
            type_no=5,
            type="NUMPAD",
            width=numpad_w,
            height=mid_h,
            location_x=numpad_x,
            location_y=mid_y,
            start_position=None,
            caption1="",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            icon=None,
            tool_tip="Enter tender amount in minor units, then press a payment type (repeat for split tenders; full balance is not taken automatically)",
            image=None,
            image_selected=None,
            font_auto_height=True,
            font_size=0,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color=None,
            fore_color=None,
            keyboard_value=None,
            fk_cashier_create_id=cid,
            fk_cashier_update_id=cid,
        ),
        FormControl(
            fk_form_id=f.id,
            fk_parent_id=None,
            name="BACK",
            form_control_function1=EventName.BACK.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=125,
            height=bottom_btn_h,
            location_x=margin,
            location_y=bottom_btn_y,
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
            tool_tip="Return to SALE form",
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=14,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0x4682B4",
            fore_color="0xFFFFFF",
            keyboard_value=None,
            fk_cashier_create_id=cid,
            fk_cashier_update_id=cid,
        ),
        FormControl(
            fk_form_id=f.id,
            fk_parent_id=None,
            name="PAYMENT_CHANGE",
            form_control_function1=EventName.CHANGE_PAYMENT.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=144,
            height=bottom_btn_h,
            location_x=margin + 125 + margin,
            location_y=bottom_btn_y,
            start_position=None,
            caption1="CHANGE",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            icon=None,
            tool_tip="Record change when cash tender exceeds the amount due",
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=14,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0x87CEEB",
            fore_color="0x000000",
            keyboard_value=None,
            fk_cashier_create_id=cid,
            fk_cashier_update_id=cid,
        ),
    ]

    bw, bh = pay_btn_w, pay_btn_h
    y1 = pay_top_pad
    y2 = pay_top_pad + bh + pay_gap_y
    xs = [pay_x0 + i * (bw + pay_gap_x) for i in range(5)]

    rows = [
        (
            y1,
            [
                ("PAY_TYPE_CASH", "CASH", EventName.CASH_PAYMENT.value, "0x90EE90", "Cash tender"),
                ("PAY_TYPE_CC", "CREDIT", EventName.CREDIT_PAYMENT.value, "0xDDA0DD", "Credit / bank card"),
                ("PAY_TYPE_CHECK", "CHECK", EventName.CHECK_PAYMENT.value, "0xF0E68C", "Check payment"),
                ("PAY_TYPE_ON_CREDIT", "ON CREDIT", EventName.CHARGE_SALE_PAYMENT.value, "0xFFB347", "Charge to customer account"),
                ("PAY_TYPE_PREPAID", "PREPAID", EventName.PREPAID_PAYMENT.value, "0x87CEFA", "Prepaid / gift card"),
            ],
        ),
        (
            y2,
            [
                ("PAY_TYPE_MOBILE", "MOBILE", EventName.OTHER_PAYMENT.value, "0x98FB98", "Mobile / digital wallet"),
                ("PAY_TYPE_BONUS", "BONUS", EventName.BONUS_PAYMENT.value, "0xFFD700", "Loyalty points — enter points on numpad, then BONUS"),
                ("PAY_TYPE_EXCHANGE", "EXCHANGE", EventName.EXCHANGE_PAYMENT.value, "0xE6E6FA", "Foreign exchange / trade-in"),
                ("PAY_TYPE_CURR_ACCT", "C. ACCOUNT", EventName.CHARGE_SALE_PAYMENT.value, "0xFFA07A", "Current account posting"),
                ("PAY_TYPE_BANK", "BANK TRANS", EventName.OTHER_PAYMENT.value, "0xB0C4DE", "Bank transfer / EFT"),
            ],
        ),
    ]

    for yy, defs in rows:
        for i, (nm, cap, ev, bg, tip) in enumerate(defs):
            controls.append(
                _btn(
                    f,
                    cid,
                    name=nm,
                    caption=cap,
                    event=ev,
                    x=xs[i],
                    y=yy,
                    w=bw,
                    h=bh,
                    tip=tip,
                    back_color=bg,
                    font_size=13,
                )
            )

    return controls
