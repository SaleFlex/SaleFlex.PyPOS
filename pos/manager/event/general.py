"""
SaleFlex.PyPOS - Point of Sale Application

Copyright (c) 2025 Ferhat Mousavi (ferhat.mousavi@gmail.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from data_layer.enums import FormName, ControlName
from data_layer import Cashier


class GeneralEvent:
    """
    General Event Handler for basic POS application operations.
    
    This class handles fundamental application events that are not specific
    to sales, payments, or configuration. It includes:
    - Application lifecycle (exit, login, logout)
    - Navigation and form management
    - Menu operations
    - Basic UI interactions
    
    All methods follow the pattern of returning True on success, False on failure,
    and handle authentication checks where appropriate.
    """
    
    # ==================== APPLICATION LIFECYCLE EVENTS ====================
    
    def _exit_application(self):
        """
        Handle application exit event.
        
        Terminates the Qt application gracefully.
        
        Returns:
            None: Method doesn't return as application exits
        """
        self.app.quit()

    def _login(self, key=None):
        """
        Handle user login authentication.
        
        Validates user credentials from combobox or textbox inputs, checks against database,
        creates admin user if needed, and transitions to menu form on success.
        
        Supports two input methods:
        - COMBOBOX (CASHIER_NAME_LIST): Select from cashier list (preferred - less touch screen use)
        - TEXTBOX (user_name): Manual username entry (fallback)
        
        Process:
        1. Check if already logged in
        2. Get username from COMBOBOX or TEXTBOX
        3. Get password from textbox
        4. Query database for matching cashier
        5. Handle admin/supervisor user creation if needed
        6. Set login status and navigate to startup form
        
        Parameters:
            key: Optional parameter from numpad input
        
        Returns:
            bool: True if login successful, False otherwise
        """
        print("\n" + "="*80)
        print("[LOGIN] _login method called!")
        print("="*80)
        
        # Skip if already logged in
        if self.login_succeed:
            print("[LOGIN] Already logged in, skipping")
            return True
        
        # Try to get username from COMBOBOX first (preferred method)
        from user_interface.control import ComboBox
        user_name_from_combo = ""
        has_combobox = False
        
        print("[LOGIN] Searching for CASHIER_NAME_LIST combobox...")
        for item in self.interface.window.children():
            if isinstance(item, ComboBox) and hasattr(item, 'name'):
                print(f"[LOGIN] Found combobox with name: '{item.name}'")
                if item.name == ControlName.CASHIER_NAME_LIST.value:
                    user_name_from_combo = item.currentText()
                    has_combobox = True
                    print(f"[LOGIN] ✓ Found CASHIER_NAME_LIST, selected value: '{user_name_from_combo}'")
                    break
        
        # If no COMBOBOX, get username from TEXTBOX
        user_name_from_textbox = ""
        password = ""
        print("[LOGIN] Getting textbox values...")
        textbox_values = self.interface.window.get_textbox_values()
        print(f"[LOGIN] Textbox values: {textbox_values}")
        
        for key, value in textbox_values.items():
            if key == "user_name":
                user_name_from_textbox = value
                print(f"[LOGIN] Found username textbox: '{value}'")
            elif key == "PASSWORD":  # Changed from "password" to "PASSWORD"
                password = value
                print(f"[LOGIN] Found password textbox: '{value}'")
        
        # Determine which username source to use
        print(f"[LOGIN] has_combobox: {has_combobox}, user_name_from_combo: '{user_name_from_combo}'")
        print(f"[LOGIN] user_name_from_textbox: '{user_name_from_textbox}', password: '{password}'")
        
        if has_combobox and user_name_from_combo:
            # COMBOBOX mode: Parse "username (name lastname)" format
            selected_cashier = user_name_from_combo
            
            # Handle SUPERVISOR login
            if selected_cashier.upper() == "SUPERVISOR":
                if password == "admin":
                    # Create or find admin user
                    admins = Cashier.filter_by(user_name="admin")
                    if not admins or len(admins) == 0:
                        cashier = Cashier(
                            no=0,
                            user_name="admin",
                            name="SUPERVISOR",
                            last_name="",
                            password="admin",
                            identity_number="",
                            description="System Administrator",
                            is_active=True,
                            is_administrator=True
                        )
                        cashier.save()
                    
                    self.login_succeed = True
                    self._navigate_after_login()
                    return True
                else:
                    return False
            
            # Parse cashier username (format: "username (name lastname)")
            # Extract username from before the opening parenthesis
            if " (" in selected_cashier:
                user_name = selected_cashier.split(" (")[0].strip()
            else:
                # Fallback: treat entire string as username
                user_name = selected_cashier.strip()
            
            if not user_name:
                return False
            
            # Find cashier by username and password
            cashiers = Cashier.filter_by(user_name=user_name, password=password, is_deleted=False)
        
        else:
            # TEXTBOX mode: Use user_name directly
            if not user_name_from_textbox:
                return False
            
            # Handle admin login with default credentials
            if user_name_from_textbox.lower() == "admin" and password == "admin":
                admins = Cashier.filter_by(user_name="admin")
                if not admins or len(admins) == 0:
                    cashier = Cashier(
                        no=0,
                        user_name="admin",
                        name="Admin",
                        last_name="User",
                        password="admin",
                        identity_number="",
                        description="System Administrator",
                        is_active=True,
                        is_administrator=True
                    )
                    cashier.save()
                
                self.login_succeed = True
                self._navigate_after_login()
                return True
            
            # Find cashier by user_name and password
            cashiers = Cashier.filter_by(user_name=user_name_from_textbox.lower(), password=password, is_deleted=False)
        
        # Validate credentials
        if not cashiers or len(cashiers) == 0:
            return False
        
        # Login successful
        self.login_succeed = True
        self.current_cashier = cashiers[0]  # Store current cashier
        self._navigate_after_login()
        return True
    
    def _navigate_after_login(self):
        """
        Navigate to the appropriate form after successful login.
        Helper method to avoid code duplication.
        Clears form history to start fresh after login.
        """
        # Clear form history on login - start with fresh navigation history
        self.clear_form_history()
        
        # Navigate to startup form or SALE form
        if self.startup_form_id:
            # Get the startup form to determine its FormName
            from data_layer.model import Form
            startup_form = Form.get_by_id(self.startup_form_id)
            
            if startup_form and startup_form.name:
                # Try to find matching FormName enum
                try:
                    form_name_enum = FormName[startup_form.name.upper()]
                    self.current_form_type = form_name_enum
                except (KeyError, AttributeError):
                    # If form name doesn't match enum, default to SALE
                    self.current_form_type = FormName.SALE
            else:
                self.current_form_type = FormName.SALE
                
            self.interface.redraw(form_id=self.startup_form_id)
        else:
            # Fallback to SALE form by name using FormName enum
            self.current_form_type = FormName.SALE
            self.interface.redraw(form_name=FormName.SALE.name)

    def _login_extended(self):
        """
        Handle extended login with additional authentication features.
        
        Currently implements same logic as regular login.
        Can be expanded for two-factor authentication, biometrics, etc.
        
        Returns:
            bool: Result of login process
        """
        return self._login()

    def _logout(self):
        """
        Handle user logout and session termination.
        
        Clears authentication status, resets session data,
        and navigates to appropriate login form based on current form's requirements.
        
        Navigation logic:
        - If current form requires need_auth=True -> navigate to LOGIN_EXT form
        - If current form requires need_login=True -> navigate to LOGIN form
        - Otherwise -> navigate to startup form or LOGIN form
        
        Returns:
            bool: Always True after successful logout
        """
        from data_layer.model import Form
        
        # Determine target form based on current form's requirements
        target_form_name = None
        
        # Check current form's authentication requirements
        if self.current_form_id:
            # Get current form from database
            current_form = Form.get_by_id(self.current_form_id)
            
            if current_form:
                if current_form.need_auth:
                    # Form requires authorization -> go to extended login
                    target_form_name = FormName.LOGIN_EXT
                    print(f"[LOGOUT] Current form '{current_form.name}' requires authorization -> redirecting to LOGIN_EXT")
                elif current_form.need_login:
                    # Form requires login -> go to regular login
                    target_form_name = FormName.LOGIN
                    print(f"[LOGOUT] Current form '{current_form.name}' requires login -> redirecting to LOGIN")
        
        # Clear authentication and session data
        self.login_succeed = False
        self.cashier_data = None
        self.document_data = None
        
        # Clear form navigation history
        self.clear_form_history()
        
        # Navigate to appropriate form
        if target_form_name:
            # Navigate based on current form's requirements
            self.current_form_type = target_form_name
            self.interface.redraw(form_name=target_form_name.name)
        elif self.startup_form_id:
            # Navigate to startup form
            self.interface.redraw(form_id=self.startup_form_id)
        else:
            # Default to LOGIN form
            self.current_form_type = FormName.LOGIN
            self.interface.redraw(form_name=FormName.LOGIN.name)
        
        return True

    def _service_code_request(self, key=None):
        """
        Handle service code authentication request.
        
        Used for accessing service/maintenance functions that require
        special authorization beyond normal cashier credentials.
        
        Parameters:
            key: Optional parameter from numpad input
        
        Returns:
            bool: True if service code accepted, False otherwise
        """
        # TODO: Implement service code validation logic
        if key is not None:
            print(f"Service code request - key pressed: {key}")
        else:
            print("Service code request - functionality to be implemented")
        return False

    def _login_service(self, key=None):
        """
        Handle service-level login for maintenance operations.
        
        Provides elevated access for technical personnel to perform
        system maintenance, updates, and configuration changes.
        
        Parameters:
            key: Optional parameter from numpad input
        
        Returns:
            bool: True if service login successful, False otherwise
        """
        # TODO: Implement service login logic
        if key is not None:
            print(f"Service login - key pressed: {key}")
        else:
            print("Service login - functionality to be implemented")
        return False

    # ==================== NAVIGATION AND FORM EVENTS ====================

    def _back(self):
        """
        Handle back/return navigation.
        
        Uses the form history stack to navigate to the previous form.
        LOGIN and LOGIN_EXT forms are excluded from history.
        Requires valid authentication to prevent unauthorized navigation.
        
        Returns:
            bool: True if navigation successful, False if not authenticated or no history
        """
        # Require authentication for navigation
        if not self.login_succeed:
            self._logout()
            return False
        
        # Get the previous form from history
        previous_form = self.pop_form_history()
        
        if previous_form is None:
            # No history available, cannot go back
            print("[BACK] No form history available")
            return False
        
        # Update current form without adding to history
        # We need to temporarily set the form directly to avoid adding to history again
        self._set_current_form_without_history(previous_form)
        
        # Redraw interface with previous form using form name
        form_name = previous_form.name
        self.interface.redraw(form_name=form_name)
        return True
    
    def _set_current_form_without_history(self, form_type):
        """
        Set the current form without adding it to history.
        
        Used by back navigation to avoid polluting the history stack.
        
        Args:
            form_type (FormName): The form type to set as current
        """
        # Access private attribute directly to bypass the setter
        self._CurrentStatus__previous_form_type = self._CurrentStatus__current_form_type
        self._CurrentStatus__current_form_type = form_type

    def _close_form(self):
        """
        Handle form close event.
        
        Closes the current form and returns to the previous form.
        Similar to back navigation but specifically for form closure.
        
        Returns:
            bool: True if form closed successfully, False otherwise
        """
        return self._back()

    def _save_changes(self):
        """
        Handle save changes event for form data.
        
        Saves any pending changes in the current form before navigation
        or form closure. Used for configuration and data entry forms.
        
        Currently supports:
        - CASHIER form: Save cashier information (to be fully implemented)
        - Other forms: Will be implemented as needed
        
        Returns:
            bool: True if changes saved successfully, False otherwise
        """
        print("\n" + "="*80)
        print("[SAVE_CHANGES] Save changes event triggered")
        print("="*80)
        
        # Check if user is authenticated
        if not self.login_succeed:
            print("[SAVE_CHANGES] User not authenticated")
            return False
        
        # Determine current form type
        current_form = self.current_form_type
        print(f"[SAVE_CHANGES] Current form: {current_form}")
        
        # Handle CASHIER form saving
        if current_form == FormName.CASHIER:
            return self._save_cashier_changes()
        
        # Handle other forms as they are implemented
        # elif current_form == FormName.CONFIG:
        #     return self._save_config_changes()
        # elif current_form == FormName.CUSTOMER:
        #     return self._save_customer_changes()
        
        # Default: functionality to be implemented for other forms
        print(f"[SAVE_CHANGES] Save functionality not yet implemented for form: {current_form}")
        return False
    
    def _save_cashier_changes(self):
        """
        Save cashier information from CASHIER form.
        
        Retrieves data from form controls (textboxes) and saves
        cashier information to the database.
        
        Form controls expected:
        - CASHIER_NAME: Username
        - NAME: First name
        - LAST_NAME: Last name
        - PASSWORD: Password
        - ID_NUMBER: Identification number
        - DESCRIPTION: Additional description
        
        Returns:
            bool: True if save successful, False otherwise
        """
        print("[SAVE_CASHIER] Collecting cashier form data...")
        
        # Get all textbox values from the form
        textbox_values = self.interface.window.get_textbox_values()
        print(f"[SAVE_CASHIER] Textbox values: {textbox_values}")
        
        # Extract cashier data from form controls
        cashier_data = {
            'user_name': textbox_values.get('CASHIER_NAME', '').strip(),
            'name': textbox_values.get('NAME', '').strip(),
            'last_name': textbox_values.get('LAST_NAME', '').strip(),
            'password': textbox_values.get('PASSWORD', '').strip(),
            'identity_number': textbox_values.get('ID_NUMBER', '').strip(),
            'description': textbox_values.get('DESCRIPTION', '').strip()
        }
        
        print(f"[SAVE_CASHIER] Collected data: {cashier_data}")
        
        # Validate required fields
        if not cashier_data['user_name']:
            print("[SAVE_CASHIER] ✗ Username is required")
            return False
        
        if not cashier_data['password']:
            print("[SAVE_CASHIER] ✗ Password is required")
            return False
        
        # TODO: Implement actual database save operation
        # This will be completed in a future update
        # For now, just log the action
        print("[SAVE_CASHIER] ✓ Data validated successfully")
        print("[SAVE_CASHIER] TODO: Implement database save operation")
        print(f"[SAVE_CASHIER] Data to be saved:")
        print(f"  - Username: {cashier_data['user_name']}")
        print(f"  - Name: {cashier_data['name']}")
        print(f"  - Last Name: {cashier_data['last_name']}")
        print(f"  - ID Number: {cashier_data['identity_number']}")
        print(f"  - Description: {cashier_data['description']}")
        
        # Return True to indicate the operation was processed
        # (even though actual save is not yet implemented)
        return True

    def _redraw_form(self):
        """
        Handle form redraw/refresh event.
        
        Forces a complete redraw of the current form, useful for
        updating display after data changes or window resize.
        
        Returns:
            bool: True if redraw successful, False otherwise
        """
        if self.login_succeed:
            if self.current_form_id:
                self.interface.redraw(form_id=self.current_form_id)
            else:
                form_name = self.current_form_type.name
                self.interface.redraw(form_name=form_name)
            return True
        return False

    # ==================== MAIN NAVIGATION EVENTS ====================

    def _sales_form(self):
        """
        Navigate to sales form.
        
        Transitions to the main sales interface where transactions
        are processed. Requires valid authentication.
        
        Returns:
            bool: True if navigation successful, False if not authenticated
        """
        if self.login_succeed:
            self.current_form_type = FormName.SALE
            self.interface.redraw(form_name=FormName.SALE.name)
            return True
        else:
            self._logout()
            return False

    def _settings_form(self):
        """
        Navigate to configuration form.
        
        Accesses system configuration and settings interface.
        Requires valid authentication.
        
        Returns:
            bool: True if navigation successful, False if not authenticated
        """
        if self.login_succeed:
            self.current_form_type = FormName.CONFIG
            self.interface.redraw(form_name=FormName.CONFIG.name)
            return True
        else:
            self._logout()
            return False

    def _closure_form(self):
        """
        Navigate to end-of-day closure form.
        
        Accesses the closure interface for end-of-shift operations,
        cash counting, and daily reporting.
        
        Returns:
            bool: True if navigation successful, False if not authenticated
        """
        if self.login_succeed:
            self.current_form_type = FormName.CLOSURE
            self.interface.redraw(form_name=FormName.CLOSURE.name)
            return True
        else:
            self._logout()
            return False

    # ==================== MENU NAVIGATION EVENTS ====================

    def _main_menu_form(self):
        """
        Navigate to function menu form.
        
        Displays available system functions and operations menu.
        
        Returns:
            bool: True if navigation successful, False if not authenticated
        """
        if self.login_succeed:
            self.current_form_type = FormName.MAIN_MENU
            self.interface.redraw(form_name=FormName.MAIN_MENU.name)
            return True
        else:
            self._logout()
            return False

    def _service_form(self):
        """
        Navigate to service form.
        """
        if self.login_succeed:
            self.current_form_type = FormName.SERVICE
            self.interface.redraw(form_name=FormName.SERVICE.name)
            return True
        else:
            self._logout()
            return False

    def _report_form(self):
        """
        Navigate to reports menu.
        
        Accesses reporting interface and report generation options.
        
        Returns:
            bool: True if navigation successful, False if not authenticated
        """
        if self.login_succeed:
            self.current_form_type = FormName.REPORT
            self.interface.redraw(form_name=FormName.REPORT.name)
            return True
        else:
            self._logout()
            return False

    # ==================== USER MANAGEMENT EVENTS ====================

    def _cashier_form(self):
        """
        Handle cashier management operations.
        
        Access cashier selection, information display, or management interface.
        
        Returns:
            bool: True if operation successful, False otherwise
        """
        if self.login_succeed:
            self.current_form_type = FormName.CASHIER
            self.interface.redraw(form_name=FormName.CASHIER.name)
            return True
        else:
            self._logout()
            return False

    def _customer_form(self):
        """
        Handle customer management operations.
        
        Access customer selection, information entry, or lookup interface.
        
        Returns:
            bool: True if operation successful, False otherwise
        """
        if self.login_succeed:
            self.current_form_type = FormName.CUSTOMER
            self.interface.redraw(form_name=FormName.CUSTOMER.name)
            return True
        else:
            self._logout()
            return False
    
    # ==================== DYNAMIC FORM NAVIGATION ====================
    
    def _navigate_to_form(self, target_form_id, transition_mode="REPLACE"):
        """
        Navigate to a form dynamically based on database definition.
        
        This method handles navigation to forms defined in the database.
        It supports two transition modes:
        - MODAL: Show the form as a modal dialog (temporary, doesn't close current form)
        - REPLACE: Replace the current form with the new one (closes current form)
        
        Args:
            target_form_id (str or UUID): The ID of the target form
            transition_mode (str): Either "MODAL" or "REPLACE" (default: "REPLACE")
            
        Returns:
            bool: True if navigation successful, False otherwise
        """
        try:
            from data_layer.model import Form
            
            # Get the target form
            target_form = Form.get_by_id(target_form_id)
            
            if not target_form:
                print(f"Form not found: {target_form_id}")
                return False
            
            # Check if form requires login
            if target_form.need_login and not self.login_succeed:
                print(f"Login required to access form: {target_form.name}")
                return False
            
            # Check if form requires special authorization
            if target_form.need_auth:
                # TODO: Implement authorization check
                print(f"Authorization check for form: {target_form.name}")
            
            # Navigate based on transition mode
            if transition_mode.upper() == "MODAL":
                # Show as modal dialog
                result = self.interface.show_modal(form_id=target_form_id)
                return result == 1  # QDialog.Accepted
            else:
                # Replace current form
                self.interface.redraw(form_id=target_form_id)
                return True
                
        except Exception as e:
            print(f"Error navigating to form {target_form_id}: {str(e)}")
            return False