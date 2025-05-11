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

from PySide6.QtWidgets import QLineEdit
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QEvent


class TextBox(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFont(QFont("Verdana", 20))
        self.setStyleSheet("QLineEdit {border-radius: 4px;}")

        self.filed_name = ""
        self.__keyboard = None

    def set_font_size(self, font_size):
        if font_size:
            self.setFont(QFont("Verdana", font_size))

    def set_password_type(self):
        self.setEchoMode(QLineEdit.EchoMode.Password)

    def set_color(self, background_color, foreground_color):
        self.setStyleSheet(f"QLineEdit {{background-color: #{background_color:06X};" +
                           f"color: #{foreground_color:06X};border-radius: 4px;}}")

    def focusInEvent(self, event):
        if self.__keyboard and self.__keyboard.is_hidden:
            self.__keyboard.display(source=self)
            self.__keyboard.raise_()
        self.repaint()
        event.accept()

    def focusOutEvent(self, event):
        if self.keyboard:
            self.keyboard.hide()
        self.repaint()
        event.accept()

    @property
    def keyboard(self):
        return self.__keyboard

    @keyboard.setter
    def keyboard(self, value):
        self.__keyboard = value
