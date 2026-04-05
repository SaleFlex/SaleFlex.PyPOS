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

from data_layer.enums import FormName, ControlName

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
