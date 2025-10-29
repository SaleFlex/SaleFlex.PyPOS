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

