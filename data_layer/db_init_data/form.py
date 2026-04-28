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

# Thin orchestrator — delegates form-row definitions to topic-based sub-modules
# under data_layer/db_init_data/forms/.
#
# Sub-module layout:
#   login.py      — form #1  LOGIN
#   main_menu.py  — form #2  MAIN_MENU
#   management.py — forms #3 SETTINGS_MENU, #4 CASHIER, #23–24 POS/LOYALTY settings
#   sale.py       — forms #5 SALE, #7 SUSPENDED_SALES_MARKET
#   closure.py    — forms #6 CLOSURE, #10 CLOSURE_DETAIL,
#                          #11 CLOSURE_RECEIPTS, #12 CLOSURE_RECEIPT_DETAIL
#   product.py    — forms #8 PRODUCT_LIST, #9 PRODUCT_DETAIL
#   stock.py      — forms #13 STOCK_INQUIRY, #14 STOCK_IN,
#                          #15 STOCK_ADJUSTMENT, #16 STOCK_MOVEMENT
#   customer.py   — forms #17 CUSTOMER_LIST, #18 CUSTOMER_DETAIL,
#                          #19 CUSTOMER_SELECT
#   payment_screen.py — form #20 PAYMENT
#   campaign_management.py — forms #21–22 CAMPAIGN_LIST, CAMPAIGN_DETAIL
#   (campaigns are opened from SETTINGS_MENU → CAMPAIGN SETTINGS)

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
from data_layer.db_init_data.forms import payment_screen
from data_layer.db_init_data.forms import campaign_management

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
        + payment_screen.get_form_data(cashier_id)
        + campaign_management.get_form_data(cashier_id)
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
