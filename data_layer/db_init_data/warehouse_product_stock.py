"""
SaleFlex.PyPOS - Database Initial Data
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

from datetime import datetime, timedelta

from data_layer.model.definition.product import Product
from data_layer.model.definition.warehouse_location import WarehouseLocation
from data_layer.model.definition.warehouse import Warehouse
from data_layer.model.definition.warehouse_product_stock import WarehouseProductStock

from core.logger import get_logger

logger = get_logger(__name__)


def _insert_warehouse_product_stock(session, admin_cashier_id: str):
    """
    Insert initial WarehouseProductStock records for all products.

    Assigns stock to the primary SALES_FLOOR location (SALES-001-A) and also
    keeps product.stock in sync with the assigned quantity.

    Stock quantities are set to represent a realistic initial inventory for a
    medium-sized UK retail store.
    """
    existing = session.query(WarehouseProductStock).first()
    if existing:
        logger.warning("✓ WarehouseProductStock records already exist, skipping insertion")
        return

    # Find the SALES_FLOOR warehouse primary location
    sales_floor_location = (
        session.query(WarehouseLocation)
        .filter(WarehouseLocation.code == "SALES-001-A", WarehouseLocation.is_deleted.is_(False))
        .first()
    )

    if not sales_floor_location:
        logger.error(
            "SALES_FLOOR location (SALES-001-A) not found. "
            "Cannot insert WarehouseProductStock."
        )
        return

    products = session.query(Product).filter(Product.is_deleted.is_(False)).all()
    if not products:
        logger.error("No products found. Cannot insert WarehouseProductStock.")
        return

    now = datetime.now()

    # Default stock configuration per product type (based on product code prefix or category)
    # Each product gets a sensible initial quantity, reorder level, and min/max levels.
    DEFAULT_STOCK_QTY = 50
    DEFAULT_MIN_STOCK = 5
    DEFAULT_MAX_STOCK = 200
    DEFAULT_REORDER_POINT = 10
    DEFAULT_REORDER_QTY = 50

    # Per-product overrides: code → (qty, min, max, reorder_pt, reorder_qty)
    # These mirror product codes set in _insert_products()
    stock_overrides = {
        # Fresh food / grocery — high turnover
        "5000157070008": (120, 20, 300, 30, 100),  # e.g. large grocery item
        "5000157070009": (80, 10, 200, 20, 80),
        "5000157070010": (60, 10, 150, 15, 60),
        "5000157070011": (100, 15, 250, 25, 80),
        "5000157070012": (40, 5, 100, 10, 40),
        # Canned / packaged
        "5000157070013": (90, 15, 250, 25, 80),
        "5000157070014": (70, 10, 180, 20, 60),
        "5000157070015": (55, 8, 140, 12, 50),
        # Beverages
        "5000157070016": (150, 30, 400, 50, 150),
        "5000157070017": (120, 20, 300, 40, 100),
        # Health & Beauty
        "5000157070018": (45, 5, 120, 10, 40),
        "5000157070019": (35, 5, 100, 8, 30),
        # Household
        "5000157070020": (60, 10, 150, 15, 50),
        "5000157070021": (40, 5, 100, 10, 35),
    }

    created_count = 0
    for product in products:
        overrides = stock_overrides.get(product.code)
        if overrides:
            qty, min_stock, max_stock, reorder_pt, reorder_qty = overrides
        else:
            qty = DEFAULT_STOCK_QTY
            min_stock = DEFAULT_MIN_STOCK
            max_stock = DEFAULT_MAX_STOCK
            reorder_pt = DEFAULT_REORDER_POINT
            reorder_qty = DEFAULT_REORDER_QTY

        stock_rec = WarehouseProductStock(
            fk_product_id=product.id,
            fk_warehouse_location_id=sales_floor_location.id,
            quantity=qty,
        )
        stock_rec.available_quantity = qty
        stock_rec.reserved_quantity = 0
        stock_rec.damaged_quantity = 0
        stock_rec.expired_quantity = 0

        stock_rec.min_stock_level = min_stock
        stock_rec.max_stock_level = max_stock
        stock_rec.reorder_point = reorder_pt
        stock_rec.reorder_quantity = reorder_qty

        stock_rec.total_received = qty
        stock_rec.total_sold = 0
        stock_rec.total_adjusted = 0

        stock_rec.last_received_date = now - timedelta(days=7)
        stock_rec.last_movement_date = now - timedelta(days=7)

        stock_rec.low_stock_alert = qty <= min_stock
        stock_rec.overstock_alert = qty >= max_stock
        stock_rec.is_active = True
        stock_rec.is_discontinued = False
        stock_rec.is_blocked = False

        stock_rec.fk_cashier_create_id = admin_cashier_id
        stock_rec.fk_cashier_update_id = admin_cashier_id

        session.add(stock_rec)

        # Sync product.stock column
        product.stock = qty
        product.min_stock = min_stock
        product.max_stock = max_stock

        created_count += 1

    logger.info(
        "✓ Inserted %s WarehouseProductStock records (SALES_FLOOR location)", created_count
    )
