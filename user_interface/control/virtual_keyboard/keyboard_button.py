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


class KeyboardButton(QtWidgets.QPushButton):
    """ KeyButton class to be used by AlphaNeumericVirtualKeyboard class
    """
    key_button_clicked_signal = QtCore.Signal(str)

    def __init__(self, key, parent=None, settings=None):
        """ KeyButton class constructor

        Parameters
        ----------
        key : str
            key of the button
        parent : QWidget, optional
            Parent widget (the default is None)
        settings : PosVirtualKeyboard, optional
            Keyboard settings from database (the default is None)
        """
        super(KeyboardButton, self).__init__(parent)
        self._key = key
        self._settings = settings
        self.set_key(key)
        self.clicked.connect(self.emit_key)
        self._apply_style(key)
        self.setFocusPolicy(Qt.NoFocus)
    
    def _apply_style(self, key):
        """Apply button style based on key type and settings
        
        Parameters
        ----------
        key : str
            key of the button
        """
        if self._settings is None:
            # Fallback to default styles if no settings provided
            self._apply_default_style(key)
            return
        
        # Build style based on database settings
        if key == "Backspace" or key == "  ":
            # Special buttons (Backspace, Enter)
            style = self._build_button_style(
                min_width=self._settings.special_button_min_width,
                max_width=self._settings.special_button_max_width
            )
        elif key == " ":
            # Space button
            style = self._build_button_style(
                min_width=self._settings.space_button_min_width,
                max_width=self._settings.space_button_max_width
            )
        else:
            # Regular buttons
            style = self._build_button_style(
                min_width=self._settings.button_min_width,
                max_width=self._settings.button_max_width
            )
        
        self.setStyleSheet(style)
    
    def _build_button_style(self, min_width, max_width):
        """Build button stylesheet from settings
        
        Parameters
        ----------
        min_width : int
            Minimum button width
        max_width : int
            Maximum button width
            
        Returns
        -------
        str
            Complete stylesheet string
        """
        s = self._settings
        
        # Base style
        style = f"QPushButton {{"
        style += f"min-width: {min_width}px;"
        style += f"max-width: {max_width}px;"
        style += f"min-height: {s.button_min_height}px;"
        style += f"max-height: {s.button_max_height}px;"
        style += f"font-size: {s.font_size}px;"
        style += f"font-family: {s.font_family};"
        style += f"border: {s.button_border_width}px solid {s.button_border_color};"
        style += f"border-radius: {s.button_border_radius}px;"
        style += f"background-color: {s.button_background_color};"
        
        # Add text color if specified
        if s.button_text_color:
            style += f"color: {s.button_text_color};"
        
        style += "}\n"
        
        # Pressed state
        style += "QPushButton:pressed {"
        style += f"background-color: {s.button_pressed_color};"
        
        # Add pressed text color if specified
        if s.button_text_color_pressed:
            style += f"color: {s.button_text_color_pressed};"
        
        style += "}"
        
        return style
    
    def _apply_default_style(self, key):
        """Apply default hardcoded styles (fallback)
        
        Parameters
        ----------
        key : str
            key of the button
        """
        if key == "Backspace":
            self.setStyleSheet("QPushButton {min-width: 100px;font-size: 20px; font-family: Noto Sans CJK JP;" +
                               "max-width: 200px; min-height:40px; max-height: 40px;" +
                               "border: 3px solid #8f8f91;border-radius: 8px;" +
                               "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #f6f7fa, stop: 1 #dadbde);}\n" +
                               "QPushButton:pressed {background-color: rgb(29, 150, 255);}")
        elif key == "  ":
            self.setStyleSheet("QPushButton {min-width: 100px;font-size: 20px;font-family: Noto Sans CJK JP;" +
                               "max-width: 200px; min-height:40px; max-height: 40px; border: 3px solid #8f8f91;" +
                               "border-radius: 8px;" +
                               "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #f6f7fa, stop: 1 #dadbde);}\n" +
                               "QPushButton:pressed {background-color: rgb(29, 150, 255);}")
        elif key == " ":
            self.setStyleSheet("QPushButton {min-width: 450px;font-size: 20px;font-family: Noto Sans CJK JP; max-width: 550px;" +
                               "min-height:40px; max-height: 40px; border: 3px solid #8f8f91;border-radius: 8px;" +
                               "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #f6f7fa, stop: 1 #dadbde);}\n" +
                               "QPushButton:pressed {background-color: rgb(29, 150, 255);}")
        else:
            self.setStyleSheet("QPushButton {min-width: 80px;font-size: 20px;font-family: Noto Sans CJK JP;" +
                               "max-width: 80px; min-height:40px; max-height: 40px; border: 3px solid #8f8f91;" +
                               "border-radius: 8px;" +
                               "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #f6f7fa, stop: 1 #dadbde);}\n" +
                               "QPushButton:pressed {background-color: rgb(29, 150, 255);}")

    def set_key(self, key):
        """ KeyButton class method to set the key and text of button

        Parameters
        ----------
        key : str
            key of the button
        """
        self._key = key
        if key == ' ':
            self.setText('Space')
            # self.resize(300, 60)
        elif key == '  ':
            self.setText('Enter')
        else:
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
