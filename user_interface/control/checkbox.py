"""
SaleFlex.PyPOS - Point of Sale Application
Copyright (C) 2025-2026 Mousavi.Tech

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
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
