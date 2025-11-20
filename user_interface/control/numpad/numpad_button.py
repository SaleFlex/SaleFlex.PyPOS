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

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt


class NumPadButton(QtWidgets.QPushButton):
    """ KeyButton class to be used by NumPad class
    """
    key_button_clicked_signal = QtCore.Signal(str)

    def __init__(self, key, parent=None, button_width=80, button_height=80, 
                 number_font_size=24, action_font_size=16, enter_font_size=18):
        """ KeyButton class constructor

        Parameters
        ----------
        key : str
            key of the button
        parent : QWidget, optional
            Parent widget (the default is None)
        button_width : int, optional
            Width of the button (default is 80)
        button_height : int, optional
            Height of the button (default is 80)
        number_font_size : int, optional
            Font size for number buttons (default is 24)
        action_font_size : int, optional
            Font size for action buttons (default is 16)
        enter_font_size : int, optional
            Font size for Enter button (default is 18)
        """
        super(NumPadButton, self).__init__(parent)
        self._key = key
        self._button_width = button_width
        self._button_height = button_height
        self._number_font_size = number_font_size
        self._action_font_size = action_font_size
        self._enter_font_size = enter_font_size
        self.set_key(key)
        self.clicked.connect(self.emit_key)
        
        # Note: Styling will be applied by NumPad's _apply_button_style method
        # We don't apply default styling here to allow NumPad to control it dynamically
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
        return QtCore.QSize(self._button_width, self._button_height)

    def key_disabled(self, flag):
        self.setDisabled(flag)
