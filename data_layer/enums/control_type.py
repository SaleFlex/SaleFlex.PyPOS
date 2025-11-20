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