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
