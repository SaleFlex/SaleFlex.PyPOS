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
    
    def _update_document_data_for_sale(self, sale_type, product=None, department=None, 
                                       quantity=1.0, unit_price=0.0, product_barcode=None, 
                                       department_no=None, line_no=None):
        """
        Update document_data with sale information.
        
        This method updates TransactionHeadTemp and creates TransactionProductTemp or
        TransactionDepartmentTemp records based on the sale type.
        
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
            from datetime import datetime
            from data_layer.model import TransactionProductTemp, TransactionDepartmentTemp, Vat
            from data_layer.model.definition.transaction_status import TransactionStatus
            from decimal import Decimal
            from data_layer.model import DepartmentMainGroup, DepartmentSubGroup
            
            if not self.document_data or not self.document_data.get("head"):
                print("[UPDATE_DOCUMENT_DATA] No document_data or head found")
                return False
            
            head = self.document_data["head"]
            
            # Ensure fk_customer_id is set (should be set in create_empty_document, but check anyway)
            if not head.fk_customer_id:
                from data_layer.model import Customer
                from data_layer.engine import Engine
                
                # Try to find or create default customer
                with Engine().get_session() as session:
                    walk_in_customer = session.query(Customer).filter(
                        Customer.name.ilike("%walk-in%") | Customer.name.ilike("%anonymous%"),
                        Customer.is_deleted == False
                    ).first()
                    
                    if walk_in_customer:
                        head.fk_customer_id = walk_in_customer.id
                    else:
                        first_customer = session.query(Customer).filter(
                            Customer.is_deleted == False
                        ).first()
                        
                        if first_customer:
                            head.fk_customer_id = first_customer.id
                        else:
                            # Create default customer
                            default_customer = Customer(
                                name="Walk-in",
                                last_name="Customer",
                                description="Default walk-in customer for POS transactions"
                            )
                            if hasattr(self, 'cashier_data') and self.cashier_data:
                                default_customer.fk_cashier_create_id = self.cashier_data.id
                                default_customer.fk_cashier_update_id = self.cashier_data.id
                            default_customer.create()
                            head.fk_customer_id = default_customer.id
            
            # Update TransactionHeadTemp fields
            # Set transaction_date_time if empty
            if not head.transaction_date_time:
                head.transaction_date_time = datetime.now()
            
            # Update transaction_status from DRAFT to ACTIVE if still DRAFT
            if head.transaction_status == TransactionStatus.DRAFT.value:
                head.transaction_status = TransactionStatus.ACTIVE.value
            
            # Get closure_number from closure
            if self.closure and self.closure.get("closure"):
                closure = self.closure["closure"]
                if closure and closure.closure_number:
                    head.closure_number = closure.closure_number
            
            # Set base_currency from CurrentStatus.current_currency
            if hasattr(self, 'current_currency') and self.current_currency:
                head.base_currency = self.current_currency
            
            # Set order_source and order_channel
            head.order_source = "in_store"
            head.order_channel = "cashier"
            
            # Calculate line_no if not provided (use current products/departments count)
            if line_no is None:
                line_no = len(self.document_data.get("products", [])) + len(self.document_data.get("departments", [])) + 1
            
            # Calculate totals
            total_price = float(quantity) * float(unit_price)
            vat_rate = 0.0
            total_vat = 0.0
            
            if sale_type in ["PLU_CODE", "PLU_BARCODE"]:
                # PLU sale - create TransactionProductTemp
                if not product:
                    print("[UPDATE_DOCUMENT_DATA] Product required for PLU sale")
                    return False
                
                # Get department from product
                dept_main_group_id = product.fk_department_main_group_id
                dept_sub_group_id = product.fk_department_sub_group_id
                
                # Get VAT rate from department
                dept_main_groups = self.product_data.get("DepartmentMainGroup", [])
                dept_main_group = next((d for d in dept_main_groups if d.id == dept_main_group_id), None)
                
                if dept_main_group and dept_main_group.fk_vat_id:
                    vats = self.product_data.get("Vat", [])
                    vat = next((v for v in vats if v.id == dept_main_group.fk_vat_id), None)
                    if vat:
                        vat_rate = float(vat.rate)
                
                # Calculate VAT: total_vat = (total_price * (vat_rate / (100 + vat_rate)))
                if vat_rate > 0:
                    total_vat = total_price * (vat_rate / (100 + vat_rate))
                
                # Create TransactionProductTemp
                product_temp = TransactionProductTemp()
                product_temp.fk_transaction_head_id = head.id
                product_temp.line_no = line_no
                product_temp.fk_department_main_group_id = dept_main_group_id
                product_temp.fk_department_sub_group_id = dept_sub_group_id
                product_temp.fk_product_id = product.id
                product_temp.product_code = product.code
                product_temp.product_name = product.short_name if product.short_name else product.name
                product_temp.product_description = product.description
                product_temp.vat_rate = Decimal(str(vat_rate))
                product_temp.unit_price = Decimal(str(unit_price))
                product_temp.quantity = Decimal(str(quantity))
                product_temp.total_price = Decimal(str(total_price))
                product_temp.total_vat = Decimal(str(total_vat))
                
                # Set product_barcode_id if provided
                if sale_type == "PLU_BARCODE" and product_barcode:
                    product_temp.fk_product_barcode_id = product_barcode.id
                
                # Add to document_data
                if "products" not in self.document_data:
                    self.document_data["products"] = []
                self.document_data["products"].append(product_temp)
                
                # Manually save the product temp model to database
                # AutoSaveDict doesn't trigger save on list.append(), so we need to save manually
                try:
                    product_temp.save()
                    print(f"[UPDATE_DOCUMENT_DATA] ✓ Saved TransactionProductTemp to database")
                except Exception as e:
                    print(f"[UPDATE_DOCUMENT_DATA] Error saving TransactionProductTemp: {e}")
                    import traceback
                    traceback.print_exc()
                
            elif sale_type == "DEPARTMENT":
                # Department sale - create TransactionDepartmentTemp
                if not department:
                    print("[UPDATE_DOCUMENT_DATA] Department required for department sale")
                    return False
                
                # Determine if department is main or sub group
                dept_main_group = None
                dept_sub_group = None
                
                if isinstance(department, DepartmentMainGroup):
                    dept_main_group = department
                elif isinstance(department, DepartmentSubGroup):
                    dept_sub_group = department
                    # Find main group from sub group
                    # First try main_group_id if it exists
                    if hasattr(department, 'main_group_id') and department.main_group_id:
                        dept_main_groups = self.product_data.get("DepartmentMainGroup", [])
                        dept_main_group = next((d for d in dept_main_groups if d.id == department.main_group_id), None)
                    
                    # If main_group_id didn't work, try to find by department_no logic
                    if not dept_main_group and department_no:
                        if department_no > 99:
                            # For sub groups > 99, extract first digit(s) to find main group
                            # For example: 101 -> main group 1, 201 -> main group 2
                            main_group_code = str(department_no)[0]  # First digit
                            dept_main_groups = self.product_data.get("DepartmentMainGroup", [])
                            dept_main_group = next((d for d in dept_main_groups if d.code == main_group_code), None)
                        
                        # If still not found, use first main group as fallback
                        if not dept_main_group:
                            dept_main_groups = self.product_data.get("DepartmentMainGroup", [])
                            if dept_main_groups:
                                dept_main_group = dept_main_groups[0]  # Fallback to first main group
                
                if not dept_main_group:
                    print("[UPDATE_DOCUMENT_DATA] Could not determine department main group")
                    return False
                
                # Get VAT rate from department main group
                if dept_main_group.fk_vat_id:
                    vats = self.product_data.get("Vat", [])
                    vat = next((v for v in vats if v.id == dept_main_group.fk_vat_id), None)
                    if vat:
                        vat_rate = float(vat.rate)
                
                # Calculate VAT: total_department_vat = (total_department * (vat_rate / (100 + vat_rate)))
                total_department = total_price
                if vat_rate > 0:
                    total_vat = total_department * (vat_rate / (100 + vat_rate))
                
                # Create TransactionDepartmentTemp
                dept_temp = TransactionDepartmentTemp()
                dept_temp.fk_transaction_head_id = head.id
                dept_temp.line_no = line_no
                dept_temp.fk_department_main_group_id = dept_main_group.id
                dept_temp.vat_rate = Decimal(str(vat_rate))
                dept_temp.total_department = Decimal(str(total_department))
                dept_temp.total_department_vat = Decimal(str(total_vat))
                
                # Set fk_department_sub_group_id if department_no > 99 or if we have a sub group
                if dept_sub_group:
                    dept_temp.fk_department_sub_group_id = dept_sub_group.id
                elif department_no and department_no > 99:
                    # Find department_sub_group
                    dept_sub_groups = self.product_data.get("DepartmentSubGroup", [])
                    dept_sub_group = next((d for d in dept_sub_groups if d.code == str(department_no)), None)
                    if dept_sub_group:
                        dept_temp.fk_department_sub_group_id = dept_sub_group.id
                
                # Add to document_data
                if "departments" not in self.document_data:
                    self.document_data["departments"] = []
                self.document_data["departments"].append(dept_temp)
                
                # Manually save the department temp model to database
                # AutoSaveDict doesn't trigger save on list.append(), so we need to save manually
                try:
                    dept_temp.save()
                    print(f"[UPDATE_DOCUMENT_DATA] ✓ Saved TransactionDepartmentTemp to database")
                except Exception as e:
                    print(f"[UPDATE_DOCUMENT_DATA] Error saving TransactionDepartmentTemp: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Update TransactionHeadTemp totals
            # Sum all products and departments
            total_amount = Decimal('0')
            total_vat_amount = Decimal('0')
            
            for prod in self.document_data.get("products", []):
                if hasattr(prod, 'total_price'):
                    total_amount += Decimal(str(prod.total_price))
                if hasattr(prod, 'total_vat'):
                    total_vat_amount += Decimal(str(prod.total_vat))
            
            for dept in self.document_data.get("departments", []):
                if hasattr(dept, 'total_department'):
                    total_amount += Decimal(str(dept.total_department))
                if hasattr(dept, 'total_department_vat'):
                    total_vat_amount += Decimal(str(dept.total_department_vat))
            
            head.total_amount = total_amount
            head.total_vat_amount = total_vat_amount
            
            # Save document_data (AutoSaveDescriptor will handle saving)
            self.document_data = self.document_data
            
            print(f"[UPDATE_DOCUMENT_DATA] ✓ Updated document_data for {sale_type} sale")
            return True
            
        except Exception as e:
            print(f"[UPDATE_DOCUMENT_DATA] Error updating document_data: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # ==================== DEPARTMENT SALES EVENTS ====================
    
    def _sale_department(self, button=None):
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
        
        # Ensure document_data exists - create if not present
        if not self.document_data:
            print("[SALE_DEPARTMENT] document_data is None, creating empty document...")
            if not self.create_empty_document():
                print("[SALE_DEPARTMENT] Failed to create empty document")
                return False
        
        try:
            # Get button control name
            if button is None or not hasattr(button, 'control_name'):
                print("[SALE_DEPARTMENT] No button provided or button missing control_name")
                return False
            
            control_name = button.control_name
            print(f"[SALE_DEPARTMENT] Processing button with control_name: '{control_name}'")
            
            # Check if control name starts with "DEPARTMENT"
            if not control_name or not control_name.upper().startswith("DEPARTMENT"):
                print(f"[SALE_DEPARTMENT] Control name '{control_name}' does not start with DEPARTMENT")
                return False
            
            # Extract department number from control name (remove "DEPARTMENT" prefix)
            department_no_str = control_name[10:]  # Remove first 10 characters "DEPARTMENT"
            print(f"[SALE_DEPARTMENT] Extracted department number string: '{department_no_str}'")
            
            if not department_no_str:
                print("[SALE_DEPARTMENT] Empty department number after removing DEPARTMENT prefix")
                return False
            
            try:
                department_no = int(department_no_str)
            except ValueError:
                print(f"[SALE_DEPARTMENT] Invalid department number: '{department_no_str}'")
                return False
            
            print(f"[SALE_DEPARTMENT] Department number: {department_no}")
            
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
                print("[SALE_DEPARTMENT] NumPad widget not found in current window")
                return False
            
            # Get price from numpad
            numpad_text = numpad.get_text()
            print(f"[SALE_DEPARTMENT] NumPad text: '{numpad_text}'")
            
            if not numpad_text or numpad_text.strip() == "":
                print("[SALE_DEPARTMENT] No price entered in numpad")
                
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
                    print(f"[SALE_DEPARTMENT] Error showing message form: {e}")
                    import traceback
                    traceback.print_exc()
                
                return False
            
            try:
                # Convert numpad text to integer (numpad value is multiplied by 10^decimal_places)
                numpad_value = int(numpad_text)
            except ValueError:
                print(f"[SALE_DEPARTMENT] Invalid price format: '{numpad_text}'")
                return False
            
            print(f"[SALE_DEPARTMENT] NumPad value (before division): {numpad_value}")
            
            # Get current currency and divide by 10^decimal_places
            from user_interface.form.message_form import MessageForm
            from data_layer.model import LabelValue
            
            # Get current currency from CurrentData
            current_currency_sign = self.current_currency if hasattr(self, 'current_currency') and self.current_currency else "GBP"
            print(f"[SALE_DEPARTMENT] Current currency sign: '{current_currency_sign}'")
            
            # Find currency from product_data (more efficient than database query)
            decimal_places = 2  # Default
            try:
                # Try to get currency from product_data if available
                if hasattr(self, 'product_data') and self.product_data:
                    all_currencies = self.product_data.get("Currency", [])
                    currency = next((c for c in all_currencies if c.sign == current_currency_sign and not c.is_deleted), None)
                    if currency and currency.decimal_places is not None:
                        decimal_places = currency.decimal_places
                        print(f"[SALE_DEPARTMENT] Currency decimal_places from product_data: {decimal_places}")
                    else:
                        print(f"[SALE_DEPARTMENT] Currency not found in product_data with sign: '{current_currency_sign}', defaulting to decimal_places=2")
                else:
                    # Fallback: query from database
                    from data_layer.model import Currency
                    currencies = Currency.filter_by(sign=current_currency_sign, is_deleted=False)
                    if currencies and len(currencies) > 0:
                        currency = currencies[0]
                        decimal_places = currency.decimal_places if currency.decimal_places is not None else 2
                        print(f"[SALE_DEPARTMENT] Currency decimal_places from database: {decimal_places}")
                    else:
                        print(f"[SALE_DEPARTMENT] Currency not found with sign: '{current_currency_sign}', defaulting to decimal_places=2")
            except Exception as e:
                print(f"[SALE_DEPARTMENT] Error getting currency decimal_places: {e}, defaulting to 2")
                decimal_places = 2
            
            # Divide by 10^decimal_places to get actual price
            divisor = 10 ** decimal_places
            price = float(numpad_value) / divisor
            print(f"[SALE_DEPARTMENT] Price after division (numpad_value / {divisor}): {price}")
            
            # Import SaleList
            from user_interface.control.sale_list.sale_list import SaleList
            
            department = None
            department_name = ""
            
            # Determine which table to query based on department number
            if 1 <= department_no <= 99:
                # Query department_main_group from product_data cache
                print(f"[SALE_DEPARTMENT] Querying department_main_group for code: '{department_no}'")
                departments = [
                    d for d in self.product_data.get("DepartmentMainGroup", [])
                    if d.code == str(department_no) and not (hasattr(d, 'is_deleted') and d.is_deleted)
                ]
                
                if not departments or len(departments) == 0:
                    print(f"[SALE_DEPARTMENT] No department_main_group found with code: '{department_no}'")
                    return False
                
                department = departments[0]
                department_name = department.name if department.name else f"Department {department_no}"
                print(f"[SALE_DEPARTMENT] Found department_main_group: {department_name}")
                
            elif department_no > 99:
                # Query department_sub_group from product_data cache
                print(f"[SALE_DEPARTMENT] Querying department_sub_group for code: '{department_no}'")
                departments = [
                    d for d in self.product_data.get("DepartmentSubGroup", [])
                    if d.code == str(department_no) and not (hasattr(d, 'is_deleted') and d.is_deleted)
                ]
                
                if not departments or len(departments) == 0:
                    print(f"[SALE_DEPARTMENT] No department_sub_group found with code: '{department_no}'")
                    return False
                
                department = departments[0]
                department_name = department.name if department.name else f"Department {department_no}"
                print(f"[SALE_DEPARTMENT] Found department_sub_group: {department_name}")
            else:
                print(f"[SALE_DEPARTMENT] Invalid department number range: {department_no}")
                return False
            
            # Check max_price if defined
            if department.max_price is not None:
                max_price = float(department.max_price)
                print(f"[SALE_DEPARTMENT] Max price check: {price} <= {max_price}")
                
                if price > max_price:
                    print(f"[SALE_DEPARTMENT] Price {price} exceeds max_price {max_price}")
                    
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
                        print(f"[SALE_DEPARTMENT] Error showing message form: {e}")
                    
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
                print("[SALE_DEPARTMENT] SaleList widget not found in current window")
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
                print(f"[SALE_DEPARTMENT] ✓ Successfully added department '{department_name}' to sale list")
                
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
                
                # Clear numpad after successful sale
                numpad.set_text("")
                print(f"[SALE_DEPARTMENT] Cleared numpad")
                
                return True
            else:
                print("[SALE_DEPARTMENT] Failed to add department to sale list")
                return False
                
        except Exception as e:
            print(f"[SALE_DEPARTMENT] Error processing department sale: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _sale_department_by_no(self, key=None):
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
            print(f"Department sale by number - key pressed: {key}")
        else:
            print("Department sale by number - functionality to be implemented")
        return False
    
    # ==================== PLU SALES EVENTS ====================
    
    def _sale_plu_code(self, button=None):
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
        
        # Ensure document_data exists - create if not present
        if not self.document_data:
            print("[SALE_PLU_CODE] document_data is None, creating empty document...")
            if not self.create_empty_document():
                print("[SALE_PLU_CODE] Failed to create empty document")
                return False
        
        try:
            # Get button control name
            if button is None or not hasattr(button, 'control_name'):
                print("[SALE_PLU_CODE] No button provided or button missing control_name")
                return False
            
            control_name = button.control_name
            print(f"[SALE_PLU_CODE] Processing button with control_name: '{control_name}'")
            
            # Check if control name starts with "PLU"
            if not control_name or not control_name.upper().startswith("PLU"):
                print(f"[SALE_PLU_CODE] Control name '{control_name}' does not start with PLU")
                return False
            
            # Extract code from control name (remove "PLU" prefix)
            product_code = control_name[3:]  # Remove first 3 characters "PLU"
            print(f"[SALE_PLU_CODE] Extracted product code: '{product_code}'")
            
            if not product_code:
                print("[SALE_PLU_CODE] Empty code after removing PLU prefix")
                return False
            
            # Import SaleList
            from user_interface.control.sale_list.sale_list import SaleList
            
            # Search for product with matching code from product_data cache
            products = [
                p for p in self.product_data.get("Product", [])
                if p.code == product_code and not (hasattr(p, 'is_deleted') and p.is_deleted)
            ]
            
            if not products or len(products) == 0:
                print(f"[SALE_PLU_CODE] No product found with code: '{product_code}'")
                return False
            
            # Get the first matching product
            product = products[0]
            print(f"[SALE_PLU_CODE] Found product: {product.name} (short_name: {product.short_name})")
            
            # Get sale price from product
            sale_price = float(product.sale_price) if product.sale_price else 0.0
            print(f"[SALE_PLU_CODE] Using sale_price: {sale_price}")
            
            if sale_price == 0.0:
                print("[SALE_PLU_CODE] Warning: Product sale_price is 0")
            
            # Find sale_list widget in the current window
            # Button's parent should be BaseWindow
            current_window = button.parent() if button else None
            
            if not current_window:
                print("[SALE_PLU_CODE] Button has no parent window")
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
                print("[SALE_PLU_CODE] SaleList widget not found in current window")
                return False
            
            # Get quantity from numpad if available
            quantity = 1.0  # Default quantity
            numpad = None
            
            # Search for NumPad widget using findChildren (searches nested widgets too)
            from user_interface.control.numpad.numpad import NumPad
            numpads = current_window.findChildren(NumPad)
            if numpads:
                numpad = numpads[0]
            
            if numpad:
                numpad_text = numpad.get_text()
                print(f"[SALE_PLU_CODE] NumPad text: '{numpad_text}'")
                
                if numpad_text and numpad_text.strip():
                    try:
                        # Try to convert numpad text to quantity (as integer or float)
                        quantity_value = float(numpad_text)
                        if quantity_value > 0:
                            quantity = quantity_value
                            print(f"[SALE_PLU_CODE] Using quantity from numpad: {quantity}")
                        else:
                            print(f"[SALE_PLU_CODE] NumPad value '{quantity_value}' is not positive, using default quantity 1.0")
                    except ValueError:
                        print(f"[SALE_PLU_CODE] NumPad text '{numpad_text}' is not a valid number, using default quantity 1.0")
                    finally:
                        # Always clear numpad after attempting to read quantity (whether valid or not)
                        numpad.set_text("")
                        print(f"[SALE_PLU_CODE] Cleared numpad")
            
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
                print(f"[SALE_PLU_CODE] ✓ Successfully added product '{product_name}' to sale list")
                
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
                
                # Update button text to show product short_name
                button.setText(product_name)
                print(f"[SALE_PLU_CODE] Updated button text to: '{product_name}'")
                
                return True
            else:
                print("[SALE_PLU_CODE] Failed to add product to sale list")
                return False
                
        except Exception as e:
            print(f"[SALE_PLU_CODE] Error processing PLU code sale: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _sale_plu_barcode(self, button=None):
        """
        Handle PLU sale by barcode scanning/entry.
        
        Processes sales using barcode from button names.
        When a button with name starting with "PLU" and function SALE_PLU_BARCODE is clicked:
        1. Extract barcode from button name (e.g., PLU5000157070008 -> 5000157070008)
        2. Look up product_barcode table for matching barcode
        3. Get product from product table using fk_product_id
        4. Add item to sale list with product's sale_price
        5. Update button text to show product.short_name
        
        Parameters:
            button: Button object that was clicked (contains control_name attribute)
        
        Returns:
            bool: True if barcode sale successful, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
        
        try:
            # Get button control name
            if button is None or not hasattr(button, 'control_name'):
                print("[SALE_PLU_BARCODE] No button provided or button missing control_name")
                return False
            
            control_name = button.control_name
            print(f"[SALE_PLU_BARCODE] Processing button with control_name: '{control_name}'")
            
            # Check if control name starts with "PLU"
            if not control_name or not control_name.upper().startswith("PLU"):
                print(f"[SALE_PLU_BARCODE] Control name '{control_name}' does not start with PLU")
                return False
            
            # Extract barcode from control name (remove "PLU" prefix)
            barcode = control_name[3:]  # Remove first 3 characters "PLU"
            print(f"[SALE_PLU_BARCODE] Extracted barcode: '{barcode}'")
            
            if not barcode:
                print("[SALE_PLU_BARCODE] Empty barcode after removing PLU prefix")
                return False
            
            # Import SaleList
            from user_interface.control.sale_list.sale_list import SaleList
            
            # Search for product_barcode with matching barcode from product_data cache
            barcode_records = [
                pb for pb in self.product_data.get("ProductBarcode", [])
                if pb.barcode == barcode and not (hasattr(pb, 'is_deleted') and pb.is_deleted)
            ]
            
            if not barcode_records or len(barcode_records) == 0:
                print(f"[SALE_PLU_BARCODE] No product found with barcode: '{barcode}'")
                return False
            
            # Get the first matching barcode record
            product_barcode = barcode_records[0]
            print(f"[SALE_PLU_BARCODE] Found product_barcode: {product_barcode}")
            
            # Get product using fk_product_id from product_data cache
            products = [
                p for p in self.product_data.get("Product", [])
                if p.id == product_barcode.fk_product_id
            ]
            
            if not products or len(products) == 0:
                print(f"[SALE_PLU_BARCODE] Product not found with id: {product_barcode.fk_product_id}")
                return False
            
            product = products[0]
            
            print(f"[SALE_PLU_BARCODE] Found product: {product.name} (short_name: {product.short_name})")
            
            # Determine sale price (prefer product_barcode.sale_price, fallback to product.sale_price)
            sale_price = float(product_barcode.sale_price) if product_barcode.sale_price else float(product.sale_price)
            print(f"[SALE_PLU_BARCODE] Using sale_price: {sale_price}")
            
            # Find sale_list widget in the current window
            # Button's parent should be BaseWindow
            current_window = button.parent() if button else None
            
            if not current_window:
                print("[SALE_PLU_BARCODE] Button has no parent window")
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
                print("[SALE_PLU_BARCODE] SaleList widget not found in current window")
                return False
            
            # Get quantity from numpad if available
            quantity = 1.0  # Default quantity
            numpad = None
            
            # Search for NumPad widget using findChildren (searches nested widgets too)
            from user_interface.control.numpad.numpad import NumPad
            numpads = current_window.findChildren(NumPad)
            if numpads:
                numpad = numpads[0]
            
            if numpad:
                numpad_text = numpad.get_text()
                print(f"[SALE_PLU_BARCODE] NumPad text: '{numpad_text}'")
                
                if numpad_text and numpad_text.strip():
                    try:
                        # Try to convert numpad text to quantity (as integer or float)
                        quantity_value = float(numpad_text)
                        if quantity_value > 0:
                            quantity = quantity_value
                            print(f"[SALE_PLU_BARCODE] Using quantity from numpad: {quantity}")
                        else:
                            print(f"[SALE_PLU_BARCODE] NumPad value '{quantity_value}' is not positive, using default quantity 1.0")
                    except ValueError:
                        print(f"[SALE_PLU_BARCODE] NumPad text '{numpad_text}' is not a valid number, using default quantity 1.0")
                    finally:
                        # Always clear numpad after attempting to read quantity (whether valid or not)
                        numpad.set_text("")
                        print(f"[SALE_PLU_BARCODE] Cleared numpad")
            
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
                print(f"[SALE_PLU_BARCODE] ✓ Successfully added product '{product_name}' to sale list")
                
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
                
                # Update button text to show product short_name
                button.setText(product_name)
                print(f"[SALE_PLU_BARCODE] Updated button text to: '{product_name}'")
                
                return True
            else:
                print("[SALE_PLU_BARCODE] Failed to add product to sale list")
                return False
                
        except Exception as e:
            print(f"[SALE_PLU_BARCODE] Error processing PLU barcode sale: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _get_plu_from_maingroup(self):
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
        print("PLU main group selection - functionality to be implemented")
        return False
    
    # ==================== REPEAT SALES EVENTS ====================
    
    def _repeat_last_sale(self):
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
        print("Repeat last sale - functionality to be implemented")
        return False
    
    def _repeat_sale(self):
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
        print("Repeat sale - functionality to be implemented")
        return False
    
    # ==================== CANCELLATION EVENTS ====================
    
    def _cancel_department(self):
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
        print("Cancel department - functionality to be implemented")
        return False
    
    def _cancel_plu(self):
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
        print("Cancel PLU - functionality to be implemented")
        return False
    
    def _cancel_last_sale(self):
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
        print("Cancel last sale - functionality to be implemented")
        return False
    
    def _cancel_sale(self):
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
        print("Cancel sale - functionality to be implemented")
        return False
    
    def _cancel_document(self):
        """
        Handle cancellation of entire transaction document.
        
        Voids the complete current transaction, clearing all items
        and resetting to new transaction state.
        
        Returns:
            bool: True if document cancellation successful, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
            
        # TODO: Implement complete transaction void
        print("Cancel document - functionality to be implemented")
        return False
    
    # ==================== TRANSACTION MODIFICATION EVENTS ====================
    
    def _change_document_type(self):
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
        print("Change document type - functionality to be implemented")
        return False
    
    def _refund(self):
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
        print("Refund - functionality to be implemented")
        return False
    
    # ==================== DISCOUNT AND SURCHARGE EVENTS ====================
    
    def _discount_by_amount(self, key=None):
        """
        Handle discount application by fixed amount.
        
        Applies a specific monetary discount to selected items
        or entire transaction.
        
        Parameters:
            key: Optional parameter from numpad input
        
        Returns:
            bool: True if discount applied successfully, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
            
        # TODO: Implement fixed amount discount logic
        if key is not None:
            print(f"Discount by amount - key pressed: {key}")
        else:
            print("Discount by amount - functionality to be implemented")
        return False
    
    def _surcharge_by_amount(self, key=None):
        """
        Handle surcharge application by fixed amount.
        
        Applies a specific monetary surcharge to selected items
        or entire transaction.
        
        Parameters:
            key: Optional parameter from numpad input
        
        Returns:
            bool: True if surcharge applied successfully, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
            
        # TODO: Implement fixed amount surcharge logic
        if key is not None:
            print(f"Surcharge by amount - key pressed: {key}")
        else:
            print("Surcharge by amount - functionality to be implemented")
        return False
    
    def _discount_by_percent(self, key=None):
        """
        Handle discount application by percentage.
        
        Applies a percentage-based discount to selected items
        or entire transaction.
        
        Parameters:
            key: Optional parameter from numpad input
        
        Returns:
            bool: True if discount applied successfully, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
            
        # TODO: Implement percentage discount logic
        if key is not None:
            print(f"Discount by percent - key pressed: {key}")
        else:
            print("Discount by percent - functionality to be implemented")
        return False
    
    def _surcharge_by_percent(self, key=None):
        """
        Handle surcharge application by percentage.
        
        Applies a percentage-based surcharge to selected items
        or entire transaction.
        
        Parameters:
            key: Optional parameter from numpad input
        
        Returns:
            bool: True if surcharge applied successfully, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
            
        # TODO: Implement percentage surcharge logic
        if key is not None:
            print(f"Surcharge by percent - key pressed: {key}")
        else:
            print("Surcharge by percent - functionality to be implemented")
        return False
    
    # ==================== INPUT MODIFICATION EVENTS ====================
    
    def _input_price(self, key=None):
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
            print(f"Input price - key pressed: {key}")
        else:
            print("Input price - functionality to be implemented")
        return False
    
    def _input_quantity(self, key=None):
        """
        Handle manual quantity entry or modification.
        
        Allows entry of specific quantities for items,
        useful for bulk sales or fractional quantities.
        
        Parameters:
            key: Optional parameter from numpad input
        
        Returns:
            bool: True if quantity input successful, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
            
        # TODO: Implement quantity entry logic
        if key is not None:
            print(f"Input quantity - key pressed: {key}")
        else:
            print("Input quantity - functionality to be implemented")
        return False
    
    def _input_amount(self, key=None):
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
            print(f"Input amount - key pressed: {key}")
        else:
            print("Input amount - functionality to be implemented")
        return False
    
    # ==================== LOOKUP AND CALCULATION EVENTS ====================
    
    def _price_lookup(self, key=None):
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
            print(f"Price lookup - key pressed: {key}")
        else:
            print("Price lookup - functionality to be implemented")
        return False
    
    def _subtotal(self):
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
        print("Subtotal - functionality to be implemented")
        return False
    
    def _total(self):
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
        print("Total - functionality to be implemented")
        return False
    
    def _clear_buffer(self):
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
        print("Clear buffer - functionality to be implemented")
        return False
    
    # ==================== ADDITIONAL SALE OPERATIONS ====================
    
    def _sale_option(self):
        """
        Handle additional sale options and modifiers.
        
        Provides access to special sale options, modifiers,
        or advanced transaction features.
        
        Returns:
            bool: True if sale option applied successfully, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
            
        # TODO: Implement sale options interface
        print("Sale option - functionality to be implemented")
        return False
    
    def _sale_shortcut(self):
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
        print("Sale shortcut event - method not implemented yet")
        return False

    # ==================== RESTAURANT TABLE OPERATIONS ====================
    
    def _table_open(self):
        """
        Handle opening a new restaurant table.
        
        Opens a new dining table for order taking in restaurant mode.
        Associates subsequent orders with the opened table.
        
        Returns:
            bool: True if table opened successfully, False otherwise
        """
        print("Table open event - method not implemented yet")
        return False
    
    def _table_close(self):
        """
        Handle closing a restaurant table.
        
        Closes an active table after payment completion.
        Finalizes all orders and clears table status.
        
        Returns:
            bool: True if table closed successfully, False otherwise
        """
        print("Table close event - method not implemented yet")
        return False
    
    def _table_select(self):
        """
        Handle selecting an existing restaurant table.
        
        Selects an active table to view or modify orders.
        Loads table's current order status and items.
        
        Returns:
            bool: True if table selected successfully, False otherwise
        """
        print("Table select event - method not implemented yet")
        return False
    
    def _table_transfer(self):
        """
        Handle transferring orders between restaurant tables.
        
        Moves orders from one table to another table.
        Updates table statuses and order associations.
        
        Returns:
            bool: True if table transferred successfully, False otherwise
        """
        print("Table transfer event - method not implemented yet")
        return False
    
    def _table_merge(self):
        """
        Handle merging multiple restaurant tables.
        
        Combines orders from multiple tables into a single table.
        Useful for large parties that need multiple tables.
        
        Returns:
            bool: True if tables merged successfully, False otherwise
        """
        print("Table merge event - method not implemented yet")
        return False
    
    def _table_split(self):
        """
        Handle splitting restaurant table orders.
        
        Divides orders from one table into multiple separate tables.
        Allows splitting checks for different payment methods.
        
        Returns:
            bool: True if table split successfully, False otherwise
        """
        print("Table split event - method not implemented yet")
        return False
    
    def _table_status(self):
        """
        Handle viewing restaurant table status.
        
        Displays current status of all tables including:
        - Active/occupied tables  
        - Order totals and item counts
        - Service time information
        
        Returns:
            bool: True if status displayed successfully, False otherwise
        """
        print("Table status event - method not implemented yet")
        return False
    
    def _table_list(self):
        """
        Handle displaying restaurant table list.
        
        Shows list of all available tables with their current status.
        Allows selection of tables for various operations.
        
        Returns:
            bool: True if table list displayed successfully, False otherwise
        """
        print("Table list event - method not implemented yet")
        return False
    
    # ==================== RESTAURANT ORDER OPERATIONS ====================
    
    def _order_add(self):
        """
        Handle adding items to restaurant order.
        
        Adds selected items to the current table's order.
        Updates order totals and sends to kitchen if configured.
        
        Returns:
            bool: True if order added successfully, False otherwise
        """
        print("Order add event - method not implemented yet")
        return False
    
    def _order_cancel(self):
        """
        Handle canceling restaurant order items.
        
        Cancels specific items from the current table's order.
        Updates totals and notifies kitchen of cancellation.
        
        Returns:
            bool: True if order canceled successfully, False otherwise
        """
        print("Order cancel event - method not implemented yet")
        return False
    
    def _order_modify(self):
        """
        Handle modifying restaurant order items.
        
        Allows modification of quantities, prices, or special instructions
        for items in the current table's order.
        
        Returns:
            bool: True if order modified successfully, False otherwise
        """
        print("Order modify event - method not implemented yet")
        return False
    
    def _order_send_to_kitchen(self):
        """
        Handle sending orders to kitchen.
        
        Sends current table's orders to kitchen for preparation.
        Updates order status and prints kitchen tickets if configured.
        
        Returns:
            bool: True if order sent successfully, False otherwise
        """
        print("Order send to kitchen event - method not implemented yet")
        return False
    
    def _order_ready(self):
        """
        Handle marking orders as ready.
        
        Marks kitchen orders as ready for serving.
        Updates order status and notifies wait staff.
        
        Returns:
            bool: True if order marked ready successfully, False otherwise
        """
        print("Order ready event - method not implemented yet")
        return False
    
    # ==================== RESTAURANT CHECK OPERATIONS ====================
    
    def _check_open(self):
        """
        Handle opening a new check for restaurant table.
        
        Creates a new check/bill for the current table.
        Initializes check with current order items.
        
        Returns:
            bool: True if check opened successfully, False otherwise
        """
        print("Check open event - method not implemented yet")
        return False
    
    def _check_close(self):
        """
        Handle closing restaurant check.
        
        Finalizes and closes the current check after payment.
        Updates table status and archives check data.
        
        Returns:
            bool: True if check closed successfully, False otherwise
        """
        print("Check close event - method not implemented yet")
        return False
    
    def _check_print(self):
        """
        Handle printing restaurant check.
        
        Prints the current check/bill for customer review.
        Shows itemized orders, taxes, and total amounts.
        
        Returns:
            bool: True if check printed successfully, False otherwise
        """
        print("Check print event - method not implemented yet")
        return False
    
    def _check_split(self):
        """
        Handle splitting restaurant check.
        
        Divides a single check into multiple separate checks.
        Allows different payment methods for different portions.
        
        Returns:
            bool: True if check split successfully, False otherwise
        """
        print("Check split event - method not implemented yet")
        return False
    
    def _check_merge(self):
        """
        Handle merging restaurant checks.
        
        Combines multiple checks into a single check.
        Useful for combining separate orders into one payment.
        
        Returns:
            bool: True if checks merged successfully, False otherwise
        """
        print("Check merge event - method not implemented yet")
        return False
    
    # ==================== MARKET SALE SUSPENSION OPERATIONS ====================
    
    def _suspend_sale(self):
        """
        Handle suspending current sale transaction.
        
        Temporarily saves the current transaction for later completion.
        Allows starting new transactions while preserving suspended one.
        
        Returns:
            bool: True if sale suspended successfully, False otherwise
        """
        print("Suspend sale event - method not implemented yet")
        return False
    
    def _resume_sale(self):
        """
        Handle resuming suspended sale transaction.
        
        Restores a previously suspended transaction for completion.
        Loads all items, totals, and transaction state.
        
        Returns:
            bool: True if sale resumed successfully, False otherwise
        """
        print("Resume sale event - method not implemented yet")
        return False
    
    def _suspend_list(self):
        """
        Handle displaying list of suspended sales.
        
        Shows all currently suspended transactions with details.
        Allows selection of suspended sale to resume or delete.
        
        Returns:
            bool: True if suspend list displayed successfully, False otherwise
        """
        print("Suspend list event - method not implemented yet")
        return False
    
    def _delete_suspended_sale(self):
        """
        Handle deleting suspended sale transaction.
        
        Permanently removes a suspended transaction from storage.
        Cannot be recovered after deletion.
        
        Returns:
            bool: True if suspended sale deleted successfully, False otherwise
        """
        print("Delete suspended sale event - method not implemented yet")
        return False
    
    def _suspend_detail(self):
        """
        Handle displaying suspended sale details.
        
        Shows detailed information about a selected suspended sale.
        Includes items, quantities, prices, and transaction metadata.
        
        Returns:
            bool: True if suspend detail displayed successfully, False otherwise
        """
        print("Suspend detail event - method not implemented yet")
        return False