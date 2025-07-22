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
    """Enum representing different names of forms used in the system."""
    NONE = 0           # No form selected.
    SALE = 1           # Sale transaction form.
    LOGIN = 2          # Login form.
    LOGIN_EXT = 3      # Extended login form.
    LOGIN_SERVICE = 4  # Service login form.
    SERVICE = 5        # Service-related form.
    SETTING = 6        # Settings configuration form.
    PARAMETER = 7      # Parameter configuration form.
    REPORT = 8         # Report form.
    FUNCTION = 9       # Function selection form.
    CUSTOMER = 10      # Customer-related form.
    VOID = 11          # Form for voiding a transaction.
    REFUND = 12        # Refund transaction form.
    STOCK = 13         # Stock management form.
    END_OF_DAY = 14    # End-of-day process form.
    TABLE = 15         # Table management form (e.g., for restaurants).
    ORDER = 16         # Order management form.
    CHECK = 17         # Check payment form.
    EMPLOYEE = 18      # Employee management form.
    RESERVATION = 19   # Reservation form.
    WAREHOUSE = 20     # Warehouse form.
    MENU = 21          # Menu form.
    CONFIG = 6         # Configuration form (same as SETTING).
    CLOSURE = 14       # End of day closure form (same as END_OF_DAY). 