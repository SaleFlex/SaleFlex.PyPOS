"""
SaleFlex.PyPOS - Point of Sale Application

Copyright (c) 2026 Ferhat Mousavi

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

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import uuid4

from core.logger import get_logger
from core.exceptions import DatabaseError

logger = get_logger(__name__)


class InventoryService:
    """
    Inventory Management Service for SaleFlex.PyPOS.

    Central service for all stock / warehouse operations:
    - Automatic stock deduction when a sale is completed
    - Automatic stock restoration when a sale is cancelled
    - Stock inquiry (current levels across all locations)
    - Manual stock adjustment
    - Goods receipt (stock-in)
    - Stock transfer between locations
    - Movement history retrieval
    - Low-stock alert checking

    All public methods are @staticmethod so they can be called without
    instantiating the class, consistent with VatService / SaleService.

    Stock always refers to the SALES_FLOOR warehouse location unless an
    explicit location is provided.  The product.stock column is kept in sync
    with the SALES_FLOOR WarehouseProductStock.quantity after every mutation.
    """

    # ------------------------------------------------------------------ #
    #  Movement number generation                                          #
    # ------------------------------------------------------------------ #

    @staticmethod
    def generate_movement_number(movement_type: str = "MOV") -> str:
        """
        Generate a unique movement reference number.

        Format: {TYPE}-{YYYYMMDD}-{HHMMSS}-{4-char random hex}
        e.g. "SALE-20250407-143022-A3F1"

        Args:
            movement_type: Short uppercase tag (SALE, ADJ, RCV, TRF, RTN …)

        Returns:
            str: Unique movement number string
        """
        now = datetime.now()
        rand_part = uuid4().hex[:4].upper()
        return f"{movement_type}-{now.strftime('%Y%m%d')}-{now.strftime('%H%M%S')}-{rand_part}"

    # ------------------------------------------------------------------ #
    #  UUID normalisation helper                                           #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _to_uuid(value):
        """
        Convert *value* to a :class:`uuid.UUID` instance.

        SQLAlchemy's UUID column type calls ``.hex`` on the value it receives,
        so plain strings (e.g. ``str(orm_obj.id)``) will raise
        ``AttributeError: 'str' object has no attribute 'hex'``.
        Calling this helper at the start of every method that accepts an ID
        parameter from the UI layer avoids that error.

        Args:
            value: A :class:`uuid.UUID`, a hyphenated UUID string, or ``None``.

        Returns:
            :class:`uuid.UUID` | ``None``
        """
        from uuid import UUID as _UUID
        if value is None:
            return None
        if isinstance(value, _UUID):
            return value
        if isinstance(value, str):
            try:
                return _UUID(value)
            except (ValueError, AttributeError):
                return value
        return value

    # ------------------------------------------------------------------ #
    #  Location helpers                                                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def find_sales_floor_location(session):
        """
        Return the WarehouseLocation record for the SALES_FLOOR warehouse.

        Looks for a Warehouse with warehouse_type='SALES_FLOOR', then returns
        its first active WarehouseLocation.  Falls back to any active location
        if the SALES_FLOOR warehouse has no dedicated locations.

        Args:
            session: Active SQLAlchemy session

        Returns:
            WarehouseLocation | None
        """
        from data_layer.model.definition.warehouse import Warehouse
        from data_layer.model.definition.warehouse_location import WarehouseLocation

        sales_floor_wh = session.query(Warehouse).filter(
            Warehouse.warehouse_type == "SALES_FLOOR",
            Warehouse.is_deleted.is_(False),
            Warehouse.is_active.is_(True),
        ).first()

        if sales_floor_wh:
            location = session.query(WarehouseLocation).filter(
                WarehouseLocation.fk_warehouse_id == sales_floor_wh.id,
                WarehouseLocation.is_deleted.is_(False),
                WarehouseLocation.is_active.is_(True),
                WarehouseLocation.is_blocked.is_(False),
            ).first()
            if location:
                return location

        # Fallback: any active location
        location = session.query(WarehouseLocation).filter(
            WarehouseLocation.is_deleted.is_(False),
            WarehouseLocation.is_active.is_(True),
            WarehouseLocation.is_blocked.is_(False),
        ).first()
        return location

    @staticmethod
    def get_stock_record(session, product_id, location_id) -> Optional[Any]:
        """
        Return the WarehouseProductStock row for (product, location), or None.

        Args:
            session: Active SQLAlchemy session
            product_id: UUID of the product
            location_id: UUID of the warehouse location

        Returns:
            WarehouseProductStock | None
        """
        from data_layer.model.definition.warehouse_product_stock import WarehouseProductStock

        product_id = InventoryService._to_uuid(product_id)
        location_id = InventoryService._to_uuid(location_id)

        return session.query(WarehouseProductStock).filter(
            WarehouseProductStock.fk_product_id == product_id,
            WarehouseProductStock.fk_warehouse_location_id == location_id,
            WarehouseProductStock.is_deleted.is_(False),
            WarehouseProductStock.is_active.is_(True),
        ).first()

    # ------------------------------------------------------------------ #
    #  Stock validation                                                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def can_sell(product, quantity: float, product_data: Optional[Dict] = None) -> tuple[bool, str]:
        """
        Check whether a product can be sold in the requested quantity.

        Validates against:
        1. product.is_allowed_negative_stock — if False, stock must be >= qty
        2. product.stock — the SALES_FLOOR mirror column

        Args:
            product: Product ORM instance
            quantity: Quantity the cashier is trying to sell
            product_data: Optional product_data cache (not used currently,
                          product.stock is authoritative)

        Returns:
            tuple (allowed: bool, reason: str)
                allowed=True means the sale may proceed.
                When False, reason contains a human-readable explanation.
        """
        if product is None:
            return False, "Product not found"

        current_stock = int(product.stock) if product.stock is not None else 0
        allow_negative = bool(product.is_allowed_negative_stock)

        if not allow_negative and current_stock < int(quantity):
            return (
                False,
                f"Insufficient stock for '{product.name}'. "
                f"Available: {current_stock}, Requested: {int(quantity)}",
            )

        return True, ""

    # ------------------------------------------------------------------ #
    #  Deduct stock on sale completion                                     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def deduct_stock_on_sale(
        transaction_head_id,
        products: List[Any],
        cashier_id=None,
    ) -> bool:
        """
        Reduce WarehouseProductStock.quantity (SALES_FLOOR) for every sold
        product line and record a WarehouseStockMovement of type SALE.

        Also keeps product.stock in sync with the SALES_FLOOR stock record.

        Cancelled lines (is_cancel=True) are skipped.

        Args:
            transaction_head_id: UUID of the completed TransactionHead (permanent)
            products: List of TransactionProduct ORM instances
            cashier_id: Optional UUID of the cashier (for audit)

        Returns:
            bool: True if all deductions succeeded, False on error
        """
        if not products:
            return True

        try:
            from data_layer.engine import Engine
            from data_layer.model.definition.warehouse_product_stock import WarehouseProductStock
            from data_layer.model.definition.warehouse_stock_movement import WarehouseStockMovement
            from data_layer.model.definition.product import Product

            with Engine().get_session() as session:
                location = InventoryService.find_sales_floor_location(session)
                if not location:
                    logger.warning(
                        "[InventoryService.deduct_stock_on_sale] "
                        "No SALES_FLOOR location found — skipping stock deduction"
                    )
                    return True

                for prod_line in products:
                    if getattr(prod_line, "is_cancel", False):
                        continue

                    product_id = getattr(prod_line, "fk_product_id", None)
                    qty = int(getattr(prod_line, "quantity", 0))
                    if not product_id or qty <= 0:
                        continue

                    # --- update WarehouseProductStock ---
                    stock_rec = InventoryService.get_stock_record(session, product_id, location.id)
                    qty_before = 0
                    qty_after = 0

                    if stock_rec:
                        qty_before = stock_rec.quantity
                        stock_rec.quantity -= qty
                        stock_rec.available_quantity = max(0, stock_rec.available_quantity - qty)
                        stock_rec.total_sold = (stock_rec.total_sold or 0) + qty
                        stock_rec.last_sold_date = datetime.now()
                        stock_rec.last_movement_date = datetime.now()

                        # low-stock alert
                        if (
                            stock_rec.min_stock_level
                            and stock_rec.quantity <= stock_rec.min_stock_level
                        ):
                            stock_rec.low_stock_alert = True

                        qty_after = stock_rec.quantity
                        session.flush()
                    else:
                        logger.warning(
                            "[InventoryService.deduct_stock_on_sale] "
                            "No stock record for product %s at location %s — movement logged only",
                            product_id,
                            location.id,
                        )

                    # --- sync product.stock ---
                    product = session.query(Product).filter(
                        Product.id == product_id
                    ).first()
                    if product:
                        product.stock = max(
                            (product.stock or 0) - qty,
                            0 if not product.is_allowed_negative_stock else (product.stock or 0) - qty,
                        )
                        session.flush()

                    # --- create WarehouseStockMovement ---
                    movement = WarehouseStockMovement(
                        fk_product_id=product_id,
                        movement_type="SALE",
                        quantity=-qty,
                    )
                    movement.id = uuid4()
                    movement.movement_number = InventoryService.generate_movement_number("SALE")
                    movement.fk_warehouse_location_from = location.id
                    movement.fk_transaction_head_id = transaction_head_id
                    movement.movement_date = datetime.now()
                    movement.status = "COMPLETED"
                    movement.quantity_before = qty_before
                    movement.quantity_after = qty_after
                    movement.is_system_generated = True
                    movement.source_system = "POS"
                    if cashier_id:
                        movement.approved_by = cashier_id
                        movement.is_approved = True
                    session.add(movement)

                session.commit()
                logger.info(
                    "[InventoryService.deduct_stock_on_sale] "
                    "✓ Stock deducted for transaction %s", transaction_head_id
                )
                return True

        except Exception as exc:
            logger.error(
                "[InventoryService.deduct_stock_on_sale] Error: %s", exc
            )
            return False

    # ------------------------------------------------------------------ #
    #  Restore stock on cancellation                                       #
    # ------------------------------------------------------------------ #

    @staticmethod
    def restore_stock_on_cancel(
        transaction_head_id,
        products: List[Any],
        cashier_id=None,
    ) -> bool:
        """
        Restore WarehouseProductStock.quantity (SALES_FLOOR) for a cancelled
        transaction and record WarehouseStockMovement of type RETURN.

        Args:
            transaction_head_id: UUID of the cancelled TransactionHead
            products: List of TransactionProduct ORM instances
            cashier_id: Optional UUID of the cashier

        Returns:
            bool: True on success, False on error
        """
        if not products:
            return True

        try:
            from data_layer.engine import Engine
            from data_layer.model.definition.warehouse_product_stock import WarehouseProductStock
            from data_layer.model.definition.warehouse_stock_movement import WarehouseStockMovement
            from data_layer.model.definition.product import Product

            with Engine().get_session() as session:
                location = InventoryService.find_sales_floor_location(session)
                if not location:
                    logger.warning(
                        "[InventoryService.restore_stock_on_cancel] "
                        "No SALES_FLOOR location — skipping stock restore"
                    )
                    return True

                for prod_line in products:
                    product_id = getattr(prod_line, "fk_product_id", None)
                    qty = int(getattr(prod_line, "quantity", 0))
                    if not product_id or qty <= 0:
                        continue

                    stock_rec = InventoryService.get_stock_record(session, product_id, location.id)
                    qty_before = 0
                    qty_after = 0

                    if stock_rec:
                        qty_before = stock_rec.quantity
                        stock_rec.quantity += qty
                        stock_rec.available_quantity = (stock_rec.available_quantity or 0) + qty
                        stock_rec.last_movement_date = datetime.now()
                        stock_rec.low_stock_alert = (
                            stock_rec.min_stock_level is not None
                            and stock_rec.quantity <= stock_rec.min_stock_level
                        )
                        qty_after = stock_rec.quantity
                        session.flush()

                    product = session.query(Product).filter(
                        Product.id == product_id
                    ).first()
                    if product:
                        product.stock = (product.stock or 0) + qty
                        session.flush()

                    movement = WarehouseStockMovement(
                        fk_product_id=product_id,
                        movement_type="RETURN",
                        quantity=qty,
                    )
                    movement.id = uuid4()
                    movement.movement_number = InventoryService.generate_movement_number("RTN")
                    movement.fk_warehouse_location_to = location.id
                    movement.fk_transaction_head_id = transaction_head_id
                    movement.movement_date = datetime.now()
                    movement.status = "COMPLETED"
                    movement.quantity_before = qty_before
                    movement.quantity_after = qty_after
                    movement.is_system_generated = True
                    movement.source_system = "POS"
                    movement.reason = "Sale cancelled"
                    if cashier_id:
                        movement.approved_by = cashier_id
                        movement.is_approved = True
                    session.add(movement)

                session.commit()
                logger.info(
                    "[InventoryService.restore_stock_on_cancel] "
                    "✓ Stock restored for cancelled transaction %s", transaction_head_id
                )
                return True

        except Exception as exc:
            logger.error(
                "[InventoryService.restore_stock_on_cancel] Error: %s", exc
            )
            return False

    # ------------------------------------------------------------------ #
    #  Stock inquiry                                                       #
    # ------------------------------------------------------------------ #

    @staticmethod
    def get_stock_summary(product_id) -> List[Dict[str, Any]]:
        """
        Return a list of stock records for a product across all warehouse locations.

        Each entry contains:
            warehouse_name, location_name, location_code, quantity,
            available_quantity, reserved_quantity, min_stock_level,
            reorder_point, low_stock_alert

        Args:
            product_id: UUID of the product

        Returns:
            list of dict, one per WarehouseProductStock row
        """
        try:
            from data_layer.engine import Engine
            from data_layer.model.definition.warehouse_product_stock import WarehouseProductStock
            from data_layer.model.definition.warehouse_location import WarehouseLocation
            from data_layer.model.definition.warehouse import Warehouse

            product_id = InventoryService._to_uuid(product_id)

            result = []
            with Engine().get_session() as session:
                stocks = session.query(WarehouseProductStock).filter(
                    WarehouseProductStock.fk_product_id == product_id,
                    WarehouseProductStock.is_deleted.is_(False),
                ).all()

                for s in stocks:
                    location = session.query(WarehouseLocation).filter(
                        WarehouseLocation.id == s.fk_warehouse_location_id
                    ).first()
                    warehouse = None
                    if location:
                        warehouse = session.query(Warehouse).filter(
                            Warehouse.id == location.fk_warehouse_id
                        ).first()

                    result.append({
                        "warehouse_name": warehouse.name if warehouse else "—",
                        "warehouse_type": warehouse.warehouse_type if warehouse else "—",
                        "location_name": location.name if location else "—",
                        "location_code": location.code if location else "—",
                        "quantity": s.quantity,
                        "available_quantity": s.available_quantity,
                        "reserved_quantity": s.reserved_quantity,
                        "min_stock_level": s.min_stock_level,
                        "reorder_point": s.reorder_point,
                        "low_stock_alert": s.low_stock_alert,
                    })

            return result

        except Exception as exc:
            logger.error("[InventoryService.get_stock_summary] Error: %s", exc)
            return []

    @staticmethod
    def get_low_stock_products(limit: int = 100) -> List[Dict[str, Any]]:
        """
        Return products whose SALES_FLOOR stock is at or below min_stock_level.

        Args:
            limit: Maximum number of results to return

        Returns:
            list of dict with keys: product_id, product_name, product_code,
            quantity, min_stock_level, reorder_point
        """
        try:
            from data_layer.engine import Engine
            from data_layer.model.definition.warehouse_product_stock import WarehouseProductStock
            from data_layer.model.definition.warehouse_location import WarehouseLocation
            from data_layer.model.definition.warehouse import Warehouse
            from data_layer.model.definition.product import Product

            result = []
            with Engine().get_session() as session:
                sales_floor = None
                wh = session.query(Warehouse).filter(
                    Warehouse.warehouse_type == "SALES_FLOOR",
                    Warehouse.is_deleted.is_(False),
                ).first()
                if wh:
                    sales_floor = session.query(WarehouseLocation).filter(
                        WarehouseLocation.fk_warehouse_id == wh.id,
                        WarehouseLocation.is_deleted.is_(False),
                    ).first()

                query = session.query(WarehouseProductStock).filter(
                    WarehouseProductStock.is_deleted.is_(False),
                    WarehouseProductStock.low_stock_alert.is_(True),
                )
                if sales_floor:
                    query = query.filter(
                        WarehouseProductStock.fk_warehouse_location_id == sales_floor.id
                    )

                for s in query.limit(limit).all():
                    product = session.query(Product).filter(
                        Product.id == s.fk_product_id
                    ).first()
                    result.append({
                        "product_id": str(s.fk_product_id),
                        "product_name": product.name if product else "—",
                        "product_code": product.code if product else "—",
                        "quantity": s.quantity,
                        "min_stock_level": s.min_stock_level,
                        "reorder_point": s.reorder_point,
                    })

            return result

        except Exception as exc:
            logger.error("[InventoryService.get_low_stock_products] Error: %s", exc)
            return []

    # ------------------------------------------------------------------ #
    #  Goods receipt (stock-in)                                            #
    # ------------------------------------------------------------------ #

    @staticmethod
    def receive_stock(
        product_id,
        location_id,
        quantity: int,
        unit_cost: Optional[Decimal] = None,
        reference_document: Optional[str] = None,
        supplier_name: Optional[str] = None,
        lot_number: Optional[str] = None,
        cashier_id=None,
        reason: Optional[str] = None,
    ) -> bool:
        """
        Receive goods into a warehouse location (stock-in).

        Increases WarehouseProductStock.quantity and records a RECEIPT movement.
        Also updates product.stock if the target location is SALES_FLOOR.

        Args:
            product_id: UUID of the product
            location_id: UUID of the target WarehouseLocation
            quantity: Number of units received (positive integer)
            unit_cost: Optional cost per unit
            reference_document: e.g. purchase order number or delivery note
            supplier_name: Name of the supplier
            lot_number: Lot / batch number
            cashier_id: UUID of the cashier performing the receipt
            reason: Free-text reason

        Returns:
            bool: True on success, False on error
        """
        if quantity <= 0:
            logger.warning("[InventoryService.receive_stock] Quantity must be > 0")
            return False

        product_id = InventoryService._to_uuid(product_id)
        location_id = InventoryService._to_uuid(location_id)

        try:
            from data_layer.engine import Engine
            from data_layer.model.definition.warehouse_product_stock import WarehouseProductStock
            from data_layer.model.definition.warehouse_stock_movement import WarehouseStockMovement
            from data_layer.model.definition.warehouse_location import WarehouseLocation
            from data_layer.model.definition.warehouse import Warehouse
            from data_layer.model.definition.product import Product

            with Engine().get_session() as session:
                stock_rec = InventoryService.get_stock_record(session, product_id, location_id)
                qty_before = 0
                qty_after = 0

                if stock_rec:
                    qty_before = stock_rec.quantity
                    stock_rec.quantity += quantity
                    stock_rec.available_quantity = (stock_rec.available_quantity or 0) + quantity
                    stock_rec.total_received = (stock_rec.total_received or 0) + quantity
                    stock_rec.last_received_date = datetime.now()
                    stock_rec.last_movement_date = datetime.now()
                    if unit_cost:
                        stock_rec.last_cost = unit_cost
                    if lot_number:
                        stock_rec.lot_number = lot_number
                    stock_rec.low_stock_alert = (
                        stock_rec.min_stock_level is not None
                        and stock_rec.quantity <= stock_rec.min_stock_level
                    )
                    qty_after = stock_rec.quantity
                    session.flush()
                else:
                    # Create a new stock record if it doesn't exist
                    stock_rec = WarehouseProductStock(
                        fk_product_id=product_id,
                        fk_warehouse_location_id=location_id,
                        quantity=quantity,
                    )
                    stock_rec.id = uuid4()
                    stock_rec.available_quantity = quantity
                    stock_rec.total_received = quantity
                    stock_rec.last_received_date = datetime.now()
                    stock_rec.last_movement_date = datetime.now()
                    if unit_cost:
                        stock_rec.last_cost = unit_cost
                    if lot_number:
                        stock_rec.lot_number = lot_number
                    qty_after = quantity
                    session.add(stock_rec)
                    session.flush()

                # Sync product.stock if SALES_FLOOR
                location = session.query(WarehouseLocation).filter(
                    WarehouseLocation.id == location_id
                ).first()
                if location:
                    wh = session.query(Warehouse).filter(
                        Warehouse.id == location.fk_warehouse_id
                    ).first()
                    if wh and wh.warehouse_type == "SALES_FLOOR":
                        product = session.query(Product).filter(
                            Product.id == product_id
                        ).first()
                        if product:
                            product.stock = qty_after
                            session.flush()

                movement = WarehouseStockMovement(
                    fk_product_id=product_id,
                    movement_type="RECEIPT",
                    quantity=quantity,
                )
                movement.id = uuid4()
                movement.movement_number = InventoryService.generate_movement_number("RCV")
                movement.fk_warehouse_location_to = location_id
                movement.movement_date = datetime.now()
                movement.status = "COMPLETED"
                movement.quantity_before = qty_before
                movement.quantity_after = qty_after
                movement.is_system_generated = False
                movement.source_system = "POS"
                if unit_cost:
                    movement.unit_cost = unit_cost
                    movement.total_cost = unit_cost * quantity
                if reference_document:
                    movement.reference_document = reference_document
                if supplier_name:
                    movement.supplier_name = supplier_name
                if lot_number:
                    movement.lot_number = lot_number
                if reason:
                    movement.reason = reason
                if cashier_id:
                    movement.approved_by = cashier_id
                    movement.is_approved = True
                session.add(movement)
                session.commit()

                logger.info(
                    "[InventoryService.receive_stock] "
                    "✓ Received %s units for product %s at location %s",
                    quantity, product_id, location_id,
                )
                return True

        except Exception as exc:
            logger.error("[InventoryService.receive_stock] Error: %s", exc)
            return False

    # ------------------------------------------------------------------ #
    #  Manual stock adjustment                                             #
    # ------------------------------------------------------------------ #

    @staticmethod
    def adjust_stock(
        product_id,
        location_id,
        counted_quantity: int,
        reason: Optional[str] = None,
        adjustment_type: str = "CYCLE_COUNT",
        cashier_id=None,
    ) -> bool:
        """
        Perform a manual stock adjustment (physical count correction).

        Sets WarehouseProductStock.quantity to counted_quantity and records
        both a WarehouseStockAdjustment and a WarehouseStockMovement.
        Also syncs product.stock if the location is SALES_FLOOR.

        Args:
            product_id: UUID of the product
            location_id: UUID of the WarehouseLocation
            counted_quantity: The physically counted quantity (new system quantity)
            reason: Free-text reason for adjustment (e.g. "Shrinkage", "Found")
            adjustment_type: CYCLE_COUNT | PHYSICAL_COUNT | LOSS | DAMAGE | FOUND | WRITE_OFF
            cashier_id: UUID of the cashier authorising the adjustment

        Returns:
            bool: True on success, False on error
        """
        product_id = InventoryService._to_uuid(product_id)
        location_id = InventoryService._to_uuid(location_id)

        try:
            from data_layer.engine import Engine
            from data_layer.model.definition.warehouse_product_stock import WarehouseProductStock
            from data_layer.model.definition.warehouse_stock_movement import WarehouseStockMovement
            from data_layer.model.definition.warehouse_stock_adjustment import WarehouseStockAdjustment
            from data_layer.model.definition.warehouse_location import WarehouseLocation
            from data_layer.model.definition.warehouse import Warehouse
            from data_layer.model.definition.product import Product

            with Engine().get_session() as session:
                stock_rec = InventoryService.get_stock_record(session, product_id, location_id)
                system_quantity = stock_rec.quantity if stock_rec else 0
                difference = counted_quantity - system_quantity

                if stock_rec:
                    qty_before = stock_rec.quantity
                    stock_rec.quantity = counted_quantity
                    stock_rec.available_quantity = counted_quantity
                    stock_rec.total_adjusted = (stock_rec.total_adjusted or 0) + abs(difference)
                    stock_rec.last_movement_date = datetime.now()
                    stock_rec.last_count_date = datetime.now()
                    stock_rec.low_stock_alert = (
                        stock_rec.min_stock_level is not None
                        and stock_rec.quantity <= stock_rec.min_stock_level
                    )
                    session.flush()
                else:
                    stock_rec = WarehouseProductStock(
                        fk_product_id=product_id,
                        fk_warehouse_location_id=location_id,
                        quantity=counted_quantity,
                    )
                    stock_rec.id = uuid4()
                    stock_rec.available_quantity = counted_quantity
                    stock_rec.last_movement_date = datetime.now()
                    stock_rec.last_count_date = datetime.now()
                    qty_before = 0
                    session.add(stock_rec)
                    session.flush()

                # Sync product.stock if SALES_FLOOR
                location = session.query(WarehouseLocation).filter(
                    WarehouseLocation.id == location_id
                ).first()
                if location:
                    wh = session.query(Warehouse).filter(
                        Warehouse.id == location.fk_warehouse_id
                    ).first()
                    if wh and wh.warehouse_type == "SALES_FLOOR":
                        product = session.query(Product).filter(
                            Product.id == product_id
                        ).first()
                        if product:
                            product.stock = counted_quantity
                            session.flush()

                # WarehouseStockAdjustment record
                adj = WarehouseStockAdjustment(
                    fk_product_id=product_id,
                    adjustment_type=adjustment_type,
                    quantity_difference=difference,
                )
                adj.id = uuid4()
                adj.adjustment_number = InventoryService.generate_movement_number("ADJ")
                adj.fk_warehouse_location_id = location_id
                adj.system_quantity = system_quantity
                adj.counted_quantity = counted_quantity
                adj.count_date = datetime.now()
                adj.count_method = "MANUAL"
                adj.status = "PROCESSED"
                adj.requires_approval = False
                adj.is_approved = True
                if cashier_id:
                    adj.approved_by = cashier_id
                    adj.approved_at = datetime.now()
                if reason:
                    adj.adjustment_reason = reason
                session.add(adj)

                # WarehouseStockMovement record
                movement = WarehouseStockMovement(
                    fk_product_id=product_id,
                    movement_type="ADJUSTMENT",
                    quantity=difference,
                )
                movement.id = uuid4()
                movement.movement_number = InventoryService.generate_movement_number("ADJ")
                if difference >= 0:
                    movement.fk_warehouse_location_to = location_id
                else:
                    movement.fk_warehouse_location_from = location_id
                movement.movement_date = datetime.now()
                movement.status = "COMPLETED"
                movement.quantity_before = qty_before
                movement.quantity_after = counted_quantity
                movement.is_system_generated = False
                movement.source_system = "POS"
                if reason:
                    movement.reason = reason
                if cashier_id:
                    movement.approved_by = cashier_id
                    movement.is_approved = True
                session.add(movement)

                session.commit()
                logger.info(
                    "[InventoryService.adjust_stock] "
                    "✓ Adjusted product %s: %s → %s (diff=%s)",
                    product_id, system_quantity, counted_quantity, difference,
                )
                return True

        except Exception as exc:
            logger.error("[InventoryService.adjust_stock] Error: %s", exc)
            return False

    # ------------------------------------------------------------------ #
    #  Stock transfer between locations                                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def transfer_stock(
        product_id,
        from_location_id,
        to_location_id,
        quantity: int,
        cashier_id=None,
        reason: Optional[str] = None,
    ) -> bool:
        """
        Transfer stock between two warehouse locations.

        Decreases from_location and increases to_location by quantity.
        Records a TRANSFER WarehouseStockMovement.
        Syncs product.stock if either location is SALES_FLOOR.

        Args:
            product_id: UUID of the product
            from_location_id: UUID of the source WarehouseLocation
            to_location_id: UUID of the destination WarehouseLocation
            quantity: Number of units to transfer (positive integer)
            cashier_id: UUID of the cashier authorising the transfer
            reason: Optional reason text

        Returns:
            bool: True on success, False on error (including insufficient stock)
        """
        if quantity <= 0:
            logger.warning("[InventoryService.transfer_stock] Quantity must be > 0")
            return False

        product_id = InventoryService._to_uuid(product_id)
        from_location_id = InventoryService._to_uuid(from_location_id)
        to_location_id = InventoryService._to_uuid(to_location_id)

        try:
            from data_layer.engine import Engine
            from data_layer.model.definition.warehouse_product_stock import WarehouseProductStock
            from data_layer.model.definition.warehouse_stock_movement import WarehouseStockMovement
            from data_layer.model.definition.warehouse_location import WarehouseLocation
            from data_layer.model.definition.warehouse import Warehouse
            from data_layer.model.definition.product import Product

            with Engine().get_session() as session:
                from_rec = InventoryService.get_stock_record(session, product_id, from_location_id)
                to_rec = InventoryService.get_stock_record(session, product_id, to_location_id)

                if from_rec is None or from_rec.quantity < quantity:
                    logger.warning(
                        "[InventoryService.transfer_stock] "
                        "Insufficient stock at source location for product %s", product_id
                    )
                    return False

                from_before = from_rec.quantity
                from_rec.quantity -= quantity
                from_rec.available_quantity = max(0, (from_rec.available_quantity or 0) - quantity)
                from_rec.last_movement_date = datetime.now()
                session.flush()

                if to_rec:
                    to_before = to_rec.quantity
                    to_rec.quantity += quantity
                    to_rec.available_quantity = (to_rec.available_quantity or 0) + quantity
                    to_rec.last_movement_date = datetime.now()
                    session.flush()
                else:
                    to_rec = WarehouseProductStock(
                        fk_product_id=product_id,
                        fk_warehouse_location_id=to_location_id,
                        quantity=quantity,
                    )
                    to_rec.id = uuid4()
                    to_rec.available_quantity = quantity
                    to_rec.last_movement_date = datetime.now()
                    to_before = 0
                    session.add(to_rec)
                    session.flush()

                # Sync product.stock for SALES_FLOOR side
                def _sync_product_stock(loc_id, new_qty):
                    loc = session.query(WarehouseLocation).filter(
                        WarehouseLocation.id == loc_id
                    ).first()
                    if loc:
                        wh = session.query(Warehouse).filter(
                            Warehouse.id == loc.fk_warehouse_id
                        ).first()
                        if wh and wh.warehouse_type == "SALES_FLOOR":
                            p = session.query(Product).filter(
                                Product.id == product_id
                            ).first()
                            if p:
                                p.stock = new_qty
                                session.flush()

                _sync_product_stock(from_location_id, from_rec.quantity)
                _sync_product_stock(to_location_id, to_rec.quantity)

                movement = WarehouseStockMovement(
                    fk_product_id=product_id,
                    movement_type="TRANSFER",
                    quantity=quantity,
                )
                movement.id = uuid4()
                movement.movement_number = InventoryService.generate_movement_number("TRF")
                movement.fk_warehouse_location_from = from_location_id
                movement.fk_warehouse_location_to = to_location_id
                movement.movement_date = datetime.now()
                movement.status = "COMPLETED"
                movement.quantity_before = from_before
                movement.quantity_after = from_rec.quantity
                movement.is_system_generated = False
                movement.source_system = "POS"
                if reason:
                    movement.reason = reason
                if cashier_id:
                    movement.approved_by = cashier_id
                    movement.is_approved = True
                session.add(movement)
                session.commit()

                logger.info(
                    "[InventoryService.transfer_stock] "
                    "✓ Transferred %s units of product %s from %s to %s",
                    quantity, product_id, from_location_id, to_location_id,
                )
                return True

        except Exception as exc:
            logger.error("[InventoryService.transfer_stock] Error: %s", exc)
            return False

    # ------------------------------------------------------------------ #
    #  Movement history                                                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def get_movement_history(
        product_id=None,
        location_id=None,
        limit: int = 200,
    ) -> List[Dict[str, Any]]:
        """
        Return stock movement history records.

        Args:
            product_id: Filter by product UUID (None = all products)
            location_id: Filter by warehouse location UUID (None = all locations)
            limit: Maximum number of records to return

        Returns:
            list of dict with movement details, ordered newest-first
        """
        product_id = InventoryService._to_uuid(product_id)
        location_id = InventoryService._to_uuid(location_id)

        try:
            from data_layer.engine import Engine
            from data_layer.model.definition.warehouse_stock_movement import WarehouseStockMovement
            from data_layer.model.definition.product import Product

            result = []
            with Engine().get_session() as session:
                query = session.query(WarehouseStockMovement).filter(
                    WarehouseStockMovement.is_deleted.is_(False)
                )
                if product_id:
                    query = query.filter(
                        WarehouseStockMovement.fk_product_id == product_id
                    )
                if location_id:
                    from sqlalchemy import or_
                    query = query.filter(
                        or_(
                            WarehouseStockMovement.fk_warehouse_location_from == location_id,
                            WarehouseStockMovement.fk_warehouse_location_to == location_id,
                        )
                    )

                movements = (
                    query.order_by(WarehouseStockMovement.movement_date.desc())
                    .limit(limit)
                    .all()
                )

                for m in movements:
                    product = session.query(Product).filter(
                        Product.id == m.fk_product_id
                    ).first() if not product_id else None

                    result.append({
                        "movement_number": m.movement_number,
                        "movement_type": m.movement_type,
                        "quantity": m.quantity,
                        "quantity_before": m.quantity_before,
                        "quantity_after": m.quantity_after,
                        "movement_date": m.movement_date.strftime("%Y-%m-%d %H:%M") if m.movement_date else "—",
                        "status": m.status,
                        "reason": m.reason or "—",
                        "reference_document": m.reference_document or "—",
                        "product_name": product.name if product else "—",
                        "product_code": product.code if product else "—",
                    })

            return result

        except Exception as exc:
            logger.error("[InventoryService.get_movement_history] Error: %s", exc)
            return []
