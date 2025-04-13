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
from PySide6.QtWidgets import QWidget, QGridLayout, QSizePolicy, QVBoxLayout, QLineEdit
from user_interface.control.numpad.numpad_button import NumPadButton


class NumPad(QWidget):
    # Signal to emit when a numpad button is clicked
    numpad_signal = QtCore.Signal(str)
    
    def __init__(self, parent=None, width=320, height=315, location_x=0, location_y=0, *args, **kwargs):
        super(NumPad, self).__init__(parent)

        self.parent = parent
        self.numpad_width = width
        self.numpad_height = height
        self.location_x = location_x
        self.location_y = location_y
        self.callback_function = None
        self.current_text = ""
        
        print("NumPad", self.numpad_width, self.numpad_height, self.location_x, self.location_y)
        
        # Set position and size
        self.setGeometry(location_x, location_y, width, height)
        
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create text display
        self.text_display = QLineEdit(self)
        self.text_display.setAlignment(Qt.AlignRight)
        self.text_display.setReadOnly(True)
        self.text_display.setMinimumHeight(50)
        self.text_display.setStyleSheet("""
            QLineEdit {
                font-size: 24px;
                font-weight: bold;
                border: 2px solid #8f8f91;
                border-radius: 5px;
                background-color: white;
                padding: 5px;
            }
        """)
        self.main_layout.addWidget(self.text_display)
        
        # Create grid layout for buttons
        self.button_layout = QGridLayout()
        self.button_layout.setSpacing(5)
        self.main_layout.addLayout(self.button_layout)
        
        # Define numpad buttons in a grid layout
        self.numpad_keys = [
            ['7', '8', '9'],
            ['4', '5', '6'],
            ['1', '2', '3'],
            ['Clear', '0', 'Backspace'],
            ['Enter']
        ]
        
        # Create the buttons
        self._create_buttons()
        
        # Make the widget visible
        self.show()

    def _create_buttons(self):
        # Create all buttons and add to layout
        for row_idx, row in enumerate(self.numpad_keys):
            for col_idx, key in enumerate(row):
                button = NumPadButton(key, self)
                
                # Connect the button's signal to our internal handler
                button.key_button_clicked_signal.connect(self._on_button_clicked)
                
                # Special case for Enter button - make it span across multiple columns
                if key == 'Enter':
                    self.button_layout.addWidget(button, row_idx, 0, 1, 3)
                else:
                    self.button_layout.addWidget(button, row_idx, col_idx)

    def _on_button_clicked(self, key):
        # Handle button click internally
        print(f"NumPad button clicked: {key}")
        
        if key == 'Clear':
            self.current_text = ""
            self.text_display.setText("")
        elif key == 'Backspace':
            self.current_text = self.current_text[:-1]
            self.text_display.setText(self.current_text)
        elif key == 'Enter':
            # If a callback function is set, call it with the current text
            if self.callback_function:
                self.callback_function(self.current_text)
            # Emit the signal with the current text
            self.numpad_signal.emit(self.current_text)
        else:
            # For digits and other keys, add to current text
            self.current_text += key
            self.text_display.setText(self.current_text)
        
        # If a callback function is set, also call it with the key
        if self.callback_function and key != 'Enter':
            self.callback_function(key)
        
        # Emit the signal with the key
        if key != 'Enter':
            self.numpad_signal.emit(key)

    def set_event(self, function):
        """Set the callback function for button clicks
        
        Parameters
        ----------
        function : callable
            The function to call when a button is clicked
        """
        self.callback_function = function
        
    def get_text(self):
        """Get the current text in display
        
        Returns
        -------
        str
            Current text value
        """
        return self.current_text
        
    def set_text(self, text):
        """Set the text in display
        
        Parameters
        ----------
        text : str
            Text to display
        """
        self.current_text = text
        self.text_display.setText(text)

    def resizeEvent(self, event):
        """Override resize event to ensure proper size
        
        Parameters
        ----------
        event : QtCore.QEvent
            Resize event
        """
        self.resize(self.numpad_width, self.numpad_height)
        event.accept()

    def paintEvent(self, event):
        """Custom paint event
        
        Parameters
        ----------
        event : QResizeEvent
            Paint event
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QtGui.QColor(240, 240, 240))
