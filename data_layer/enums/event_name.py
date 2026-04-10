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
    SELECT_CASHIER = "SELECT_CASHIER"               # Select cashier from management list
    ADD_NEW_CASHIER = "ADD_NEW_CASHIER"             # Add new cashier (admin only)
    CUSTOMER_FORM = "CUSTOMER_FORM"                 # Customer form
    CHANGE_DOCUMENT_TYPE = "CHANGE_DOCUMENT_TYPE"   # Change document type
    CUSTOMER = "CUSTOMER"                           # Customer function
    REFUND = "REFUND"                               # Refund function
    DISCOUNT_BY_AMOUNT = "DISCOUNT_BY_AMOUNT"       # Discount by amount
    MARKUP_BY_AMOUNT = "MARKUP_BY_AMOUNT"           # Markup by amount
    DISCOUNT_BY_PERCENT = "DISCOUNT_BY_PERCENT"     # Discount by percent
    MARKUP_BY_PERCENT = "MARKUP_BY_PERCENT"         # Markup by percent
    INPUT_PRICE = "INPUT_PRICE"                     # Input price
    INPUT_QUANTITY = "INPUT_QUANTITY"               # Input quantity
    PLU_INQUIRY = "PLU_INQUIRY"                     # PLU: show price and stock by warehouse (no sale)
    APPLY_COUPON = "APPLY_COUPON"                  # Enter / scan coupon for requires_coupon campaigns
    INPUT_AMOUNT = "INPUT_AMOUNT"                   # Input amount
    PRICE_LOOKUP = "PRICE_LOOKUP"                   # Price lookup
    SUBTOTAL = "SUBTOTAL"                           # Calculate subtotal
    TOTAL = "TOTAL"                                 # Calculate total
    SALE_OPTION = "SALE_OPTION"                     # Sale options
    CLEAR_BUFFER = "CLEAR_BUFFER"                   # Clear buffer
    PAYMENT = "PAYMENT"                             # Open PAYMENT form (full payment screen from SALE dual button)
    CASH_PAYMENT = "CASH_PAYMENT"                   # Cash payment - Customer pays with cash
    CREDIT_PAYMENT = "CREDIT_PAYMENT"               # Credit card payment - Customer pays with a credit card
    CHECK_PAYMENT = "CHECK_PAYMENT"                 # Check payment - Customer pays using a check
    EXCHANGE_PAYMENT = "EXCHANGE_PAYMENT"           # Exchange payment - Customer pays with a foreign currency
    PREPAID_PAYMENT = "PREPAID_PAYMENT"             # Prepaid payment - Customer pays using a prepaid card
    CHARGE_SALE_PAYMENT = "CHARGE_SALE_PAYMENT"     # Charge sale payment - Customer buys on account (store credit / house charge / IOU)
    OTHER_PAYMENT = "OTHER_PAYMENT"                 # Other payment method - Customer pays using another or unspecified payment method
    BONUS_PAYMENT = "BONUS_PAYMENT"                 # Loyalty points redemption (applies discount; not a cash tender line)
    CHANGE_PAYMENT = "CHANGE_PAYMENT"               # Change payment - Calculate and record change amount
    PAYMENT_DETAIL = "PAYMENT_DETAIL"               # Payment details
    CANCEL_DOCUMENT = "CANCEL_DOCUMENT"             # Cancel document
    CLOSURE = "CLOSURE"                             # Cash register closure
    CLOSURE_DETAIL_FORM = "CLOSURE_DETAIL_FORM"     # Open closure detail form for selected closure
    CLOSURE_RECEIPTS_FORM = "CLOSURE_RECEIPTS_FORM" # Open closure receipts list for selected closure
    CLOSURE_RECEIPT_DETAIL_FORM = "CLOSURE_RECEIPT_DETAIL_FORM"  # Open receipt detail for selected receipt
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
    STOCK_SEARCH = "STOCK_SEARCH"                  # Search products within stock forms
    STOCK_DETAIL = "STOCK_DETAIL"                  # Show per-location detail for selected product
    STOCK_IN_SEARCH = "STOCK_IN_SEARCH"            # Search products on goods-receipt form
    STOCK_IN_CONFIRM = "STOCK_IN_CONFIRM"          # Confirm goods receipt (stock-in)
    STOCK_ADJUSTMENT_SEARCH = "STOCK_ADJUSTMENT_SEARCH"   # Search products on adjustment form
    STOCK_ADJUSTMENT_CONFIRM = "STOCK_ADJUSTMENT_CONFIRM" # Confirm manual stock adjustment
    STOCK_MOVEMENT_SEARCH = "STOCK_MOVEMENT_SEARCH"       # Search movement history
    WAREHOUSE_RECEIPT = "WAREHOUSE_RECEIPT"        # Warehouse receipt
    WAREHOUSE_ISSUE = "WAREHOUSE_ISSUE"            # Warehouse issue
    WAREHOUSE_TRANSFER = "WAREHOUSE_TRANSFER"      # Warehouse transfer
    WAREHOUSE_ADJUSTMENT = "WAREHOUSE_ADJUSTMENT"  # Warehouse adjustment
    WAREHOUSE_COUNT = "WAREHOUSE_COUNT"            # Warehouse count
    WAREHOUSE_LOCATION = "WAREHOUSE_LOCATION"      # Warehouse location

    # Product Management Events
    PRODUCT_LIST_FORM = "PRODUCT_LIST_FORM"        # Navigate to product list / search form
    PRODUCT_SEARCH = "PRODUCT_SEARCH"              # Execute product search from search textbox
    PRODUCT_DETAIL = "PRODUCT_DETAIL"              # Open product detail dialog for selected product
    PRODUCT_DETAIL_SAVE = "PRODUCT_DETAIL_SAVE"    # Save product info changes from product detail dialog

    # Customer Management Events
    CUSTOMER_LIST_FORM = "CUSTOMER_LIST_FORM"      # Navigate to customer list / search form
    CUSTOMER_SEARCH = "CUSTOMER_SEARCH"            # Execute customer search from search textbox
    CUSTOMER_DETAIL = "CUSTOMER_DETAIL"            # Open customer detail dialog for selected customer
    CUSTOMER_DETAIL_SAVE = "CUSTOMER_DETAIL_SAVE"  # Save customer info changes from customer detail dialog
    CUSTOMER_ADD = "CUSTOMER_ADD"                  # Open blank customer detail form to add a new customer
    CUSTOMER_LIST_BACK = "CUSTOMER_LIST_BACK"      # Context-aware BACK from customer list; assigns selected/added customer to the active sale when opened from SALE form
    CUSTOMER_SELECT = "CUSTOMER_SELECT"            # Select highlighted customer from CUSTOMER_SELECT form, assign to active sale, and return to SALE form
    CUSTOMER_SELECT_FORM = "CUSTOMER_SELECT_FORM"  # Navigate to CUSTOMER_SELECT form (used by SALE form's CUSTOMER dual button)