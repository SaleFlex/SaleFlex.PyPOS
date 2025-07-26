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
    """Enum representing different control names used in the system."""
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    CASHIER_NAME = "CASHIER_NAME"
    CASHIER_NAME_LIST = "CASHIER_NAME_LIST"
    PASSWORD = "PASSWORD"
    ADMIN_PASSWORD = "ADMIN_PASSWORD"
    EXIT = "EXIT"
    BARCODE_LENGTH = "BARCODE_LENGTH"
    IMAGE_FOLDER = "IMAGE_FOLDER"
    DEBUG_MODE_STATE = "DEBUG_MODE_STATE"
    ISO_CULTURE_NAME = "ISO_CULTURE_NAME"
    LICENSE_OWNER = "LICENSE_OWNER"
    WAIT_AFTER_RECEIPT = "WAIT_AFTER_RECEIPT"
    DATABASE_POS_FILE_NAME = "DATABASE_POS_FILE_NAME"
    DATABASE_SALE_FILE_NAME = "DATABASE_SALE_FILE_NAME"
    BACKCOLOR_DEPARTMENT = "BACKCOLOR_DEPARTMENT"
    BACKCOLOR_FUNCTION = "BACKCOLOR_FUNCTION"
    BACKCOLOR_MESSAGEBOX = "BACKCOLOR_MESSAGEBOX"
    BACKCOLOR_PAYMENT = "BACKCOLOR_PAYMENT"
    BACKCOLOR_PLU = "BACKCOLOR_PLU"
    BACKCOLOR_TOTAL = "BACKCOLOR_TOTAL" 