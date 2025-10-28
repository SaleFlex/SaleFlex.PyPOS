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


class EventName(enum.Enum):
    """
    Enum representing different event names and custom function names used in the system.
    
    Event names are used to define the behavior of controls (buttons, textboxes, etc.) in forms.
    These events are typically assigned to controls via the form_control_function1 field in the database.
    
    Relationship with ControlName:
    -----------------------------
    Event names work together with ControlName enums to create a complete control behavior system.
    A control's name (ControlName) identifies what it is, and the event (EventName) defines what it does.
    
    Common Pairings:
    ---------------
    - ControlName.LOGIN + EventName.LOGIN or EventName.LOGIN_EXTENDED
    - ControlName.LOGOUT + EventName.LOGOUT
    - ControlName.EXIT + EventName.EXIT_APPLICATION
    - ControlName.CASHIER_NAME + EventName.LOGIN or EventName.SAVE_CHANGES
    - ControlName.CASHIER_NAME_LIST + EventName.LOGIN or EventName.SAVE_CHANGES
    - ControlName.PASSWORD + EventName.LOGIN or EventName.SAVE_CHANGES
    - ControlName.BARCODE_LENGTH + EventName.SAVE_CHANGES
    - ControlName.IMAGE_FOLDER + EventName.SAVE_CHANGES
    - ControlName.LICENSE_OWNER + EventName.NONE (display only)
    
    Event Categories:
    ----------------
    Application Lifecycle: EXIT_APPLICATION, LOGIN, LOGIN_EXTENDED, LOGOUT
    Sales Operations: SALE, SALE_DEPARTMENT, SALE_PLU_CODE, SALE_PLU_BARCODE, etc.
    Payment Operations: PAYMENT, CASH_PAYMENT, CREDIT_PAYMENT, CHECK_PAYMENT, etc.
    Document Operations: CANCEL_DOCUMENT, CHANGE_DOCUMENT_TYPE, TOTAL, SUBTOTAL
    Configuration: CONFIG, SAVE_CHANGES, SERVICE_* events
    Navigation: BACK, CLOSE_FORM, REDRAW_FORM, various *_MENU events
    Stock/Warehouse: STOCK_IN, STOCK_OUT, WAREHOUSE_RECEIPT, etc.
    Restaurant: TABLE_OPEN, TABLE_CLOSE, ORDER_ADD, CHECK_PRINT, etc.
    Market: SUSPEND_SALE, RESUME_SALE, SUSPEND_LIST
    """
    
    NONE = "NONE"                                   # No event
    EXIT_APPLICATION = "EXIT_APPLICATION"           # Exit application
    LOGIN = "LOGIN"                                 # User login
    LOGIN_EXTENDED = "LOGIN_EXTENDED"               # Extended login
    LOGOUT = "LOGOUT"                               # User logout
    SALE = "SALE"                                   # General sale event
    CONFIG = "CONFIG"                               # General configuration event  
    BACK = "BACK"                                   # General back/return event
    SERVICE_CODE_REQUEST = "SERVICE_CODE_REQUEST"   # Service code request
    LOGIN_SERVICE = "LOGIN_SERVICE"                 # Service login
    CLOSE_FORM = "CLOSE_FORM"                       # Close form
    SAVE_CHANGES = "SAVE_CHANGES"                   # Save changes
    SALE_DEPARTMENT = "SALE_DEPARTMENT"             # Sale by department
    SALE_DEPARTMENT_BY_NO = "SALE_DEPARTMENT_BY_NO" # Sale department by number
    SALE_PLU_CODE = "SALE_PLU_CODE"                 # Sale by PLU code
    SALE_PLU_BARCODE = "SALE_PLU_BARCODE"           # Sale by PLU barcode
    GET_PLU_FROM_MAINGROUP = "GET_PLU_FROM_MAINGROUP" # Get PLU from main group
    REPEAT_LAST_SALE = "REPEAT_LAST_SALE"           # Repeat last sale
    REPEAT_SALE = "REPEAT_SALE"                     # Repeat sale
    CANCEL_DEPARTMENT = "CANCEL_DEPARTMENT"         # Cancel department sale
    CANCEL_PLU = "CANCEL_PLU"                       # Cancel PLU sale
    CANCEL_LAST_SALE = "CANCEL_LAST_SALE"           # Cancel last sale
    CANCEL_SALE = "CANCEL_SALE"                     # Cancel sale
    OPEN_CASH_DRAWER = "OPEN_CASH_DRAWER"           # Open cash drawer
    MAIN_MENU_FORM = "MAIN_MENU_FORM"               # Main menu form
    SUB_MENU_FORM = "SUB_MENU_FORM"                 # Sub menu form
    FUNCTION_FORM = "FUNCTION_FORM"                 # Function form
    SALES_FORM = "SALES_FORM"                       # Sales form
    SERVICE_FORM = "SERVICE_FORM"                   # Service form
    SETTING_FORM = "SETTING_FORM"                   # Settings form
    REPORT_FORM = "REPORT_MENU"                     # Reports menu
    CLOSURE_FORM = "CLOSURE_FORM"                   # Closure form
    CASHIER_FORM = "CASHIER_FORM"                   # Cashier form
    CASHIER = "CASHIER"                             # Cashier function
    CUSTOMER_FORM = "CUSTOMER_FORM"                 # Customer form
    CHANGE_DOCUMENT_TYPE = "CHANGE_DOCUMENT_TYPE"   # Change document type
    CUSTOMER = "CUSTOMER"                           # Customer function
    REFUND = "REFUND"                               # Refund function
    DISCOUNT_BY_AMOUNT = "DISCOUNT_BY_AMOUNT"       # Discount by amount
    SURCHARGE_BY_AMOUNT = "SURCHARGE_BY_AMOUNT"     # Surcharge by amount
    DISCOUNT_BY_PERCENT = "DISCOUNT_BY_PERCENT"     # Discount by percent
    SURCHARGE_BY_PERCENT = "SURCHARGE_BY_PERCENT"   # Surcharge by percent
    INPUT_PRICE = "INPUT_PRICE"                     # Input price
    INPUT_QUANTITY = "INPUT_QUANTITY"               # Input quantity
    INPUT_AMOUNT = "INPUT_AMOUNT"                   # Input amount
    PRICE_LOOKUP = "PRICE_LOOKUP"                   # Price lookup
    SUBTOTAL = "SUBTOTAL"                           # Calculate subtotal
    TOTAL = "TOTAL"                                 # Calculate total
    SALE_OPTION = "SALE_OPTION"                     # Sale options
    CLEAR_BUFFER = "CLEAR_BUFFER"                   # Clear buffer
    PAYMENT = "PAYMENT"                             # General payment
    CASH_PAYMENT = "CASH_PAYMENT"                   # Cash payment
    CREDIT_PAYMENT = "CREDIT_PAYMENT"               # Credit card payment
    CHECK_PAYMENT = "CHECK_PAYMENT"                 # Check payment
    EXCHANGE_PAYMENT = "EXCHANGE_PAYMENT"           # Exchange payment
    PREPAID_PAYMENT = "PREPAID_PAYMENT"             # Prepaid payment
    CHARGE_SALE_PAYMENT = "CHARGE_SALE_PAYMENT"     # Charge sale payment
    OTHER_PAYMENT = "OTHER_PAYMENT"                 # Other payment method
    PAYMENT_DETAIL = "PAYMENT_DETAIL"               # Payment details
    CANCEL_DOCUMENT = "CANCEL_DOCUMENT"             # Cancel document
    CLOSURE = "CLOSURE"                             # Cash register closure
    STOCK_ENTRY_FORM = "STOCK_ENTRY_FORM"           # Stock entry form
    SALE_DETAIL_REPORT = "SALE_DETAIL_REPORT"       # Sale detail report
    PLU_SALE_REPORT = "PLU_SALE_REPORT"             # PLU sales report
    POS_SUMMARY_REPORT = "POS_SUMMARY_REPORT"       # POS summary report
    SET_DISPLAY_BRIGHTNESS = "SET_DISPLAY_BRIGHTNESS"   # Set display brightness
    SET_PRINTER_INTENSITY = "SET_PRINTER_INTENSITY"     # Set printer intensity
    SET_CASHIER = "SET_CASHIER"                         # Set cashier
    SET_SUPERVISOR = "SET_SUPERVISOR"                   # Set supervisor
    SET_RECEIPT_HEADER = "SET_RECEIPT_HEADER"           # Set receipt header
    SET_RECEIPT_FOOTER = "SET_RECEIPT_FOOTER"           # Set receipt footer
    SET_IDLE_MESSAGE = "SET_IDLE_MESSAGE"               # Set idle message
    SET_BARCODE_DEFINITION = "SET_BARCODE_DEFINITION"   # Set barcode definition
    SET_VAT_DEFINITION = "SET_VAT_DEFINITION"           # Set VAT definition
    SET_DEPARTMENT_DEFINITION = "SET_DEPARTMENT_DEFINITION"  # Set department definition
    SET_CURRENCY_DEFINITION = "SET_CURRENCY_DEFINITION" # Set currency definition
    SET_PLU_DEFINITION = "SET_PLU_DEFINITION"           # Set PLU definition
    SET_PLU_MAINGROUP_DEFINITION = "SET_PLU_MAINGROUP_DEFINITION"  # Set PLU main group definition
    SET_DISCOUNT_RATE = "SET_DISCOUNT_RATE"             # Set discount rate
    SET_SURCHARGE_RATE = "SET_SURCHARGE_RATE"           # Set surcharge rate
    SERVICE_COMPANY_INFO = "SERVICE_COMPANY_INFO"       # Service company info
    SERVICE_CHANGE_DATE_TIME = "SERVICE_CHANGE_DATE_TIME"  # Change date and time
    SERVICE_PARAMETER_DOWNLOAD = "SERVICE_PARAMETER_DOWNLOAD"  # Parameter download
    SERVICE_SET_RECEIPT_LIMIT = "SERVICE_SET_RECEIPT_LIMIT"    # Set receipt limit
    SERVICE_RESET_TO_FACTORY_MODE = "SERVICE_RESET_TO_FACTORY_MODE"  # Reset to factory mode
    SERVICE_RESET_PASSWORD = "SERVICE_RESET_PASSWORD"   # Reset password
    SERVICE_CHANGE_PASSWORD = "SERVICE_CHANGE_PASSWORD" # Change password
    SERVICE_POS_ACTIVE = "SERVICE_POS_ACTIVE"           # POS activation service
    SERVICE_SOFTWARE_DOWNLOAD = "SERVICE_SOFTWARE_DOWNLOAD"  # Software download
    INVOICE_LIST = "INVOICE_LIST"                   # Invoice list
    WAYBILL_LIST = "WAYBILL_LIST"                   # Waybill list
    RETURN_LIST = "RETURN_LIST"                     # Return list
    SERVICE_GET_PLU_LIST = "SERVICE_GET_PLU_LIST"   # Get PLU list service
    STOCK_LIST = "STOCK_LIST"                       # Stock list
    SUSPEND_PAYMENT = "SUSPEND_PAYMENT"             # Suspend payment
    BACK_PAYMENT = "BACK_PAYMENT"                   # Back payment
    SALE_SHORTCUT = "SALE_SHORTCUT"                 # Sale shortcut
    REDRAW_FORM = "REDRAW_FORM"                     # Redraw form
    
    # Restaurant Table and Check Operations
    TABLE_OPEN = "TABLE_OPEN"                      # Open table
    TABLE_CLOSE = "TABLE_CLOSE"                    # Close table
    TABLE_SELECT = "TABLE_SELECT"                  # Select table
    TABLE_TRANSFER = "TABLE_TRANSFER"              # Transfer table
    TABLE_MERGE = "TABLE_MERGE"                    # Merge tables
    TABLE_SPLIT = "TABLE_SPLIT"                    # Split table
    TABLE_STATUS = "TABLE_STATUS"                  # Table status
    TABLE_LIST = "TABLE_LIST"                      # Table list
    ORDER_ADD = "ORDER_ADD"                        # Add order
    ORDER_CANCEL = "ORDER_CANCEL"                  # Cancel order
    ORDER_MODIFY = "ORDER_MODIFY"                  # Modify order
    ORDER_SEND_TO_KITCHEN = "ORDER_SEND_TO_KITCHEN"  # Send to kitchen
    ORDER_READY = "ORDER_READY"                    # Order ready
    CHECK_OPEN = "CHECK_OPEN"                      # Open check
    CHECK_CLOSE = "CHECK_CLOSE"                    # Close check
    CHECK_PRINT = "CHECK_PRINT"                    # Print check
    CHECK_SPLIT = "CHECK_SPLIT"                    # Split check
    CHECK_MERGE = "CHECK_MERGE"                    # Merge checks
    
    # Market Sale Suspension Operations
    SUSPEND_SALE = "SUSPEND_SALE"                  # Suspend sale
    RESUME_SALE = "RESUME_SALE"                    # Resume suspended sale
    SUSPEND_LIST = "SUSPEND_LIST"                  # List suspended sales
    DELETE_SUSPENDED_SALE = "DELETE_SUSPENDED_SALE"  # Delete suspended sale
    SUSPEND_DETAIL = "SUSPEND_DETAIL"              # Suspended sale detail
    
    # Warehouse Stock Operations  
    STOCK_IN = "STOCK_IN"                          # Stock receipt
    STOCK_OUT = "STOCK_OUT"                        # Stock issue
    STOCK_TRANSFER = "STOCK_TRANSFER"              # Stock transfer
    STOCK_ADJUSTMENT = "STOCK_ADJUSTMENT"          # Stock adjustment
    STOCK_COUNT = "STOCK_COUNT"                    # Stock count
    STOCK_MOVEMENT = "STOCK_MOVEMENT"              # Stock movement
    STOCK_INQUIRY = "STOCK_INQUIRY"                # Stock inquiry
    WAREHOUSE_RECEIPT = "WAREHOUSE_RECEIPT"        # Warehouse receipt
    WAREHOUSE_ISSUE = "WAREHOUSE_ISSUE"            # Warehouse issue
    WAREHOUSE_TRANSFER = "WAREHOUSE_TRANSFER"      # Warehouse transfer
    WAREHOUSE_ADJUSTMENT = "WAREHOUSE_ADJUSTMENT"  # Warehouse adjustment
    WAREHOUSE_COUNT = "WAREHOUSE_COUNT"            # Warehouse count
    WAREHOUSE_LOCATION = "WAREHOUSE_LOCATION"      # Warehouse location 