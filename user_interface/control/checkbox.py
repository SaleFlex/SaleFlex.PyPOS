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

from PySide6.QtWidgets import QCheckBox
from PySide6.QtGui import QFont


class CheckBox(QCheckBox):
    """Boolean field control for dynamic forms; checked = True, unchecked = False."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFont(QFont("Verdana", 20))
        self.setStyleSheet("QCheckBox { spacing: 10px; }")
        self.field_name = ""

    def set_font_size(self, font_size):
        if font_size:
            self.setFont(QFont("Verdana", int(font_size)))

    def set_color(self, background_color, foreground_color):
        self.setStyleSheet(
            f"QCheckBox {{ spacing: 10px; background-color: #{background_color:06X};"
            f"color: #{foreground_color:06X}; }}"
        )

    def bool_value(self) -> bool:
        return self.isChecked()
