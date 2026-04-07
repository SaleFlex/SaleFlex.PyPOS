"""
SaleFlex.PyPOS - Point of Sale Application

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

from data_layer.enums import FormName, ControlName

from core.logger import get_logger

logger = get_logger(__name__)


class WarehouseEvent:
    """
    Warehouse / Inventory Event Handler.

    Handles all stock and warehouse operations:
    - Stock inquiry          (STOCK_INQUIRY form)
    - Goods receipt          (STOCK_IN form)
    - Manual adjustment      (STOCK_ADJUSTMENT form)
    - Movement history       (STOCK_MOVEMENT form)
    - Search within forms
    - Confirm actions (save stock-in / confirm adjustment)
    """

    # ================================================================== #
    #  Navigation helpers                                                  #
    # ================================================================== #

    def _stock_inquiry_event(self) -> bool:
        """Navigate to the Stock Inquiry form."""
        if not self.login_succeed:
            self._logout_event()
            return False

        self.current_form_type = FormName.STOCK_INQUIRY
        self.interface.redraw(form_name=FormName.STOCK_INQUIRY.name)
        return True

    def _stock_in_event(self) -> bool:
        """Navigate to the Goods Receipt (Stock-In) form."""
        if not self.login_succeed:
            self._logout_event()
            return False

        self.current_form_type = FormName.STOCK_IN
        self.interface.redraw(form_name=FormName.STOCK_IN.name)
        return True

    def _stock_adjustment_event(self) -> bool:
        """Navigate to the Stock Adjustment form."""
        if not self.login_succeed:
            self._logout_event()
            return False

        self.current_form_type = FormName.STOCK_ADJUSTMENT
        self.interface.redraw(form_name=FormName.STOCK_ADJUSTMENT.name)
        return True

    def _stock_movement_event(self) -> bool:
        """Navigate to the Stock Movement History form."""
        if not self.login_succeed:
            self._logout_event()
            return False

        self.current_form_type = FormName.STOCK_MOVEMENT
        self.interface.redraw(form_name=FormName.STOCK_MOVEMENT.name)
        return True

    # ================================================================== #
    #  Stock Inquiry — search and detail                                   #
    # ================================================================== #

    def _stock_search_event(self) -> bool:
        """
        Execute a stock search on the STOCK_INQUIRY form.

        Reads STOCK_SEARCH_TEXTBOX, queries Product + WarehouseProductStock
        and populates STOCK_INQUIRY_DATAGRID with results:
            Code | Name | Short Name | Sale Price | Total Stock | Low Stock Alert
        """
        if not self.login_succeed:
            return False

        try:
            from user_interface.control import TextBox, DataGrid
            window = self.interface.window
            if not window:
                return False

            search_term = ""
            for child in window.children():
                if isinstance(child, TextBox):
                    name = getattr(child, "name", "")
                    if name == ControlName.STOCK_SEARCH_TEXTBOX.value:
                        search_term = child.text().strip()
                        break

            from data_layer.model.definition.product import Product
            from data_layer.model.definition.warehouse_product_stock import WarehouseProductStock
            from data_layer.engine import Engine

            with Engine().get_session() as session:
                query = session.query(Product).filter(
                    Product.is_deleted.is_(False)
                )
                if search_term:
                    like_term = f"%{search_term}%"
                    from sqlalchemy import or_
                    query = query.filter(
                        or_(
                            Product.name.ilike(like_term),
                            Product.short_name.ilike(like_term),
                            Product.code.ilike(like_term),
                        )
                    )

                products = query.order_by(Product.name).limit(500).all()

            columns = ["Code", "Name", "Short Name", "Sale Price", "Stock", "Low Stock"]
            rows = []
            product_ids = []

            for p in products:
                low_stock_flag = "⚠" if (
                    p.stock is not None
                    and p.min_stock is not None
                    and p.min_stock > 0
                    and p.stock <= p.min_stock
                ) else ""
                rows.append([
                    p.code or "",
                    p.name or "",
                    p.short_name or "",
                    str(p.sale_price) if p.sale_price is not None else "0",
                    str(p.stock) if p.stock is not None else "0",
                    low_stock_flag,
                ])
                product_ids.append(str(p.id))

            for child in window.children():
                if isinstance(child, DataGrid):
                    name = getattr(child, "name", "")
                    if name == ControlName.STOCK_INQUIRY_DATAGRID.value:
                        child.set_columns(columns)
                        child.set_data(rows)
                        child._product_ids = product_ids
                        break

            logger.info("[STOCK_SEARCH] Found %s products for '%s'", len(rows), search_term)
            return True

        except Exception as exc:
            logger.error("[STOCK_SEARCH] Error: %s", exc)
            return False

    def _stock_detail_event(self) -> bool:
        """
        Show per-location stock breakdown for the selected product.

        Reads the selected row from STOCK_INQUIRY_DATAGRID, then fills
        STOCK_DETAIL_DATAGRID with WarehouseProductStock entries.
        """
        if not self.login_succeed:
            return False

        try:
            from user_interface.control import DataGrid
            from pos.service.inventory_service import InventoryService

            window = self.interface.window
            if not window:
                return False

            product_id = None
            for child in window.children():
                if isinstance(child, DataGrid):
                    name = getattr(child, "name", "")
                    if name == ControlName.STOCK_INQUIRY_DATAGRID.value:
                        idx = child.get_selected_row_index()
                        ids = getattr(child, "_product_ids", [])
                        if 0 <= idx < len(ids):
                            product_id = ids[idx]
                        break

            if not product_id:
                logger.warning("[STOCK_DETAIL] No product selected")
                return False

            summary = InventoryService.get_stock_summary(product_id)

            columns = ["Warehouse", "Type", "Location", "Qty", "Available", "Reserved", "Min", "Reorder", "Alert"]
            rows = [
                [
                    s["warehouse_name"],
                    s["warehouse_type"],
                    s["location_name"],
                    str(s["quantity"]),
                    str(s["available_quantity"]),
                    str(s["reserved_quantity"]),
                    str(s["min_stock_level"]),
                    str(s["reorder_point"]),
                    "⚠" if s["low_stock_alert"] else "",
                ]
                for s in summary
            ]

            for child in window.children():
                if isinstance(child, DataGrid):
                    name = getattr(child, "name", "")
                    if name == ControlName.STOCK_DETAIL_DATAGRID.value:
                        child.set_columns(columns)
                        child.set_data(rows)
                        break

            return True

        except Exception as exc:
            logger.error("[STOCK_DETAIL] Error: %s", exc)
            return False

    # ================================================================== #
    #  Goods Receipt (Stock-In)                                           #
    # ================================================================== #

    def _stock_in_search_event(self) -> bool:
        """Search products on the STOCK_IN form and fill STOCK_IN_PRODUCT_DATAGRID."""
        if not self.login_succeed:
            return False

        try:
            from user_interface.control import TextBox, DataGrid
            from data_layer.model.definition.product import Product
            from data_layer.engine import Engine

            window = self.interface.window
            if not window:
                return False

            search_term = ""
            for child in window.children():
                if isinstance(child, TextBox):
                    name = getattr(child, "name", "")
                    if name == ControlName.STOCK_SEARCH_TEXTBOX.value:
                        search_term = child.text().strip()
                        break

            with Engine().get_session() as session:
                query = session.query(Product).filter(Product.is_deleted.is_(False))
                if search_term:
                    from sqlalchemy import or_
                    query = query.filter(
                        or_(
                            Product.name.ilike(f"%{search_term}%"),
                            Product.code.ilike(f"%{search_term}%"),
                        )
                    )
                products = query.order_by(Product.name).limit(300).all()

            columns = ["Code", "Name", "Current Stock"]
            rows = []
            product_ids = []
            for p in products:
                rows.append([
                    p.code or "",
                    p.name or "",
                    str(p.stock) if p.stock is not None else "0",
                ])
                product_ids.append(str(p.id))

            for child in window.children():
                if isinstance(child, DataGrid):
                    name = getattr(child, "name", "")
                    if name == ControlName.STOCK_IN_PRODUCT_DATAGRID.value:
                        child.set_columns(columns)
                        child.set_data(rows)
                        child._product_ids = product_ids
                        break

            return True

        except Exception as exc:
            logger.error("[STOCK_IN_SEARCH] Error: %s", exc)
            return False

    def _stock_in_confirm_event(self) -> bool:
        """
        Confirm goods receipt.

        Reads selected product from STOCK_IN_PRODUCT_DATAGRID and quantity
        from STOCK_QUANTITY_TEXTBOX, then calls InventoryService.receive_stock()
        for the SALES_FLOOR location.
        """
        if not self.login_succeed:
            return False

        try:
            from user_interface.control import TextBox, DataGrid
            from user_interface.form.message_form import MessageForm
            from pos.service.inventory_service import InventoryService
            from data_layer.engine import Engine
            from data_layer.model.definition.product import Product

            window = self.interface.window
            if not window:
                return False

            # --- find product ---
            product_id = None
            for child in window.children():
                if isinstance(child, DataGrid):
                    if getattr(child, "name", "") == ControlName.STOCK_IN_PRODUCT_DATAGRID.value:
                        idx = child.get_selected_row_index()
                        ids = getattr(child, "_product_ids", [])
                        if 0 <= idx < len(ids):
                            product_id = ids[idx]
                        break

            if not product_id:
                MessageForm.show_error(window, "Please select a product first.", "No Selection")
                return False

            # --- find quantity ---
            qty_text = ""
            reason_text = ""
            for child in window.children():
                if isinstance(child, TextBox):
                    name = getattr(child, "name", "")
                    if name == ControlName.STOCK_QUANTITY_TEXTBOX.value:
                        qty_text = child.text().strip()
                    elif name == ControlName.STOCK_REASON_TEXTBOX.value:
                        reason_text = child.text().strip()

            try:
                quantity = int(float(qty_text))
                if quantity <= 0:
                    raise ValueError("must be > 0")
            except ValueError:
                MessageForm.show_error(window, "Please enter a valid quantity (positive integer).", "Invalid Quantity")
                return False

            # --- find SALES_FLOOR location ---
            with Engine().get_session() as session:
                location = InventoryService.find_sales_floor_location(session)

            if not location:
                MessageForm.show_error(window, "SALES_FLOOR location not found in database.", "Configuration Error")
                return False

            cashier_id = None
            if hasattr(self, "cashier_data") and self.cashier_data:
                cashier_id = self.cashier_data.id

            success = InventoryService.receive_stock(
                product_id=product_id,
                location_id=location.id,
                quantity=quantity,
                reason=reason_text or "Manual goods receipt",
                cashier_id=cashier_id,
            )

            if success:
                # Refresh product cache
                try:
                    from data_layer.model.definition.product import Product as _Product
                    self.refresh_product_data_model(_Product)
                    from data_layer.model.definition.warehouse_product_stock import WarehouseProductStock as _WPS
                    self.refresh_product_data_model(_WPS)
                    from data_layer.model.definition.warehouse_stock_movement import WarehouseStockMovement as _WSM
                    self.refresh_product_data_model(_WSM)
                except Exception:
                    pass

                MessageForm.show_info(window, f"✓ Received {quantity} units successfully.", "Stock Updated")

                # Refresh the product list
                self._stock_in_search_event()
                return True
            else:
                MessageForm.show_error(window, "Failed to record goods receipt. Check logs.", "Error")
                return False

        except Exception as exc:
            logger.error("[STOCK_IN_CONFIRM] Error: %s", exc)
            return False

    # ================================================================== #
    #  Stock Adjustment                                                    #
    # ================================================================== #

    def _stock_adjustment_search_event(self) -> bool:
        """Search products on STOCK_ADJUSTMENT form."""
        if not self.login_succeed:
            return False

        try:
            from user_interface.control import TextBox, DataGrid
            from data_layer.model.definition.product import Product
            from data_layer.engine import Engine

            window = self.interface.window
            if not window:
                return False

            search_term = ""
            for child in window.children():
                if isinstance(child, TextBox):
                    if getattr(child, "name", "") == ControlName.STOCK_SEARCH_TEXTBOX.value:
                        search_term = child.text().strip()
                        break

            with Engine().get_session() as session:
                query = session.query(Product).filter(Product.is_deleted.is_(False))
                if search_term:
                    from sqlalchemy import or_
                    query = query.filter(
                        or_(
                            Product.name.ilike(f"%{search_term}%"),
                            Product.code.ilike(f"%{search_term}%"),
                        )
                    )
                products = query.order_by(Product.name).limit(300).all()

            columns = ["Code", "Name", "Current Stock", "Min Stock"]
            rows = []
            product_ids = []
            for p in products:
                rows.append([
                    p.code or "",
                    p.name or "",
                    str(p.stock) if p.stock is not None else "0",
                    str(p.min_stock) if p.min_stock is not None else "0",
                ])
                product_ids.append(str(p.id))

            for child in window.children():
                if isinstance(child, DataGrid):
                    if getattr(child, "name", "") == ControlName.STOCK_ADJUSTMENT_DATAGRID.value:
                        child.set_columns(columns)
                        child.set_data(rows)
                        child._product_ids = product_ids
                        break

            return True

        except Exception as exc:
            logger.error("[STOCK_ADJ_SEARCH] Error: %s", exc)
            return False

    def _stock_adjustment_confirm_event(self) -> bool:
        """
        Confirm a manual stock adjustment.

        Reads selected product from STOCK_ADJUSTMENT_DATAGRID, new quantity from
        STOCK_QUANTITY_TEXTBOX, and reason from STOCK_REASON_TEXTBOX, then calls
        InventoryService.adjust_stock().
        """
        if not self.login_succeed:
            return False

        try:
            from user_interface.control import TextBox, DataGrid
            from user_interface.form.message_form import MessageForm
            from pos.service.inventory_service import InventoryService
            from data_layer.engine import Engine

            window = self.interface.window
            if not window:
                return False

            product_id = None
            for child in window.children():
                if isinstance(child, DataGrid):
                    if getattr(child, "name", "") == ControlName.STOCK_ADJUSTMENT_DATAGRID.value:
                        idx = child.get_selected_row_index()
                        ids = getattr(child, "_product_ids", [])
                        if 0 <= idx < len(ids):
                            product_id = ids[idx]
                        break

            if not product_id:
                MessageForm.show_error(window, "Please select a product first.", "No Selection")
                return False

            qty_text = ""
            reason_text = ""
            for child in window.children():
                if isinstance(child, TextBox):
                    name = getattr(child, "name", "")
                    if name == ControlName.STOCK_QUANTITY_TEXTBOX.value:
                        qty_text = child.text().strip()
                    elif name == ControlName.STOCK_REASON_TEXTBOX.value:
                        reason_text = child.text().strip()

            try:
                counted_qty = int(float(qty_text))
                if counted_qty < 0:
                    raise ValueError("cannot be negative")
            except ValueError:
                MessageForm.show_error(window, "Please enter a valid non-negative integer quantity.", "Invalid Quantity")
                return False

            with Engine().get_session() as session:
                location = InventoryService.find_sales_floor_location(session)

            if not location:
                MessageForm.show_error(window, "SALES_FLOOR location not found.", "Configuration Error")
                return False

            cashier_id = None
            if hasattr(self, "cashier_data") and self.cashier_data:
                cashier_id = self.cashier_data.id

            success = InventoryService.adjust_stock(
                product_id=product_id,
                location_id=location.id,
                counted_quantity=counted_qty,
                reason=reason_text or "Manual cycle-count adjustment",
                cashier_id=cashier_id,
            )

            if success:
                try:
                    from data_layer.model.definition.product import Product as _Product
                    self.refresh_product_data_model(_Product)
                    from data_layer.model.definition.warehouse_product_stock import WarehouseProductStock as _WPS
                    self.refresh_product_data_model(_WPS)
                    from data_layer.model.definition.warehouse_stock_movement import WarehouseStockMovement as _WSM
                    self.refresh_product_data_model(_WSM)
                except Exception:
                    pass

                MessageForm.show_info(window, f"✓ Stock adjusted to {counted_qty} units.", "Adjustment Saved")
                self._stock_adjustment_search_event()
                return True
            else:
                MessageForm.show_error(window, "Failed to save adjustment. Check logs.", "Error")
                return False

        except Exception as exc:
            logger.error("[STOCK_ADJ_CONFIRM] Error: %s", exc)
            return False

    # ================================================================== #
    #  Stock Movement History                                              #
    # ================================================================== #

    def _stock_movement_search_event(self) -> bool:
        """
        Search movement history on the STOCK_MOVEMENT form.

        Reads optional product filter from STOCK_SEARCH_TEXTBOX and populates
        STOCK_MOVEMENT_DATAGRID with WarehouseStockMovement records.
        """
        if not self.login_succeed:
            return False

        try:
            from user_interface.control import TextBox, DataGrid
            from pos.service.inventory_service import InventoryService
            from data_layer.model.definition.product import Product
            from data_layer.engine import Engine

            window = self.interface.window
            if not window:
                return False

            search_term = ""
            for child in window.children():
                if isinstance(child, TextBox):
                    if getattr(child, "name", "") == ControlName.STOCK_SEARCH_TEXTBOX.value:
                        search_term = child.text().strip()
                        break

            # Resolve product_id from search term if provided
            product_id = None
            if search_term:
                with Engine().get_session() as session:
                    from sqlalchemy import or_
                    p = session.query(Product).filter(
                        Product.is_deleted.is_(False),
                        or_(
                            Product.name.ilike(f"%{search_term}%"),
                            Product.code.ilike(f"%{search_term}%"),
                        )
                    ).first()
                    if p:
                        product_id = p.id

            history = InventoryService.get_movement_history(
                product_id=product_id,
                limit=200,
            )

            columns = ["Movement No", "Type", "Qty", "Before", "After", "Date", "Status", "Reason"]
            rows = [
                [
                    h["movement_number"],
                    h["movement_type"],
                    str(h["quantity"]),
                    str(h["quantity_before"]) if h["quantity_before"] is not None else "—",
                    str(h["quantity_after"]) if h["quantity_after"] is not None else "—",
                    h["movement_date"],
                    h["status"],
                    h["reason"],
                ]
                for h in history
            ]

            for child in window.children():
                if isinstance(child, DataGrid):
                    if getattr(child, "name", "") == ControlName.STOCK_MOVEMENT_DATAGRID.value:
                        child.set_columns(columns)
                        child.set_data(rows)
                        break

            logger.info("[STOCK_MOVEMENT_SEARCH] Loaded %s movement records", len(rows))
            return True

        except Exception as exc:
            logger.error("[STOCK_MOVEMENT_SEARCH] Error: %s", exc)
            return False

    # ================================================================== #
    #  Stub handlers (kept for completeness / future use)                  #
    # ================================================================== #

    def _stock_out_event(self) -> bool:
        logger.warning("[WarehouseEvent] Stock-out event — not separately implemented; handled via sale completion")
        return False

    def _stock_transfer_event(self) -> bool:
        logger.warning("[WarehouseEvent] Stock transfer — navigate to STOCK_IN and use transfer workflow")
        return False

    def _stock_count_event(self) -> bool:
        """Cycle count — delegates to adjustment form."""
        return self._stock_adjustment_event()

    def _warehouse_receipt_event(self) -> bool:
        return self._stock_in_event()

    def _warehouse_issue_event(self) -> bool:
        logger.warning("[WarehouseEvent] Warehouse issue — handled via sale completion flow")
        return False

    def _warehouse_transfer_event(self) -> bool:
        logger.warning("[WarehouseEvent] Warehouse transfer not yet implemented")
        return False

    def _warehouse_adjustment_event(self) -> bool:
        return self._stock_adjustment_event()

    def _warehouse_count_event(self) -> bool:
        return self._stock_adjustment_event()

    def _warehouse_location_event(self) -> bool:
        logger.warning("[WarehouseEvent] Warehouse location management not yet implemented")
        return False
