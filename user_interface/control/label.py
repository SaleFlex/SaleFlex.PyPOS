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

from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QFont


class Label(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFont(QFont("Verdana", 20))
        self._click_handler = None

    def set_color(self, background_color, foreground_color):
        # If background color is white (0xFFFFFF) or None, make it transparent
        # Labels should not have borders or background like textboxes
        if background_color is None or background_color == 0xFFFFFF:
            self.setStyleSheet(f"QLabel {{background-color: transparent;" +
                              f"color: #{foreground_color:06X};}}")
        else:
            self.setStyleSheet(f"QLabel {{background-color: #{background_color:06X};" +
                              f"color: #{foreground_color:06X};}}")

    def set_event(self, function):
        """Set a click event handler for the label."""
        self._click_handler = function

    def mousePressEvent(self, event):
        """Handle mouse press events on the label."""
        super().mousePressEvent(event)
        if self._click_handler is not None:
            self._click_handler()

