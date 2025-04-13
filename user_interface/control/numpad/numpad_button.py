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

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt


class NumPadButton(QtWidgets.QPushButton):
    """ KeyButton class to be used by NumPad class
    """
    key_button_clicked_signal = QtCore.Signal(str)

    def __init__(self, key, parent=None):
        """ KeyButton class constructor

        Parameters
        ----------
        key : str
            key of the button
        parent : QWidget, optional
            Parent widget (the default is None)
        """
        super(NumPadButton, self).__init__(parent)
        self._key = key
        self.set_key(key)
        self.clicked.connect(self.emit_key)
        
        # Apply appropriate styling based on button type
        if key.isdigit():
            # Number buttons - make them large and prominent
            self.setStyleSheet("""
                QPushButton {
                    min-width: 60px;
                    max-width: 100px;
                    min-height: 60px;
                    max-height: 100px;
                    font-size: 24px;
                    font-weight: bold;
                    font-family: Noto Sans CJK JP;
                    border: 3px solid #8f8f91;
                    border-radius: 8px;
                    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #dadbde);
                }
                QPushButton:pressed {
                    background-color: #4a90e2;
                    color: white;
                }
            """)
        elif key == "Backspace":
            # Backspace button - distinctive styling
            self.setStyleSheet("""
                QPushButton {
                    min-width: 60px;
                    max-width: 100px;
                    min-height: 60px;
                    max-height: 100px;
                    font-size: 16px;
                    font-family: Noto Sans CJK JP;
                    border: 3px solid #8f8f91;
                    border-radius: 8px;
                    background-color: #ffcccb;
                }
                QPushButton:pressed {
                    background-color: #ff9999;
                    color: white;
                }
            """)
        elif key == "Clear":
            # Clear button - distinctive styling
            self.setStyleSheet("""
                QPushButton {
                    min-width: 60px;
                    max-width: 100px;
                    min-height: 60px;
                    max-height: 100px;
                    font-size: 16px;
                    font-family: Noto Sans CJK JP;
                    border: 3px solid #8f8f91;
                    border-radius: 8px;
                    background-color: #ffe6cc;
                }
                QPushButton:pressed {
                    background-color: #ffcc99;
                    color: white;
                }
            """)
        elif key == "Enter":
            # Enter button - make it wide and stand out
            self.setStyleSheet("""
                QPushButton {
                    min-width: 100%;
                    min-height: 60px;
                    max-height: 100px;
                    font-size: 18px;
                    font-weight: bold;
                    font-family: Noto Sans CJK JP;
                    border: 3px solid #8f8f91;
                    border-radius: 8px;
                    background-color: #c8e6c9;
                }
                QPushButton:pressed {
                    background-color: #81c784;
                    color: white;
                }
            """)
        else:
            # Default styling for other buttons
            self.setStyleSheet("""
                QPushButton {
                    min-width: 60px;
                    max-width: 100px;
                    min-height: 60px;
                    max-height: 100px;
                    font-size: 16px;
                    font-family: Noto Sans CJK JP;
                    border: 3px solid #8f8f91;
                    border-radius: 8px;
                    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #dadbde);
                }
                QPushButton:pressed {
                    background-color: rgb(29, 150, 255);
                }
            """)
            
        self.setFocusPolicy(Qt.NoFocus)

    def set_key(self, key):
        """ KeyButton class method to set the key and text of button

        Parameters
        ----------
        key : str
            key of the button
        """
        self._key = key
        self.setText(key)

    def emit_key(self):
        """ KeyButton class method to return key as a qt signal
        """
        self.key_button_clicked_signal.emit(str(self._key))

    def sizeHint(self):
        """ KeyButton class method to return size

        Returns
        -------
        QSize
            Size of the created button
        """
        return QtCore.QSize(80, 80)

    def key_disabled(self, flag):
        self.setDisabled(flag)
