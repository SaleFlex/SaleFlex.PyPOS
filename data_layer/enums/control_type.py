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


class ControlType(enum.Enum):
    """Enum representing different types of form controls."""
    NONE = 0
    BUTTON = 1
    PICTURE = 2
    LABEL = 3
    TEXT_BOX = 4
    COMBO_BOX = 5
    TOOL_BAR = 6
    MENU = 7
    MENU_ITEM = 8
    MENU_SUB_ITEM = 9
    TAB_PAGE = 10
    TAB_PAGE_ITEM = 11
    PANEL = 12
    WEB_BROWSER = 13
    GROUP = 14
    DATA_VIEW = 15
    POP_UP = 16
    LIST_BOX = 17
    CHECK_BOX = 18 