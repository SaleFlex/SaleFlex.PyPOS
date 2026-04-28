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

from PySide6.QtWidgets import QLineEdit
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QEvent


class TextBox(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFont(QFont("Verdana", 20))
        self.setStyleSheet("QLineEdit {border-radius: 4px;}")

        self.field_name = ""
        self.__keyboard = None
        self.__enter_function = None

    def set_font_size(self, font_size):
        if font_size:
            self.setFont(QFont("Verdana", font_size))

    def set_password_type(self):
        self.setEchoMode(QLineEdit.EchoMode.Password)

    def set_color(self, background_color, foreground_color):
        self.setStyleSheet(f"QLineEdit {{background-color: #{background_color:06X};" +
                           f"color: #{foreground_color:06X};border-radius: 4px;}}")

    def focusInEvent(self, event):
        # Ensure keyboard is displayed when textbox gets focus
        # This works for both regular textboxes and panel-contained textboxes
        if self.__keyboard:
            if self.__keyboard.is_hidden:
                self.__keyboard.display(source=self)
            self.__keyboard.raise_()
        self.repaint()
        event.accept()

    def focusOutEvent(self, event):
        if self.keyboard:
            self.keyboard.hide()
        self.repaint()
        event.accept()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self.__enter_function:
                self.__enter_function()
                event.accept()
                return
        super().keyPressEvent(event)

    @property
    def keyboard(self):
        return self.__keyboard

    @keyboard.setter
    def keyboard(self, value):
        self.__keyboard = value

    @property
    def enter_function(self):
        return self.__enter_function

    @enter_function.setter
    def enter_function(self, value):
        self.__enter_function = value
