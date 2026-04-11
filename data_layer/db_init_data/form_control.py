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

# Thin orchestrator — delegates form-control creation to topic-based sub-modules
# under data_layer/db_init_data/forms/.
#
# Insertion strategy
# ──────────────────
# Phase 1 – Bulk insert (simple list-based controls):
#   All controls whose fk_parent_id does not depend on a freshly-assigned UUID
#   are collected into a single list and added to the session together.
#
# Phase 2 – Parent-ID wiring (after first flush):
#   Panel children whose fk_parent_id must reference the panel's DB-assigned UUID
#   are updated now that the flush has populated those IDs.
#
# Phase 3 – Tab-based forms (after first flush):
#   Forms that use TABCONTROL + FormControlTab (PRODUCT_DETAIL, CUSTOMER_DETAIL)
#   and inventory forms use their own session.flush() calls internally.

from sqlalchemy.orm import Session

from core.logger import get_logger
from data_layer.model.definition.form import Form
from data_layer.model.definition.form_control import FormControl

from data_layer.db_init_data.forms import login
from data_layer.db_init_data.forms import main_menu
from data_layer.db_init_data.forms import management
from data_layer.db_init_data.forms import setting_form
from data_layer.db_init_data.forms import sale
from data_layer.db_init_data.forms import closure
from data_layer.db_init_data.forms import product
from data_layer.db_init_data.forms import stock
from data_layer.db_init_data.forms import customer
from data_layer.db_init_data.forms import payment_screen
from data_layer.db_init_data.forms import campaign_management

logger = get_logger(__name__)


def _insert_form_controls(session: Session, cashier_id: str):
    """Insert all default form controls if the FormControl table is empty."""
    if session.query(FormControl).count() > 0:
        return

    # ── Load form objects by form_no ─────────────────────────────────────────
    def _form(no):
        return session.query(Form).filter(Form.form_no == no).first()

    login_form                  = _form(1)
    main_menu_form              = _form(2)
    config_form                 = _form(3)
    cashier_form                = _form(4)
    sale_form                   = _form(5)
    closure_form                = _form(6)
    suspended_sales_market_form = _form(7)
    product_list_form           = _form(8)
    product_detail_form         = _form(9)
    closure_detail_form         = _form(10)
    closure_receipts_form       = _form(11)
    closure_receipt_detail_form = _form(12)
    stock_inquiry_form          = _form(13)
    stock_in_form               = _form(14)
    stock_adjustment_form       = _form(15)
    stock_movement_form         = _form(16)
    customer_list_form          = _form(17)
    customer_detail_form        = _form(18)
    customer_select_form        = _form(19)
    payment_form                = _form(20)
    campaign_list_form          = _form(21)
    campaign_detail_form        = _form(22)
    pos_settings_form           = _form(23)
    loyalty_settings_form       = _form(24)

    required = [
        login_form,
        main_menu_form,
        config_form,
        cashier_form,
        sale_form,
        closure_form,
        suspended_sales_market_form,
        product_list_form,
        pos_settings_form,
        loyalty_settings_form,
    ]
    if not all(required):
        logger.warning("One or more required forms not found. Cannot insert form controls.")
        return

    # ── Phase 1: Collect simple (non-tab) controls ───────────────────────────
    cashier_controls, cashier_panel_children = management.get_cashier_form_controls(
        cashier_form, cashier_id
    )

    all_controls = (
        login.get_form_controls(login_form, cashier_id)
        + sale.get_sale_form_controls(sale_form, cashier_id)
        + main_menu.get_form_controls(main_menu_form, cashier_id)
        + cashier_controls
        + closure.get_closure_form_controls(closure_form, cashier_id)
        + closure.get_closure_detail_form_controls(closure_detail_form, cashier_id)
        + closure.get_closure_receipts_form_controls(closure_receipts_form, cashier_id)
        + closure.get_closure_receipt_detail_form_controls(closure_receipt_detail_form, cashier_id)
        + sale.get_suspended_sales_form_controls(suspended_sales_market_form, cashier_id)
        + product.get_product_list_form_controls(product_list_form, cashier_id)
        + customer.get_customer_list_form_controls(customer_list_form, cashier_id)
        + customer.get_customer_select_form_controls(customer_select_form, cashier_id)
        + payment_screen.get_payment_form_controls(payment_form, cashier_id)
        + (
            campaign_management.get_campaign_list_form_controls(campaign_list_form, cashier_id)
            if campaign_list_form
            else []
        )
    )

    for control in all_controls:
        session.add(control)

    # ── Phase 2: Flush → wire panel parent IDs ───────────────────────────────
    session.flush()

    management.update_cashier_panel_parents(cashier_controls, cashier_panel_children)

    # Settings hub (#3) and dedicated POS / Loyalty forms (#23–24)
    setting_form.insert_settings_menu_controls(session, config_form, cashier_id)
    setting_form.insert_pos_settings_form_controls(session, pos_settings_form, cashier_id)
    setting_form.insert_loyalty_settings_form_controls(session, loyalty_settings_form, cashier_id)

    # ── Phase 3: Tab-based and inventory forms ───────────────────────────────
    product.insert_product_detail_controls(session, product_detail_form, cashier_id)

    stock.insert_stock_form_controls(session, {
        'inquiry':    stock_inquiry_form,
        'stock_in':   stock_in_form,
        'adjustment': stock_adjustment_form,
        'movement':   stock_movement_form,
    }, cashier_id)

    customer.insert_customer_detail_controls(session, customer_detail_form, cashier_id)

    if campaign_detail_form:
        campaign_management.insert_campaign_detail_controls(session, campaign_detail_form, cashier_id)

    session.commit()
    logger.info("✓ %s form controls inserted successfully", len(all_controls))
