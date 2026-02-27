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
from data_layer import Cashier



from core.logger import get_logger

logger = get_logger(__name__)

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
    
    def _exit_application_event(self):
        """
        Handle application exit event.
        
        Terminates the Qt application gracefully.
        
        Returns:
            None: Method doesn't return as application exits
        """
        self.app.quit()

    def _login_event(self, key=None):
        """
        Handle user login authentication.
        
        Validates user credentials from combobox or textbox inputs, checks against
        pos_data cache (loaded at startup to minimize disk I/O), creates admin user
        if needed, and transitions to menu form on success.
        
        Supports two input methods:
        - COMBOBOX (CASHIER_NAME_LIST): Select from cashier list (preferred - less touch screen use)
        - TEXTBOX (user_name): Manual username entry (fallback)
        
        Process:
        1. Check if already logged in
        2. Get username from COMBOBOX or TEXTBOX
        3. Get password from textbox
        4. Search pos_data cache for matching cashier (avoids database read)
        5. Handle admin/supervisor user creation if needed (updates cache automatically)
        6. Set login status and navigate to startup form
        
        Note: All cashier lookups are performed from pos_data cache to minimize disk I/O.
        Only when creating a new admin user is a database write performed, and the cache
        is automatically updated.
        
        Parameters:
            key: Optional parameter from numpad input
        
        Returns:
            bool: True if login successful, False otherwise
        """
        logger.debug("\n" + "="*80)
        logger.debug("[LOGIN] _login method called!")
        logger.debug("="*80)
        
        # Skip if already logged in
        if self.login_succeed:
            logger.warning("[LOGIN] Already logged in, skipping")
            return True
        
        # Try to get username from COMBOBOX first (preferred method)
        from user_interface.control import ComboBox
        user_name_from_combo = ""
        has_combobox = False
        
        logger.debug("[LOGIN] Searching for CASHIER_NAME_LIST combobox...")
        for item in self.interface.window.children():
            if isinstance(item, ComboBox) and hasattr(item, 'name'):
                logger.debug("[LOGIN] Found combobox with name: '%s'", item.name)
                if item.name == ControlName.CASHIER_NAME_LIST.value:
                    user_name_from_combo = item.currentText()
                    has_combobox = True
                    logger.info("[LOGIN] ✓ Found CASHIER_NAME_LIST, selected value: '%s'", user_name_from_combo)
                    break
        
        # If no COMBOBOX, get username from TEXTBOX
        user_name_from_textbox = ""
        password = ""
        logger.debug("[LOGIN] Getting textbox values...")
        textbox_values = self.interface.window.get_textbox_values()
        logger.debug("[LOGIN] Textbox values: %s", textbox_values)
        
        for key, value in textbox_values.items():
            if key == "user_name":
                user_name_from_textbox = value
                logger.debug("[LOGIN] Found username textbox: '%s'", value)
            elif key == "PASSWORD":  # Changed from "password" to "PASSWORD"
                password = value
                logger.debug("[LOGIN] Found password textbox: '%s'", value)
        
        # Determine which username source to use
        logger.debug("[LOGIN] has_combobox: %s, user_name_from_combo: '%s'", has_combobox, user_name_from_combo)
        logger.debug("[LOGIN] user_name_from_textbox: '%s', password: '%s'", user_name_from_textbox, password)
        
        if has_combobox and user_name_from_combo:
            # COMBOBOX mode: Parse "username (name lastname)" format
            selected_cashier = user_name_from_combo
            
            # Handle SUPERVISOR login
            if selected_cashier.upper() == "SUPERVISOR":
                if password == "admin":
                    # Try to find admin user from pos_data first (avoids database read)
                    all_cashiers = self.pos_data.get("Cashier", [])
                    admin_cashiers = [c for c in all_cashiers if c.user_name == "admin" and not c.is_deleted]
                    
                    if admin_cashiers:
                        cashier = admin_cashiers[0]
                    else:
                        # Admin not found in cache, create new one
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
                        # Update pos_data cache after creating new cashier
                        self.update_pos_data_cache(cashier)
                    
                    # Set cashier_data after successful login
                    self.cashier_data = cashier
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
            
            # Find cashier by username and password from pos_data (avoids database read)
            all_cashiers = self.pos_data.get("Cashier", [])
            cashiers = [c for c in all_cashiers 
                        if c.user_name == user_name 
                        and c.password == password 
                        and not c.is_deleted]
        
        else:
            # TEXTBOX mode: Use user_name directly
            if not user_name_from_textbox:
                return False
            
            # Handle admin login with default credentials
            if user_name_from_textbox.lower() == "admin" and password == "admin":
                # Try to find admin user from pos_data first (avoids database read)
                all_cashiers = self.pos_data.get("Cashier", [])
                admin_cashiers = [c for c in all_cashiers if c.user_name == "admin" and not c.is_deleted]
                
                if admin_cashiers:
                    cashier = admin_cashiers[0]
                else:
                    # Admin not found in cache, create new one
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
                    # Update pos_data cache after creating new cashier
                    self.update_pos_data_cache(cashier)
                
                # Set cashier_data after successful login
                self.cashier_data = cashier
                self.login_succeed = True
                self._navigate_after_login()
                return True
            
            # Find cashier by user_name and password from pos_data (avoids database read)
            all_cashiers = self.pos_data.get("Cashier", [])
            cashiers = [c for c in all_cashiers 
                        if c.user_name == user_name_from_textbox.lower() 
                        and c.password == password 
                        and not c.is_deleted]
        
        # Validate credentials
        if not cashiers or len(cashiers) == 0:
            return False
        
        # Login successful - set cashier_data
        self.cashier_data = cashiers[0]
        self.login_succeed = True
        
        # Create document_data immediately after login so StatusBar can display it
        # Try to load incomplete document first, if none exists, create new empty document
        if not self.document_data:
            logger.debug("[LOGIN] No document_data after login, trying to load incomplete document...")
            if not self.load_incomplete_document():
                logger.debug("[LOGIN] No incomplete document found, creating new empty document...")
                if not self.create_empty_document():
                    logger.error("[LOGIN] Failed to create empty document")
        
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
            
            # If navigating to SALE form, ensure document_data exists
            if self.current_form_type == FormName.SALE:
                if not self.document_data:
                    logger.debug("[NAVIGATE_AFTER_LOGIN] No document_data, trying to load incomplete document...")
                    if not self.load_incomplete_document():
                        logger.debug("[NAVIGATE_AFTER_LOGIN] No incomplete document found, creating new empty document...")
                        if not self.create_empty_document():
                            logger.error("[NAVIGATE_AFTER_LOGIN] Failed to create empty document")
                
            self.interface.redraw(form_id=self.startup_form_id)
        else:
            # Fallback to SALE form by name using FormName enum
            self.current_form_type = FormName.SALE
            
            # Ensure document_data exists for SALE form
            if not self.document_data:
                logger.debug("[NAVIGATE_AFTER_LOGIN] No document_data, trying to load incomplete document...")
                if not self.load_incomplete_document():
                    logger.debug("[NAVIGATE_AFTER_LOGIN] No incomplete document found, creating new empty document...")
                    if not self.create_empty_document():
                        logger.error("[NAVIGATE_AFTER_LOGIN] Failed to create empty document")
            
            self.interface.redraw(form_name=FormName.SALE.name)

    def _login_extended_event(self):
        """
        Handle extended login with additional authentication features.
        
        Currently implements same logic as regular login.
        Can be expanded for two-factor authentication, biometrics, etc.
        
        Returns:
            bool: Result of login process
        """
        return self._login_event()

    def _logout_event(self):
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
                    logger.debug("[LOGOUT] Current form '%s' requires authorization -> redirecting to LOGIN_EXT", current_form.name)
                elif current_form.need_login:
                    # Form requires login -> go to regular login
                    target_form_name = FormName.LOGIN
                    logger.debug("[LOGOUT] Current form '%s' requires login -> redirecting to LOGIN", current_form.name)
        
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
            # Get startup form to determine its FormName
            startup_form = Form.get_by_id(self.startup_form_id)
            if startup_form and startup_form.name:
                try:
                    form_name_enum = FormName[startup_form.name.upper()]
                    self.current_form_type = form_name_enum
                except (KeyError, AttributeError):
                    # If form name doesn't match enum, keep current or set to LOGIN
                    self.current_form_type = FormName.LOGIN
            else:
                self.current_form_type = FormName.LOGIN
            self.interface.redraw(form_id=self.startup_form_id)
        else:
            # Default to LOGIN form
            self.current_form_type = FormName.LOGIN
            self.interface.redraw(form_name=FormName.LOGIN.name)
        
        return True

    def _service_code_request_event(self, key=None):
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
            logger.debug("Service code request - key pressed: %s", key)
        else:
            logger.debug("Service code request - functionality to be implemented")
        return False

    def _login_service_event(self, key=None):
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
            logger.debug("Service login - key pressed: %s", key)
        else:
            logger.debug("Service login - functionality to be implemented")
        return False

    # ==================== NAVIGATION AND FORM EVENTS ====================

    def _back_event(self):
        """
        Handle back/return navigation.
        
        Uses the form history stack to navigate to the previous form.
        LOGIN and LOGIN_EXT forms are excluded from history.
        Requires valid authentication to prevent unauthorized navigation.
        
        Returns:
            bool: True if navigation successful, False if not authenticated or no history
        """
        logger.debug("\n[BACK] Back button pressed")
        logger.debug("[BACK] Login status: %s", self.login_succeed)
        logger.debug("[BACK] Form history length: %s", len(self.form_history))
        logger.debug("[BACK] Form history: %s", [f.name for f in self.form_history])
        
        # Require authentication for navigation
        if not self.login_succeed:
            logger.debug("[BACK] User not logged in, calling logout")
            self._logout_event()
            return False
        
        # Get the previous form from history
        previous_form_type = self.pop_form_history()
        
        if previous_form_type is None:
            # No history available, cannot go back
            logger.debug("[BACK] No form history available")
            return False
        
        logger.debug("[BACK] Previous form from history: %s", previous_form_type.name)
        
        # Find the form from database by name
        from data_layer.model import Form
        forms = Form.filter_by(name=previous_form_type.name, is_deleted=False)
        
        if not forms or len(forms) == 0:
            logger.error("[BACK] Form not found in database: %s", previous_form_type.name)
            return False
        
        previous_form = forms[0]
        logger.debug("[BACK] Found form in database: %s (ID: %s)", previous_form.name, previous_form.id)
        
        # Update current form without adding to history
        # We need to temporarily set the form directly to avoid adding to history again
        self._set_current_form_without_history(previous_form_type)
        
        # Set current_form_id as well
        self._CurrentStatus__current_form_id = previous_form.id
        logger.debug("[BACK] Set current_form_type to: %s", previous_form_type.name)
        logger.debug("[BACK] Set current_form_id to: %s", previous_form.id)
        
        # Redraw interface with previous form using form ID
        # Use skip_history_update=True to avoid adding back to history
        logger.debug("[BACK] Redrawing interface with form_id: %s", previous_form.id)
        self.interface.redraw(form_id=previous_form.id, skip_history_update=True)
        logger.info("[BACK] Back navigation completed successfully")
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

    def _close_form_event(self):
        """
        Handle form close event.
        
        Closes the current form and returns to the previous form.
        Similar to back navigation but specifically for form closure.
        
        Returns:
            bool: True if form closed successfully, False otherwise
        """
        return self._back_event()

    def _save_changes_event(self):
        """
        General panel-based save changes handler for any form.
        
        This method implements a generic save mechanism that works with any form
        that follows the panel-based pattern:
        - Forms with SAVE button must have at least one PANEL
        - Panel name matches model name (e.g., "POS_SETTINGS" -> PosSettings)
        - Textbox names inside panel match model field names (uppercase -> lowercase)
        - Example: "BACKEND_IP1" textbox -> "backend_ip1" model field
        
        This allows creating forms for any model by:
        1. Creating a form with a SAVE button
        2. Adding a PANEL with name matching the model (e.g., "CASHIER", "POS_SETTINGS")
        3. Adding labels and textboxes inside the panel with names matching model fields
        
        Returns:
            bool: True if changes saved successfully, False otherwise
        """
        logger.debug("\n" + "="*80)
        logger.debug("[SAVE_CHANGES] Save changes event triggered")
        logger.debug("="*80)
        
        # Check if user is authenticated
        if not self.login_succeed:
            logger.debug("[SAVE_CHANGES] User not authenticated")
            return False
        
        # Determine current form type
        current_form = self.current_form_type
        logger.debug("[SAVE_CHANGES] Current form: %s", current_form)
        
        try:
            # Check if interface and window are available
            if not hasattr(self, 'interface') or not self.interface:
                logger.error("[SAVE_CHANGES] ✗ Interface not available")
                return False
            
            if not hasattr(self.interface, 'window') or not self.interface.window:
                logger.error("[SAVE_CHANGES] ✗ Window not available")
                return False
            
            # Get window reference
            window = self.interface.window
            
            # Check if window is still valid
            if not window:
                logger.error("[SAVE_CHANGES] ✗ Window reference is None")
                return False
            
            try:
                # Try to access window to check if it's still valid
                _ = window.children()
            except RuntimeError:
                logger.error("[SAVE_CHANGES] ✗ Window widget already deleted")
                return False
            
            # Find all panels in the form
            if not hasattr(window, '_panels'):
                logger.error("[SAVE_CHANGES] ✗ No panels found in form")
                logger.warning("[SAVE_CHANGES] ⚠ Forms with SAVE button must have at least one PANEL")
                return False
            
            try:
                panels = window._panels
            except RuntimeError:
                logger.error("[SAVE_CHANGES] ✗ Cannot access panels - window widget may be deleted")
                return False
            
            logger.debug("[SAVE_CHANGES] Found %s panel(s) in form", len(panels))
            
            if len(panels) == 0:
                logger.error("[SAVE_CHANGES] ✗ No panels found in form")
                logger.warning("[SAVE_CHANGES] ⚠ Forms with SAVE button must have at least one PANEL")
                return False
            
            # Process each panel
            all_saved = True
            for panel_name, panel in panels.items():
                logger.debug("\n[SAVE_CHANGES] Processing panel: %s", panel_name)
                
                # Check if panel is still valid before processing
                try:
                    _ = panel.get_content_widget() if hasattr(panel, 'get_content_widget') else None
                except RuntimeError:
                    logger.warning("[SAVE_CHANGES] ⚠ Panel '%s' widget already deleted, skipping", panel_name)
                    all_saved = False
                    continue
                
                # Get all textbox values from this panel
                try:
                    textbox_values = window.get_panel_textbox_values(panel_name)
                except RuntimeError as e:
                    logger.error("[SAVE_CHANGES] ⚠ Error getting textbox values from panel '%s': %s", panel_name, e)
                    all_saved = False
                    continue
                logger.debug("[SAVE_CHANGES] Collected %s textbox values from panel %s", len(textbox_values), panel_name)
                
                if not textbox_values:
                    logger.warning("[SAVE_CHANGES] ⚠ No textbox values found in panel %s", panel_name)
                    continue
                
                # Convert panel name to model class name
                # Panel name is uppercase (e.g., "POS_SETTINGS")
                # Model class name is PascalCase (e.g., "PosSettings")
                model_class_name = self._panel_name_to_model_class(panel_name)
                logger.debug("[SAVE_CHANGES] Model class name: %s", model_class_name)
                
                # Get model class dynamically
                try:
                    # Import model definition module
                    from data_layer.model.definition import __all__ as model_names
                    import data_layer.model.definition as model_module
                    
                    if model_class_name not in model_names:
                        logger.error("[SAVE_CHANGES] ✗ Model class '%s' not found in model definitions", model_class_name)
                        all_saved = False
                        continue
                    
                    model_class = getattr(model_module, model_class_name)
                    logger.debug("[SAVE_CHANGES] Found model class: %s", model_class.__name__)
                    
                    # Get the model instance to update
                    # Try to get from CurrentData cache first (for commonly used models)
                    model_instance = self._get_model_instance(model_class_name, model_class)
                    
                    if not model_instance:
                        logger.error("[SAVE_CHANGES] ✗ Could not get or create %s instance", model_class_name)
                        all_saved = False
                        continue
                    
                    # Update model fields with textbox values
                    updated_fields = []
                    for field_name, field_value in textbox_values.items():
                        if hasattr(model_instance, field_name):
                            # Convert value based on field type
                            old_value = getattr(model_instance, field_name, None)
                            
                            # Get field type from model
                            field_type = type(getattr(model_instance, field_name, None))
                            
                            # Convert value to appropriate type
                            if field_value.strip() == "":
                                # Empty string -> None for nullable fields
                                new_value = None
                            elif field_type == int or (old_value is not None and isinstance(old_value, int)):
                                try:
                                    new_value = int(field_value) if field_value.strip() else None
                                except ValueError:
                                    logger.error("[SAVE_CHANGES] ⚠ Cannot convert '%s' to int for field '%s', skipping", field_value, field_name)
                                    continue
                            elif field_type == bool or (old_value is not None and isinstance(old_value, bool)):
                                # Boolean fields
                                new_value = field_value.lower() in ('true', '1', 'yes', 'on')
                            else:
                                # String fields
                                new_value = field_value.strip()
                            
                            # Only update if value changed
                            if old_value != new_value:
                                setattr(model_instance, field_name, new_value)
                                updated_fields.append(field_name)
                                logger.debug("[SAVE_CHANGES]   Updated %s: %s -> %s", field_name, old_value, new_value)
                    
                    if updated_fields:
                        # Save the model
                        model_instance.save()
                        logger.info("[SAVE_CHANGES] ✓ Saved %s field(s) to %s", len(updated_fields), model_class_name)
                        
                        # Update cache if this is a cached model
                        self._update_model_cache(model_class_name, model_instance)
                    else:
                        logger.warning("[SAVE_CHANGES] ⚠ No fields changed for %s", model_class_name)
                    
                except Exception as e:
                    logger.error("[SAVE_CHANGES] ✗ Error saving %s: %s", model_class_name, e)
                    all_saved = False
                    continue
            
            if all_saved:
                logger.info("\n[SAVE_CHANGES] ✓ All panels saved successfully")
            else:
                logger.error("\n[SAVE_CHANGES] ⚠ Some panels had errors during save")
            
            return all_saved
            
        except Exception as e:
            logger.error("[SAVE_CHANGES] ✗ Error in save_changes: %s", e)
            return False
    
    def _panel_name_to_model_class(self, panel_name):
        """
        Convert panel name to model class name.
        
        Args:
            panel_name (str): Panel name in uppercase (e.g., "POS_SETTINGS")
            
        Returns:
            str: Model class name in PascalCase (e.g., "PosSettings")
        """
        # Convert uppercase with underscores to PascalCase
        # POS_SETTINGS -> PosSettings
        # CASHIER -> Cashier
        # CASHIER_INFO -> CashierInfo
        parts = panel_name.lower().split('_')
        model_class_name = ''.join(word.capitalize() for word in parts)
        return model_class_name
    
    def _get_model_instance(self, model_class_name, model_class):
        """
        Get model instance for saving.
        
        Tries to get from CurrentData cache first (for commonly used models),
        otherwise gets from database or creates new instance.
        
        Args:
            model_class_name (str): Model class name (e.g., "PosSettings", "Cashier")
            model_class: Model class object
            
        Returns:
            Model instance or None if error
        """
        # Check if this model is cached in CurrentData
        if model_class_name == "PosSettings":
            model_instance = self.pos_settings
            if not model_instance:
                logger.error("[SAVE_CHANGES] ✗ PosSettings instance not found in CurrentData")
                return None
            return model_instance
        
        elif model_class_name == "Cashier":
            # For Cashier, use the cached instance from CurrentData
            model_instance = self.cashier_data
            if not model_instance:
                logger.error("[SAVE_CHANGES] ✗ Cashier instance not found in CurrentData")
                return None
            # Unwrap if it's an AutoSaveModel
            if hasattr(model_instance, 'unwrap'):
                model_instance = model_instance.unwrap()
            return model_instance
        
        else:
            # For other models, get the first instance or create new
            try:
                instances = model_class.get_all(is_deleted=False)
                if instances and len(instances) > 0:
                    return instances[0]
                else:
                    logger.warning("[SAVE_CHANGES] ⚠ No %s instance found, creating new...", model_class_name)
                    return model_class()
            except Exception as e:
                logger.error("[SAVE_CHANGES] ✗ Error getting %s instance: %s", model_class_name, e)
                return None
    
    def _update_model_cache(self, model_class_name, model_instance):
        """
        Update CurrentData cache for commonly used models.
        
        Args:
            model_class_name (str): Model class name (e.g., "PosSettings", "Cashier")
            model_instance: Model instance that was just saved
        """
        if model_class_name == "PosSettings":
            self.pos_settings = model_instance
            logger.info("[SAVE_CHANGES] ✓ Updated pos_settings cache")
        elif model_class_name == "Cashier":
            self.cashier_data = model_instance
            logger.info("[SAVE_CHANGES] ✓ Updated cashier_data cache")
        # Add other cached models here as needed
    
    def _redraw_form_event(self):
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

    def _update_sale_screen_controls(self):
        """
        Update sale screen controls (sale_list, amount_table, payment_list) 
        from document_data when transaction_status is ACTIVE.
        
        This method delegates to SaleService for the actual update logic.
        
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            # Check if document_data exists
            if not self.document_data:
                logger.debug("[UPDATE_SALE_SCREEN] No document_data found")
                return False
            
            # Get window reference
            window = self.interface.window
            if not window:
                logger.error("[UPDATE_SALE_SCREEN] Window not found")
                return False
            
            # Delegate to SaleService
            from pos.service.sale_service import SaleService
            return SaleService.update_sale_screen_controls(
                window=window,
                document_data=self.document_data,
                pos_data=self.pos_data if hasattr(self, 'pos_data') else None
            )
            
        except Exception as e:
            logger.error("[UPDATE_SALE_SCREEN] Error updating sale screen controls: %s", e)
            return False

    # ==================== MAIN NAVIGATION EVENTS ====================

    def _sales_form_event(self):
        """
        Navigate to sales form.
        
        Transitions to the main sales interface where transactions
        are processed. Requires valid authentication.
        
        Creates a new empty document if one doesn't exist or loads
        incomplete document from database. After form is redrawn,
        updates controls if transaction_status is ACTIVE.
        
        Returns:
            bool: True if navigation successful, False if not authenticated
        """
        if self.login_succeed:
            self.current_form_type = FormName.SALE
            
            # Ensure document_data exists - try to load incomplete document first,
            # if none exists, create a new empty document
            if not self.document_data:
                logger.debug("[SALES_FORM] No document_data, trying to load incomplete document...")
                if not self.load_incomplete_document():
                    logger.debug("[SALES_FORM] No incomplete document found, creating new empty document...")
                    if not self.create_empty_document():
                        logger.error("[SALES_FORM] Failed to create empty document")
                        # Continue anyway - form will open but transaction won't work
            
            # Redraw the form
            self.interface.redraw(form_name=FormName.SALE.name)
            
            # Update controls if transaction_status is ACTIVE
            # Use QTimer to ensure controls are created before updating
            from PySide6.QtCore import QTimer
            QTimer.singleShot(100, self._update_sale_screen_controls)
            
            return True
        else:
            self._logout_event()
            return False

    def _settings_form_event(self):
        """
        Navigate to configuration form.
        
        Accesses system configuration and settings interface.
        Requires valid authentication.
        
        Returns:
            bool: True if navigation successful, False if not authenticated
        """
        if self.login_succeed:
            self.current_form_type = FormName.SETTING
            self.interface.redraw(form_name=FormName.SETTING.name)
            return True
        else:
            self._logout_event()
            return False

    def _closure_form_event(self):
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
            self._logout_event()
            return False

    # ==================== MENU NAVIGATION EVENTS ====================

    def _main_menu_form_event(self):
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
            self._logout_event()
            return False

    def _service_form_event(self):
        """
        Navigate to service form.
        """
        if self.login_succeed:
            self.current_form_type = FormName.SERVICE
            self.interface.redraw(form_name=FormName.SERVICE.name)
            return True
        else:
            self._logout_event()
            return False

    def _report_form_event(self):
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
            self._logout_event()
            return False

    # ==================== USER MANAGEMENT EVENTS ====================

    def _cashier_form_event(self):
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
            self._logout_event()
            return False

    def _customer_form_event(self):
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
            self._logout_event()
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
                logger.error("Form not found: %s", target_form_id)
                return False
            
            # Check if form requires login
            if target_form.need_login and not self.login_succeed:
                logger.debug("Login required to access form: %s", target_form.name)
                return False
            
            # Check if form requires special authorization
            if target_form.need_auth:
                # TODO: Implement authorization check
                logger.debug("Authorization check for form: %s", target_form.name)
            
            # Navigate based on transition mode
            if transition_mode.upper() == "MODAL":
                # Show as modal dialog (don't update current_form_type for modal dialogs)
                result = self.interface.show_modal(form_id=target_form_id)
                return result == 1  # QDialog.Accepted
            else:
                # Replace current form - update current_form_type
                if target_form.name:
                    try:
                        form_name_enum = FormName[target_form.name.upper()]
                        self.current_form_type = form_name_enum
                    except (KeyError, AttributeError):
                        # If form name doesn't match enum, keep current
                        pass
                self.interface.redraw(form_id=target_form_id)
                return True
                
        except Exception as e:
            logger.error("Error navigating to form %s: %s", target_form_id, str(e))
            return False