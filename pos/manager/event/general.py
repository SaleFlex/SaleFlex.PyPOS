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

from data_layer.enums import FormName
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

    def _login(self):
        """
        Handle user login authentication.
        
        Validates user credentials from textbox inputs, checks against database,
        creates admin user if needed, and transitions to menu form on success.
        
        Process:
        1. Check if already logged in
        2. Get username and password from UI textboxes  
        3. Query database for matching cashier
        4. Handle admin user creation if needed
        5. Set login status and navigate to menu
        
        Returns:
            bool: True if login successful, False otherwise
        """
        # Skip if already logged in
        if self.login_succeed:
            return True
            
        # Extract credentials from textbox inputs
        user_name = ""
        password = ""
        for key, value in self.interface.window.get_textbox_values().items():
            if key == "user_name":
                user_name = value
            if key == "password":
                password = value
        
        # Query database for matching cashier credentials
        cashiers = Cashier.filter_by(user_name=user_name.lower(), password=password)

        # Validate credentials - reject if no match and not admin
        if len(cashiers) == 0 and not (user_name.lower() == "admin" and password == "admin"):
            return False
            
        # Create admin user if using default admin credentials
        if len(cashiers) == 0 and (user_name.lower() == "admin" and password == "admin"):
            cashier = Cashier(user_name=user_name.lower(), password=password,
                              name="", last_name="", identity_number="", description="",
                              is_active=True, is_administrator=True)
            cashier.save()
        
        # Set authentication status and navigate to main menu
        self.login_succeed = True
        self.current_form_type = FormName.MENU
        self.interface.redraw(self.current_form_type)
        return True

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
        and returns to login form.
        
        Returns:
            bool: Always True after successful logout
        """
        # Clear authentication and session data
        self.login_succeed = False
        self.cashier_data = None
        self.document_data = None
        
        # Navigate back to login form
        self.current_form_type = FormName.LOGIN
        self.interface.redraw(self.current_form_type)
        return True

    def _service_code_request(self):
        """
        Handle service code authentication request.
        
        Used for accessing service/maintenance functions that require
        special authorization beyond normal cashier credentials.
        
        Returns:
            bool: True if service code accepted, False otherwise
        """
        # TODO: Implement service code validation logic
        print("Service code request - functionality to be implemented")
        return False

    def _login_service(self):
        """
        Handle service-level login for maintenance operations.
        
        Provides elevated access for technical personnel to perform
        system maintenance, updates, and configuration changes.
        
        Returns:
            bool: True if service login successful, False otherwise
        """
        # TODO: Implement service login logic
        print("Service login - functionality to be implemented")
        return False

    # ==================== NAVIGATION AND FORM EVENTS ====================

    def _back(self):
        """
        Handle back/return navigation.
        
        Swaps current and previous form types to implement back functionality.
        Requires valid authentication to prevent unauthorized navigation.
        
        Returns:
            bool: True if navigation successful, False if not authenticated
        """
        # Require authentication for navigation
        if not self.login_succeed:
            self._logout()
            return False
            
        # Swap current and previous forms to go back
        temp_form_type = self.current_form_type
        self.current_form_type = self.previous_form_type
        self.previous_form_type = temp_form_type
        
        # Redraw interface with previous form
        self.interface.redraw(self.current_form_type)
        return True

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
        
        Returns:
            bool: True if changes saved successfully, False otherwise
        """
        # TODO: Implement form data saving logic
        print("Save changes - functionality to be implemented")
        return False

    def _redraw_form(self):
        """
        Handle form redraw/refresh event.
        
        Forces a complete redraw of the current form, useful for
        updating display after data changes or window resize.
        
        Returns:
            bool: True if redraw successful, False otherwise
        """
        if self.login_succeed:
            self.interface.redraw(self.current_form_type)
            return True
        return False

    # ==================== MAIN NAVIGATION EVENTS ====================

    def _sale(self):
        """
        Navigate to sales form.
        
        Transitions to the main sales interface where transactions
        are processed. Requires valid authentication.
        
        Returns:
            bool: True if navigation successful, False if not authenticated
        """
        if self.login_succeed:
            self.current_form_type = FormName.SALE
            self.interface.redraw(self.current_form_type)
            return True
        else:
            self._logout()
            return False

    def _configuration(self):
        """
        Navigate to configuration form.
        
        Accesses system configuration and settings interface.
        Requires valid authentication.
        
        Returns:
            bool: True if navigation successful, False if not authenticated
        """
        if self.login_succeed:
            self.current_form_type = FormName.CONFIG
            self.interface.redraw(self.current_form_type)
            return True
        else:
            self._logout()
            return False

    def _closure(self):
        """
        Navigate to end-of-day closure form.
        
        Accesses the closure interface for end-of-shift operations,
        cash counting, and daily reporting.
        
        Returns:
            bool: True if navigation successful, False if not authenticated
        """
        if self.login_succeed:
            self.current_form_type = FormName.CLOSURE
            self.interface.redraw(self.current_form_type)
            return True
        else:
            self._logout()
            return False

    # ==================== MENU NAVIGATION EVENTS ====================

    def _function_menu(self):
        """
        Navigate to function menu.
        
        Displays available system functions and operations menu.
        
        Returns:
            bool: True if navigation successful, False if not authenticated
        """
        if self.login_succeed:
            # TODO: Define FormName.FUNCTION_MENU if needed
            print("Function menu - navigation to be implemented")
            return True
        else:
            self._logout()
            return False

    def _sales_menu(self):
        """
        Navigate to sales menu.
        
        Displays sales-related options and shortcuts menu.
        
        Returns:
            bool: True if navigation successful, False if not authenticated
        """
        if self.login_succeed:
            # Navigate to sales form or sales submenu
            return self._sale()
        else:
            self._logout()
            return False

    def _service_menu(self):
        """
        Navigate to service menu.
        
        Accesses service and maintenance options menu.
        Typically requires elevated permissions.
        
        Returns:
            bool: True if navigation successful, False if not authenticated
        """
        if self.login_succeed:
            # TODO: Implement service menu navigation
            print("Service menu - navigation to be implemented") 
            return True
        else:
            self._logout()
            return False

    def _setting_menu(self):
        """
        Navigate to settings menu.
        
        Displays system settings and configuration options.
        
        Returns:
            bool: True if navigation successful, False if not authenticated
        """
        if self.login_succeed:
            # Navigate to configuration form
            return self._configuration()
        else:
            self._logout()
            return False

    def _report_menu(self):
        """
        Navigate to reports menu.
        
        Accesses reporting interface and report generation options.
        
        Returns:
            bool: True if navigation successful, False if not authenticated
        """
        if self.login_succeed:
            # TODO: Define FormName.REPORT_MENU if needed
            print("Report menu - navigation to be implemented")
            return True
        else:
            self._logout()
            return False

    # ==================== USER MANAGEMENT EVENTS ====================

    def _cashier(self):
        """
        Handle cashier management operations.
        
        Access cashier selection, information display, or management interface.
        
        Returns:
            bool: True if operation successful, False otherwise
        """
        if self.login_succeed:
            # TODO: Implement cashier management interface
            print("Cashier management - functionality to be implemented")
            return True
        else:
            self._logout()
            return False

    def _customer(self):
        """
        Handle customer management operations.
        
        Access customer selection, information entry, or lookup interface.
        
        Returns:
            bool: True if operation successful, False otherwise
        """
        if self.login_succeed:
            # TODO: Implement customer management interface
            print("Customer management - functionality to be implemented")
            return True
        else:
            self._logout()
            return False