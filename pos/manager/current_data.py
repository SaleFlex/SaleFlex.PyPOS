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


class CurrentData:
    """
    Session Data Manager for SaleFlex Point of Sale System.
    
    This class is responsible for holding and managing session-specific data
    that persists throughout the user's current session but is cleared when
    the application restarts or the user logs out.
    
    The class serves as a centralized data container for:
    - Current cashier information and authentication details
    - Active document/transaction data being processed
    - Temporary session state that needs to be shared across components
    
    This class is designed to be inherited by the main Application class,
    providing session data access throughout the application lifecycle.
    
    Attributes:
        cashier_data: Information about the currently logged-in cashier
        document_data: Current transaction/document being processed
    """
    
    def __init__(self):
        """
        Initialize the session data container.
        
        Sets all session data attributes to None, indicating that no user
        is currently logged in and no document is being processed.
        
        These attributes will be populated when:
        - cashier_data: Set during successful login process
        - document_data: Set when starting a new transaction/document
        - pos_data: Populated after database initialization with rarely-changing
          reference data to reduce disk I/O during runtime
        """
        # Information about the currently logged-in cashier
        # Contains user details, permissions, and authentication status
        self.cashier_data = None
        
        # Current transaction or document being processed
        # Holds the active sale, return, or other document data
        self.document_data = None

        # Cached reference data loaded at startup (after DB init)
        # Example keys: "Cashier", "City", "Country", ...
        self.pos_data = {}
