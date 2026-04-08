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

# Thin orchestrator — delegates form-row definitions to topic-based sub-modules
# under data_layer/db_init_data/forms/.
#
# Sub-module layout:
#   login.py      — form #1  LOGIN
#   main_menu.py  — form #2  MAIN_MENU
#   management.py — forms #3 SETTING, #4 CASHIER
#   sale.py       — forms #5 SALE, #7 SUSPENDED_SALES_MARKET
#   closure.py    — forms #6 CLOSURE, #10 CLOSURE_DETAIL,
#                          #11 CLOSURE_RECEIPTS, #12 CLOSURE_RECEIPT_DETAIL
#   product.py    — forms #8 PRODUCT_LIST, #9 PRODUCT_DETAIL
#   stock.py      — forms #13 STOCK_INQUIRY, #14 STOCK_IN,
#                          #15 STOCK_ADJUSTMENT, #16 STOCK_MOVEMENT
#   customer.py   — forms #17 CUSTOMER_LIST, #18 CUSTOMER_DETAIL,
#                          #19 CUSTOMER_SELECT

from sqlalchemy.orm import Session

from core.logger import get_logger
from data_layer.model.definition.form import Form

from data_layer.db_init_data.forms import login
from data_layer.db_init_data.forms import main_menu
from data_layer.db_init_data.forms import management
from data_layer.db_init_data.forms import sale
from data_layer.db_init_data.forms import closure
from data_layer.db_init_data.forms import product
from data_layer.db_init_data.forms import stock
from data_layer.db_init_data.forms import customer

logger = get_logger(__name__)


def _insert_default_forms(session: Session, cashier_id: str):
    """Insert all default forms if the Form table is empty."""
    if session.query(Form).first():
        logger.warning("✓ Forms already exist, skipping insertion")
        return

    forms_data = (
        login.get_form_data(cashier_id)
        + main_menu.get_form_data(cashier_id)
        + management.get_form_data(cashier_id)
        + sale.get_form_data(cashier_id)
        + closure.get_form_data(cashier_id)
        + product.get_form_data(cashier_id)
        + stock.get_form_data(cashier_id)
        + customer.get_form_data(cashier_id)
    )

    try:
        for form_data in forms_data:
            session.add(Form(**form_data))

        session.commit()
        logger.info("✓ Inserted %s default forms", len(forms_data))

    except Exception as e:
        session.rollback()
        logger.error("✗ Error inserting forms: %s", e)
        raise
