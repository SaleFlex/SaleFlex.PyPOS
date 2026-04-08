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

    Provides:
        _customer_list_form_event  – navigate to the Customer List / search form
        _customer_search_event     – execute a customer search and populate the datagrid
        _customer_detail_event     – open the Customer Detail dialog for the selected customer
        _customer_detail_save_event – save customer info changes from the detail dialog
    """

    # ------------------------------------------------------------------ #
    #  Navigation                                                          #
    # ------------------------------------------------------------------ #

    def _customer_list_form_event(self) -> bool:
        """
        Navigate to the Customer List form.

        Returns:
            bool: True on success, False if the user is not authenticated.
        """
        if not self.login_succeed:
            self._logout_event()
            return False

        self.current_form_type = FormName.CUSTOMER_LIST
        self.interface.redraw(form_name=FormName.CUSTOMER_LIST.name)
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
                    query = query.filter(
                        or_(
                            Customer.name.ilike(like_term),
                            Customer.last_name.ilike(like_term),
                            Customer.phone_number.ilike(like_term),
                            Customer.email_address.ilike(like_term),
                        )
                    )

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

        The CUSTOMER panel contains label/textbox pairs whose textbox names
        (uppercase) map directly to ``Customer`` model field names (lowercase).

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

            # Determine which customer to update
            customer_id = getattr(self, 'current_customer_id', None)
            if not customer_id:
                logger.error("[CUSTOMER_DETAIL_SAVE] current_customer_id is not set")
                return False

            from uuid import UUID as _UUID
            if isinstance(customer_id, str):
                customer_id = _UUID(customer_id)

            from data_layer.model.definition.customer import Customer
            from data_layer.engine import Engine

            # Only basic scalar text fields are editable in the info panel
            _field_types = {
                'name':           str,
                'last_name':      str,
                'phone_number':   str,
                'email_address':  str,
                'address_line_1': str,
                'address_line_2': str,
                'address_line_3': str,
                'zip_code':       str,
                'description':    str,
            }

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
                    if field_name.lower() not in _field_types:
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

                session.commit()
                logger.info(
                    "[CUSTOMER_DETAIL_SAVE] Customer '%s %s' saved. Fields updated: %s",
                    customer.name, customer.last_name, updated_fields
                )

            return True

        except Exception as exc:
            logger.error("[CUSTOMER_DETAIL_SAVE] Error: %s", exc)
            return False
