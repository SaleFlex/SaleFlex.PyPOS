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

import enum


class FormName(enum.Enum):
    """
    Enum representing different names of forms used in the system.
    
    Form names are used throughout the application to identify specific forms.
    These names work together with ControlName and EventName enums to create
    a complete form and event handling system.
    
    Usage Examples:
    --------------
    - In application.py: Use FormName.LOGIN instead of 'LOGIN' string
    - In event handlers: Use FormName.SALE when navigating to sales form
    - In dynamic_renderer.py: Use FormName when looking up forms by name
    
    Form Categories:
    ---------------
    Authentication Forms (LOGIN, LOGIN_EXT, LOGIN_SERVICE):
        - LOGIN: Standard login form with username/password
        - LOGIN_EXT: Extended login with additional authentication
        - LOGIN_SERVICE: Service/maintenance personnel login
        - Controls in these forms typically use ControlName.CASHIER_NAME,
          ControlName.PASSWORD, ControlName.LOGIN, ControlName.LOGOUT
    
    Transaction Forms (SALE, REFUND, VOID):
        - SALE: Main sales transaction form
        - REFUND: Product/transaction refund form
        - VOID: Transaction voiding form
    
    Configuration Forms (SETTING, CONFIG, PARAMETER, CASHIER_CONFIG):
        - SETTING/CONFIG: System settings and configuration (same form, value=6)
        - PARAMETER: Parameter configuration form
        - CASHIER_CONFIG: Cashier-specific configuration
        - Controls in these forms use ControlName values like BARCODE_LENGTH,
          IMAGE_FOLDER, DEBUG_MODE_STATE, etc.
    
    Operational Forms (CLOSURE, END_OF_DAY, REPORT):
        - CLOSURE/END_OF_DAY: End-of-shift operations (same form, value=15)
        - REPORT: Reporting and analytics form
    
    Restaurant Forms (TABLE, ORDER, CHECK):
        - TABLE: Table management for restaurant operations
        - ORDER: Order entry and management
        - CHECK: Check/bill handling
    
    Business Forms (CUSTOMER, EMPLOYEE, STOCK, WAREHOUSE):
        - CUSTOMER: Customer information and management
        - EMPLOYEE: Employee management
        - STOCK: Stock/inventory management
        - WAREHOUSE: Warehouse operations
    
    Other Forms (FUNCTION, MENU, SERVICE, RESERVATION):
        - FUNCTION: Function menu/selection
        - MENU: General menu form
        - SERVICE: Service operations
        - RESERVATION: Reservation management
        - CASHIER_PERFORMANCE_TARGET: Cashier performance targets
    """
    
    NONE = 0           # No form selected.
    SALE = 1           # Sale transaction form.
    LOGIN = 2          # Login form.
    LOGIN_EXT = 3      # Extended login form.
    LOGIN_SERVICE = 4  # Service login form.
    SERVICE = 5        # Service-related form.
    SETTING = 6        # Settings configuration form.
    CASHIER_CONFIG = 7  # Cashier configuration form.
    PARAMETER = 8      # Parameter configuration form.
    REPORT = 9         # Report form.
    FUNCTION = 10      # Function selection form.
    CUSTOMER = 11      # Customer-related form.
    VOID = 12          # Form for voiding a transaction.
    REFUND = 13        # Refund transaction form.
    STOCK = 14         # Stock management form.
    END_OF_DAY = 15    # End-of-day process form.
    TABLE = 16         # Table management form (e.g., for restaurants).
    ORDER = 17         # Order management form.
    CHECK = 18         # Check payment form.
    EMPLOYEE = 19      # Employee management form.
    RESERVATION = 20   # Reservation form.
    WAREHOUSE = 21     # Warehouse form.
    MENU = 22          # Menu form.
    CONFIG = 6         # Configuration form (same as SETTING).
    CLOSURE = 15       # End of day closure form (same as END_OF_DAY). 
    CASHIER_PERFORMANCE_TARGET = 23      # Cashier performance target form.