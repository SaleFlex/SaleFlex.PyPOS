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

from sqlalchemy.orm import Session

from core.logger import get_logger
from data_layer.model.definition.form import Form
from data_layer.model.definition.form_control import FormControl
from data_layer.model.definition.form_control_tab import FormControlTab
from data_layer.enums import ControlName, EventName

logger = get_logger(__name__)


def _insert_form_controls(session: Session, cashier_id: str):
    """
    Insert initial form controls for login and sale forms.
    
    Args:
        session: Database session
        cashier_id: ID of the cashier creating the records
    """
    # Check if form controls already exist
    if session.query(FormControl).count() > 0:
        return
    
    # Get form IDs
    login_form = session.query(Form).filter(Form.form_no == 1).first()
    main_menu_form = session.query(Form).filter(Form.form_no == 2).first()
    config_form = session.query(Form).filter(Form.form_no == 3).first()
    cashier_form = session.query(Form).filter(Form.form_no == 4).first()
    sale_form = session.query(Form).filter(Form.form_no == 5).first()
    closure_form = session.query(Form).filter(Form.form_no == 6).first()
    suspended_sales_market_form = session.query(Form).filter(Form.form_no == 7).first()
    product_list_form = session.query(Form).filter(Form.form_no == 8).first()
    product_detail_form = session.query(Form).filter(Form.form_no == 9).first()
    closure_detail_form = session.query(Form).filter(Form.form_no == 10).first()
    closure_receipts_form = session.query(Form).filter(Form.form_no == 11).first()
    closure_receipt_detail_form = session.query(Form).filter(Form.form_no == 12).first()
    stock_inquiry_form = session.query(Form).filter(Form.form_no == 13).first()
    stock_in_form = session.query(Form).filter(Form.form_no == 14).first()
    stock_adjustment_form = session.query(Form).filter(Form.form_no == 15).first()
    stock_movement_form = session.query(Form).filter(Form.form_no == 16).first()
    customer_list_form = session.query(Form).filter(Form.form_no == 17).first()
    customer_detail_form = session.query(Form).filter(Form.form_no == 18).first()

    if not login_form or not sale_form or not main_menu_form or not config_form or not cashier_form or not closure_form or not suspended_sales_market_form or not product_list_form:
        logger.warning("Forms not found. Cannot insert form controls.")
        return
    
    # Login form controls
    # Using ControlName and EventName enums for consistency
    login_form_controls = [
        FormControl(
            fk_form_id=login_form.id,
            fk_parent_id=None,
            name=ControlName.CASHIER_NAME_LIST.value,  # Special name for auto-loading cashiers
            form_control_function1=EventName.LOGIN.value,  # Used to add SUPERVISOR option
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
            list_values=None,  # Auto-populated from database
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
            fk_cashier_update_id=cashier_id
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
            fk_cashier_update_id=cashier_id
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
            fk_cashier_update_id=cashier_id
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
            fk_cashier_update_id=cashier_id
        )
    ]
    
    # Sale form controls
    sale_form_controls = [
        FormControl(
            fk_form_id=sale_form.id,
            fk_parent_id=None,
            name="SALESLIST",
            form_control_function1=EventName.SALE_OPTION.value,
            form_control_function2=None,
            type_no=4,
            type="SALESLIST",
            width=769,
            height=250,
            location_x=252,
            location_y=1,
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
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        FormControl(
            fk_form_id=sale_form.id,
            fk_parent_id=None,
            name="NUMPAD",
            form_control_function1=EventName.SALE_PLU_BARCODE.value,
            form_control_function2=None,
            type_no=5,
            type="NUMPAD",
            width=242,
            height=338,
            location_x=779,
            location_y=404,
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
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        FormControl(
            fk_form_id=sale_form.id,
            fk_parent_id=None,
            name="PAYMENTLIST",
            form_control_function1="PAYMENTLIST",  # Custom control, not an event
            form_control_function2=None,
            type_no=6,
            type="PAYMENTLIST",
            width=230,
            height=246,
            location_x=547,
            location_y=404,
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
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        # PLU (inquiry) — left half: price + per-warehouse stock, no sale.
        FormControl(
            fk_form_id=sale_form.id,
            fk_parent_id=None,
            name="PLU_INQUIRY",
            form_control_function1=EventName.PLU_INQUIRY.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=114,
            height=90,
            location_x=547,
            location_y=652,
            start_position=None,
            caption1="PLU",
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
            font_size=18,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0x5CB85C",
            fore_color="0xFFFFFF",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        # X (quantity multiplier) — right half. Commits numpad value as quantity for next sale.
        FormControl(
            fk_form_id=sale_form.id,
            fk_parent_id=None,
            name="QTY_MULTIPLIER",
            form_control_function1=EventName.INPUT_QUANTITY.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=114,
            height=90,
            location_x=663,
            location_y=652,
            start_position=None,
            caption1="X",
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
            font_size=20,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0xFFD700",  # Gold
            fore_color="0x000000",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        FormControl(
            fk_form_id=sale_form.id,
            fk_parent_id=None,
            name="AMOUNTSTABLE",
            form_control_function1="AMOUNTSTABLE",  # Custom control, not an event
            form_control_function2=None,
            type_no=7,
            type="AMOUNTSTABLE",
            width=250,
            height=213,
            location_x=1,
            location_y=1,
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
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        FormControl(
            fk_form_id=sale_form.id,
            fk_parent_id=None,
            name="BACK",
            form_control_function1=EventName.BACK.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=125,
            height=113,
            location_x=1,
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
            tool_tip=None,
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=12,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0xD3D3D3",  # Light Gray
            fore_color="0x000000",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        )
    ]
    
    # Department buttons
    department_buttons = [
        FormControl(
            fk_form_id=sale_form.id,
            fk_parent_id=None,
            name="DEPARTMENT1",
            form_control_function1=EventName.SALE_DEPARTMENT.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=125,
            height=100,
            location_x=1,
            location_y=215,
            start_position=None,
            caption1="FOOD",
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
            font_size=10,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0x98FB98",  # Pale Green
            fore_color="0x000000",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        FormControl(
            fk_form_id=sale_form.id,
            fk_parent_id=None,
            name="DEPARTMENT2",
            form_control_function1=EventName.SALE_DEPARTMENT.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=125,
            height=100,
            location_x=1,
            location_y=316,
            start_position=None,
            caption1="TOBACCO",
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
            font_size=10,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0x98FB98",  # Pale Green
            fore_color="0x000000",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        FormControl(
            fk_form_id=sale_form.id,
            fk_parent_id=None,
            name="DEPARTMENT3",
            form_control_function1=EventName.SALE_DEPARTMENT.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=125,
            height=99,
            location_x=1,
            location_y=417,
            start_position=None,
            caption1="INDIVIDUAL",
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
            font_size=10,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0x98FB98",  # Pale Green
            fore_color="0x000000",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        )
    ]
    
    # PLU buttons
    plu_buttons = [
        FormControl(
            fk_form_id=sale_form.id,
            fk_parent_id=None,
            name="PLU1",
            form_control_function1=EventName.SALE_PLU_CODE.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=125,
            height=100,
            location_x=126,
            location_y=215,
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
            font_size=12,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0xFFE4B5",  # Moccasin
            fore_color="0x000000",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        FormControl(
            fk_form_id=sale_form.id,
            fk_parent_id=None,
            name="PLU2",
            form_control_function1=EventName.SALE_PLU_CODE.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=125,
            height=100,
            location_x=126,
            location_y=316,
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
            font_size=12,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0xFFE4B5",  # Moccasin
            fore_color="0x000000",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        FormControl(
            fk_form_id=sale_form.id,
            fk_parent_id=None,
            name="PLU3",
            form_control_function1=EventName.SALE_PLU_CODE.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=125,
            height=99,
            location_x=126,
            location_y=417,
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
            font_size=12,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0xFFE4B5",  # Moccasin
            fore_color="0x000000",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        )
    ]
    
    # Product barcode buttons
    product_barcode_buttons = [
        ("PLU5000157070008", 252, 252),
        ("PLU7622210449283", 362, 252),
        ("PLU5000328721575", 472, 252),
        ("PLU8711200334532", 582, 252),
        ("PLU5449000000996", 692, 252),
        ("PLU0746817004304", 802, 252),
        ("PLU7622210700394", 912, 252),
        ("PLU5000328355037", 252, 327),
        ("PLU5000157077916", 362, 327),
        ("PLU5010044003089", 472, 327),
        ("PLU5740900802725", 582, 327),
        ("PLU8001090390021", 692, 327),
        ("PLU8714100852703", 802, 327),
        ("PLU5000171054815", 912, 327)
    ]
    
    product_controls = []
    for plu_name, x, y in product_barcode_buttons:
        height = 75 if y == 252 else 76
        product_controls.append(
            FormControl(
                fk_form_id=sale_form.id,
                fk_parent_id=None,
                name=plu_name,
                form_control_function1=EventName.SALE_PLU_BARCODE.value,
                form_control_function2=None,
                type_no=1,
                type="BUTTON",
                width=109,
                height=height,
                location_x=x,
                location_y=y,
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
                font_size=12,
                input_type="ALPHANUMERIC",
                text_image_relation=None,
                back_color="0xFFB6C1",  # Light Pink
                fore_color="0x000000",
                keyboard_value=None,
                fk_cashier_create_id=cashier_id,
                fk_cashier_update_id=cashier_id
            )
        )
    
    # Cash payment buttons
    cash_payment_buttons = [
        FormControl(
            fk_form_id=sale_form.id,
            fk_parent_id=None,
            name="CASH2000",
            form_control_function1=EventName.CASH_PAYMENT.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=144,
            height=83,
            location_x=251,
            location_y=404,
            start_position=None,
            caption1="20 £",
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
            font_size=12,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0x87CEEB",  # Sky Blue
            fore_color="0x000000",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        FormControl(
            fk_form_id=sale_form.id,
            fk_parent_id=None,
            name="CASH5000",
            form_control_function1=EventName.CASH_PAYMENT.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=144,
            height=83,
            location_x=251,
            location_y=487,
            start_position=None,
            caption1="50 £",
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
            font_size=12,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0x87CEEB",  # Sky Blue
            fore_color="0x000000",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        FormControl(
            fk_form_id=sale_form.id,
            fk_parent_id=None,
            name="CASH10000",
            form_control_function1=EventName.CASH_PAYMENT.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=144,
            height=82,
            location_x=251,
            location_y=570,
            start_position=None,
            caption1="100 £",
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
            font_size=12,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0x87CEEB",  # Sky Blue
            fore_color="0x000000",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        # CHANGE payment button — placed where CANCEL used to be
        FormControl(
            fk_form_id=sale_form.id,
            fk_parent_id=None,
            name="CHANGE",
            form_control_function1=EventName.CHANGE_PAYMENT.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=144,
            height=90,
            location_x=251,
            location_y=652,
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
            tool_tip="Calculate and record change amount",
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=14,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0x87CEEB",  # Sky Blue
            fore_color="0x000000",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        FormControl(
            fk_form_id=sale_form.id,
            fk_parent_id=None,
            name="PAYMENT_CASH",
            form_control_function1=EventName.CASH_PAYMENT.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=150,
            height=137,
            location_x=396,
            location_y=404,
            start_position=None,
            caption1="CASH",
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
            font_size=12,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0x90EE90",  # Light Green
            fore_color="0x000000",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        FormControl(
            fk_form_id=sale_form.id,
            fk_parent_id=None,
            name="PAYMENT_CREDIT",
            form_control_function1=EventName.CREDIT_PAYMENT.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=150,
            height=111,
            location_x=396,
            location_y=541,
            start_position=None,
            caption1="CREDIT CARD",
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
            font_size=12,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0xDDA0DD",  # Plum
            fore_color="0x000000",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        # Dual-function SUSPEND/CANCEL button
        # Normal state  (caption1/function1): SUSPEND — suspend the current sale
        # Alternate state (caption2/function2): CANCEL  — cancel the current document
        # The FUNC button toggles between the two states for all dual-function buttons.
        FormControl(
            fk_form_id=sale_form.id,
            fk_parent_id=None,
            name="PAYMENT_SUSPEND",
            form_control_function1=EventName.SUSPEND_SALE.value,
            form_control_function2=EventName.CANCEL_DOCUMENT.value,
            type_no=1,
            type="BUTTON",
            width=150,
            height=90,
            location_x=396,
            location_y=652,
            start_position=None,
            caption1="SUSPEND",
            caption2="CANCEL",
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            icon=None,
            tool_tip="Suspend current sale (FUNC: Cancel document)",
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=14,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0xFF8C00",  # DarkOrange
            fore_color="0x000000",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        # FUNC mode-toggle button — pressing this switches all dual-function buttons
        # on the form between their first (normal) and second (alternate) function.
        # This button has no event of its own; it is handled specially by the renderer.
        FormControl(
            fk_form_id=sale_form.id,
            fk_parent_id=None,
            name="FUNC",
            form_control_function1=None,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=125,
            height=113,
            location_x=126,
            location_y=630,
            start_position=None,
            caption1="FUNC",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            icon=None,
            tool_tip="Switch dual-function buttons to their alternate function",
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=14,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0x4682B4",  # Steel Blue
            fore_color="0xFFFFFF",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        FormControl(
            fk_form_id=sale_form.id,
            fk_parent_id=None,
            name="SUBTOTAL",
            form_control_function1=EventName.SUBTOTAL.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=250,
            height=113,
            location_x=1,
            location_y=517,
            start_position=None,
            caption1="SUB TOTAL",
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
            font_size=12,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0x2F4F4F",  # Dark Slate Gray
            fore_color="0xFFFFFF",  # White
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        )
    ]
    
    # Main Menu form controls
    # Layout (1024x768): 7 main buttons centred at x=312 w=400, spacing=90px
    # Row 1 SALES       y=70   h=80
    # Row 2 CLOSURE     y=160  h=80
    # Row 3 SETTINGS    y=250  h=80
    # Row 4 CASHIER     y=340  h=80
    # Row 5 PRODUCTS(half) + WAREHOUSE(half)  y=430  h=75
    # Row 6 CUSTOMER    y=515  h=75
    # LOGOUT bottom-right corner  y=630  h=99
    main_menu_form_controls = [
        FormControl(
            fk_form_id=main_menu_form.id,
            fk_parent_id=None,
            name="GOTO_SALE",
            form_control_function1=EventName.SALES_FORM.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=400,
            height=80,
            location_x=312,
            location_y=70,
            start_position=None,
            caption1="SALES",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            icon=None,
            tool_tip="Go to Sales Form",
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=16,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0x228B22",
            fore_color="0xFFFFFF",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        FormControl(
            fk_form_id=main_menu_form.id,
            fk_parent_id=None,
            name="GOTO_CLOSURE",
            form_control_function1=EventName.CLOSURE_FORM.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=400,
            height=80,
            location_x=312,
            location_y=160,
            start_position=None,
            caption1="CLOSURE",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            icon=None,
            tool_tip="Go to Closure Form",
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=16,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0xDC143C",  # Crimson - distinctive color for closure operation
            fore_color="0xFFFFFF",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        FormControl(
            fk_form_id=main_menu_form.id,
            fk_parent_id=None,
            name="GOTO_CONFIG",
            form_control_function1=EventName.SETTING_FORM.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=400,
            height=80,
            location_x=312,
            location_y=250,
            start_position=None,
            caption1="SETTINGS",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            icon=None,
            tool_tip="Go to Settings Form",
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=16,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0x4682B4",
            fore_color="0xFFFFFF",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        FormControl(
            fk_form_id=main_menu_form.id,
            fk_parent_id=None,
            name="GOTO_CASHIER",
            form_control_function1=EventName.CASHIER_FORM.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=400,
            height=80,
            location_x=312,
            location_y=340,
            start_position=None,
            caption1="CASHIER MANAGEMENT",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            icon=None,
            tool_tip="Go to Cashier Management Form",
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=16,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0xFF8C00",
            fore_color="0xFFFFFF",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        FormControl(
            fk_form_id=main_menu_form.id,
            fk_parent_id=None,
            name="GOTO_PRODUCTS",
            form_control_function1=EventName.PRODUCT_LIST_FORM.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=195,
            height=75,
            location_x=312,
            location_y=430,
            start_position=None,
            caption1="PRODUCTS",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            icon=None,
            tool_tip="Go to Product List",
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=14,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0x8B0000",
            fore_color="0xFFFFFF",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        FormControl(
            fk_form_id=main_menu_form.id,
            fk_parent_id=None,
            name="GOTO_WAREHOUSE",
            form_control_function1=EventName.STOCK_INQUIRY.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=195,
            height=75,
            location_x=517,
            location_y=430,
            start_position=None,
            caption1="WAREHOUSE",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            icon=None,
            tool_tip="Open Warehouse / Inventory Management",
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=14,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0x1A5276",
            fore_color="0xFFFFFF",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        FormControl(
            fk_form_id=main_menu_form.id,
            fk_parent_id=None,
            name="GOTO_CUSTOMER",
            form_control_function1=EventName.CUSTOMER_LIST_FORM.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=400,
            height=75,
            location_x=312,
            location_y=515,
            start_position=None,
            caption1="CUSTOMER",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            icon=None,
            tool_tip="Open Customer Management",
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=16,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0x7D3C98",
            fore_color="0xFFFFFF",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        FormControl(
            fk_form_id=main_menu_form.id,
            fk_parent_id=None,
            name=ControlName.LOGOUT.value,
            form_control_function1=EventName.LOGOUT.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=125,
            height=99,
            location_x=880,
            location_y=630,
            start_position=None,
            caption1="LOGOUT",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            icon=None,
            tool_tip="Exit current user session",
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=12,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0x4682B4",
            fore_color="0xFFFFFF",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        )
    ]
    
    # Configuration form controls
    # First create the Panel control (name matches model name)
    config_panel = FormControl(
        fk_form_id=config_form.id,
        fk_parent_id=None,
        name="POS_SETTINGS",  # Model name in uppercase
        form_control_function1=None,
        form_control_function2=None,
        type_no=10,  # New type number for Panel
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
        fk_cashier_update_id=cashier_id
    )
    
    # Store panel ID for child controls (will be set after panel is added to session)
    # For now, we'll use a placeholder and update after panel creation
    config_panel_id_placeholder = None  # Will be set after panel is created
    
    # PosSettings field controls - all will be children of the panel
    # Field definitions with labels and field names (field names match model attributes)
    pos_settings_fields = [
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
    
    # Create label and textbox pairs for each field
    pos_settings_controls = []
    start_y = 20  # Starting Y position inside panel
    label_width = 200
    textbox_width = 400
    control_height = 40
    spacing = 10
    row_height = control_height + spacing
    
    for i, (label_text, field_name, input_type) in enumerate(pos_settings_fields):
        y_pos = start_y + (i * row_height)
        
        # Label
        label_control = FormControl(
            fk_form_id=config_form.id,
            fk_parent_id=None,  # Will be set to panel ID after panel is created
            parent_name="POS_SETTINGS",  # Panel name matches model name
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
            fk_cashier_update_id=cashier_id
        )
        pos_settings_controls.append(label_control)
        
        # TextBox or CheckBox — name uppercase maps to model attribute via .lower()
        if input_type == "CHECKBOX":
            field_control = FormControl(
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
                fk_cashier_update_id=cashier_id
            )
        else:
            field_control = FormControl(
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
                fk_cashier_update_id=cashier_id
            )
        pos_settings_controls.append(field_control)
    
    # SAVE button (outside panel)
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
        back_color="0x228B22",  # Forest Green for save action
        fore_color="0xFFFFFF",
        keyboard_value=None,
        fk_cashier_create_id=cashier_id,
        fk_cashier_update_id=cashier_id
    )
    
    # BACK button (outside panel)
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
        fk_cashier_update_id=cashier_id
    )
    
    # Combine all config form controls
    config_form_controls = [config_panel] + pos_settings_controls + [save_button, back_button]
    
    # After panel is added to session, update child controls' fk_parent_id
    # Note: This will be done after adding to session and committing to get the panel ID
    
    # Cashier form controls

    # First create the Panel control (name matches model name)
    cashier_panel = FormControl(
        fk_form_id=cashier_form.id,
        fk_parent_id=None,
        name="CASHIER",  # Model name in uppercase
        form_control_function1=None,
        form_control_function2=None,
        type_no=10,  # Panel type
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
        fk_cashier_update_id=cashier_id
    )

    # Create label and textbox pairs for each field
    cashier_controls = []

    # Cashier selection combobox (admin only - populated and shown dynamically at runtime)
    cashier_mgmt_list = FormControl(
        fk_form_id=cashier_form.id,
        fk_parent_id=None,  # Will be set to panel ID after panel is created
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
        fk_cashier_update_id=cashier_id
    )
    cashier_controls.append(cashier_mgmt_list)

    # ADD NEW CASHIER button (admin only - shown/hidden dynamically at runtime)
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
        back_color="0x8B4513",  # SaddleBrown - distinct admin action color
        fore_color="0xFFFFFF",
        keyboard_value=None,
        fk_cashier_create_id=cashier_id,
        fk_cashier_update_id=cashier_id
    )

    # Cashier field controls - all will be children of the panel
    # Field definitions with labels and field names (field names match model attributes)
    cashier_fields = [
        ("No", "no", "NUMERIC"),
        ("Username", "user_name", "ALPHANUMERIC"),
        ("Name", "name", "ALPHANUMERIC"),
        ("Last Name", "last_name", "ALPHANUMERIC"),
        ("Password", "password", "PASSWORD"),
        ("Identity Number", "identity_number", "ALPHANUMERIC"),
        ("Description", "description", "ALPHANUMERIC"),
        ("Is Administrator", "is_administrator", "CHECKBOX"),
        ("Is Active", "is_active", "CHECKBOX"),
    ]
    
    start_y = 70  # Starting Y position inside panel
    label_width = 200
    textbox_width = 400
    control_height = 40
    spacing = 10
    row_height = control_height + spacing
    
    for i, (label_text, field_name, input_type) in enumerate(cashier_fields):
        y_pos = start_y + (i * row_height)
        
        # Label
        label_control = FormControl(
            fk_form_id=cashier_form.id,
            fk_parent_id=None,  # Will be set to panel ID after panel is created
            parent_name="CASHIER",  # Panel name matches model name
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
            fk_cashier_update_id=cashier_id
        )
        cashier_controls.append(label_control)
        
        if input_type == "CHECKBOX":
            field_control = FormControl(
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
                fk_cashier_update_id=cashier_id
            )
        else:
            field_control = FormControl(
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
                fk_cashier_update_id=cashier_id
            )
        cashier_controls.append(field_control)
    
    # SAVE button (outside panel)
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
        back_color="0x228B22",  # Forest Green for save action
        fore_color="0xFFFFFF",
        keyboard_value=None,
        fk_cashier_create_id=cashier_id,
        fk_cashier_update_id=cashier_id
    )
    
    # BACK button (outside panel)
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
        fk_cashier_update_id=cashier_id
    )
    
    # Combine all cashier form controls
    cashier_form_controls = [cashier_mgmt_list, add_new_cashier_button, cashier_panel] + cashier_controls + [save_button, back_button]
    
    # Closure form controls
    closure_form_controls = [
        # DataGrid to display previous closures (selectable for DETAIL / RECEIPTS)
        FormControl(
            fk_form_id=closure_form.id,
            fk_parent_id=None,
            name=ControlName.CLOSURE.value,
            form_control_function1=EventName.NONE.value,
            form_control_function2=None,
            type_no=9,
            type="DATAGRID",
            width=900,
            height=400,
            location_x=62,
            location_y=50,
            start_position=None,
            caption1="Closure History",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="NORMAL",
            font="Tahoma",
            icon=None,
            tool_tip="Select a closure to view details or its receipts",
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=10,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0xFFFFFF",
            fore_color="0x000000",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        # Closure button (execute closure operation)
        FormControl(
            fk_form_id=closure_form.id,
            fk_parent_id=None,
            name=ControlName.CLOSURE.value,
            form_control_function1=EventName.CLOSURE.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=400,
            height=80,
            location_x=312,
            location_y=480,
            start_position=None,
            caption1="CLOSURE",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            icon=None,
            tool_tip="Execute closure operation",
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
            fk_cashier_update_id=cashier_id
        ),
        # DETAIL button – bottom-left: open closure detail form for the selected closure
        FormControl(
            fk_form_id=closure_form.id,
            fk_parent_id=None,
            name="CLOSURE_DETAIL",
            form_control_function1=EventName.CLOSURE_DETAIL_FORM.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=200,
            height=99,
            location_x=62,
            location_y=630,
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
            tool_tip="View details of the selected closure",
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=14,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0x2E8B57",
            fore_color="0xFFFFFF",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        # RECEIPTS button – right of DETAIL: open receipts list for the selected closure
        FormControl(
            fk_form_id=closure_form.id,
            fk_parent_id=None,
            name="CLOSURE_RECEIPTS",
            form_control_function1=EventName.CLOSURE_RECEIPTS_FORM.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=200,
            height=99,
            location_x=280,
            location_y=630,
            start_position=None,
            caption1="RECEIPTS",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            icon=None,
            tool_tip="View receipts of the selected closure",
            image=None,
            image_selected=None,
            font_auto_height=False,
            font_size=14,
            input_type="ALPHANUMERIC",
            text_image_relation=None,
            back_color="0x4169E1",
            fore_color="0xFFFFFF",
            keyboard_value=None,
            fk_cashier_create_id=cashier_id,
            fk_cashier_update_id=cashier_id
        ),
        # BACK button – bottom-right
        FormControl(
            fk_form_id=closure_form.id,
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
            fk_cashier_update_id=cashier_id
        )
    ]

    # ------------------------------------------------------------------ #
    # CLOSURE_DETAIL form controls                                         #
    # ------------------------------------------------------------------ #
    closure_detail_form_controls = []
    if closure_detail_form:
        closure_detail_form_controls = [
            # Key/value DataGrid showing closure summary fields
            FormControl(
                fk_form_id=closure_detail_form.id,
                fk_parent_id=None,
                name=ControlName.CLOSURE_DETAIL_GRID.value,
                form_control_function1=EventName.NONE.value,
                form_control_function2=None,
                type_no=9,
                type="DATAGRID",
                width=900,
                height=560,
                location_x=62,
                location_y=50,
                start_position=None,
                caption1="Closure Details",
                caption2=None,
                list_values=None,
                dock=None,
                alignment=None,
                text_alignment="LEFT",
                character_casing="NORMAL",
                font="Tahoma",
                icon=None,
                tool_tip="Detailed summary of the selected closure",
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
                fk_cashier_update_id=cashier_id
            ),
            # BACK button – bottom-right
            FormControl(
                fk_form_id=closure_detail_form.id,
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
                tool_tip="Back to Closure List",
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
                fk_cashier_update_id=cashier_id
            ),
        ]

    # ------------------------------------------------------------------ #
    # CLOSURE_RECEIPTS form controls                                       #
    # ------------------------------------------------------------------ #
    closure_receipts_form_controls = []
    if closure_receipts_form:
        closure_receipts_form_controls = [
            # DataGrid listing receipts that belong to the selected closure
            FormControl(
                fk_form_id=closure_receipts_form.id,
                fk_parent_id=None,
                name=ControlName.CLOSURE_RECEIPTS_DATAGRID.value,
                form_control_function1=EventName.NONE.value,
                form_control_function2=None,
                type_no=9,
                type="DATAGRID",
                width=900,
                height=480,
                location_x=62,
                location_y=50,
                start_position=None,
                caption1="Closure Receipts",
                caption2=None,
                list_values=None,
                dock=None,
                alignment=None,
                text_alignment="CENTER",
                character_casing="NORMAL",
                font="Tahoma",
                icon=None,
                tool_tip="Select a receipt to view its details",
                image=None,
                image_selected=None,
                font_auto_height=False,
                font_size=10,
                input_type="ALPHANUMERIC",
                text_image_relation=None,
                back_color="0xFFFFFF",
                fore_color="0x000000",
                keyboard_value=None,
                fk_cashier_create_id=cashier_id,
                fk_cashier_update_id=cashier_id
            ),
            # DETAIL button – bottom-left: open receipt detail form
            FormControl(
                fk_form_id=closure_receipts_form.id,
                fk_parent_id=None,
                name="RECEIPT_DETAIL",
                form_control_function1=EventName.CLOSURE_RECEIPT_DETAIL_FORM.value,
                form_control_function2=None,
                type_no=1,
                type="BUTTON",
                width=200,
                height=99,
                location_x=62,
                location_y=630,
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
                tool_tip="View details of the selected receipt",
                image=None,
                image_selected=None,
                font_auto_height=False,
                font_size=14,
                input_type="ALPHANUMERIC",
                text_image_relation=None,
                back_color="0x2E8B57",
                fore_color="0xFFFFFF",
                keyboard_value=None,
                fk_cashier_create_id=cashier_id,
                fk_cashier_update_id=cashier_id
            ),
            # BACK button – bottom-right
            FormControl(
                fk_form_id=closure_receipts_form.id,
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
                tool_tip="Back to Closure List",
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
                fk_cashier_update_id=cashier_id
            ),
        ]

    # ------------------------------------------------------------------ #
    # CLOSURE_RECEIPT_DETAIL form controls                                 #
    # ------------------------------------------------------------------ #
    closure_receipt_detail_form_controls = []
    if closure_receipt_detail_form:
        closure_receipt_detail_form_controls = [
            # Upper DataGrid – key/value receipt header information
            FormControl(
                fk_form_id=closure_receipt_detail_form.id,
                fk_parent_id=None,
                name=ControlName.CLOSURE_RECEIPT_DETAIL_GRID.value,
                form_control_function1=EventName.NONE.value,
                form_control_function2=None,
                type_no=9,
                type="DATAGRID",
                width=900,
                height=250,
                location_x=62,
                location_y=50,
                start_position=None,
                caption1="Receipt Info",
                caption2=None,
                list_values=None,
                dock=None,
                alignment=None,
                text_alignment="LEFT",
                character_casing="NORMAL",
                font="Tahoma",
                icon=None,
                tool_tip="General information about the selected receipt",
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
                fk_cashier_update_id=cashier_id
            ),
            # Lower DataGrid – sold items / line products of the receipt
            FormControl(
                fk_form_id=closure_receipt_detail_form.id,
                fk_parent_id=None,
                name=ControlName.CLOSURE_RECEIPT_ITEMS_GRID.value,
                form_control_function1=EventName.NONE.value,
                form_control_function2=None,
                type_no=9,
                type="DATAGRID",
                width=900,
                height=295,
                location_x=62,
                location_y=318,
                start_position=None,
                caption1="Items",
                caption2=None,
                list_values=None,
                dock=None,
                alignment=None,
                text_alignment="CENTER",
                character_casing="NORMAL",
                font="Tahoma",
                icon=None,
                tool_tip="Products / items sold in this receipt",
                image=None,
                image_selected=None,
                font_auto_height=False,
                font_size=10,
                input_type="ALPHANUMERIC",
                text_image_relation=None,
                back_color="0xF8F8FF",
                fore_color="0x000000",
                keyboard_value=None,
                fk_cashier_create_id=cashier_id,
                fk_cashier_update_id=cashier_id
            ),
            # BACK button – bottom-right
            FormControl(
                fk_form_id=closure_receipt_detail_form.id,
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
                tool_tip="Back to Receipts List",
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
                fk_cashier_update_id=cashier_id
            ),
        ]

    # Suspended sales list (market sector) — receipt no, line count, total
    suspended_sales_market_controls = [
        FormControl(
            fk_form_id=suspended_sales_market_form.id,
            fk_parent_id=None,
            name=ControlName.SUSPENDED_SALES_DATAGRID.value,
            form_control_function1=EventName.NONE.value,
            form_control_function2=None,
            type_no=9,
            type="DATAGRID",
            width=900,
            height=520,
            location_x=62,
            location_y=50,
            start_position=None,
            caption1="Suspended receipts",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="NORMAL",
            font="Tahoma",
            icon=None,
            tool_tip="Pending suspended sale documents",
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
            fk_cashier_update_id=cashier_id
        ),
        FormControl(
            fk_form_id=suspended_sales_market_form.id,
            fk_parent_id=None,
            name="ACTIVATE_SUSPENDED",
            form_control_function1=EventName.RESUME_SALE.value,
            form_control_function2=None,
            type_no=1,
            type="BUTTON",
            width=200,
            height=99,
            location_x=62,
            location_y=630,
            start_position=None,
            caption1="ACTIVATE",
            caption2=None,
            list_values=None,
            dock=None,
            alignment=None,
            text_alignment="CENTER",
            character_casing="UPPER",
            font="Tahoma",
            icon=None,
            tool_tip="Resume selected suspended sale on the register",
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
            fk_cashier_update_id=cashier_id
        ),
        FormControl(
            fk_form_id=suspended_sales_market_form.id,
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
            fk_cashier_update_id=cashier_id
        ),
    ]
    
    # ------------------------------------------------------------------ #
    #  Product List form controls  (form_no = 8)                         #
    # ------------------------------------------------------------------ #
    # Layout (1024 x 768):
    #   y=10   : Search textbox  (x=10, w=820, h=50)
    #   y=10   : Search button   (x=840, w=170, h=50)
    #   y=75   : DataGrid        (x=10, w=1000, h=570)
    #   y=660  : Back button     (x=10, w=150, h=65)
    #   y=660  : Detail button   (x=860, w=150, h=65)
    product_list_form_controls = [
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
            fk_cashier_update_id=cashier_id
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
            fk_cashier_update_id=cashier_id
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
            fk_cashier_update_id=cashier_id
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
            fk_cashier_update_id=cashier_id
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
            fk_cashier_update_id=cashier_id
        ),
    ]  # STOCK_INQUIRY_BTN removed: now accessed via WAREHOUSE button on main menu

    # ------------------------------------------------------------------ #
    #  Customer List form controls  (form_no = 17)                       #
    # ------------------------------------------------------------------ #
    # Layout (1024 x 768):
    #   y=10  : Search textbox  (x=10, w=820, h=50)
    #   y=10  : Search button   (x=840, w=170, h=50)
    #   y=75  : DataGrid        (x=10, w=1000, h=555)
    #   y=650 : Back button     (x=860, w=150, h=65)
    #   y=650 : Detail button   (x=10,  w=150, h=65)
    customer_list_form_controls = [
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
            fk_cashier_update_id=cashier_id
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
            fk_cashier_update_id=cashier_id
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
            fk_cashier_update_id=cashier_id
        ),
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
            fk_cashier_update_id=cashier_id
        ),
        FormControl(
            fk_form_id=customer_list_form.id,
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
            tool_tip="Return to main menu",
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
            fk_cashier_update_id=cashier_id
        ),
    ]

    # Combine all controls
    all_controls = (
        login_form_controls + 
        sale_form_controls + 
        department_buttons + 
        plu_buttons + 
        product_controls + 
        cash_payment_buttons +
        main_menu_form_controls +
        config_form_controls +
        cashier_form_controls +
        closure_form_controls +
        suspended_sales_market_controls +
        product_list_form_controls +
        customer_list_form_controls +
        closure_detail_form_controls +
        closure_receipts_form_controls +
        closure_receipt_detail_form_controls
    )
    # Note: inventory form controls are added after the first flush (see below)
    
    # Add all controls to session
    for control in all_controls:
        session.add(control)
    
    # Flush to get IDs for parent-child relationships
    session.flush()
    
    # Update parent IDs for config form panel children
    # Find the panel control
    config_panel_control = None
    for control in config_form_controls:
        if control.type == "PANEL" and control.name == "POS_SETTINGS":
            config_panel_control = control
            break
    
    if config_panel_control:
        # Update all child controls to reference the panel
        for control in pos_settings_controls:
            if control.parent_name == "POS_SETTINGS":
                control.fk_parent_id = config_panel_control.id
    
    # Update parent IDs for cashier form panel children
    # Find the panel control
    cashier_panel_control = None
    for control in cashier_form_controls:
        if control.type == "PANEL" and control.name == "CASHIER":
            cashier_panel_control = control
            break
    
    if cashier_panel_control:
        # Update all child controls to reference the panel
        for control in cashier_controls:
            if control.parent_name == "CASHIER":
                control.fk_parent_id = cashier_panel_control.id

    # ------------------------------------------------------------------ #
    # PRODUCT_DETAIL form: TABCONTROL + FormControlTab pages              #
    # Tab 0 (Product Info): PANEL with label/textbox pairs (editable)     #
    # Tabs 1-3: DATAGRIDs for barcodes, attributes, variants              #
    # SAVE + BACK buttons at bottom (outside tabs)                        #
    # These must be inserted after the first flush so UUIDs are available. #
    # ------------------------------------------------------------------ #
    if product_detail_form:
        # 1. Create the TABCONTROL that fills most of the 1004×694 dialog area
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
        session.flush()  # obtain pd_tab_control.id

        # 2. Create FormControlTab records (one per tab page)
        _tab_defs = [
            (0, "Product Info",  "Basic product information, unit and manufacturer"),
            (1, "Barcodes",      "Barcodes assigned to this product"),
            (2, "Attributes",    "Custom attributes / features of this product"),
            (3, "Variants",      "Product variants (colour, size, etc.)"),
        ]
        tab_records = []
        for tab_index, tab_title, tab_tooltip in _tab_defs:
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
        session.flush()  # obtain tab UUIDs

        # 3a. Create PANEL named "PRODUCT" inside Tab 0 (Product Info)
        #     Panel name "PRODUCT" maps to the Product model for data loading.
        #     fk_parent_id = pd_tab_control.id  →  renderer sees it as a tab-child panel
        #     fk_tab_id    = tab_records[0].id  →  places panel inside tab page 0
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
        session.flush()  # obtain product_panel.id for child controls

        # 3b. Create label/textbox pairs inside the PRODUCT panel
        #     Field names (lowercase) must match Product model attributes exactly.
        #     Control names (uppercase) are used by _create_textbox to load field values.
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

        _pd_label_width  = 200
        _pd_field_width  = 560
        _pd_ctrl_height  = 40
        _pd_spacing      = 10
        _pd_row_height   = _pd_ctrl_height + _pd_spacing
        _pd_start_y      = 20

        product_panel_controls = []
        for i, (lbl_text, field_name, input_type) in enumerate(product_info_fields):
            y_pos = _pd_start_y + (i * _pd_row_height)

            label_ctrl = FormControl(
                fk_form_id=product_detail_form.id,
                fk_parent_id=product_panel.id,
                parent_name="PRODUCT",
                name=f"LBL_{field_name.upper()}",
                form_control_function1=EventName.NONE.value,
                form_control_function2=None,
                type_no=8,
                type="LABEL",
                width=_pd_label_width,
                height=_pd_ctrl_height,
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
            )
            product_panel_controls.append(label_ctrl)

            field_ctrl = FormControl(
                fk_form_id=product_detail_form.id,
                fk_parent_id=product_panel.id,
                parent_name="PRODUCT",
                name=field_name.upper(),
                form_control_function1=EventName.NONE.value,
                form_control_function2=None,
                type_no=2,
                type="TEXTBOX",
                width=_pd_field_width,
                height=_pd_ctrl_height,
                location_x=_pd_label_width + 20,
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
            )
            product_panel_controls.append(field_ctrl)

        for ctrl in product_panel_controls:
            session.add(ctrl)

        # 3c. Create DATAGRIDs for tabs 1, 2, 3 (Barcodes, Attributes, Variants)
        _grid_defs = [
            (ControlName.PRODUCT_BARCODE_GRID.value,   tab_records[1], "Product barcodes"),
            (ControlName.PRODUCT_ATTRIBUTE_GRID.value, tab_records[2], "Product attributes"),
            (ControlName.PRODUCT_VARIANT_GRID.value,   tab_records[3], "Product variants"),
        ]
        for grid_name, tab_rec, tooltip in _grid_defs:
            grid_ctrl = FormControl(
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
            )
            session.add(grid_ctrl)

        # 4. SAVE button — saves changes from the PRODUCT panel to the database
        save_detail_btn = FormControl(
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
        )
        session.add(save_detail_btn)

        # 5. BACK button — closes the dialog (right side, no data loss)
        back_detail_btn = FormControl(
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
        )
        session.add(back_detail_btn)
        session.flush()

    # ------------------------------------------------------------------ #
    #  Inventory forms: STOCK_INQUIRY, STOCK_IN, STOCK_ADJUSTMENT,        #
    #  STOCK_MOVEMENT  (form_no 13–16)                                    #
    # ------------------------------------------------------------------ #

    def _make_inventory_controls(form, confirm_event, confirm_caption, confirm_color,
                                 grid_name, search_event, has_secondary_grid=False,
                                 secondary_grid_name=None, show_qty=False, show_reason=False):
        """Helper: generate controls list for an inventory form."""
        controls = [
            # Search textbox
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
            # Search button
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

        # Main DataGrid
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

        current_y = 75 + main_grid_height + 10  # y after main grid

        # Optional secondary DataGrid
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

        # Optional Quantity textbox
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

        # Optional Reason textbox
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

        # BACK button
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

        # Optional CONFIRM button
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

    if stock_inquiry_form:
        for ctrl in _make_inventory_controls(
            form=stock_inquiry_form,
            confirm_event=EventName.STOCK_DETAIL.value,
            confirm_caption="DETAIL",
            confirm_color="0x8B4513",
            grid_name=ControlName.STOCK_INQUIRY_DATAGRID.value,
            search_event=EventName.STOCK_SEARCH.value,
            has_secondary_grid=True,
            secondary_grid_name=ControlName.STOCK_DETAIL_DATAGRID.value,
        ):
            session.add(ctrl)

        # Navigation buttons: STOCK IN / ADJUSTMENT / HISTORY
        _nav_buttons = [
            ("STOCK_IN_NAV_BTN",  "STOCK IN",   EventName.STOCK_IN.value,         205, "0x1E8449", "Go to Goods Receipt (Stock-In) form"),
            ("STOCK_ADJ_NAV_BTN", "ADJUSTMENT", EventName.STOCK_ADJUSTMENT.value, 400, "0xB7950B", "Go to Manual Stock Adjustment form"),
            ("STOCK_MOV_NAV_BTN", "HISTORY",    EventName.STOCK_MOVEMENT.value,   595, "0x1A7A7A", "Go to Stock Movement History form"),
        ]
        for btn_name, caption, event, loc_x, color, tip in _nav_buttons:
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
            confirm_event=None,
            confirm_caption=None,
            confirm_color=None,
            grid_name=ControlName.STOCK_MOVEMENT_DATAGRID.value,
            search_event=EventName.STOCK_MOVEMENT_SEARCH.value,
        ):
            session.add(ctrl)

    # ------------------------------------------------------------------ #
    # CUSTOMER_DETAIL form: TABCONTROL + FormControlTab pages             #
    # Tab 0 (Customer Info):    PANEL with label/textbox pairs (editable) #
    # Tab 1 (Activity History): DATAGRID with transaction history         #
    # SAVE + BACK buttons at bottom (outside tabs)                        #
    # ------------------------------------------------------------------ #
    if customer_detail_form:
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

        _cd_tab_defs = [
            (0, "Customer Info",      "Personal details and contact information"),
            (1, "Activity History",   "Transaction history for this customer"),
        ]
        cd_tab_records = []
        for tab_index, tab_title, tab_tooltip in _cd_tab_defs:
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

        # Tab 0 – PANEL named "CUSTOMER" maps to the Customer model
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

        # Field definitions: (label_text, field_name, input_type)
        customer_info_fields = [
            ("First Name",    "name",           "ALPHANUMERIC"),
            ("Last Name",     "last_name",      "ALPHANUMERIC"),
            ("Phone",         "phone_number",   "ALPHANUMERIC"),
            ("E-mail",        "email_address",  "ALPHANUMERIC"),
            ("Address 1",     "address_line_1", "ALPHANUMERIC"),
            ("Address 2",     "address_line_2", "ALPHANUMERIC"),
            ("City / Area",   "address_line_3", "ALPHANUMERIC"),
            ("Post Code",     "zip_code",       "ALPHANUMERIC"),
            ("Description",   "description",    "ALPHANUMERIC"),
        ]

        _cd_label_width  = 200
        _cd_field_width  = 560
        _cd_ctrl_height  = 40
        _cd_spacing      = 8
        _cd_row_height   = _cd_ctrl_height + _cd_spacing
        _cd_start_y      = 15

        cd_panel_controls = []
        for i, (lbl_text, field_name, input_type) in enumerate(customer_info_fields):
            y_pos = _cd_start_y + (i * _cd_row_height)

            label_ctrl = FormControl(
                fk_form_id=customer_detail_form.id,
                fk_parent_id=customer_panel.id,
                parent_name="CUSTOMER",
                name=f"LBL_{field_name.upper()}",
                form_control_function1=EventName.NONE.value,
                form_control_function2=None,
                type_no=8,
                type="LABEL",
                width=_cd_label_width,
                height=_cd_ctrl_height,
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
            )
            cd_panel_controls.append(label_ctrl)

            field_ctrl = FormControl(
                fk_form_id=customer_detail_form.id,
                fk_parent_id=customer_panel.id,
                parent_name="CUSTOMER",
                name=field_name.upper(),
                form_control_function1=EventName.NONE.value,
                form_control_function2=None,
                type_no=2,
                type="TEXTBOX",
                width=_cd_field_width,
                height=_cd_ctrl_height,
                location_x=_cd_label_width + 20,
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
            )
            cd_panel_controls.append(field_ctrl)

        for ctrl in cd_panel_controls:
            session.add(ctrl)

        # Tab 1 – DATAGRID for activity / transaction history
        activity_grid = FormControl(
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
        )
        session.add(activity_grid)

        # SAVE button
        cd_save_btn = FormControl(
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
        )
        session.add(cd_save_btn)

        # BACK / CLOSE button
        cd_back_btn = FormControl(
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
        )
        session.add(cd_back_btn)
        session.flush()

    session.commit()
    logger.info("%s form controls inserted successfully", len(all_controls)) 