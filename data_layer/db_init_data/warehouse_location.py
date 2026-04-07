"""
SaleFlex.PyPOS - Database Initial Data

Copyright (c) 2025 Ferhat Mousavi

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

from data_layer.model.definition.warehouse import Warehouse
from data_layer.model.definition.warehouse_location import WarehouseLocation

from core.logger import get_logger

logger = get_logger(__name__)


def _insert_warehouse_locations(session, admin_cashier_id: str):
    """
    Insert default warehouse locations for every pre-seeded warehouse.

    Each warehouse type gets one primary WarehouseLocation record that serves as the
    stock management location for that warehouse area.  The SALES_FLOOR location is
    the authoritative location for all POS-driven stock deductions.
    """
    existing = session.query(WarehouseLocation).first()
    if existing:
        logger.warning("✓ Warehouse locations already exist, skipping insertion")
        return

    warehouses = session.query(Warehouse).filter(
        Warehouse.is_deleted.is_(False)
    ).all()

    if not warehouses:
        logger.error("No warehouses found. Cannot insert warehouse locations.")
        return

    wh_map = {wh.warehouse_type: wh for wh in warehouses}

    # Location definitions keyed by warehouse_type
    location_defs = {
        "MAIN": [
            {
                "name": "Main Storage Area",
                "code": "MAIN-001-A",
                "description": "General storage racks in main warehouse",
                "location_type": "RACK",
                "level": 1,
                "aisle_number": "A",
                "shelf_level": 1,
                "bay_position": "01",
                "is_pick_location": True,
                "is_replenishment_location": True,
                "is_display_location": False,
                "is_customer_accessible": False,
            }
        ],
        "BACKROOM": [
            {
                "name": "Backroom Storage",
                "code": "BACK-001-A",
                "description": "Backroom stock area accessible to store staff only",
                "location_type": "SHELF",
                "level": 1,
                "aisle_number": "B",
                "shelf_level": 1,
                "bay_position": "01",
                "is_pick_location": True,
                "is_replenishment_location": True,
                "is_display_location": False,
                "is_customer_accessible": False,
            }
        ],
        "SALES_FLOOR": [
            {
                "name": "Sales Floor — General",
                "code": "SALES-001-A",
                "description": "Primary sales floor location. Used for all POS stock deductions.",
                "location_type": "GONDOLA",
                "level": 1,
                "aisle_number": "S",
                "shelf_level": 1,
                "bay_position": "01",
                "is_pick_location": True,
                "is_replenishment_location": True,
                "is_display_location": True,
                "is_customer_accessible": True,
            },
            {
                "name": "Sales Floor — Electronics",
                "code": "SALES-001-B",
                "description": "Electronics and high-value items display area",
                "location_type": "DISPLAY",
                "level": 1,
                "aisle_number": "E",
                "shelf_level": 1,
                "bay_position": "01",
                "is_pick_location": True,
                "is_replenishment_location": True,
                "is_display_location": True,
                "is_customer_accessible": True,
                "high_value_items_only": True,
            },
            {
                "name": "Sales Floor — Checkout Counter",
                "code": "SALES-001-C",
                "description": "Checkout area impulse-buy products",
                "location_type": "COUNTER",
                "level": 1,
                "aisle_number": "C",
                "shelf_level": 1,
                "bay_position": "01",
                "is_pick_location": True,
                "is_replenishment_location": True,
                "is_display_location": True,
                "is_customer_accessible": True,
            },
        ],
        "COLD_STORAGE": [
            {
                "name": "Cold Storage — Chilled",
                "code": "COLD-001-A",
                "description": "2–8°C refrigerated rack for dairy and short-shelf items",
                "location_type": "RACK",
                "level": 1,
                "aisle_number": "R",
                "shelf_level": 1,
                "bay_position": "01",
                "requires_refrigeration": True,
                "is_pick_location": True,
                "is_replenishment_location": True,
                "is_display_location": False,
                "is_customer_accessible": False,
            }
        ],
        "SECURITY": [
            {
                "name": "Security Cage",
                "code": "SEC-001-A",
                "description": "Locked security area for high-value merchandise",
                "location_type": "ZONE",
                "level": 1,
                "aisle_number": "K",
                "shelf_level": 1,
                "bay_position": "01",
                "restricted_access": True,
                "high_value_items_only": True,
                "is_pick_location": True,
                "is_replenishment_location": True,
                "is_display_location": False,
                "is_customer_accessible": False,
            }
        ],
        "TEMPORARY": [
            {
                "name": "Temporary Returns Area",
                "code": "TEMP-001-A",
                "description": "Staging area for returned and pending items",
                "location_type": "ZONE",
                "level": 1,
                "aisle_number": "T",
                "shelf_level": 1,
                "bay_position": "01",
                "is_pick_location": False,
                "is_replenishment_location": False,
                "is_display_location": False,
                "is_customer_accessible": False,
            }
        ],
    }

    created_count = 0
    for wh_type, locations in location_defs.items():
        warehouse = wh_map.get(wh_type)
        if not warehouse:
            logger.warning("Warehouse type '%s' not found, skipping locations", wh_type)
            continue

        for loc_def in locations:
            loc = WarehouseLocation(
                name=loc_def["name"],
                code=loc_def["code"],
                location_type=loc_def["location_type"],
                fk_warehouse_id=warehouse.id,
            )
            loc.description = loc_def.get("description")
            loc.level = loc_def.get("level", 1)
            loc.aisle_number = loc_def.get("aisle_number")
            loc.shelf_level = loc_def.get("shelf_level", 1)
            loc.bay_position = loc_def.get("bay_position")
            loc.is_pick_location = loc_def.get("is_pick_location", True)
            loc.is_replenishment_location = loc_def.get("is_replenishment_location", True)
            loc.is_display_location = loc_def.get("is_display_location", False)
            loc.is_customer_accessible = loc_def.get("is_customer_accessible", False)
            loc.restricted_access = loc_def.get("restricted_access", False)
            loc.high_value_items_only = loc_def.get("high_value_items_only", False)
            loc.requires_refrigeration = loc_def.get("requires_refrigeration", False)
            loc.is_active = True
            loc.is_blocked = False
            loc.fk_cashier_create_id = admin_cashier_id
            loc.fk_cashier_update_id = admin_cashier_id

            session.add(loc)
            created_count += 1

    logger.info("✓ Inserted %s warehouse locations", created_count)
