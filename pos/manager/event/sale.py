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



from core.logger import get_logger

logger = get_logger(__name__)

class SaleEvent:
    """
    Sales Event Handler for POS transaction operations.
    
    This class handles all sales-related events including:
    - Department and PLU sales
    - Product lookup and selection
    - Quantity and price modifications
    - Transaction cancellations and voids
    - Discount and surcharge operations
    - Subtotal and total calculations
    
    All methods require valid authentication and return True on success,
    False on failure. Methods update the current transaction state and
    refresh the display as needed.
    """
    
    def _check_stock_for_sale(self, product, quantity: float, window=None) -> bool:
        """
        Validate that the product can be sold in the requested quantity.

        Calls InventoryService.can_sell().  If the check fails and window is
        provided, shows a red error MessageForm.  If the product allows
        negative stock the check always passes.

        Args:
            product: Product ORM instance (from product_data cache)
            quantity: Quantity the cashier wants to sell
            window: Optional QWidget for displaying the error dialog

        Returns:
            bool: True if the sale is allowed, False if it must be blocked
        """
        try:
            from pos.service.inventory_service import InventoryService
            allowed, reason = InventoryService.can_sell(product, quantity)
            if not allowed:
                logger.warning("[STOCK_CHECK] %s", reason)
                if window:
                    from user_interface.form.message_form import MessageForm
                    MessageForm.show_error(window, reason, "Insufficient Stock")
                return False
            return True
        except Exception as exc:
            logger.error("[STOCK_CHECK] Error during stock check: %s", exc)
            return True  # Fail-open: don't block sale on unexpected errors

    def _ensure_document_open(self):
        """
        Ensure that document_data exists and is open (not closed).
        
        This method checks if document_data exists and is in an open state.
        If document_data is None or the document is closed/completed, 
        it creates a new empty document.
        
        Returns:
            bool: True if document is open (or was successfully created), False otherwise
        """
        from data_layer.model.definition.transaction_status import TransactionStatus
        
        # Check if document_data exists
        if not self.document_data:
            logger.debug("[ENSURE_DOCUMENT_OPEN] document_data is None, creating empty document...")
            if not self.create_empty_document():
                logger.error("[ENSURE_DOCUMENT_OPEN] Failed to create empty document")
                return False
            return True
        
        # Check if document has a head
        if not self.document_data.get("head"):
            logger.debug("[ENSURE_DOCUMENT_OPEN] document_data has no head, creating empty document...")
            if not self.create_empty_document():
                logger.error("[ENSURE_DOCUMENT_OPEN] Failed to create empty document")
                return False
            return True
        
        # Check if document is closed or completed
        head = self.document_data["head"]
        is_closed = getattr(head, 'is_closed', False)
        transaction_status = getattr(head, 'transaction_status', None)
        
        if is_closed or transaction_status == TransactionStatus.COMPLETED.value:
            logger.debug("[ENSURE_DOCUMENT_OPEN] Document is closed (is_closed=%s, status=%s), creating new empty document...", is_closed, transaction_status)
            if not self.create_empty_document():
                logger.error("[ENSURE_DOCUMENT_OPEN] Failed to create empty document")
                return False
            return True
        
        # Document is open and ready
        return True
    
    def _update_document_data_for_sale(self, sale_type, product=None, department=None, 
                                       quantity=1.0, unit_price=0.0, product_barcode=None, 
                                       department_no=None, line_no=None):
        """
        Update document_data with sale information.
        
        This method delegates to SaleService.add_sale_to_document for the actual
        business logic, keeping the event handler focused on UI coordination.
        
        Args:
            sale_type: "PLU_CODE", "PLU_BARCODE", or "DEPARTMENT"
            product: Product object (for PLU sales)
            department: DepartmentMainGroup or DepartmentSubGroup object (for department sales)
            quantity: Quantity sold
            unit_price: Unit price
            product_barcode: ProductBarcode object (for PLU_BARCODE sales)
            department_no: Department number (for department sales)
            line_no: Line number in sale list (row number)
        
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            from pos.service import SaleService
            
            if not self.document_data or not self.document_data.get("head"):
                logger.debug("[UPDATE_DOCUMENT_DATA] No document_data or head found")
                return False
            
            # Get current currency
            current_currency = self.current_currency if hasattr(self, 'current_currency') and self.current_currency else None
            
            # Get cashier data
            cashier_data = self.cashier_data if hasattr(self, 'cashier_data') and self.cashier_data else None
            
            # Delegate to SaleService
            success = SaleService.add_sale_to_document(
                document_data=self.document_data,
                sale_type=sale_type,
                product=product,
                department=department,
                quantity=quantity,
                unit_price=unit_price,
                product_barcode=product_barcode,
                department_no=department_no,
                line_no=line_no,
                product_data=self.product_data,
                current_currency=current_currency,
                closure=self.closure if hasattr(self, 'closure') else None,
                cashier_data=cashier_data
            )
            
            if success:
                # Save document_data (AutoSaveDescriptor will handle saving)
                self.document_data = self.document_data
                logger.info("[UPDATE_DOCUMENT_DATA] ✓ Updated document_data for %s sale", sale_type)
                from pos.peripherals.hooks import sync_line_display_from_document
                sync_line_display_from_document(self, self.document_data)
            
            return success
            
        except Exception as e:
            logger.error("[UPDATE_DOCUMENT_DATA] Error updating document_data: %s", e)
            return False
    
    # ==================== DEPARTMENT SALES EVENTS ====================
    
    def _sale_department_event(self, button=None):
        """
        Handle department-based sale entry.
        
        Allows sale of items by department category rather than specific PLU.
        User enters price manually and system records sale under department.
        
        Process:
        1. Verify authentication and transaction state
        2. Extract department number from button name (remove "DEPARTMENT" prefix)
        3. Get price from numpad
        4. Look up department info from department_main_group (1-99) or department_sub_group (>99)
        5. Check max_price if defined
        6. Add department sale to current transaction
        7. Update transaction display
        
        Parameters:
            button: Button object that was clicked (contains control_name attribute)
        
        Returns:
            bool: True if department sale successful, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
        
        # Ensure document is open (create new if None or closed)
        if not self._ensure_document_open():
            logger.error("[SALE_DEPARTMENT] Failed to ensure document is open")
            return False
        
        try:
            # Get button control name
            if button is None or not hasattr(button, 'control_name'):
                logger.debug("[SALE_DEPARTMENT] No button provided or button missing control_name")
                return False
            
            control_name = button.control_name
            logger.debug("[SALE_DEPARTMENT] Processing button with control_name: '%s'", control_name)
            
            # Check if control name starts with "DEPARTMENT"
            if not control_name or not control_name.upper().startswith("DEPARTMENT"):
                logger.debug("[SALE_DEPARTMENT] Control name '%s' does not start with DEPARTMENT", control_name)
                return False
            
            # Extract department number from control name (remove "DEPARTMENT" prefix)
            department_no_str = control_name[10:]  # Remove first 10 characters "DEPARTMENT"
            logger.debug("[SALE_DEPARTMENT] Extracted department number string: '%s'", department_no_str)
            
            if not department_no_str:
                logger.debug("[SALE_DEPARTMENT] Empty department number after removing DEPARTMENT prefix")
                return False
            
            try:
                department_no = int(department_no_str)
            except ValueError:
                logger.debug("[SALE_DEPARTMENT] Invalid department number: '%s'", department_no_str)
                return False
            
            logger.debug("[SALE_DEPARTMENT] Department number: %s", department_no)
            
            # Find numpad widget in the current window to get price
            current_window = button.parent() if button else None
            numpad = None
            
            if current_window:
                # Search for NumPad widget in window's children
                from user_interface.control.numpad.numpad import NumPad
                for child in current_window.children():
                    if isinstance(child, NumPad):
                        numpad = child
                        break
            
            if not numpad:
                logger.error("[SALE_DEPARTMENT] NumPad widget not found in current window")
                return False
            
            # Get price from numpad
            numpad_text = numpad.get_text()
            logger.debug("[SALE_DEPARTMENT] NumPad text: '%s'", numpad_text)
            
            if not numpad_text or numpad_text.strip() == "":
                logger.debug("[SALE_DEPARTMENT] No price entered in numpad")
                
                # Show error message using MessageForm
                try:
                    from user_interface.form.message_form import MessageForm
                    from data_layer.model import LabelValue
                    
                    # Get error message from LabelValue
                    label_values = LabelValue.filter_by(key="NoAmountEntered", culture_info="en-GB", is_deleted=False)
                    if label_values and len(label_values) > 0:
                        error_message = label_values[0].value
                    else:
                        error_message = "Please enter an amount."
                    
                    # Show error dialog
                    MessageForm.show_error(current_window, error_message, "")
                except Exception as e:
                    logger.error("[SALE_DEPARTMENT] Error showing message form: %s", e)
                
                return False
            
            try:
                # Convert numpad text to integer (numpad value is multiplied by 10^decimal_places)
                numpad_value = int(numpad_text)
            except ValueError:
                logger.debug("[SALE_DEPARTMENT] Invalid price format: '%s'", numpad_text)
                return False
            
            logger.debug("[SALE_DEPARTMENT] NumPad value (before division): %s", numpad_value)
            
            # Get current currency and divide by 10^decimal_places
            from user_interface.form.message_form import MessageForm
            from data_layer.model import LabelValue
            
            # Get current currency from CurrentData
            current_currency_sign = self.current_currency if hasattr(self, 'current_currency') and self.current_currency else "GBP"
            logger.debug("[SALE_DEPARTMENT] Current currency sign: '%s'", current_currency_sign)
            
            # Find currency from product_data (more efficient than database query)
            decimal_places = 2  # Default
            try:
                # Try to get currency from product_data if available
                if hasattr(self, 'product_data') and self.product_data:
                    all_currencies = self.product_data.get("Currency", [])
                    currency = next((c for c in all_currencies if c.sign == current_currency_sign and not c.is_deleted), None)
                    if currency and currency.decimal_places is not None:
                        decimal_places = currency.decimal_places
                        logger.debug("[SALE_DEPARTMENT] Currency decimal_places from product_data: %s", decimal_places)
                    else:
                        logger.error("[SALE_DEPARTMENT] Currency not found in product_data with sign: '%s', defaulting to decimal_places=2", current_currency_sign)
                else:
                    # Fallback: query from database
                    from data_layer.model import Currency
                    currencies = Currency.filter_by(sign=current_currency_sign, is_deleted=False)
                    if currencies and len(currencies) > 0:
                        currency = currencies[0]
                        decimal_places = currency.decimal_places if currency.decimal_places is not None else 2
                        logger.debug("[SALE_DEPARTMENT] Currency decimal_places from database: %s", decimal_places)
                    else:
                        logger.error("[SALE_DEPARTMENT] Currency not found with sign: '%s', defaulting to decimal_places=2", current_currency_sign)
            except Exception as e:
                logger.error("[SALE_DEPARTMENT] Error getting currency decimal_places: %s, defaulting to 2", e)
                decimal_places = 2
            
            # Divide by 10^decimal_places to get actual price
            divisor = 10 ** decimal_places
            price = float(numpad_value) / divisor
            logger.debug("[SALE_DEPARTMENT] Price after division (numpad_value / %s): %s", divisor, price)
            
            # Import SaleList
            from user_interface.control.sale_list.sale_list import SaleList
            
            department = None
            department_name = ""
            
            # Determine which table to query based on department number
            if 1 <= department_no <= 99:
                # Query department_main_group from product_data cache
                logger.debug("[SALE_DEPARTMENT] Querying department_main_group for code: '%s'", department_no)
                departments = [
                    d for d in self.product_data.get("DepartmentMainGroup", [])
                    if d.code == str(department_no) and not (hasattr(d, 'is_deleted') and d.is_deleted)
                ]
                
                if not departments or len(departments) == 0:
                    logger.debug("[SALE_DEPARTMENT] No department_main_group found with code: '%s'", department_no)
                    return False
                
                department = departments[0]
                department_name = department.name if department.name else f"Department {department_no}"
                logger.debug("[SALE_DEPARTMENT] Found department_main_group: %s", department_name)
                
            elif department_no > 99:
                # Query department_sub_group from product_data cache
                logger.debug("[SALE_DEPARTMENT] Querying department_sub_group for code: '%s'", department_no)
                departments = [
                    d for d in self.product_data.get("DepartmentSubGroup", [])
                    if d.code == str(department_no) and not (hasattr(d, 'is_deleted') and d.is_deleted)
                ]
                
                if not departments or len(departments) == 0:
                    logger.debug("[SALE_DEPARTMENT] No department_sub_group found with code: '%s'", department_no)
                    return False
                
                department = departments[0]
                department_name = department.name if department.name else f"Department {department_no}"
                logger.debug("[SALE_DEPARTMENT] Found department_sub_group: %s", department_name)
            else:
                logger.debug("[SALE_DEPARTMENT] Invalid department number range: %s", department_no)
                return False
            
            # Check max_price if defined
            if department.max_price is not None:
                max_price = float(department.max_price)
                logger.debug("[SALE_DEPARTMENT] Max price check: %s <= %s", price, max_price)
                
                if price > max_price:
                    logger.debug("[SALE_DEPARTMENT] Price %s exceeds max_price %s", price, max_price)
                    
                    # Show error message using MessageForm
                    try:
                        # Get error message from LabelValue
                        label_values = LabelValue.filter_by(key="PriceExceedsMaxPrice", culture_info="en-GB", is_deleted=False)
                        if label_values and len(label_values) > 0:
                            error_message_template = label_values[0].value
                            # Replace placeholders
                            error_message = error_message_template.replace("{price}", f"{price:.2f}").replace("{max_price}", f"{max_price:.2f}")
                        else:
                            error_message = f"The price entered ({price:.2f}) is greater than the allowed amount({max_price:.2f})."
                        
                        # Show error dialog
                        MessageForm.show_error(current_window, error_message, "")
                    except Exception as e:
                        logger.error("[SALE_DEPARTMENT] Error showing message form: %s", e)
                    
                    return False
            
            # Find sale_list widget in the current window
            sale_list = None
            
            if current_window:
                # Check if window has sale_list attribute (set in _create_sale_list)
                if hasattr(current_window, 'sale_list'):
                    sale_list = current_window.sale_list
                else:
                    # Fallback: Search for SaleList widget in window's children
                    for child in current_window.children():
                        if isinstance(child, SaleList):
                            sale_list = child
                            break
            
            if not sale_list:
                logger.error("[SALE_DEPARTMENT] SaleList widget not found in current window")
                return False
            
            # Add department sale to sale list
            quantity = 1.0  # Default quantity for department sales
            
            success = sale_list.add_product(
                product_name=department_name,
                quantity=quantity,
                unit_price=price,
                department_no=department_no,
                reference_id=0,  # Department uses UUID, so we use 0 and rely on department_no
                transaction_type="DEPARTMENT"
            )
            
            if success:
                logger.info("[SALE_DEPARTMENT] ✓ Successfully added department '%s' to sale list", department_name)
                
                # Update document_data
                # Get line_no from sale_list
                line_no = len(sale_list.custom_sales_data_list)
                self._update_document_data_for_sale(
                    sale_type="DEPARTMENT",
                    department=department,
                    quantity=quantity,
                    unit_price=price,
                    department_no=department_no,
                    line_no=line_no
                )
                
                # Store the DB record ID in SalesData so REPEAT/DELETE can find it later
                if self.document_data and self.document_data.get("departments") and sale_list.custom_sales_data_list:
                    sale_list.custom_sales_data_list[-1].reference_id = str(self.document_data["departments"][-1].id)
                
                # Update amount_table with new totals
                if hasattr(current_window, 'amount_table') and current_window.amount_table:
                    from pos.service import SaleService
                    if self.document_data and self.document_data.get("head"):
                        SaleService.update_amount_table_from_document(
                            current_window.amount_table,
                            self.document_data["head"]
                        )
                        logger.info("[SALE_DEPARTMENT] ✓ Updated amount_table")
                
                # Clear numpad after successful sale
                numpad.set_text("")
                logger.debug("[SALE_DEPARTMENT] Cleared numpad")
                
                return True
            else:
                logger.error("[SALE_DEPARTMENT] Failed to add department to sale list")
                return False
                
        except Exception as e:
            logger.error("[SALE_DEPARTMENT] Error processing department sale: %s", str(e))
            return False
    
    def _sale_department_by_no_event(self, key=None):
        """
        Handle department sale by department number entry.
        
        Allows user to enter department number directly rather than
        using department buttons, useful for quick entry.
        
        Parameters:
            key: Optional parameter from numpad input
        
        Returns:
            bool: True if department sale successful, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
            
        # TODO: Implement department number entry logic
        if key is not None:
            logger.debug("Department sale by number - key pressed: %s", key)
        else:
            logger.debug("Department sale by number - functionality to be implemented")
        return False
    
    # ==================== PLU SALES EVENTS ====================
    
    def _sale_plu_code_event(self, button=None):
        """
        Handle PLU (Price Look-Up) sale by product code.
        
        Processes sale of specific products using PLU codes from button names.
        When a button with name starting with "PLU" and function SALE_PLU_CODE is clicked:
        1. Extract code from button name (e.g., PLU5000157070008 -> 5000157070008)
        2. Look up product table for matching code
        3. Add item to sale list with product's sale_price
        4. Update button text to show product.short_name
        
        Parameters:
            button: Button object that was clicked (contains control_name attribute)
        
        Returns:
            bool: True if PLU sale successful, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
        
        # Ensure document is open (create new if None or closed)
        if not self._ensure_document_open():
            logger.error("[SALE_PLU_CODE] Failed to ensure document is open")
            return False
        
        try:
            # Get button control name
            if button is None or not hasattr(button, 'control_name'):
                logger.debug("[SALE_PLU_CODE] No button provided or button missing control_name")
                return False
            
            control_name = button.control_name
            logger.debug("[SALE_PLU_CODE] Processing button with control_name: '%s'", control_name)
            
            # Check if control name starts with "PLU"
            if not control_name or not control_name.upper().startswith("PLU"):
                logger.debug("[SALE_PLU_CODE] Control name '%s' does not start with PLU", control_name)
                return False
            
            # Extract code from control name (remove "PLU" prefix)
            product_code = control_name[3:]  # Remove first 3 characters "PLU"
            logger.debug("[SALE_PLU_CODE] Extracted product code: '%s'", product_code)
            
            if not product_code:
                logger.debug("[SALE_PLU_CODE] Empty code after removing PLU prefix")
                return False
            
            # Import SaleList
            from user_interface.control.sale_list.sale_list import SaleList
            
            # Search for product with matching code from product_data cache
            products = [
                p for p in self.product_data.get("Product", [])
                if p.code == product_code and not (hasattr(p, 'is_deleted') and p.is_deleted)
            ]
            
            if not products or len(products) == 0:
                logger.debug("[SALE_PLU_CODE] No product found with code: '%s'", product_code)
                return False
            
            # Get the first matching product
            product = products[0]
            logger.debug("[SALE_PLU_CODE] Found product: %s (short_name: %s)", product.name, product.short_name)
            
            # Get sale price from product
            sale_price = float(product.sale_price) if product.sale_price else 0.0
            logger.debug("[SALE_PLU_CODE] Using sale_price: %s", sale_price)
            
            if sale_price == 0.0:
                logger.warning("[SALE_PLU_CODE] Warning: Product sale_price is 0")
            
            # Find sale_list widget in the current window
            # Button's parent should be BaseWindow
            current_window = button.parent() if button else None
            
            if not current_window:
                logger.debug("[SALE_PLU_CODE] Button has no parent window")
                return False
            
            sale_list = None
            
            # Check if window has sale_list attribute (set in _create_sale_list)
            if hasattr(current_window, 'sale_list'):
                sale_list = current_window.sale_list
            else:
                # Fallback: Search for SaleList widget using findChildren (searches nested widgets too)
                sale_lists = current_window.findChildren(SaleList)
                if sale_lists:
                    sale_list = sale_lists[0]
            
            if not sale_list:
                logger.error("[SALE_PLU_CODE] SaleList widget not found in current window")
                return False
            
            # Determine quantity: pending_quantity (set by X button) takes priority over numpad
            quantity = self._get_and_reset_pending_quantity(current_window)
            logger.debug("[SALE_PLU_CODE] Using quantity: %s", quantity)

            # Stock availability check
            if not self._check_stock_for_sale(product, quantity, current_window):
                return False

            # Add product to sale list
            product_name = product.short_name if product.short_name else product.name
            
            success = sale_list.add_product(
                product_name=product_name,
                quantity=quantity,
                unit_price=sale_price,
                barcode="",  # No barcode for code-based lookup
                reference_id=str(product.id),
                plu_no=product.code
            )
            
            if success:
                logger.info("[SALE_PLU_CODE] ✓ Successfully added product '%s' to sale list", product_name)
                
                # Update document_data
                # Get line_no from sale_list
                line_no = len(sale_list.custom_sales_data_list)
                self._update_document_data_for_sale(
                    sale_type="PLU_CODE",
                    product=product,
                    quantity=quantity,
                    unit_price=sale_price,
                    line_no=line_no
                )
                
                # Store the DB record ID in SalesData so REPEAT/DELETE can find it later
                if self.document_data and self.document_data.get("products") and sale_list.custom_sales_data_list:
                    sale_list.custom_sales_data_list[-1].reference_id = str(self.document_data["products"][-1].id)
                
                # Update amount_table with new totals
                if hasattr(current_window, 'amount_table') and current_window.amount_table:
                    from pos.service import SaleService
                    if self.document_data and self.document_data.get("head"):
                        SaleService.update_amount_table_from_document(
                            current_window.amount_table,
                            self.document_data["head"]
                        )
                        logger.info("[SALE_PLU_CODE] ✓ Updated amount_table")
                
                # Update button text to show product short_name
                button.setText(product_name)
                logger.debug("[SALE_PLU_CODE] Updated button text to: '%s'", product_name)
                
                return True
            else:
                logger.error("[SALE_PLU_CODE] Failed to add product to sale list")
                return False
                
        except Exception as e:
            logger.error("[SALE_PLU_CODE] Error processing PLU code sale: %s", str(e))
            return False
    
    def _sale_plu_barcode_event(self, button=None):
        """
        Handle PLU sale by barcode scanning/entry.
        
        Two call modes:
        1. Button click: button is a widget with control_name starting with "PLU".
           Extracts barcode from button name, looks up product, and sells.
        2. Numpad Enter: button is a plain string (the full accumulated numpad text).
           The numpad uses set_enter_event so this is only called on Enter, never
           on individual digit presses. Delegates to _sale_plu_numpad_enter_event.

        Parameters:
            button: Button widget (control_name attribute) OR plain string from numpad Enter
        
        Returns:
            bool: True if barcode sale successful, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False

        # When called from numpad Enter, button is a plain string
        if isinstance(button, str):
            return self._sale_plu_numpad_enter_event(button)

        # Ensure document is open (create new if None or closed)
        if not self._ensure_document_open():
            logger.error("[SALE_PLU_BARCODE] Failed to ensure document is open")
            return False
        
        try:
            # Get button control name
            if button is None or not hasattr(button, 'control_name'):
                logger.debug("[SALE_PLU_BARCODE] No button provided or button missing control_name")
                return False
            
            control_name = button.control_name
            logger.debug("[SALE_PLU_BARCODE] Processing button with control_name: '%s'", control_name)
            
            # Check if control name starts with "PLU"
            if not control_name or not control_name.upper().startswith("PLU"):
                logger.debug("[SALE_PLU_BARCODE] Control name '%s' does not start with PLU", control_name)
                return False
            
            # Extract barcode from control name (remove "PLU" prefix)
            barcode = control_name[3:]  # Remove first 3 characters "PLU"
            logger.debug("[SALE_PLU_BARCODE] Extracted barcode: '%s'", barcode)
            
            if not barcode:
                logger.debug("[SALE_PLU_BARCODE] Empty barcode after removing PLU prefix")
                return False
            
            # Import SaleList
            from user_interface.control.sale_list.sale_list import SaleList
            
            # Search for product_barcode with matching barcode from product_data cache
            barcode_records = [
                pb for pb in self.product_data.get("ProductBarcode", [])
                if pb.barcode == barcode and not (hasattr(pb, 'is_deleted') and pb.is_deleted)
            ]
            
            if not barcode_records or len(barcode_records) == 0:
                logger.debug("[SALE_PLU_BARCODE] No product found with barcode: '%s'", barcode)
                return False
            
            # Get the first matching barcode record
            product_barcode = barcode_records[0]
            logger.debug("[SALE_PLU_BARCODE] Found product_barcode: %s", product_barcode)
            
            # Get product using fk_product_id from product_data cache
            products = [
                p for p in self.product_data.get("Product", [])
                if p.id == product_barcode.fk_product_id
            ]
            
            if not products or len(products) == 0:
                logger.error("[SALE_PLU_BARCODE] Product not found with id: %s", product_barcode.fk_product_id)
                return False
            
            product = products[0]
            
            logger.debug("[SALE_PLU_BARCODE] Found product: %s (short_name: %s)", product.name, product.short_name)
            
            # Determine sale price (prefer product_barcode.sale_price, fallback to product.sale_price)
            sale_price = float(product_barcode.sale_price) if product_barcode.sale_price else float(product.sale_price)
            logger.debug("[SALE_PLU_BARCODE] Using sale_price: %s", sale_price)
            
            # Find sale_list widget in the current window
            # Button's parent should be BaseWindow
            current_window = button.parent() if button else None
            
            if not current_window:
                logger.debug("[SALE_PLU_BARCODE] Button has no parent window")
                return False
            
            sale_list = None
            
            # Check if window has sale_list attribute (set in _create_sale_list)
            if hasattr(current_window, 'sale_list'):
                sale_list = current_window.sale_list
            else:
                # Fallback: Search for SaleList widget using findChildren (searches nested widgets too)
                sale_lists = current_window.findChildren(SaleList)
                if sale_lists:
                    sale_list = sale_lists[0]
            
            if not sale_list:
                logger.error("[SALE_PLU_BARCODE] SaleList widget not found in current window")
                return False
            
            # Determine quantity: pending_quantity (set by X button) takes priority over numpad
            quantity = self._get_and_reset_pending_quantity(current_window)

            # Stock availability check
            if not self._check_stock_for_sale(product, quantity, current_window):
                return False

            # Add product to sale list
            product_name = product.short_name if product.short_name else product.name
            
            success = sale_list.add_product(
                product_name=product_name,
                quantity=quantity,
                unit_price=sale_price,
                barcode=barcode,
                reference_id=str(product_barcode.id),
                plu_no=product.code
            )
            
            if success:
                logger.info("[SALE_PLU_BARCODE] ✓ Successfully added product '%s' to sale list", product_name)
                
                # Update document_data
                # Get line_no from sale_list
                line_no = len(sale_list.custom_sales_data_list)
                self._update_document_data_for_sale(
                    sale_type="PLU_BARCODE",
                    product=product,
                    quantity=quantity,
                    unit_price=sale_price,
                    product_barcode=product_barcode,
                    line_no=line_no
                )
                
                # Store the DB record ID in SalesData so REPEAT/DELETE can find it later
                if self.document_data and self.document_data.get("products") and sale_list.custom_sales_data_list:
                    sale_list.custom_sales_data_list[-1].reference_id = str(self.document_data["products"][-1].id)
                
                # Update amount_table with new totals
                if hasattr(current_window, 'amount_table') and current_window.amount_table:
                    from pos.service import SaleService
                    if self.document_data and self.document_data.get("head"):
                        SaleService.update_amount_table_from_document(
                            current_window.amount_table,
                            self.document_data["head"]
                        )
                        logger.info("[SALE_PLU_BARCODE] ✓ Updated amount_table")
                
                # Update button text to show product short_name
                button.setText(product_name)
                logger.debug("[SALE_PLU_BARCODE] Updated button text to: '%s'", product_name)
                
                return True
            else:
                logger.error("[SALE_PLU_BARCODE] Failed to add product to sale list")
                return False
                
        except Exception as e:
            logger.error("[SALE_PLU_BARCODE] Error processing PLU barcode sale: %s", str(e))
            return False

    def _resolve_product_by_barcode_or_code(self, lookup_text):
        """
        Match ProductBarcode.barcode then Product.code (same order as numpad sale).

        Returns:
            tuple: (product, product_barcode_or_none, sale_type) where sale_type is
                   'PLU_BARCODE', 'PLU_CODE', or None if not found.
        """
        lookup_text = (lookup_text or "").strip()
        if not lookup_text:
            return None, None, None

        barcode_records = [
            pb for pb in self.product_data.get("ProductBarcode", [])
            if pb.barcode == lookup_text and not (hasattr(pb, "is_deleted") and pb.is_deleted)
        ]
        if barcode_records:
            product_barcode = barcode_records[0]
            products = [
                p for p in self.product_data.get("Product", [])
                if p.id == product_barcode.fk_product_id
            ]
            if products:
                return products[0], product_barcode, "PLU_BARCODE"

        code_matches = [
            p for p in self.product_data.get("Product", [])
            if p.code == lookup_text and not (hasattr(p, "is_deleted") and p.is_deleted)
        ]
        if code_matches:
            return code_matches[0], None, "PLU_CODE"

        return None, None, None

    def _warehouse_stock_summary_text(self, product_id):
        """
        Aggregate WarehouseProductStock quantities by warehouse name for display.
        """
        from collections import defaultdict

        stocks = [
            s for s in self.product_data.get("WarehouseProductStock", [])
            if s.fk_product_id == product_id and not (hasattr(s, "is_deleted") and s.is_deleted)
        ]
        locations = {
            loc.id: loc for loc in self.product_data.get("WarehouseLocation", [])
            if not (hasattr(loc, "is_deleted") and loc.is_deleted)
        }
        warehouses = {
            w.id: w for w in self.product_data.get("Warehouse", [])
            if not (hasattr(w, "is_deleted") and w.is_deleted)
        }

        by_wh = defaultdict(int)
        for s in stocks:
            qty = int(s.quantity or 0)
            loc = locations.get(s.fk_warehouse_location_id)
            wh_name = "—"
            if loc:
                wh = warehouses.get(loc.fk_warehouse_id)
                wh_name = (wh.name or wh.code or str(wh.id)) if wh else (loc.name or loc.code or "—")
            by_wh[wh_name] += qty

        if by_wh:
            lines = [f"{name}: {qty}" for name, qty in sorted(by_wh.items(), key=lambda x: x[0])]
            return "\n".join(lines)

        products = [p for p in self.product_data.get("Product", []) if p.id == product_id]
        if products:
            p = products[0]
            master = int(getattr(p, "stock", 0) or 0)
            return f"Product card stock: {master}"
        return "No stock information."

    def _plu_inquiry_execute(self, lookup_text, window=None, clear_numpad=True):
        """
        Show price and warehouse stock for a barcode / product code. Does not sell.
        """
        from user_interface.control.numpad.numpad import NumPad
        from user_interface.form.message_form import MessageForm
        from pos.service.vat_service import VatService

        if not self.login_succeed:
            self._logout()
            return False

        if window is None:
            window = self.interface.window if hasattr(self, "interface") else None
        if not window:
            logger.error("[PLU_INQUIRY] No window")
            return False

        product, product_barcode, sale_type = self._resolve_product_by_barcode_or_code(lookup_text)
        if product is None:
            try:
                from data_layer.model import LabelValue

                label_values = LabelValue.filter_by(
                    key="ProductNotFound", culture_info="en-GB", is_deleted=False
                )
                error_msg = label_values[0].value if label_values else f"Product not found: {lookup_text}"
                MessageForm.show_error(window, error_msg, "")
            except Exception:
                MessageForm.show_error(window, f"Product not found: {lookup_text}", "")
            return False

        if sale_type == "PLU_BARCODE" and product_barcode and product_barcode.sale_price:
            sale_price = float(product_barcode.sale_price)
        else:
            sale_price = float(product.sale_price) if product.sale_price else 0.0

        sign = self.current_currency if hasattr(self, "current_currency") and self.current_currency else "GBP"
        decimals = VatService.get_currency_decimal_places(sign, self.product_data)
        price_line = f"Price: {sale_price:.{decimals}f} {sign}"

        pname = product.short_name if product.short_name else product.name
        line1 = f"{pname}  ({lookup_text.strip()})"
        line2 = f"{price_line}\n\nStock by warehouse:\n{self._warehouse_stock_summary_text(product.id)}"

        MessageForm.show_info(window, line1, line2)

        if clear_numpad:
            numpads = window.findChildren(NumPad)
            if numpads:
                numpads[0].set_text("")

        return True

    def _plu_inquiry_event(self, key=None):
        """
        PLU button: if numpad has text, inquiry immediately; if empty, arm so the
        next Enter runs inquiry instead of a sale.
        """
        if not self.login_succeed:
            self._logout()
            return False

        try:
            from user_interface.control.numpad.numpad import NumPad

            window = None
            if key is not None and hasattr(key, "parent"):
                window = key.parent()
            if window is None:
                window = self.interface.window if hasattr(self, "interface") else None
            if not window:
                logger.error("[PLU_INQUIRY] Could not resolve parent window")
                return False

            numpad = None
            numpads = window.findChildren(NumPad)
            if numpads:
                numpad = numpads[0]
            if not numpad:
                logger.error("[PLU_INQUIRY] NumPad not found")
                return False

            raw = numpad.get_text() or ""
            text = raw.strip()
            if text:
                if hasattr(self, "awaiting_plu_inquiry"):
                    self.awaiting_plu_inquiry = False
                return self._plu_inquiry_execute(text, window=window, clear_numpad=True)

            self.awaiting_plu_inquiry = True
            logger.debug("[PLU_INQUIRY] Armed — next Enter will show price/stock")
            return True

        except Exception as e:
            logger.error("[PLU_INQUIRY] Error: %s", str(e))
            return False

    def _sale_plu_numpad_enter_event(self, text):
        """
        Handle product lookup and sale triggered by numpad Enter key.

        Search order:
          1. ProductBarcode.barcode  → exact match
          2. Product.code            → exact match
        Uses pending_quantity (set by X button) if > 1, otherwise defaults to 1.

        Parameters:
            text: String entered on the numpad before Enter was pressed

        Returns:
            bool: True if a product was found and sold, False otherwise
        """
        logger.debug("[NUMPAD_ENTER] Lookup for text: '%s'", text)

        if hasattr(self, "awaiting_plu_inquiry") and self.awaiting_plu_inquiry:
            self.awaiting_plu_inquiry = False
            if text and str(text).strip():
                return self._plu_inquiry_execute(str(text).strip(), clear_numpad=True)
            logger.debug("[NUMPAD_ENTER] PLU inquiry armed but empty input")
            return False

        if not text or not text.strip():
            logger.debug("[NUMPAD_ENTER] Empty text, nothing to do")
            return False

        if not self._ensure_document_open():
            logger.error("[NUMPAD_ENTER] Failed to ensure document is open")
            return False

        try:
            from user_interface.control.sale_list.sale_list import SaleList
            from user_interface.control.numpad.numpad import NumPad
            from user_interface.form.message_form import MessageForm

            window = self.interface.window if hasattr(self, 'interface') else None
            if not window:
                logger.error("[NUMPAD_ENTER] No window found")
                return False

            # Find sale_list
            sale_list = getattr(window, 'sale_list', None)
            if not sale_list:
                sale_lists = window.findChildren(SaleList)
                sale_list = sale_lists[0] if sale_lists else None
            if not sale_list:
                logger.error("[NUMPAD_ENTER] SaleList not found")
                return False

            # Find numpad (to clear it on success)
            numpad = None
            numpads = window.findChildren(NumPad)
            if numpads:
                numpad = numpads[0]

            lookup_text = text.strip()

            # --- Step 1: search ProductBarcode ---
            barcode_records = [
                pb for pb in self.product_data.get("ProductBarcode", [])
                if pb.barcode == lookup_text and not (hasattr(pb, 'is_deleted') and pb.is_deleted)
            ]

            product = None
            product_barcode = None
            sale_type = None

            if barcode_records:
                product_barcode = barcode_records[0]
                products = [
                    p for p in self.product_data.get("Product", [])
                    if p.id == product_barcode.fk_product_id
                ]
                if products:
                    product = products[0]
                    sale_type = "PLU_BARCODE"
                    logger.debug("[NUMPAD_ENTER] Found via barcode: %s", product.name)

            # --- Step 2: search Product.code if barcode not found ---
            if product is None:
                code_matches = [
                    p for p in self.product_data.get("Product", [])
                    if p.code == lookup_text and not (hasattr(p, 'is_deleted') and p.is_deleted)
                ]
                if code_matches:
                    product = code_matches[0]
                    sale_type = "PLU_CODE"
                    logger.debug("[NUMPAD_ENTER] Found via product code: %s", product.name)

            # --- Product not found ---
            if product is None:
                logger.debug("[NUMPAD_ENTER] No product found for: '%s'", lookup_text)
                try:
                    from data_layer.model import LabelValue
                    label_values = LabelValue.filter_by(key="ProductNotFound", culture_info="en-GB", is_deleted=False)
                    error_msg = label_values[0].value if label_values else f"Product not found: {lookup_text}"
                    MessageForm.show_error(window, error_msg, "")
                except Exception:
                    MessageForm.show_error(window, f"Product not found: {lookup_text}", "")
                return False

            # Determine sale price
            if sale_type == "PLU_BARCODE" and product_barcode and product_barcode.sale_price:
                sale_price = float(product_barcode.sale_price)
            else:
                sale_price = float(product.sale_price) if product.sale_price else 0.0

            # Determine quantity: pending_quantity takes priority
            quantity = self._get_and_reset_pending_quantity(window)

            # Stock availability check
            if not self._check_stock_for_sale(product, quantity, window):
                if numpad:
                    numpad.set_text("")
                return False

            product_name = product.short_name if product.short_name else product.name

            success = sale_list.add_product(
                product_name=product_name,
                quantity=quantity,
                unit_price=sale_price,
                barcode=lookup_text if sale_type == "PLU_BARCODE" else "",
                reference_id=str(product_barcode.id) if product_barcode else str(product.id),
                plu_no=product.code
            )

            if success:
                line_no = len(sale_list.custom_sales_data_list)
                self._update_document_data_for_sale(
                    sale_type=sale_type,
                    product=product,
                    quantity=quantity,
                    unit_price=sale_price,
                    product_barcode=product_barcode,
                    line_no=line_no
                )

                # Store the DB record ID in SalesData so REPEAT/DELETE can find it later
                if self.document_data and self.document_data.get("products") and sale_list.custom_sales_data_list:
                    sale_list.custom_sales_data_list[-1].reference_id = str(self.document_data["products"][-1].id)

                if hasattr(window, 'amount_table') and window.amount_table:
                    from pos.service import SaleService
                    if self.document_data and self.document_data.get("head"):
                        SaleService.update_amount_table_from_document(
                            window.amount_table,
                            self.document_data["head"]
                        )

                # Clear numpad after successful sale
                if numpad:
                    numpad.set_text("")

                logger.info("[NUMPAD_ENTER] ✓ Sold '%s' qty=%s via %s", product_name, quantity, sale_type)
                return True
            else:
                logger.error("[NUMPAD_ENTER] Failed to add product '%s' to sale list", product_name)
                return False

        except Exception as e:
            logger.error("[NUMPAD_ENTER] Error: %s", str(e))
            return False

    # ==================== QUANTITY HELPER ====================

    def _get_and_reset_pending_quantity(self, window=None):
        """
        Return the effective sale quantity and reset pending state.

        Priority order:
          1. self.pending_quantity if > 1  (set by X / quantity button)
          2. Numpad value (if numeric and positive)
          3. Default: 1.0

        After reading, pending_quantity is reset to 1.0, the numpad is cleared,
        and the status bar is refreshed to show 'x1'.

        Parameters:
            window: The current BaseWindow (used to locate the NumPad widget)

        Returns:
            float: Quantity to use for the sale
        """
        from user_interface.control.numpad.numpad import NumPad

        quantity = 1.0

        # Priority 1: pending_quantity set by X button
        if hasattr(self, 'pending_quantity') and self.pending_quantity > 1.0:
            quantity = self.pending_quantity
            logger.debug("[QTY] Using pending_quantity: %s", quantity)
        elif window:
            # Priority 2: read from numpad
            numpad = None
            numpads = window.findChildren(NumPad)
            if numpads:
                numpad = numpads[0]
            if numpad:
                numpad_text = numpad.get_text()
                if numpad_text and numpad_text.strip():
                    try:
                        qty_val = float(numpad_text)
                        if qty_val > 0:
                            quantity = qty_val
                            logger.debug("[QTY] Using numpad quantity: %s", quantity)
                    except ValueError:
                        pass
                # Always clear numpad after reading
                numpad.set_text("")

        # Reset pending_quantity and refresh status bar
        self.pending_quantity = 1.0
        self._refresh_status_bar()

        return quantity

    def _refresh_status_bar(self):
        """Trigger an immediate status bar refresh if the window is available."""
        try:
            window = self.interface.window if hasattr(self, 'interface') else None
            if window and hasattr(window, 'statusbar') and window.statusbar:
                window.statusbar.update_display()
        except Exception:
            pass
    
    def _get_plu_from_maingroup_event(self):
        """
        Handle PLU selection from main product group.
        
        Displays products organized by main groups, allowing
        user to browse and select items by category.
        
        Returns:
            bool: True if PLU selection successful, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
            
        # TODO: Implement main group PLU selection
        logger.debug("PLU main group selection - functionality to be implemented")
        return False
    
    # ==================== REPEAT SALES EVENTS ====================
    
    def _repeat_last_sale_event(self):
        """
        Handle repeat of the last completed sale.
        
        Duplicates the most recent transaction, adding all items
        with same quantities and prices to current transaction.
        
        Returns:
            bool: True if repeat sale successful, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
            
        # TODO: Implement last sale repeat logic
        logger.debug("Repeat last sale - functionality to be implemented")
        return False
    
    def _repeat_sale_event(self):
        """
        Handle repeat of a selected previous sale.
        
        Allows user to select from history of transactions
        and duplicate a chosen sale.
        
        Returns:
            bool: True if repeat sale successful, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
            
        # TODO: Implement sale history selection and repeat
        logger.debug("Repeat sale - functionality to be implemented")
        return False
    
    # ==================== CANCELLATION EVENTS ====================
    
    def _cancel_department_event(self):
        """
        Handle cancellation of department sale items.
        
        Removes or voids department-based items from current transaction.
        May require supervisor approval depending on system settings.
        
        Returns:
            bool: True if cancellation successful, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
            
        # TODO: Implement department cancellation logic
        logger.debug("Cancel department - functionality to be implemented")
        return False
    
    def _cancel_plu_event(self):
        """
        Handle cancellation of PLU sale items.
        
        Removes or voids specific PLU items from current transaction.
        Updates inventory and transaction totals accordingly.
        
        Returns:
            bool: True if cancellation successful, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
            
        # TODO: Implement PLU cancellation logic
        logger.debug("Cancel PLU - functionality to be implemented")
        return False
    
    def _cancel_last_sale_event(self):
        """
        Handle cancellation of the last entered sale item.
        
        Removes the most recently added item from transaction,
        useful for quick error correction.
        
        Returns:
            bool: True if cancellation successful, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
            
        # TODO: Implement last item cancellation logic
        logger.debug("Cancel last sale - functionality to be implemented")
        return False
    
    def _cancel_sale_event(self):
        """
        Handle cancellation of selected sale items.
        
        Allows user to select specific items from transaction
        list and remove them.
        
        Returns:
            bool: True if cancellation successful, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
            
        # TODO: Implement item selection and cancellation
        logger.debug("Cancel sale - functionality to be implemented")
        return False
    
    def _cancel_document_event(self, button=None):
        """
        Handle cancellation of the entire transaction document (CANCEL button).

        Behaviour:
        - Open document with at least one active line:
            * Sets transaction_status = CANCELLED, is_cancel = True, is_closed = True
            * Sets cancel_reason = "Canceled by cashier: {username}"
            * Persists via complete_document(is_cancel=True, cancel_reason=...)
            * Shows a confirmation message box with receipt/closure number and total
            * Creates a new empty draft document for the next sale
        - No open document (or only an empty draft):
            * Shows a warning message box — no open document found

        Returns:
            bool: True if document cancelled successfully, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False

        from user_interface.form.message_form import MessageForm
        from data_layer.auto_save import AutoSaveModel
        from PySide6.QtWidgets import QApplication

        window = None
        try:
            app_qt = QApplication.instance()
            if app_qt:
                window = app_qt.activeWindow()
        except Exception:
            pass
        if window is None and hasattr(self, "interface") and self.interface:
            window = getattr(self.interface, "window", None)

        try:
            dd = self.document_data
            if not dd or not dd.get("head"):
                MessageForm.show_info(
                    window,
                    "No Open Document",
                    "There is no open document to cancel."
                )
                return False

            head = dd["head"]
            head_obj = head.unwrap() if isinstance(head, AutoSaveModel) else head

            from data_layer.model.definition.transaction_status import TransactionStatus

            status = getattr(head_obj, "transaction_status", None)
            is_closed = getattr(head_obj, "is_closed", False)
            is_pending = getattr(head_obj, "is_pending", False)

            if is_closed or is_pending or status in (
                TransactionStatus.COMPLETED.value,
                TransactionStatus.CANCELLED.value,
            ):
                MessageForm.show_info(
                    window,
                    "No Open Document",
                    "There is no open document to cancel."
                )
                return False

            products = dd.get("products") or []
            departments = dd.get("departments") or []

            def _is_active(rec):
                actual = rec.unwrap() if isinstance(rec, AutoSaveModel) else rec
                return not getattr(actual, "is_cancel", False)

            has_active_lines = any(_is_active(p) for p in products) or \
                               any(_is_active(d) for d in departments)

            if not has_active_lines:
                MessageForm.show_info(
                    window,
                    "No Open Document",
                    "There is no open document to cancel."
                )
                return False

            # Build cancellation info for the message box
            receipt_no = getattr(head_obj, "receipt_number", "—")
            closure_no = getattr(head_obj, "closure_number", "—")
            total_amt = getattr(head_obj, "total_amount", 0) or 0
            try:
                total_str = f"{float(total_amt):.2f}"
            except Exception:
                total_str = str(total_amt)

            # Determine cashier username
            cashier_username = "unknown"
            if hasattr(self, "cashier_data") and self.cashier_data:
                cd = self.cashier_data
                if isinstance(cd, AutoSaveModel):
                    cd = cd.unwrap()
                cashier_username = getattr(cd, "user_name", None) or \
                                   getattr(cd, "name", None) or "unknown"

            cancel_reason = f"Canceled by cashier: {cashier_username}"

            # Persist cancellation via complete_document
            success = self.complete_document(is_cancel=True, cancel_reason=cancel_reason)

            if not success:
                MessageForm.show_error(
                    window,
                    "Cancel Failed",
                    "An error occurred while cancelling the document."
                )
                return False

            # Clear UI controls
            if window:
                if hasattr(window, "sale_list") and window.sale_list:
                    window.sale_list.clear_products()
                if hasattr(window, "payment_list") and window.payment_list:
                    window.payment_list.clear_payments()
                if hasattr(window, "amount_table") and window.amount_table:
                    from decimal import Decimal
                    window.amount_table.receipt_total_price = Decimal("0")
                    window.amount_table.discount_total_amount = Decimal("0")
                    window.amount_table.receipt_total_payment = Decimal("0")

            self._update_statusbar()
            from pos.peripherals.hooks import sync_line_display_cleared
            sync_line_display_cleared(self)

            # Show confirmation message
            MessageForm.show_info(
                window,
                "Transaction Cancelled",
                f"Receipt No: {receipt_no}\n"
                f"Closure No: {closure_no}\n"
                f"Total: {total_str}\n\n"
                f"The transaction has been cancelled.\n"
                f"{cancel_reason}"
            )

            # Create a new draft for the next sale
            self.create_empty_document()

            logger.info(
                "[CANCEL_DOCUMENT] Document cancelled — receipt=%s closure=%s total=%s reason=%s",
                receipt_no, closure_no, total_str, cancel_reason
            )
            return True

        except Exception as e:
            logger.error("[CANCEL_DOCUMENT] Unexpected error: %s", e)
            try:
                MessageForm.show_error(
                    window,
                    "Cancel Failed",
                    f"An unexpected error occurred: {e}"
                )
            except Exception:
                pass
            return False
    
    # ==================== TRANSACTION MODIFICATION EVENTS ====================
    
    def _change_document_type_event(self):
        """
        Handle change of document type for current transaction.
        
        Allows switching between sale, return, exchange, and other
        document types while maintaining transaction items.
        
        Returns:
            bool: True if document type changed successfully, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
            
        # TODO: Implement document type switching
        logger.debug("Change document type - functionality to be implemented")
        return False
    
    def _refund_event(self):
        """
        Handle refund/return transaction processing.
        
        Processes returned items, validates return policy,
        and calculates refund amounts.
        
        Returns:
            bool: True if refund processed successfully, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
            
        # TODO: Implement refund processing logic
        logger.debug("Refund - functionality to be implemented")
        return False
    
    # ==================== DISCOUNT AND MARKUP EVENTS ====================
    
    def _discount_by_amount_event(self, key=None):
        """
        Apply a fixed monetary discount to the last sold line item.

        Flow
        ----
        1. Verify authentication and that at least one active product exists.
        2. Open ``DiscountInputDialog`` (MODE_AMOUNT, max = last item total).
        3. On APPLY:
           a. Strike through / cancel the last product row in the sale list.
           b. Mark the matching ``TransactionProductTemp`` as cancelled in DB.
           c. Recalculate VAT for the discounted price.
           d. Clone the original DB record with the new price/VAT and save it.
           e. Add the discounted product row to the sale list.
           f. Recalculate document totals and refresh the amount table.

        Returns:
            bool: True if discount was applied, False otherwise.
        """
        if not self.login_succeed:
            self._logout()
            return False

        return self._apply_item_discount(mode="AMOUNT")

    def _markup_by_amount_event(self, key=None):
        """
        Apply a fixed monetary markup to the last sold line item (FUNC + DISC AMT).

        Same flow as item discount, but the line total increases by the entered amount.
        """
        if not self.login_succeed:
            self._logout()
            return False

        return self._apply_item_markup(mode="AMOUNT")
    
    def _discount_by_percent_event(self, key=None):
        """
        Apply a percentage-based discount to the last sold line item.

        Flow
        ----
        1. Verify authentication and that at least one active product exists.
        2. Open ``DiscountInputDialog`` (MODE_PERCENT, range 1 %–100 %).
        3. On APPLY:
           a. Strike through / cancel the last product row in the sale list.
           b. Mark the matching ``TransactionProductTemp`` as cancelled in DB.
           c. Calculate the discounted total (total × (1 − pct/100)).
           d. Recalculate VAT for the discounted price.
           e. Clone the original DB record with the new price/VAT and save it.
           f. Add the discounted product row to the sale list.
           g. Recalculate document totals and refresh the amount table.

        Returns:
            bool: True if discount was applied, False otherwise.
        """
        if not self.login_succeed:
            self._logout()
            return False

        return self._apply_item_discount(mode="PERCENT")

    # ------------------------------------------------------------------
    # Shared discount implementation
    # ------------------------------------------------------------------

    def _apply_item_discount(self, mode: str) -> bool:
        """
        Core implementation shared by amount- and percentage-discount events.

        Parameters
        ----------
        mode : str
            ``"AMOUNT"`` or ``"PERCENT"``

        Returns
        -------
        bool
            ``True`` if a discount was successfully applied, ``False`` otherwise.
        """
        from decimal import Decimal
        from uuid import uuid4

        from PySide6.QtWidgets import QApplication

        from data_layer.auto_save import AutoSaveModel
        from data_layer.model import TransactionProductTemp
        from pos.service import SaleService
        from pos.service.vat_service import VatService
        from user_interface.form.discount_input_dialog import DiscountInputDialog
        from user_interface.form.message_form import MessageForm

        # ── 1. Locate the active window and sale_list ──────────────────
        active_window = None
        app_qt = QApplication.instance()
        if app_qt:
            active_window = app_qt.activeWindow()
        if not active_window or not hasattr(active_window, "sale_list"):
            if hasattr(self, "interface") and self.interface:
                active_window = getattr(self.interface, "window", None)
        if not active_window or not hasattr(active_window, "sale_list"):
            logger.error("[DISCOUNT] No window with sale_list found")
            return False

        sale_list = active_window.sale_list

        # ── 2. Find the last non-cancelled PLU / DEPARTMENT row ────────
        last_row_index = -1
        last_sales_data = None
        for idx in range(len(sale_list.custom_sales_data_list) - 1, -1, -1):
            sd = sale_list.custom_sales_data_list[idx]
            if sd.transaction_type in ("PLU", "DEPARTMENT") and not sd.is_canceled:
                last_row_index = idx
                last_sales_data = sd
                break

        if last_sales_data is None:
            MessageForm.show_error(
                active_window,
                "No product found to apply discount to.",
                "Please sell at least one product first.",
            )
            return False

        product_name   = last_sales_data.name_of_product
        product_total  = last_sales_data.total_amount   # float
        product_qty    = last_sales_data.quantity        # float
        reference_id   = str(last_sales_data.reference_id)

        # ── 3. Determine currency decimal places ───────────────────────
        currency_sign = getattr(self, "current_currency", None) or "GBP"
        decimal_places = VatService.get_currency_decimal_places(
            currency_sign, getattr(self, "product_data", None)
        )

        # ── 4. Open the discount input dialog ─────────────────────────
        if mode == "PERCENT":
            entered = DiscountInputDialog.show_percent(
                active_window, product_name, product_total
            )
        else:
            entered = DiscountInputDialog.show_amount(
                active_window, product_name, product_total, decimal_places
            )

        if entered is None:
            return False  # user cancelled

        # ── 5. Calculate new totals ───────────────────────────────────
        if mode == "PERCENT":
            discount_factor  = Decimal(str(entered)) / Decimal("100")
            discount_amount  = Decimal(str(product_total)) * discount_factor
            new_total        = Decimal(str(product_total)) - discount_amount
        else:
            discount_amount  = Decimal(str(entered))
            new_total        = Decimal(str(product_total)) - discount_amount

        # Prevent zero or negative totals
        min_total = Decimal(str(10 ** (-decimal_places)))
        if new_total < min_total:
            new_total = min_total

        new_unit_price = new_total / Decimal(str(product_qty)) if product_qty else new_total

        # ── 6. Find original TransactionProductTemp in document_data ──
        original_db_record = None
        if self.document_data and reference_id:
            for rec in self.document_data.get("products", []):
                actual = rec.unwrap() if isinstance(rec, AutoSaveModel) else rec
                if str(actual.id) == reference_id:
                    original_db_record = actual
                    break

        # ── 7. Cancel the last row in the sale list (UI strikethrough) ─
        sale_list.cancel_transaction(last_row_index)

        # ── 8. Cancel the original DB record ──────────────────────────
        if original_db_record:
            original_db_record.is_cancel = True
            try:
                original_db_record.save()
                logger.info("[DISCOUNT] Cancelled original record %s", original_db_record.id)
            except Exception as exc:
                logger.error("[DISCOUNT] Error saving cancelled record: %s", exc)

        # ── 9. Recalculate VAT for the new price ──────────────────────
        vat_rate = Decimal("0")
        if original_db_record and hasattr(original_db_record, "vat_rate"):
            vat_rate = Decimal(str(original_db_record.vat_rate or "0"))

        new_total_vat = VatService.calculate_vat(
            float(new_total), float(vat_rate), currency_sign,
            getattr(self, "product_data", None)
        )

        # ── 10. Clone the DB record with discounted amounts ───────────
        new_line_no = (
            len(self.document_data.get("products", []))
            + len(self.document_data.get("departments", []))
            + 1
        ) if self.document_data else 1

        new_db_id = None
        if original_db_record:
            try:
                new_prod = TransactionProductTemp()
                for col in original_db_record.__table__.columns.keys():
                    if hasattr(original_db_record, col):
                        setattr(new_prod, col, getattr(original_db_record, col))
                new_prod.id            = uuid4()
                new_prod.line_no       = new_line_no
                new_prod.unit_price    = new_unit_price
                new_prod.total_price   = new_total
                new_prod.total_vat     = Decimal(str(new_total_vat))
                new_prod.unit_discount = discount_amount
                new_prod.is_cancel     = False
                new_prod.is_voided     = False

                if mode == "PERCENT":
                    new_prod.discount_rate   = Decimal(str(entered))
                    new_prod.discount_reason = f"Discount {entered:.2f}%"
                else:
                    new_prod.discount_rate   = None
                    new_prod.discount_reason = (
                        f"Discount {entered:.{decimal_places}f} {currency_sign}"
                    )

                new_prod.save()
                new_db_id = str(new_prod.id)

                if "products" not in self.document_data:
                    self.document_data["products"] = []
                self.document_data["products"].append(new_prod)
                logger.info("[DISCOUNT] Saved discounted record %s, total=%s", new_db_id, new_total)

            except Exception as exc:
                logger.error("[DISCOUNT] Error cloning DB record: %s", exc)

        # ── 11. Add the discounted row to the sale list ────────────────
        sale_list.add_product(
            product_name=product_name,
            quantity=product_qty,
            unit_price=float(new_unit_price),
            reference_id=new_db_id or 0,
            plu_no=last_sales_data.plu_no,
            department_no=last_sales_data.department_no,
            transaction_type=last_sales_data.transaction_type,
        )
        # Ensure the new row's reference_id is linked to the new DB record
        if new_db_id and sale_list.custom_sales_data_list:
            sale_list.custom_sales_data_list[-1].reference_id = new_db_id

        # ── 12. Recalculate document totals ───────────────────────────
        if self.document_data and self.document_data.get("head"):
            head = self.document_data["head"]
            if isinstance(head, AutoSaveModel):
                head = head.unwrap()
            try:
                totals = SaleService.calculate_document_totals(self.document_data)
                head.total_amount     = totals["total_amount"]
                head.total_vat_amount = totals["total_vat_amount"]
                head.save()
                logger.info(
                    "[DISCOUNT] Updated totals: total=%s vat=%s",
                    head.total_amount, head.total_vat_amount,
                )
            except Exception as exc:
                logger.error("[DISCOUNT] Error recalculating totals: %s", exc)

            if hasattr(active_window, "amount_table") and active_window.amount_table:
                try:
                    SaleService.update_amount_table_from_document(
                        active_window.amount_table, head
                    )
                except Exception as exc:
                    logger.error("[DISCOUNT] Error updating amount_table: %s", exc)

        # ── 13. Line display sync ─────────────────────────────────────
        try:
            from pos.peripherals.hooks import sync_line_display_from_document
            if self.document_data:
                sync_line_display_from_document(self, self.document_data)
        except Exception:
            pass

        logger.info(
            "[DISCOUNT] mode=%s entered=%s discount_amount=%s new_total=%s product='%s'",
            mode, entered, discount_amount, new_total, product_name,
        )
        return True

    def _markup_by_percent_event(self, key=None):
        """
        Apply a percentage markup to the last sold line item (FUNC + DISC %).

        Percentage range 1 %–100 %; line total becomes total × (1 + pct/100).
        """
        if not self.login_succeed:
            self._logout()
            return False

        return self._apply_item_markup(mode="PERCENT")

    def _apply_item_markup(self, mode: str) -> bool:
        """
        Core implementation for amount- and percentage-based line markups.

        Parameters
        ----------
        mode : str
            ``"AMOUNT"`` or ``"PERCENT"``
        """
        from decimal import Decimal
        from uuid import uuid4

        from PySide6.QtWidgets import QApplication

        from data_layer.auto_save import AutoSaveModel
        from data_layer.model import TransactionProductTemp
        from pos.service import SaleService
        from pos.service.vat_service import VatService
        from user_interface.form.discount_input_dialog import DiscountInputDialog
        from user_interface.form.message_form import MessageForm

        active_window = None
        app_qt = QApplication.instance()
        if app_qt:
            active_window = app_qt.activeWindow()
        if not active_window or not hasattr(active_window, "sale_list"):
            if hasattr(self, "interface") and self.interface:
                active_window = getattr(self.interface, "window", None)
        if not active_window or not hasattr(active_window, "sale_list"):
            logger.error("[MARKUP] No window with sale_list found")
            return False

        sale_list = active_window.sale_list

        last_row_index = -1
        last_sales_data = None
        for idx in range(len(sale_list.custom_sales_data_list) - 1, -1, -1):
            sd = sale_list.custom_sales_data_list[idx]
            if sd.transaction_type in ("PLU", "DEPARTMENT") and not sd.is_canceled:
                last_row_index = idx
                last_sales_data = sd
                break

        if last_sales_data is None:
            MessageForm.show_error(
                active_window,
                "No product found to apply markup to.",
                "Please sell at least one product first.",
            )
            return False

        product_name = last_sales_data.name_of_product
        product_total = last_sales_data.total_amount
        product_qty = last_sales_data.quantity
        reference_id = str(last_sales_data.reference_id)

        currency_sign = getattr(self, "current_currency", None) or "GBP"
        decimal_places = VatService.get_currency_decimal_places(
            currency_sign, getattr(self, "product_data", None)
        )

        if mode == "PERCENT":
            entered = DiscountInputDialog.show_markup_percent(
                active_window, product_name, product_total
            )
        else:
            entered = DiscountInputDialog.show_markup_amount(
                active_window, product_name, product_total, decimal_places
            )

        if entered is None:
            return False

        if mode == "PERCENT":
            markup_factor = Decimal(str(entered)) / Decimal("100")
            markup_amount = Decimal(str(product_total)) * markup_factor
            new_total = Decimal(str(product_total)) + markup_amount
        else:
            markup_amount = Decimal(str(entered))
            new_total = Decimal(str(product_total)) + markup_amount

        new_unit_price = new_total / Decimal(str(product_qty)) if product_qty else new_total

        original_db_record = None
        if self.document_data and reference_id:
            for rec in self.document_data.get("products", []):
                actual = rec.unwrap() if isinstance(rec, AutoSaveModel) else rec
                if str(actual.id) == reference_id:
                    original_db_record = actual
                    break

        sale_list.cancel_transaction(last_row_index)

        if original_db_record:
            original_db_record.is_cancel = True
            try:
                original_db_record.save()
                logger.info("[MARKUP] Cancelled original record %s", original_db_record.id)
            except Exception as exc:
                logger.error("[MARKUP] Error saving cancelled record: %s", exc)

        vat_rate = Decimal("0")
        if original_db_record and hasattr(original_db_record, "vat_rate"):
            vat_rate = Decimal(str(original_db_record.vat_rate or "0"))

        new_total_vat = VatService.calculate_vat(
            float(new_total), float(vat_rate), currency_sign,
            getattr(self, "product_data", None)
        )

        new_line_no = (
            len(self.document_data.get("products", []))
            + len(self.document_data.get("departments", []))
            + 1
        ) if self.document_data else 1

        new_db_id = None
        if original_db_record:
            try:
                new_prod = TransactionProductTemp()
                for col in original_db_record.__table__.columns.keys():
                    if hasattr(original_db_record, col):
                        setattr(new_prod, col, getattr(original_db_record, col))
                new_prod.id = uuid4()
                new_prod.line_no = new_line_no
                new_prod.unit_price = new_unit_price
                new_prod.total_price = new_total
                new_prod.total_vat = Decimal(str(new_total_vat))
                new_prod.unit_discount = Decimal("0")
                new_prod.is_cancel = False
                new_prod.is_voided = False
                new_prod.discount_rate = None
                if mode == "PERCENT":
                    new_prod.discount_reason = f"Markup {entered:.2f}%"
                else:
                    new_prod.discount_reason = (
                        f"Markup {entered:.{decimal_places}f} {currency_sign}"
                    )

                new_prod.save()
                new_db_id = str(new_prod.id)

                if "products" not in self.document_data:
                    self.document_data["products"] = []
                self.document_data["products"].append(new_prod)
                logger.info("[MARKUP] Saved marked-up record %s, total=%s", new_db_id, new_total)

            except Exception as exc:
                logger.error("[MARKUP] Error cloning DB record: %s", exc)

        sale_list.add_product(
            product_name=product_name,
            quantity=product_qty,
            unit_price=float(new_unit_price),
            reference_id=new_db_id or 0,
            plu_no=last_sales_data.plu_no,
            department_no=last_sales_data.department_no,
            transaction_type=last_sales_data.transaction_type,
        )
        if new_db_id and sale_list.custom_sales_data_list:
            sale_list.custom_sales_data_list[-1].reference_id = new_db_id

        if self.document_data and self.document_data.get("head"):
            head = self.document_data["head"]
            if isinstance(head, AutoSaveModel):
                head = head.unwrap()
            try:
                totals = SaleService.calculate_document_totals(self.document_data)
                head.total_amount = totals["total_amount"]
                head.total_vat_amount = totals["total_vat_amount"]
                head.save()
                logger.info(
                    "[MARKUP] Updated totals: total=%s vat=%s",
                    head.total_amount, head.total_vat_amount,
                )
            except Exception as exc:
                logger.error("[MARKUP] Error recalculating totals: %s", exc)

            if hasattr(active_window, "amount_table") and active_window.amount_table:
                try:
                    SaleService.update_amount_table_from_document(
                        active_window.amount_table, head
                    )
                except Exception as exc:
                    logger.error("[MARKUP] Error updating amount_table: %s", exc)

        try:
            from pos.peripherals.hooks import sync_line_display_from_document
            if self.document_data:
                sync_line_display_from_document(self, self.document_data)
        except Exception:
            pass

        logger.info(
            "[MARKUP] mode=%s entered=%s markup_amount=%s new_total=%s product='%s'",
            mode, entered, markup_amount, new_total, product_name,
        )
        return True

    # ==================== INPUT MODIFICATION EVENTS ====================
    
    def _input_price_event(self, key=None):
        """
        Handle manual price entry or modification.
        
        Allows override of default item prices, typically
        for price adjustments or special pricing.
        
        Parameters:
            key: Optional parameter from numpad input
        
        Returns:
            bool: True if price input successful, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
            
        # TODO: Implement price override logic
        if key is not None:
            logger.debug("Input price - key pressed: %s", key)
        else:
            logger.debug("Input price - functionality to be implemented")
        return False
    
    def _input_quantity_event(self, key=None):
        """
        Handle the X (quantity multiplier) button.

        Reads the current numpad value and stores it as pending_quantity so the
        next sale operation (PLU button or barcode Enter) uses that quantity.
        Clears the numpad and updates the status bar to show 'x{qty}'.

        Parameters:
            key: Button widget passed when called from a button click event.
                 Also accepts a plain string (e.g. from numpad callback) but
                 individual digit presses are ignored.

        Returns:
            bool: True if quantity was set, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False

        try:
            from user_interface.control.numpad.numpad import NumPad

            # Resolve the parent window regardless of how we were called
            window = None
            if key is not None and hasattr(key, 'parent'):
                window = key.parent()
            if window is None:
                window = self.interface.window if hasattr(self, 'interface') else None

            if not window:
                logger.error("[INPUT_QTY] Could not resolve parent window")
                return False

            # Find numpad
            numpad = None
            numpads = window.findChildren(NumPad)
            if numpads:
                numpad = numpads[0]

            if not numpad:
                logger.error("[INPUT_QTY] NumPad not found")
                return False

            numpad_text = numpad.get_text()
            logger.debug("[INPUT_QTY] NumPad text: '%s'", numpad_text)

            if not numpad_text or not numpad_text.strip():
                logger.debug("[INPUT_QTY] No quantity entered in numpad")
                return False

            try:
                qty_value = float(numpad_text)
            except ValueError:
                logger.debug("[INPUT_QTY] Invalid quantity: '%s'", numpad_text)
                return False

            if qty_value <= 0:
                logger.debug("[INPUT_QTY] Quantity must be positive, got: %s", qty_value)
                return False

            self.pending_quantity = qty_value
            logger.info("[INPUT_QTY] pending_quantity set to: %s", self.pending_quantity)

            if hasattr(self, "awaiting_plu_inquiry"):
                self.awaiting_plu_inquiry = False

            # Clear numpad and refresh status bar immediately
            numpad.set_text("")
            self._refresh_status_bar()

            return True

        except Exception as e:
            logger.error("[INPUT_QTY] Error: %s", str(e))
            return False
    
    def _input_amount_event(self, key=None):
        """
        Handle manual amount entry for calculations.
        
        Allows direct entry of monetary amounts for
        calculations or special transactions.
        
        Parameters:
            key: Optional parameter from numpad input
        
        Returns:
            bool: True if amount input successful, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
            
        # TODO: Implement amount entry logic
        if key is not None:
            logger.debug("Input amount - key pressed: %s", key)
        else:
            logger.debug("Input amount - functionality to be implemented")
        return False
    
    # ==================== LOOKUP AND CALCULATION EVENTS ====================
    
    def _price_lookup_event(self, key=None):
        """
        Handle price lookup for items without selling.
        
        Displays item information and pricing without
        adding to current transaction.
        
        Parameters:
            key: Optional parameter from numpad input
        
        Returns:
            bool: True if lookup successful, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
            
        # TODO: Implement price lookup logic
        if key is not None:
            logger.debug("Price lookup - key pressed: %s", key)
        else:
            logger.debug("Price lookup - functionality to be implemented")
        return False
    
    def _subtotal_event(self):
        """
        Handle subtotal calculation and display.
        
        Calculates and displays current transaction subtotal
        before taxes and final total.
        
        Returns:
            bool: True if subtotal calculated successfully, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
            
        # TODO: Implement subtotal calculation
        logger.debug("Subtotal - functionality to be implemented")
        return False
    
    def _total_event(self):
        """
        Handle final total calculation and payment preparation.
        
        Calculates final transaction total including taxes,
        discounts, and prepares for payment processing.
        
        Returns:
            bool: True if total calculated successfully, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
            
        # TODO: Implement total calculation and payment prep
        logger.debug("Total - functionality to be implemented")
        return False
    
    def _clear_buffer_event(self):
        """
        Handle clearing of input buffer or temporary data.
        
        Clears any temporary input values, calculations,
        or pending operations without affecting transaction.
        
        Returns:
            bool: True if buffer cleared successfully, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
            
        # TODO: Implement buffer clearing logic
        logger.debug("Clear buffer - functionality to be implemented")
        return False
    
    # ==================== ADDITIONAL SALE OPERATIONS ====================
    
    def _sale_option_event(self):
        """
        Handle REPEAT and DELETE actions triggered from the sale list item popup.
        
        Called automatically by SaleList.on_item_clicked after the visual update
        has already been applied.  Syncs the chosen action with document_data and
        the database, then refreshes the amount_table.
        
        Returns:
            bool: True if the action was processed successfully, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False

        from PySide6.QtWidgets import QApplication
        from pos.service import SaleService
        from data_layer.auto_save import AutoSaveModel

        try:
            # Locate the window that owns the sale_list
            active_window = None
            app_qt = QApplication.instance()
            if app_qt:
                active_window = app_qt.activeWindow()

            if not active_window or not hasattr(active_window, 'sale_list'):
                # Fallback: use the interface window
                if hasattr(self, 'interface') and self.interface:
                    active_window = getattr(self.interface, 'window', None)

            if not active_window or not hasattr(active_window, 'sale_list'):
                logger.error("[SALE_OPTION] No window with sale_list found")
                return False

            sale_list = active_window.sale_list
            action = getattr(sale_list, 'last_action', None)
            sales_data = getattr(sale_list, 'last_action_data', None)

            if not action or not sales_data:
                logger.debug("[SALE_OPTION] No pending action in sale_list")
                return False

            # Consume the pending action immediately to prevent double-processing
            sale_list.last_action = None
            sale_list.last_action_data = None

            if not self.document_data or not self.document_data.get("head"):
                logger.error("[SALE_OPTION] No document_data or head found")
                return False

            head = self.document_data["head"]
            if isinstance(head, AutoSaveModel):
                head = head.unwrap()

            reference_id = str(sales_data.reference_id) if sales_data.reference_id else None
            transaction_type = sales_data.transaction_type  # "PLU", "DEPARTMENT", "SUBTOTAL", …

            logger.debug("[SALE_OPTION] action=%s type=%s ref=%s", action, transaction_type, reference_id)

            # Only PLU / DEPARTMENT lines have matching DB records
            if transaction_type not in ("PLU", "DEPARTMENT"):
                logger.debug("[SALE_OPTION] Non-product row (%s) – no DB update needed", transaction_type)
                return True

            if action == "DELETE":
                return self._handle_sale_item_delete(active_window, sale_list, head, reference_id, transaction_type)
            elif action == "REPEAT":
                return self._handle_sale_item_repeat(active_window, sale_list, head, reference_id, transaction_type)

            return False

        except Exception as e:
            logger.error("[SALE_OPTION] Unexpected error: %s", e)
            return False

    def _handle_sale_item_delete(self, window, sale_list, head, reference_id, transaction_type):
        """
        Persist a DELETE (cancel) action to document_data and the database.

        Marks the matching TransactionProductTemp / TransactionDepartmentTemp as
        cancelled, recalculates the document totals, and – when the document is
        left empty – marks the head as CANCELLED so a fresh document is created
        on the next sale.
        """
        from decimal import Decimal
        from pos.service import SaleService
        from data_layer.auto_save import AutoSaveModel
        from data_layer.model.definition.transaction_status import TransactionStatus

        try:
            # Locate and cancel the matching DB record
            db_record = None
            records = (
                self.document_data.get("products", [])
                if transaction_type == "PLU"
                else self.document_data.get("departments", [])
            )
            for rec in records:
                actual = rec.unwrap() if isinstance(rec, AutoSaveModel) else rec
                if reference_id and str(actual.id) == reference_id:
                    db_record = actual
                    break

            if db_record:
                db_record.is_cancel = True
                db_record.save()
                logger.info("[SALE_OPTION] Cancelled %s record %s", transaction_type, db_record.id)
            else:
                logger.warning("[SALE_OPTION] DELETE: DB record not found (ref=%s type=%s)", reference_id, transaction_type)

            # Recalculate totals skipping all cancelled lines
            totals = SaleService.calculate_document_totals(self.document_data)
            head.total_amount = totals["total_amount"]
            head.total_vat_amount = totals["total_vat_amount"]

            # Determine whether any active (non-cancelled) lines remain
            def _is_active(rec):
                actual = rec.unwrap() if isinstance(rec, AutoSaveModel) else rec
                return not getattr(actual, 'is_cancel', False)

            has_active = any(_is_active(p) for p in self.document_data.get("products", [])) or \
                         any(_is_active(d) for d in self.document_data.get("departments", []))

            if not has_active:
                # Document is now empty – cancel and close it
                logger.info("[SALE_OPTION] All items deleted – cancelling document")
                head.is_cancel = True
                head.is_closed = True
                head.transaction_status = TransactionStatus.CANCELLED.value
                head.total_amount = Decimal('0')
                head.total_vat_amount = Decimal('0')
                head.save()
                self.document_data = None
                self._update_statusbar()

                # Zero out the amount_table
                if hasattr(window, 'amount_table') and window.amount_table:
                    window.amount_table.receipt_total_price = Decimal('0')
                    window.amount_table.discount_total_amount = Decimal('0')
                    window.amount_table.receipt_total_payment = Decimal('0')
            else:
                head.save()
                if hasattr(window, 'amount_table') and window.amount_table:
                    SaleService.update_amount_table_from_document(window.amount_table, head)

            logger.info("[SALE_OPTION] DELETE complete – total_amount=%s",
                        head.total_amount if self.document_data else Decimal('0'))
            from pos.peripherals.hooks import sync_line_display_cleared, sync_line_display_from_document
            if self.document_data:
                sync_line_display_from_document(self, self.document_data)
            else:
                sync_line_display_cleared(self)
            return True

        except Exception as e:
            logger.error("[SALE_OPTION] DELETE error: %s", e)
            return False

    def _handle_sale_item_repeat(self, window, sale_list, head, reference_id, transaction_type):
        """
        Persist a REPEAT action to document_data and the database.

        Clones the original TransactionProductTemp / TransactionDepartmentTemp,
        saves the new record, links its ID to the freshly-added SalesData row,
        and refreshes the document totals and amount_table.
        """
        from uuid import uuid4
        from pos.service import SaleService
        from data_layer.auto_save import AutoSaveModel

        try:
            # Locate the original DB record
            db_record = None
            records = (
                self.document_data.get("products", [])
                if transaction_type == "PLU"
                else self.document_data.get("departments", [])
            )
            for rec in records:
                actual = rec.unwrap() if isinstance(rec, AutoSaveModel) else rec
                if reference_id and str(actual.id) == reference_id:
                    db_record = actual
                    break

            # line_no for the new record = total existing lines + 1
            new_line_no = (
                len(self.document_data.get("products", [])) +
                len(self.document_data.get("departments", []))
            ) + 1

            new_db_id = None

            if db_record and transaction_type == "PLU":
                from data_layer.model import TransactionProductTemp
                new_prod = TransactionProductTemp()
                for col in db_record.__table__.columns.keys():
                    if hasattr(db_record, col):
                        setattr(new_prod, col, getattr(db_record, col))
                new_prod.id = uuid4()
                new_prod.line_no = new_line_no
                new_prod.is_cancel = False
                new_prod.save()
                if "products" not in self.document_data:
                    self.document_data["products"] = []
                self.document_data["products"].append(new_prod)
                new_db_id = str(new_prod.id)
                logger.info("[SALE_OPTION] REPEAT: saved new product record %s (line_no=%s)", new_prod.id, new_line_no)

            elif db_record and transaction_type == "DEPARTMENT":
                from data_layer.model import TransactionDepartmentTemp
                new_dept = TransactionDepartmentTemp()
                for col in db_record.__table__.columns.keys():
                    if hasattr(db_record, col):
                        setattr(new_dept, col, getattr(db_record, col))
                new_dept.id = uuid4()
                new_dept.line_no = new_line_no
                new_dept.is_cancel = False
                new_dept.save()
                if "departments" not in self.document_data:
                    self.document_data["departments"] = []
                self.document_data["departments"].append(new_dept)
                new_db_id = str(new_dept.id)
                logger.info("[SALE_OPTION] REPEAT: saved new department record %s (line_no=%s)", new_dept.id, new_line_no)

            else:
                logger.warning("[SALE_OPTION] REPEAT: DB record not found (ref=%s type=%s)", reference_id, transaction_type)

            # Link the new DB record ID to the newly-appended SalesData row
            if new_db_id and sale_list.custom_sales_data_list:
                sale_list.custom_sales_data_list[-1].reference_id = new_db_id

            # Recalculate and persist updated totals
            totals = SaleService.calculate_document_totals(self.document_data)
            head.total_amount = totals["total_amount"]
            head.total_vat_amount = totals["total_vat_amount"]
            head.save()

            if hasattr(window, 'amount_table') and window.amount_table:
                SaleService.update_amount_table_from_document(window.amount_table, head)

            logger.info("[SALE_OPTION] REPEAT complete – total_amount=%s", head.total_amount)
            from pos.peripherals.hooks import sync_line_display_from_document
            sync_line_display_from_document(self, self.document_data)
            return True

        except Exception as e:
            logger.error("[SALE_OPTION] REPEAT error: %s", e)
            return False
    
    def _sale_shortcut_event(self):
        """
        Handle sale shortcut operations.
        
        Processes quick sale shortcuts configured for frequently used items.
        Shortcut can trigger PLU sales, department sales, or function calls.
        
        Process:
        1. Verify authentication and transaction state
        2. Get shortcut configuration from button/control
        3. Execute shortcut action (PLU, department, or function)
        4. Update transaction state and refresh display
        
        Returns:
            bool: True if shortcut executed successfully, False otherwise
        """
        logger.warning("Sale shortcut event - method not implemented yet")
        return False

    # ==================== RESTAURANT TABLE OPERATIONS ====================
    
    def _table_open_event(self):
        """
        Handle opening a new restaurant table.
        
        Opens a new dining table for order taking in restaurant mode.
        Associates subsequent orders with the opened table.
        
        Returns:
            bool: True if table opened successfully, False otherwise
        """
        logger.warning("Table open event - method not implemented yet")
        return False
    
    def _table_close_event(self):
        """
        Handle closing a restaurant table.
        
        Closes an active table after payment completion.
        Finalizes all orders and clears table status.
        
        Returns:
            bool: True if table closed successfully, False otherwise
        """
        logger.warning("Table close event - method not implemented yet")
        return False
    
    def _table_select_event(self):
        """
        Handle selecting an existing restaurant table.
        
        Selects an active table to view or modify orders.
        Loads table's current order status and items.
        
        Returns:
            bool: True if table selected successfully, False otherwise
        """
        logger.warning("Table select event - method not implemented yet")
        return False
    
    def _table_transfer_event(self):
        """
        Handle transferring orders between restaurant tables.
        
        Moves orders from one table to another table.
        Updates table statuses and order associations.
        
        Returns:
            bool: True if table transferred successfully, False otherwise
        """
        logger.warning("Table transfer event - method not implemented yet")
        return False
    
    def _table_merge_event(self):
        """
        Handle merging multiple restaurant tables.
        
        Combines orders from multiple tables into a single table.
        Useful for large parties that need multiple tables.
        
        Returns:
            bool: True if tables merged successfully, False otherwise
        """
        logger.warning("Table merge event - method not implemented yet")
        return False
    
    def _table_split_event(self):
        """
        Handle splitting restaurant table orders.
        
        Divides orders from one table into multiple separate tables.
        Allows splitting checks for different payment methods.
        
        Returns:
            bool: True if table split successfully, False otherwise
        """
        logger.warning("Table split event - method not implemented yet")
        return False
    
    def _table_status_event(self):
        """
        Handle viewing restaurant table status.
        
        Displays current status of all tables including:
        - Active/occupied tables  
        - Order totals and item counts
        - Service time information
        
        Returns:
            bool: True if status displayed successfully, False otherwise
        """
        logger.warning("Table status event - method not implemented yet")
        return False
    
    def _table_list_event(self):
        """
        Handle displaying restaurant table list.
        
        Shows list of all available tables with their current status.
        Allows selection of tables for various operations.
        
        Returns:
            bool: True if table list displayed successfully, False otherwise
        """
        logger.warning("Table list event - method not implemented yet")
        return False
    
    # ==================== RESTAURANT ORDER OPERATIONS ====================
    
    def _order_add_event(self):
        """
        Handle adding items to restaurant order.
        
        Adds selected items to the current table's order.
        Updates order totals and sends to kitchen if configured.
        
        Returns:
            bool: True if order added successfully, False otherwise
        """
        logger.warning("Order add event - method not implemented yet")
        return False
    
    def _order_cancel_event(self):
        """
        Handle canceling restaurant order items.
        
        Cancels specific items from the current table's order.
        Updates totals and notifies kitchen of cancellation.
        
        Returns:
            bool: True if order canceled successfully, False otherwise
        """
        logger.warning("Order cancel event - method not implemented yet")
        return False
    
    def _order_modify_event(self):
        """
        Handle modifying restaurant order items.
        
        Allows modification of quantities, prices, or special instructions
        for items in the current table's order.
        
        Returns:
            bool: True if order modified successfully, False otherwise
        """
        logger.warning("Order modify event - method not implemented yet")
        return False
    
    def _order_send_to_kitchen_event(self):
        """
        Handle sending orders to kitchen.
        
        Sends current table's orders to kitchen for preparation.
        Updates order status and prints kitchen tickets if configured.
        
        Returns:
            bool: True if order sent successfully, False otherwise
        """
        logger.warning("Order send to kitchen event - method not implemented yet")
        return False
    
    def _order_ready_event(self):
        """
        Handle marking orders as ready.
        
        Marks kitchen orders as ready for serving.
        Updates order status and notifies wait staff.
        
        Returns:
            bool: True if order marked ready successfully, False otherwise
        """
        logger.warning("Order ready event - method not implemented yet")
        return False
    
    # ==================== RESTAURANT CHECK OPERATIONS ====================
    
    def _check_open_event(self):
        """
        Handle opening a new check for restaurant table.
        
        Creates a new check/bill for the current table.
        Initializes check with current order items.
        
        Returns:
            bool: True if check opened successfully, False otherwise
        """
        logger.warning("Check open event - method not implemented yet")
        return False
    
    def _check_close_event(self):
        """
        Handle closing restaurant check.
        
        Finalizes and closes the current check after payment.
        Updates table status and archives check data.
        
        Returns:
            bool: True if check closed successfully, False otherwise
        """
        logger.warning("Check close event - method not implemented yet")
        return False
    
    def _check_print_event(self):
        """
        Handle printing restaurant check.
        
        Prints the current check/bill for customer review.
        Shows itemized orders, taxes, and total amounts.
        
        Returns:
            bool: True if check printed successfully, False otherwise
        """
        logger.warning("Check print event - method not implemented yet")
        return False
    
    def _check_split_event(self):
        """
        Handle splitting restaurant check.
        
        Divides a single check into multiple separate checks.
        Allows different payment methods for different portions.
        
        Returns:
            bool: True if check split successfully, False otherwise
        """
        logger.warning("Check split event - method not implemented yet")
        return False
    
    def _check_merge_event(self):
        """
        Handle merging restaurant checks.
        
        Combines multiple checks into a single check.
        Useful for combining separate orders into one payment.
        
        Returns:
            bool: True if checks merged successfully, False otherwise
        """
        logger.warning("Check merge event - method not implemented yet")
        return False
    
    # ==================== MARKET SALE SUSPENSION OPERATIONS ====================
    
    def _suspend_sale_event(self):
        """
        Handle suspending current sale transaction.
        
        Temporarily saves the current transaction for later completion.
        Allows starting new transactions while preserving suspended one.
        
        Returns:
            bool: True if sale suspended successfully, False otherwise
        """
        from data_layer.enums import FormName
        from data_layer.auto_save import AutoSaveModel
        from data_layer.model.definition.transaction_status import TransactionStatus

        if not self.login_succeed:
            return False

        dd = self.document_data
        if dd and dd.get("head"):
            products = dd.get("products") or []
            departments = dd.get("departments") or []
            line_count = len(products) + len(departments)
            if line_count == 0:
                # New DRAFT (or any empty open document) before first line: show parked-sales list
                self.interface.redraw(form_name=FormName.SUSPENDED_SALES_MARKET.name)
                logger.info("[SUSPEND_SALE] Empty cart — opened suspended sales list")
                return True

            head = dd["head"]
            head_obj = head.unwrap() if isinstance(head, AutoSaveModel) else head
            if getattr(head_obj, "is_pending", False):
                logger.warning("[SUSPEND_SALE] Document already marked pending")
                return False

            status = getattr(head_obj, "transaction_status", None)
            if status not in (
                TransactionStatus.ACTIVE.value,
                TransactionStatus.DRAFT.value,
            ):
                logger.info("[SUSPEND_SALE] Not in suspendable status: %s", status)
                return False

            if not self.set_document_pending(True):
                logger.error("[SUSPEND_SALE] set_document_pending failed")
                return False

            self.document_data = None
            if not self.create_empty_document():
                logger.error("[SUSPEND_SALE] Failed to create new draft after suspend")
            self.interface.redraw(form_name=FormName.SALE.name)
            logger.info("[SUSPEND_SALE] Sale suspended; new draft created and UI refreshed")
            return True

        self.interface.redraw(form_name=FormName.SUSPENDED_SALES_MARKET.name)
        logger.info("[SUSPEND_SALE] Opened suspended sales list (market)")
        return True
    
    def _resume_sale_event(self):
        """
        Handle resuming suspended sale transaction.
        
        Restores a previously suspended transaction for completion.
        Loads all items, totals, and transaction state.
        
        Returns:
            bool: True if sale resumed successfully, False otherwise
        """
        from data_layer.enums import FormName, ControlName
        from user_interface.control.datagrid import DataGrid
        from PySide6.QtWidgets import QApplication

        if not self.login_succeed:
            return False

        window = QApplication.instance().activeWindow() if QApplication.instance() else None
        if not window:
            return False

        grid = None
        for w in window.findChildren(DataGrid):
            if getattr(w, "name", None) == ControlName.SUSPENDED_SALES_DATAGRID.value:
                grid = w
                break
        if not grid:
            logger.warning("[RESUME_SALE] Suspended sales grid not found")
            return False

        row = grid.get_selected_row()
        if not row:
            logger.info("[RESUME_SALE] No row selected")
            return False

        head_id_str = row[0].strip() if row[0] else ""
        if not head_id_str:
            return False

        self.abandon_empty_open_document_if_any()

        if not self.resume_suspended_market_document(head_id_str):
            return False

        self.prepare_navigation_resume_sale_from_suspended_market()
        self.interface.redraw(form_name=FormName.SALE.name, skip_history_update=True)
        logger.info("[RESUME_SALE] Resumed document %s", head_id_str)
        return True
    
    def _suspend_list_event(self):
        """
        Handle displaying list of suspended sales.
        
        Shows all currently suspended transactions with details.
        Allows selection of suspended sale to resume or delete.
        
        Returns:
            bool: True if suspend list displayed successfully, False otherwise
        """
        logger.warning("Suspend list event - method not implemented yet")
        return False
    
    def _delete_suspended_sale_event(self):
        """
        Handle deleting suspended sale transaction.
        
        Permanently removes a suspended transaction from storage.
        Cannot be recovered after deletion.
        
        Returns:
            bool: True if suspended sale deleted successfully, False otherwise
        """
        logger.warning("Delete suspended sale event - method not implemented yet")
        return False
    
    def _suspend_detail_event(self):
        """
        Handle displaying suspended sale details.
        
        Shows detailed information about a selected suspended sale.
        Includes items, quantities, prices, and transaction metadata.
        
        Returns:
            bool: True if suspend detail displayed successfully, False otherwise
        """
        logger.warning("Suspend detail event - method not implemented yet")
        return False