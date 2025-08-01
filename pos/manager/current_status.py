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
        - Login form is the initial form to display
        - No document processing is active
        
        All private attributes are initialized to safe default values
        that represent an inactive or initial state.
        """
        # User authentication status - False until successful login
        self.__login_succeed = False
        
        # Form navigation tracking - initially no previous form
        self.__previous_form_type = FormName.NONE
        
        # Current active form - application starts with login form
        self.__current_form_type = FormName.LOGIN     # initial form
        
        # Document processing states - initially inactive
        self.__document_state = DocumentState.NONE
        self.__document_type = DocumentType.NONE
        self.__document_result = DocumentResult.NONE

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
        
        Args:
            value (FormName): The new form type to display
        """
        # Save current form as previous before changing
        self.__previous_form_type = self.__current_form_type
        # Set the new current form
        self.__current_form_type = value

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
