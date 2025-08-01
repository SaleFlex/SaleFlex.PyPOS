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


class ControlTypeName(enum.Enum):
    """Enum representing different control type names used in the system."""
    BUTTON = "BUTTON"
    COMBOBOX = "COMBOBOX"
    TEXTBOX = "TEXTBOX"
    LABEL = "LABEL"
    PICTURE = "PICTURE"
    NUMPAD = "NUMPAD"
    SALESLIST = "SALESLIST"
    PAYMENTLIST = "PAYMENTLIST"
    AMOUNTSTABLE = "AMOUNTSTABLE"
    MENU = "MENU"
    WEBBROWSER = "WEBBROWSER" 