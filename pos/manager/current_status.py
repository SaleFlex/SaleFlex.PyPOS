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

from data_layer.enums import FormName
from pos.data import DocumentState, DocumentType, DocumentResult


class CurrentStatus:
    """
    Application State Manager for SaleFlex Point of Sale System.
    
    This class manages the current operational state of the POS application,
    tracking user authentication, UI navigation, and document processing states.
    It uses the property pattern with private attributes to provide controlled
    access to state information while maintaining data integrity.
    
    The class handles several key aspects of application state:
    - User authentication status
    - UI form navigation (current and previous forms)
    - Document processing states (state, type, result)
    
    All attributes use private variables with property decorators to ensure
    controlled access and potential validation of state changes.
    
    This class is designed to be inherited by the main Application class,
    providing state management capabilities throughout the application.
    """
    
    def __init__(self):
        """
        Initialize the application state manager.
        
        Sets up initial state values representing a fresh application start:
        - User is not logged in
        - No previous form history
        - Startup form will be loaded from database
        - No document processing is active
        
        All private attributes are initialized to safe default values
        that represent an inactive or initial state.
        """
        # User authentication status - False until successful login
        self.__login_succeed = False
        
        # Form navigation tracking - initially no previous form
        self.__previous_form_type = FormName.NONE
        
        # Current active form - will be set from database
        self.__current_form_type = FormName.LOGIN     # fallback if no startup form found
        self.__current_form_id = None  # UUID of current form from database
        self.__startup_form_id = None  # UUID of startup form
        
        # Form history stack for back button functionality
        # LOGIN and LOGIN_EXT are excluded from history
        self.__form_history = []
        
        # Document processing states - default to FISCAL_RECEIPT with NONE state
        self.__document_state = DocumentState.NONE
        self.__document_type = DocumentType.FISCAL_RECEIPT
        self.__document_result = DocumentResult.NONE
        
        # Current currency - will be loaded from PosSettings.working_currency
        self.__current_currency = None
    
    def load_startup_form(self):
        """
        Load the startup form ID from database.
        
        This method should be called after database initialization.
        It queries the database for the form marked as startup.
        """
        try:
            from user_interface.render.dynamic_renderer import DynamicFormRenderer
            startup_form = DynamicFormRenderer.get_startup_form()
            if startup_form:
                self.__startup_form_id = startup_form.id
                self.__current_form_id = startup_form.id
        except Exception as e:
            print(f"Error loading startup form: {e}")
            self.__startup_form_id = None
            self.__current_form_id = None

    @property
    def login_succeed(self):
        """
        Get the current user authentication status.
        
        Returns:
            bool: True if user is successfully logged in, False otherwise
        """
        return self.__login_succeed

    @login_succeed.setter
    def login_succeed(self, value):
        """
        Set the user authentication status.
        
        Args:
            value (bool): New authentication status
        """
        self.__login_succeed = value

    @property
    def current_form_type(self):
        """
        Get the currently active form type.
        
        Returns:
            FormName: The enum value representing the current form
        """
        return self.__current_form_type

    @current_form_type.setter
    def current_form_type(self, value):
        """
        Set the current form type and automatically update form history.
        
        When changing to a new form, the current form becomes the previous form,
        enabling proper navigation history tracking and back button functionality.
        
        LOGIN and LOGIN_EXT forms are excluded from history as they are shown
        based on need_login and need_auth requirements, not user navigation.
        
        Args:
            value (FormName): The new form type to display
        """
        # Debug logging
        print(f"\n[CURRENT_FORM_TYPE SETTER] Changing form:")
        print(f"  From: {self.__current_form_type.name if self.__current_form_type else 'None'}")
        print(f"  To: {value.name if value else 'None'}")
        print(f"  Current history length: {len(self.__form_history)}")
        
        # Don't add LOGIN or LOGIN_EXT to history - they're shown by need_login/need_auth
        if self.__current_form_type not in [FormName.NONE, FormName.LOGIN, FormName.LOGIN_EXT]:
            # Add current form to history before changing (if not already the last item)
            if not self.__form_history or self.__form_history[-1] != self.__current_form_type:
                self.__form_history.append(self.__current_form_type)
                print(f"  ✓ Added {self.__current_form_type.name} to history")
                # Limit form history to last 30 forms
                if len(self.__form_history) > 30:
                    removed = self.__form_history.pop(0)  # Remove oldest entry
                    print(f"  ✓ Removed oldest entry: {removed.name} (history limit reached)")
            else:
                print(f"  ✗ Skipped adding {self.__current_form_type.name} (already last in history)")
        else:
            print(f"  ✗ Skipped adding {self.__current_form_type.name} (LOGIN/LOGIN_EXT/NONE excluded)")
        
        # Save current form as previous before changing
        self.__previous_form_type = self.__current_form_type
        # Set the new current form
        self.__current_form_type = value
        print(f"  Final history length: {len(self.__form_history)}")
        print(f"  Final history: {[f.name for f in self.__form_history]}")

    @property
    def previous_form_type(self):
        """
        Get the previously active form type.
        
        Used for navigation history and implementing back button functionality.
        
        Returns:
            FormName: The enum value representing the previous form
        """
        return self.__previous_form_type

    @previous_form_type.setter
    def previous_form_type(self, value):
        """
        Set the previous form type.
        
        Typically used for manual navigation history manipulation or
        resetting navigation state.
        
        Args:
            value (FormName): The form type to set as previous
        """
        self.__previous_form_type = value

    @property
    def document_state(self):
        """
        Get the current document processing state.
        
        Tracks whether a document is being created, edited, printed, etc.
        
        Returns:
            DocumentState: Current state of document processing
        """
        return self.__document_state

    @document_state.setter
    def document_state(self, value):
        """
        Set the document processing state.
        
        Args:
            value (DocumentState): New document processing state
        """
        self.__document_state = value

    @property
    def document_type(self):
        """
        Get the current document type being processed.
        
        Indicates whether processing a sale, return, refund, etc.
        
        Returns:
            DocumentType: Type of document currently being processed
        """
        return self.__document_type

    @document_type.setter
    def document_type(self, value):
        """
        Set the document type being processed.
        
        Args:
            value (DocumentType): Type of document to process
        """
        self.__document_type = value

    @property
    def document_result(self):
        """
        Get the result of the last document processing operation.
        
        Indicates success, failure, or specific error conditions.
        
        Returns:
            DocumentResult: Result of the last document operation
        """
        return self.__document_result

    @document_result.setter
    def document_result(self, value):
        """
        Set the result of document processing operation.
        
        Args:
            value (DocumentResult): Result of the document operation
        """
        self.__document_result = value
    
    @property
    def current_form_id(self):
        """
        Get the current form ID from database.
        
        Returns:
            UUID or None: The ID of the current form
        """
        return self.__current_form_id
    
    @current_form_id.setter
    def current_form_id(self, value):
        """
        Set the current form ID.
        
        Args:
            value (UUID): The form ID to set as current
        """
        self.__current_form_id = value
    
    @property
    def startup_form_id(self):
        """
        Get the startup form ID.
        
        Returns:
            UUID or None: The ID of the startup form
        """
        return self.__startup_form_id
    
    @property
    def form_history(self):
        """
        Get the form navigation history stack.
        
        Returns:
            list: List of FormName enums representing navigation history
        """
        return self.__form_history
    
    def clear_form_history(self):
        """
        Clear the form navigation history.
        
        Used when logging out or resetting navigation state.
        """
        self.__form_history = []
    
    def pop_form_history(self):
        """
        Remove and return the last form from history.
        
        Returns:
            FormName or None: The last form in history, or None if history is empty
        """
        if self.__form_history:
            return self.__form_history.pop()
        return None
    
    @property
    def current_currency(self):
        """
        Get the current working currency sign.
        
        Returns:
            str or None: The currency sign (e.g., "GBP", "USD") or None if not set
        """
        return self.__current_currency
    
    @current_currency.setter
    def current_currency(self, value):
        """
        Set the current working currency sign.
        
        Args:
            value (str): The currency sign to set (e.g., "GBP", "USD")
        """
        self.__current_currency = value
