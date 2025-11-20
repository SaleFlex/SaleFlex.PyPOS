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

import enum


class ControlName(enum.Enum):
    """
    Enum representing different control names used in the system.
    
    Control names have special meanings when used in form controls (buttons, textboxes, comboboxes, etc.).
    These names are typically used together with EventName enums in form_control_function_1 field.
    The system recognizes these names and performs specific actions or populates controls accordingly.
    
    Authentication & Login Controls:
    --------------------------------
    LOGIN: Control (usually button) for login operation.
           Typically paired with EventName.LOGIN or EventName.LOGIN_EXTENDED in form_control_function_1.
           LOGIN_EXTENDED also shows is_auth forms (more secure forms).
    
    LOGOUT: Control (usually button) for logout operation.
            Typically paired with EventName.LOGOUT in form_control_function_1.
    
    CASHIER_NAME: Control (usually textbox) in LOGIN, LOGIN_EXT, LOGIN_SERVICE, or CASHIER_CONFIG forms
                  to contain cashier name information.
                  Typically paired with EventName.LOGIN, EventName.LOGIN_EXTENDED, or EventName.SAVE_CHANGES.
    
    CASHIER_NAME_LIST: Control (usually combobox) in LOGIN, LOGIN_EXT, LOGIN_SERVICE, or CASHIER_CONFIG forms
                       to contain cashier selection list. System automatically populates with cashier list.
                       Typically paired with EventName.LOGIN, EventName.LOGIN_EXTENDED, or EventName.SAVE_CHANGES.
    
    PASSWORD: Control (usually textbox) in LOGIN, LOGIN_EXT, LOGIN_SERVICE, or CASHIER_CONFIG forms
              to contain password information.
              Typically paired with EventName.LOGIN, EventName.LOGIN_EXTENDED, or EventName.SAVE_CHANGES.
    
    ADMIN_PASSWORD: Control (usually textbox) in LOGIN, LOGIN_EXT, LOGIN_SERVICE, or CASHIER_CONFIG forms
                    to contain administrator password information.
                    Typically paired with EventName.LOGIN, EventName.LOGIN_EXTENDED, or EventName.SAVE_CHANGES.
    
    Cashier Information Controls:
    -----------------------------
    NAME: Control (usually textbox) in CASHIER or CASHIER_CONFIG forms to contain cashier's first name.
          Typically paired with EventName.SAVE_CHANGES in form_control_function_1.
    
    LAST_NAME: Control (usually textbox) in CASHIER or CASHIER_CONFIG forms to contain cashier's last name.
               Typically paired with EventName.SAVE_CHANGES in form_control_function_1.
    
    ID_NUMBER: Control (usually textbox) in CASHIER or CASHIER_CONFIG forms to contain cashier's identification number.
               Typically paired with EventName.SAVE_CHANGES in form_control_function_1.
    
    DESCRIPTION: Control (usually textbox) in CASHIER or CASHIER_CONFIG forms to contain additional information.
                 Typically paired with EventName.SAVE_CHANGES in form_control_function_1.
    
    Application Controls:
    --------------------
    EXIT: Control (usually button) for exiting the application.
          Typically paired with EventName.EXIT_APPLICATION in form_control_function_1.
    
    BACK: Control (usually button) for going back to the previous form or menu.
          Typically paired with EventName.BACK in form_control_function_1.
    
    Configuration Controls:
    ----------------------
    BARCODE_LENGTH: Control (usually textbox) in SETTING or CONFIG forms containing barcode length information.
                    Typically paired with EventName.SAVE_CHANGES in form_control_function_1.
    
    IMAGE_FOLDER: Control (usually textbox) in SETTING or CONFIG forms containing image folder path information.
                  Typically paired with EventName.SAVE_CHANGES in form_control_function_1.
    
    DEBUG_MODE_STATE: Control (usually checkbox) in SETTING or CONFIG forms indicating whether debug mode is enabled.
                      Typically paired with EventName.SAVE_CHANGES in form_control_function_1.
    
    WAIT_AFTER_RECEIPT: Control (usually checkbox) in SETTING or CONFIG forms indicating whether to wait
                        for printer response after printing receipt or invoice.
                        Typically paired with EventName.SAVE_CHANGES in form_control_function_1.
    
    ISO_CULTURE_NAME: Control (usually textbox) in SETTING or CONFIG forms containing language/culture information.
                      Typically paired with EventName.SAVE_CHANGES in form_control_function_1.
    
    DATABASE_POS_FILE_NAME: Control (usually textbox) in SETTING or CONFIG forms containing the POS database filename.
                            Typically paired with EventName.SAVE_CHANGES in form_control_function_1.
    
    DATABASE_SALE_FILE_NAME: Control (usually textbox) in SETTING or CONFIG forms containing the sales database filename.
                             Typically paired with EventName.SAVE_CHANGES in form_control_function_1.
    
    LICENSE_OWNER: Control (usually textbox or label) in any form displaying license owner information.
                   Typically paired with EventName.NONE in form_control_function_1.
    
    Display & Color Controls:
    ------------------------
    BACKCOLOR_DEPARTMENT: Background color configuration for department buttons.
    BACKCOLOR_FUNCTION: Background color configuration for function buttons.
    BACKCOLOR_MESSAGEBOX: Background color configuration for message boxes.
    BACKCOLOR_PAYMENT: Background color configuration for payment buttons.
    BACKCOLOR_PLU: Background color configuration for PLU (Price Look-Up) buttons.
    BACKCOLOR_TOTAL: Background color configuration for total display areas.
    """
    
    # Authentication & Login Controls
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    CASHIER_NAME = "CASHIER_NAME"
    CASHIER_NAME_LIST = "CASHIER_NAME_LIST"
    PASSWORD = "PASSWORD"
    ADMIN_PASSWORD = "ADMIN_PASSWORD"
    
    # Cashier Information Controls
    NAME = "NAME"
    LAST_NAME = "LAST_NAME"
    ID_NUMBER = "ID_NUMBER"
    DESCRIPTION = "DESCRIPTION"
    
    # Application Controls
    EXIT = "EXIT"
    BACK = "BACK"
    SAVE = "SAVE"
    
    # End of Day Controls
    CLOSURE = "CLOSURE"
    
    # Configuration Controls
    BARCODE_LENGTH = "BARCODE_LENGTH"
    IMAGE_FOLDER = "IMAGE_FOLDER"
    DEBUG_MODE_STATE = "DEBUG_MODE_STATE"
    ISO_CULTURE_NAME = "ISO_CULTURE_NAME"
    LICENSE_OWNER = "LICENSE_OWNER"
    WAIT_AFTER_RECEIPT = "WAIT_AFTER_RECEIPT"
    DATABASE_POS_FILE_NAME = "DATABASE_POS_FILE_NAME"
    DATABASE_SALE_FILE_NAME = "DATABASE_SALE_FILE_NAME"
    
    # Display & Color Controls
    BACKCOLOR_DEPARTMENT = "BACKCOLOR_DEPARTMENT"
    BACKCOLOR_FUNCTION = "BACKCOLOR_FUNCTION"
    BACKCOLOR_MESSAGEBOX = "BACKCOLOR_MESSAGEBOX"
    BACKCOLOR_PAYMENT = "BACKCOLOR_PAYMENT"
    BACKCOLOR_PLU = "BACKCOLOR_PLU"
    BACKCOLOR_TOTAL = "BACKCOLOR_TOTAL"
    
    # Data Display Controls
    DATAGRID = "DATAGRID" 