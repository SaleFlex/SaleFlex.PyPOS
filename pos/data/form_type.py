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

from enum import Enum, auto


class FormType(Enum):
    """Enum representing different types of forms used in the system."""
    NONE = auto()           # No form type selected
    LOGIN = auto()          # Login form
    MENU = auto()           # Menu form
    SALE = auto()           # Sale transaction form
    SERVICE = auto()        # Service form
    CONFIG = auto()         # Configuration form
    PARAMETER = auto()      # Parameter settings form
    REPORT = auto()         # Report form
    FUNCTION = auto()       # Function selection form
    CUSTOMER = auto()       # Customer management form
    VOID = auto()           # Void transaction form
    REFUND = auto()         # Refund transaction form
    STOCK = auto()          # Stock management form
    CLOSURE = auto()        # End of day closure form
    TABLE = auto()          # Table management form (for restaurants)
    ORDER = auto()          # Order management form
    CHECK = auto()          # Check payment form
    EMPLOYEE = auto()       # Employee management form
    RESERVATION = auto()    # Reservation form
    WAREHOUSE = auto()      # Warehouse management form 