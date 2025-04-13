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

from PySide6 import QtGui, QtCore, QtWidgets
from PySide6.QtGui import QPainter, Qt
from PySide6.QtWidgets import QWidget, QGridLayout, QSizePolicy, QVBoxLayout, QAbstractButton


class NumPad(QAbstractButton):
    def __init__(self, parent=None, width=320, height=315, location_x=0, location_y=0, *args, **kwargs):
        QAbstractButton.__init__(self, parent=parent)

        self.parent = parent
        self.numpad_width = width
        self.numpad_height = height
        self.location_x = location_x
        self.location_y = location_y
        print("NumPad", self.numpad_width, self.numpad_height, self.location_x, self.location_y)
        self.setParent(parent)

    staticMetaObject = QtCore.QMetaObject()

    def display(self, parent):
        self.layout.move(self.location_x, self.location_y)
        # self.show()

    def set_event(self, function):
        pass

    def resizeEvent(self, event):
        """ Overrides method in QtGui.QWidget

        Parameters
        ----------
        event : QtCore.QEvent
            Event handle when AddPatientScreen widget resizes

        """
        self.resize(self.numpad_width, self.numpad_height)
        event.accept()

    def paintEvent(self, event):
        """ Overrides resizeEvent method in QtGui.QWidget

        Parameters
        ----------
        event : QResizeEvent
            event handle raised by resize event

        """
        pass
