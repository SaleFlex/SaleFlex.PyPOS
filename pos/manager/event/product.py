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

from data_layer.enums import FormName, ControlName, EventName

from core.logger import get_logger

logger = get_logger(__name__)


class ProductEvent:
    """
    Event handlers for Product Management operations.

    Provides:
        _product_list_form_event  – navigate to the Product List / search form
        _product_search_event     – execute a product search and populate the datagrid
        _product_detail_event     – open the Product Detail dialog for the selected product
    """

    # ------------------------------------------------------------------ #
    #  Navigation                                                          #
    # ------------------------------------------------------------------ #

    def _product_list_form_event(self) -> bool:
        """
        Navigate to the Product List form.

        Returns:
            bool: True on success, False if the user is not authenticated.
        """
        if not self.login_succeed:
            self._logout_event()
            return False

        self.current_form_type = FormName.PRODUCT_LIST
        self.interface.redraw(form_name=FormName.PRODUCT_LIST.name)
        return True

    # ------------------------------------------------------------------ #
    #  Search                                                              #
    # ------------------------------------------------------------------ #

    def _product_search_event(self) -> bool:
        """
        Read the search textbox on the Product List form, query the database
        and populate the product datagrid with matching results.

        Matching logic:
            - Returns products whose ``name`` or ``short_name`` contains the
              search term (case-insensitive LIKE), or an exact prefix match.
            - An empty search term returns all non-deleted products (capped at
              500 rows to avoid performance problems on large catalogues).

        Returns:
            bool: True on success, False on error or missing authentication.
        """
        if not self.login_succeed:
            return False

        try:
            from user_interface.control import TextBox, DataGrid
            window = self.interface.window
            if not window:
                logger.error("[PRODUCT_SEARCH] Window not available")
                return False

            # 1. Read the search query from the dedicated textbox
            search_term = ""
            for child in window.children():
                if isinstance(child, TextBox):
                    name = getattr(child, "name", "") or getattr(child, "__name__", "")
                    if name == ControlName.PRODUCT_SEARCH_TEXTBOX.value:
                        search_term = child.text().strip()
                        break

            # 2. Query the database
            from data_layer.model.definition.product import Product
            from data_layer.engine import Engine

            engine = Engine()
            with engine.get_session() as session:
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
                        )
                    )

                products = query.order_by(Product.name).limit(500).all()

            # 3. Populate the datagrid
            columns = ["Code", "Name", "Short Name", "Sale Price", "Stock"]
            rows = []
            product_ids = []
            for p in products:
                rows.append([
                    p.code or "",
                    p.name or "",
                    p.short_name or "",
                    str(p.sale_price) if p.sale_price is not None else "",
                    str(p.stock) if p.stock is not None else "",
                ])
                product_ids.append(str(p.id))

            for child in window.children():
                if isinstance(child, DataGrid):
                    name = getattr(child, "name", "")
                    if name == ControlName.PRODUCT_LIST_DATAGRID.value:
                        child.set_columns(columns)
                        child.set_data(rows)
                        # Store product IDs on the datagrid for later retrieval
                        child._product_ids = product_ids
                        break

            logger.info("[PRODUCT_SEARCH] Found %s product(s) for query '%s'",
                        len(rows), search_term)
            return True

        except Exception as exc:
            logger.error("[PRODUCT_SEARCH] Error: %s", exc)
            return False

    # ------------------------------------------------------------------ #
    #  Detail                                                              #
    # ------------------------------------------------------------------ #

    def _product_detail_event(self) -> bool:
        """
        Open the Product Detail modal dialog for the currently selected row
        in the product datagrid.

        The dialog is a fully DB-driven ``DynamicDialog`` that renders the
        ``PRODUCT_DETAIL`` form (form_no=9) which contains a ``TABCONTROL``
        with four tabs: Product Info, Barcodes, Attributes, and Variants.

        Before showing the dialog this method stores the selected product UUID
        in ``self.current_product_id`` so the grid-population helpers in
        ``DynamicDialog`` and ``BaseWindow`` can load the correct data.

        Returns:
            bool: True if the dialog was opened, False if no row is selected
                  or if an error occurs.
        """
        if not self.login_succeed:
            return False

        try:
            from user_interface.control import DataGrid
            window = self.interface.window
            if not window:
                logger.error("[PRODUCT_DETAIL] Window not available")
                return False

            # Find the product datagrid and retrieve the selected product's UUID
            product_id = None
            for child in window.children():
                if isinstance(child, DataGrid):
                    name = getattr(child, "name", "")
                    if name == ControlName.PRODUCT_LIST_DATAGRID.value:
                        selected_index = child.get_selected_row_index()
                        product_ids = getattr(child, "_product_ids", [])
                        if 0 <= selected_index < len(product_ids):
                            product_id = product_ids[selected_index]
                        break

            if not product_id:
                logger.warning("[PRODUCT_DETAIL] No product selected")
                return False

            # Store for use by DynamicDialog grid-population helpers
            self.current_product_id = product_id

            # Show the DB-driven PRODUCT_DETAIL form as a modal dialog
            self.interface.show_modal(form_name=FormName.PRODUCT_DETAIL.name)

            logger.info("[PRODUCT_DETAIL] Opened detail for product id: %s", product_id)
            return True

        except Exception as exc:
            logger.error("[PRODUCT_DETAIL] Error: %s", exc)
            return False

    # ------------------------------------------------------------------ #
    #  Save                                                                #
    # ------------------------------------------------------------------ #

    def _product_detail_save_event(self) -> bool:
        """
        Save product info changes entered in the PRODUCT panel of the
        PRODUCT_DETAIL modal dialog back to the database.

        The PRODUCT panel contains label/textbox pairs whose textbox names
        (uppercase) map directly to ``Product`` model field names (lowercase).
        Only basic scalar fields (code, name, short_name, sale_price,
        purchase_price, stock, min_stock, max_stock, description) are written;
        FK references (unit, manufacturer) are not modified here.

        Returns:
            bool: True if the product was saved successfully, False otherwise.
        """
        if not self.login_succeed:
            return False

        try:
            # Retrieve the active modal dialog (PRODUCT_DETAIL is a modal)
            active_dialogs = getattr(self.interface, 'active_dialogs', [])
            if not active_dialogs:
                logger.error("[PRODUCT_DETAIL_SAVE] No active dialog found")
                return False

            dialog = active_dialogs[-1]

            # Read all textbox values from the PRODUCT panel
            values = dialog.get_panel_textbox_values("PRODUCT")
            if not values:
                logger.warning("[PRODUCT_DETAIL_SAVE] No values found in PRODUCT panel")
                return False

            logger.debug("[PRODUCT_DETAIL_SAVE] Collected values: %s", list(values.keys()))

            # Determine which product to update
            product_id = getattr(self, 'current_product_id', None)
            if not product_id:
                logger.error("[PRODUCT_DETAIL_SAVE] current_product_id is not set")
                return False

            from uuid import UUID as _UUID
            if isinstance(product_id, str):
                product_id = _UUID(product_id)

            from data_layer.model.definition.product import Product
            from data_layer.engine import Engine

            # Field type coercion map — only scalar editable fields
            _field_types = {
                'code':           str,
                'name':           str,
                'short_name':     str,
                'description':    str,
                'sale_price':     float,
                'purchase_price': float,
                'stock':          int,
                'min_stock':      int,
                'max_stock':      int,
            }

            engine = Engine()
            with engine.get_session() as session:
                product = session.query(Product).filter(
                    Product.id == product_id
                ).first()

                if not product:
                    logger.error("[PRODUCT_DETAIL_SAVE] Product not found for id: %s", product_id)
                    return False

                updated_fields = []
                for field_name, raw_value in values.items():
                    if field_name not in _field_types:
                        continue
                    try:
                        conv = _field_types[field_name]
                        if raw_value == '' or raw_value is None:
                            coerced = None
                        else:
                            coerced = conv(raw_value)
                        setattr(product, field_name, coerced)
                        updated_fields.append(field_name)
                    except (ValueError, TypeError) as exc:
                        logger.warning(
                            "[PRODUCT_DETAIL_SAVE] Could not convert field '%s' value '%s': %s",
                            field_name, raw_value, exc
                        )

                session.commit()
                logger.info(
                    "[PRODUCT_DETAIL_SAVE] Product '%s' saved. Fields updated: %s",
                    product.name, updated_fields
                )

            return True

        except Exception as exc:
            logger.error("[PRODUCT_DETAIL_SAVE] Error: %s", exc)
            return False
