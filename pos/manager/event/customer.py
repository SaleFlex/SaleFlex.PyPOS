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


class CustomerEvent:
    """
    Event handlers for Customer Management operations.

    Two separate customer list forms are supported:
      - ``CUSTOMER_LIST``   — opened from the Main Menu; has DETAIL + ADD + BACK buttons.
      - ``CUSTOMER_SELECT`` — opened from the SALE form (via FUNC → CUSTOMER dual button);
                              has SELECT + ADD + BACK buttons.  SELECT immediately assigns
                              the chosen customer to the active sale and returns to SALE.

    Provides:
        _customer_list_form_event    – navigate to CUSTOMER_LIST (Main Menu) or CUSTOMER_SELECT (SALE)
        _customer_select_form_event  – navigate directly to CUSTOMER_SELECT (SALE context)
        _customer_search_event       – execute a customer search (shared by both list forms)
        _customer_detail_event       – open the Customer Detail dialog for the selected customer
        _customer_detail_save_event  – save customer info changes from the detail dialog (create or update)
        _customer_add_event          – open a blank Customer Detail modal to add a new customer
        _customer_select_event       – assign selected (or last-added) customer to the active sale → SALE
        _customer_list_back_event    – context-aware BACK (legacy, CUSTOMER_LIST form)
        _assign_customer_to_sale     – helper: set fk_customer_id on the active TransactionHeadTemp
    """

    # ------------------------------------------------------------------ #
    #  Navigation                                                          #
    # ------------------------------------------------------------------ #

    def _customer_list_form_event(self) -> bool:
        """
        Navigate to the appropriate customer list form based on context:

        - Called from the **SALE form** → opens ``CUSTOMER_SELECT`` (SELECT + ADD + BACK).
        - Called from any other form   → opens ``CUSTOMER_LIST``   (DETAIL + ADD + BACK).

        Sets ``_customer_from_sale`` so that subsequent events know the context.

        Returns:
            bool: True on success, False if the user is not authenticated.
        """
        if not self.login_succeed:
            self._logout_event()
            return False

        # Detect whether we were called from the SALE form
        self._customer_from_sale = (
            getattr(self, 'current_form_type', None) == FormName.SALE
        )

        if self._customer_from_sale:
            # Reset previous sale-customer selection; the cashier must pick again
            self.current_sale_customer_id = None
            logger.info("[CUSTOMER_LIST] Opened from SALE form — routing to CUSTOMER_SELECT")
            self.current_form_type = FormName.CUSTOMER_SELECT
            self.interface.redraw(form_name=FormName.CUSTOMER_SELECT.name)
        else:
            logger.info("[CUSTOMER_LIST] Opened from non-SALE form — routing to CUSTOMER_LIST")
            self.current_form_type = FormName.CUSTOMER_LIST
            self.interface.redraw(form_name=FormName.CUSTOMER_LIST.name)

        return True

    def _customer_select_form_event(self) -> bool:
        """
        Navigate directly to the ``CUSTOMER_SELECT`` form (SALE context).

        This is an explicit entry point for ``CUSTOMER_SELECT_FORM`` events so that
        the SALE form dual button can target it directly if desired.

        Returns:
            bool: True on success, False if the user is not authenticated.
        """
        if not self.login_succeed:
            self._logout_event()
            return False

        self._customer_from_sale = True
        self.current_sale_customer_id = None
        self.current_form_type = FormName.CUSTOMER_SELECT
        self.interface.redraw(form_name=FormName.CUSTOMER_SELECT.name)
        logger.info("[CUSTOMER_SELECT_FORM] Navigated to CUSTOMER_SELECT form")
        return True

    # ------------------------------------------------------------------ #
    #  Search                                                              #
    # ------------------------------------------------------------------ #

    def _customer_search_event(self) -> bool:
        """
        Read the search textbox on the Customer List form, query the database
        and populate the customer datagrid with matching results.

        Matching logic:
            - Returns customers whose ``name``, ``last_name``, ``phone_number``,
              or ``email_address`` contains the search term (case-insensitive).
            - An empty search term returns all active non-deleted customers
              (capped at 500 rows).
            - Walk-in customer is excluded from results.

        Returns:
            bool: True on success, False on error or missing authentication.
        """
        if not self.login_succeed:
            return False

        try:
            from user_interface.control import TextBox, DataGrid
            window = self.interface.window
            if not window:
                logger.error("[CUSTOMER_SEARCH] Window not available")
                return False

            # 1. Read the search query from the dedicated textbox
            search_term = ""
            for child in window.children():
                if isinstance(child, TextBox):
                    name = getattr(child, "name", "") or getattr(child, "__name__", "")
                    if name == ControlName.CUSTOMER_SEARCH_TEXTBOX.value:
                        search_term = child.text().strip()
                        break

            # 2. Query the database
            from data_layer.model.definition.customer import Customer
            from data_layer.engine import Engine
            from sqlalchemy import or_

            engine = Engine()
            with engine.get_session() as session:
                query = session.query(Customer).filter(
                    Customer.is_deleted.is_(False),
                    Customer.is_walkin.is_(False),
                )

                if search_term:
                    like_term = f"%{search_term}%"
                    from pos.service.loyalty_service import LoyaltyService

                    or_clauses = [
                        Customer.name.ilike(like_term),
                        Customer.last_name.ilike(like_term),
                        Customer.phone_number.ilike(like_term),
                        Customer.email_address.ilike(like_term),
                    ]
                    cc = LoyaltyService.default_phone_country_for_search()
                    normalized = LoyaltyService.normalize_phone(search_term, cc)
                    if normalized:
                        or_clauses.append(Customer.phone_normalized == normalized)
                    query = query.filter(or_(*or_clauses))

                customers = query.order_by(Customer.last_name, Customer.name).limit(500).all()

            # 3. Populate the datagrid
            columns = ["First Name", "Last Name", "Phone", "E-mail", "City"]
            rows = []
            customer_ids = []
            for c in customers:
                rows.append([
                    c.name or "",
                    c.last_name or "",
                    c.phone_number or "",
                    c.email_address or "",
                    c.address_line_3 or "",
                ])
                customer_ids.append(str(c.id))

            for child in window.children():
                if isinstance(child, DataGrid):
                    name = getattr(child, "name", "")
                    if name == ControlName.CUSTOMER_LIST_DATAGRID.value:
                        child.set_columns(columns)
                        child.set_data(rows)
                        child._customer_ids = customer_ids
                        break

            logger.info("[CUSTOMER_SEARCH] Found %s customer(s) for query '%s'",
                        len(rows), search_term)
            return True

        except Exception as exc:
            logger.error("[CUSTOMER_SEARCH] Error: %s", exc)
            return False

    # ------------------------------------------------------------------ #
    #  Detail                                                              #
    # ------------------------------------------------------------------ #

    def _customer_detail_event(self) -> bool:
        """
        Open the Customer Detail modal dialog for the currently selected row
        in the customer datagrid.

        The dialog is a fully DB-driven ``DynamicDialog`` that renders the
        ``CUSTOMER_DETAIL`` form (form_no=18) which contains a ``TABCONTROL``
        with two tabs: Customer Info and Activity History.

        Before showing the dialog this method stores the selected customer UUID
        in ``self.current_customer_id`` so the tab-population helpers can load
        the correct data.

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
                logger.error("[CUSTOMER_DETAIL] Window not available")
                return False

            # Find the customer datagrid and retrieve the selected customer's UUID
            customer_id = None
            for child in window.children():
                if isinstance(child, DataGrid):
                    name = getattr(child, "name", "")
                    if name == ControlName.CUSTOMER_LIST_DATAGRID.value:
                        selected_index = child.get_selected_row_index()
                        customer_ids = getattr(child, "_customer_ids", [])
                        if 0 <= selected_index < len(customer_ids):
                            customer_id = customer_ids[selected_index]
                        break

            if not customer_id:
                logger.warning("[CUSTOMER_DETAIL] No customer selected")
                return False

            # Store for use by DynamicDialog grid-population helpers
            self.current_customer_id = customer_id
            # Edit mode: allow DynamicDialog to auto-load customer data into panel
            self._customer_add_mode = False

            # When opened from the SALE form, record this customer as the intended
            # sale-customer so that BACK on the list will assign them to the transaction.
            if getattr(self, '_customer_from_sale', False):
                self.current_sale_customer_id = customer_id
                logger.info(
                    "[CUSTOMER_DETAIL] Sale context — pre-selected customer for sale: %s",
                    customer_id
                )

            # Show the DB-driven CUSTOMER_DETAIL form as a modal dialog
            self.interface.show_modal(form_name=FormName.CUSTOMER_DETAIL.name)

            logger.info("[CUSTOMER_DETAIL] Opened detail for customer id: %s", customer_id)
            return True

        except Exception as exc:
            logger.error("[CUSTOMER_DETAIL] Error: %s", exc)
            return False

    # ------------------------------------------------------------------ #
    #  Save                                                                #
    # ------------------------------------------------------------------ #

    def _customer_detail_save_event(self) -> bool:
        """
        Save customer info changes entered in the CUSTOMER panel of the
        CUSTOMER_DETAIL modal dialog back to the database.

        Handles two scenarios:
        - **Update** (``current_customer_id`` is set): updates the existing ``Customer`` record.
        - **Create** (``current_customer_id`` is None / empty): inserts a new ``Customer`` record.

        When the form was opened from the SALE form (``_customer_from_sale = True``), the
        saved customer's UUID is stored in ``current_sale_customer_id`` so that the
        context-aware BACK button on the Customer List can assign it to the active sale.

        Returns:
            bool: True if the customer was saved successfully, False otherwise.
        """
        if not self.login_succeed:
            return False

        try:
            # Retrieve the active modal dialog
            active_dialogs = getattr(self.interface, 'active_dialogs', [])
            if not active_dialogs:
                logger.error("[CUSTOMER_DETAIL_SAVE] No active dialog found")
                return False

            dialog = active_dialogs[-1]

            # Read all textbox values from the CUSTOMER panel
            values = dialog.get_panel_textbox_values("CUSTOMER")
            if not values:
                logger.warning("[CUSTOMER_DETAIL_SAVE] No values found in CUSTOMER panel")
                return False

            logger.debug("[CUSTOMER_DETAIL_SAVE] Collected values: %s", list(values.keys()))

            from data_layer.model.definition.customer import Customer
            from data_layer.engine import Engine

            # Only basic scalar text fields are editable in the info panel
            _editable_fields = {
                'name', 'last_name', 'phone_number', 'email_address',
                'address_line_1', 'address_line_2', 'address_line_3',
                'zip_code', 'description',
            }

            customer_id = getattr(self, 'current_customer_id', None)

            if not customer_id:
                # ── CREATE new customer ──────────────────────────────────
                engine = Engine()
                with engine.get_session() as session:
                    new_customer = Customer(
                        is_active=True,
                        is_walkin=False,
                    )
                    for field_name, raw_value in values.items():
                        if field_name.lower() not in _editable_fields:
                            continue
                        coerced = str(raw_value).strip() if raw_value else None
                        setattr(new_customer, field_name.lower(), coerced)

                    from pos.service.loyalty_service import LoyaltyService

                    LoyaltyService.sync_customer_phone_normalized(session, new_customer)
                    dup = LoyaltyService.validate_unique_phone_normalized(session, new_customer)
                    if dup:
                        from user_interface.form.message_form import MessageForm

                        MessageForm.show_error(self.interface.window, dup, "Telefon")
                        return False

                    session.add(new_customer)
                    session.commit()
                    session.refresh(new_customer)

                    new_id = str(new_customer.id)
                    self.current_customer_id = new_id
                    # Leave add mode now that the record exists
                    self._customer_add_mode = False

                    # If opened from SALE, mark this new customer for assignment
                    if getattr(self, '_customer_from_sale', False):
                        self.current_sale_customer_id = new_id
                        self.current_sale_customer_name = (
                            new_customer.name or ""
                        ).strip()

                    logger.info(
                        "[CUSTOMER_DETAIL_SAVE] New customer created: '%s %s' (id=%s)",
                        new_customer.name, new_customer.last_name, new_id
                    )

                    from pos.service.customer_segment_service import CustomerSegmentService

                    CustomerSegmentService.sync_for_customer_id(new_customer.id)

                    if hasattr(dialog, "repopulate_customer_activity_grid"):
                        dialog.repopulate_customer_activity_grid()
            else:
                # ── UPDATE existing customer ─────────────────────────────
                from uuid import UUID as _UUID
                if isinstance(customer_id, str):
                    customer_id = _UUID(customer_id)

                engine = Engine()
                with engine.get_session() as session:
                    customer = session.query(Customer).filter(
                        Customer.id == customer_id
                    ).first()

                    if not customer:
                        logger.error("[CUSTOMER_DETAIL_SAVE] Customer not found for id: %s", customer_id)
                        return False

                    if customer.is_walkin:
                        logger.warning("[CUSTOMER_DETAIL_SAVE] Walk-in customer cannot be edited")
                        return False

                    updated_fields = []
                    for field_name, raw_value in values.items():
                        if field_name.lower() not in _editable_fields:
                            continue
                        try:
                            coerced = str(raw_value).strip() if raw_value else None
                            setattr(customer, field_name.lower(), coerced)
                            updated_fields.append(field_name)
                        except (ValueError, TypeError) as exc:
                            logger.warning(
                                "[CUSTOMER_DETAIL_SAVE] Could not process field '%s' value '%s': %s",
                                field_name, raw_value, exc
                            )

                    from pos.service.loyalty_service import LoyaltyService

                    LoyaltyService.sync_customer_phone_normalized(session, customer)
                    dup = LoyaltyService.validate_unique_phone_normalized(session, customer)
                    if dup:
                        from user_interface.form.message_form import MessageForm

                        MessageForm.show_error(self.interface.window, dup, "Telefon")
                        return False

                    session.commit()

                    from pos.service.customer_segment_service import CustomerSegmentService

                    CustomerSegmentService.sync_for_customer_id(customer_id)

                    # If opened from SALE, ensure sale-customer is recorded
                    if getattr(self, '_customer_from_sale', False):
                        self.current_sale_customer_id = str(customer_id)

                    logger.info(
                        "[CUSTOMER_DETAIL_SAVE] Customer '%s %s' updated. Fields: %s",
                        customer.name, customer.last_name, updated_fields
                    )

                    if hasattr(dialog, "repopulate_customer_activity_grid"):
                        dialog.repopulate_customer_activity_grid()

            return True

        except Exception as exc:
            logger.error("[CUSTOMER_DETAIL_SAVE] Error: %s", exc)
            return False

    # ------------------------------------------------------------------ #
    #  SELECT (CUSTOMER_SELECT form — SALE context)                       #
    # ------------------------------------------------------------------ #

    def _customer_select_event(self) -> bool:
        """
        Assign the chosen customer to the active sale transaction and navigate
        back to the SALE form.

        Selection priority:
        1. A row highlighted in the ``CUSTOMER_LIST_DATAGRID`` on the current window.
        2. ``current_sale_customer_id`` — set by ``_customer_add_event`` +
           ``_customer_detail_save_event`` when a new customer was just created.

        If neither source yields a customer ID the event is a no-op (warning logged).

        Returns:
            bool: True on success, False if no customer could be identified or an
                  error occurs.
        """
        if not self.login_succeed:
            return False

        try:
            customer_id = None

            # Priority 1 — row selected in the datagrid
            from user_interface.control import DataGrid
            window = self.interface.window
            if window:
                for child in window.children():
                    if isinstance(child, DataGrid):
                        name = getattr(child, "name", "")
                        if name == ControlName.CUSTOMER_LIST_DATAGRID.value:
                            selected_index = child.get_selected_row_index()
                            customer_ids = getattr(child, "_customer_ids", [])
                            if 0 <= selected_index < len(customer_ids):
                                customer_id = customer_ids[selected_index]
                            break

            # Priority 2 — customer created via ADD on this form
            if not customer_id:
                customer_id = getattr(self, 'current_sale_customer_id', None)

            if not customer_id:
                logger.warning(
                    "[CUSTOMER_SELECT] No customer selected and no recently added customer — "
                    "select a row or press ADD first"
                )
                return False

            # Assign customer to sale and navigate back
            self._assign_customer_to_sale(customer_id)
            self._customer_from_sale = False

            logger.info("[CUSTOMER_SELECT] Customer %s selected — returning to SALE", customer_id)
            return self._back_event()

        except Exception as exc:
            logger.error("[CUSTOMER_SELECT] Error: %s", exc)
            return False

    # ------------------------------------------------------------------ #
    #  Add new customer                                                    #
    # ------------------------------------------------------------------ #

    def _customer_add_event(self) -> bool:
        """
        Open the Customer Detail modal dialog with an empty (blank) panel,
        allowing the cashier to fill in details for a new customer and save.

        Sets ``current_customer_id = None`` so that the SAVE handler knows to
        create a new ``Customer`` record instead of updating an existing one.
        Sets ``_customer_add_mode = True`` so that DynamicDialog skips the
        fallback model-loading step (which would otherwise load the Walk-in
        Customer and pre-fill the panel).

        Returns:
            bool: True if the dialog was opened, False on error.
        """
        if not self.login_succeed:
            return False

        # Signal "add" mode: no existing customer; suppress auto-load in DynamicDialog
        self.current_customer_id = None
        self._customer_add_mode = True

        self.interface.show_modal(form_name=FormName.CUSTOMER_DETAIL.name)
        logger.info("[CUSTOMER_ADD] Opened blank Customer Detail modal for new customer")
        return True

    # ------------------------------------------------------------------ #
    #  Context-aware BACK from Customer List                               #
    # ------------------------------------------------------------------ #

    def _customer_list_back_event(self) -> bool:
        """
        Context-aware BACK navigation from the Customer List form.

        - **SALE context** (``_customer_from_sale = True``): If a customer was
          selected or created (``current_sale_customer_id`` is set), the customer
          is assigned to the active sale transaction's ``TransactionHeadTemp`` record
          before navigating back to SALE.  If no customer was chosen the form history
          is still popped and the cashier returns to SALE without any change.
        - **Main-Menu context**: behaves identically to the generic ``_back_event``.

        Returns:
            bool: True on successful navigation, False otherwise.
        """
        if getattr(self, '_customer_from_sale', False):
            sale_customer_id = getattr(self, 'current_sale_customer_id', None)
            if sale_customer_id:
                self._assign_customer_to_sale(sale_customer_id)
            else:
                logger.info(
                    "[CUSTOMER_LIST_BACK] Sale context but no customer selected — "
                    "returning to SALE without customer assignment"
                )
            # Always clear the SALE context flag when leaving the list
            self._customer_from_sale = False

        return self._back_event()

    # ------------------------------------------------------------------ #
    #  Helper                                                              #
    # ------------------------------------------------------------------ #

    def _assign_customer_to_sale(self, customer_id) -> bool:
        """
        Assign the given customer to the active sale transaction.

        Updates ``fk_customer_id`` on the ``TransactionHeadTemp`` record held in
        ``self.document_data['head']`` and persists the change to the database.

        Args:
            customer_id: UUID or UUID string of the customer to assign.

        Returns:
            bool: True on success, False if no active document is present or an
                  error occurs.
        """
        try:
            if not self.document_data:
                logger.warning("[ASSIGN_CUSTOMER] No active document — cannot assign customer")
                return False

            doc = self.document_data
            if hasattr(doc, 'unwrap'):
                doc = doc.unwrap()

            head = doc.get('head') if isinstance(doc, dict) else None
            if head is None:
                logger.warning("[ASSIGN_CUSTOMER] No 'head' key in document_data")
                return False

            from data_layer.auto_save import AutoSaveModel
            head_obj = head.unwrap() if isinstance(head, AutoSaveModel) else head

            from uuid import UUID as _UUID
            if isinstance(customer_id, str):
                customer_id = _UUID(customer_id)

            head_obj.fk_customer_id = customer_id
            if hasattr(head_obj, 'save'):
                head_obj.save()

            from pos.service.loyalty_service import LoyaltyService

            LoyaltyService.ensure_loyalty_on_sale_assignment(head_obj, customer_id)

            # Update the display name shown in the status bar
            try:
                from data_layer.model.definition.customer import Customer as _Customer
                cust = _Customer.get_by_id(customer_id)
                if cust:
                    self.current_sale_customer_name = (cust.name or "").strip() or "Walk-in"
                else:
                    self.current_sale_customer_name = "Walk-in"
            except Exception:
                self.current_sale_customer_name = "Walk-in"

            logger.info(
                "[ASSIGN_CUSTOMER] Customer %s (%s) assigned to active sale transaction",
                customer_id, self.current_sale_customer_name
            )

            try:
                from pos.service import SaleService

                win = None
                if hasattr(self, "interface") and self.interface:
                    win = getattr(self.interface, "window", None)
                SaleService.refresh_campaign_discounts_after_cart_change(
                    self.document_data,
                    win,
                    getattr(self, "product_data", None),
                )
            except Exception as exc:
                logger.warning("[ASSIGN_CUSTOMER] Campaign refresh after assign: %s", exc)

            return True

        except Exception as exc:
            logger.error("[ASSIGN_CUSTOMER] Error assigning customer to sale: %s", exc)
            return False
