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
    
    Application Controls:
    --------------------
    EXIT: Control (usually button) for exiting the application.
          Typically paired with EventName.EXIT_APPLICATION in form_control_function_1.
    
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
    
    # Application Controls
    EXIT = "EXIT"
    
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