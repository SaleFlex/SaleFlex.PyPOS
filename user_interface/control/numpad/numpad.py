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
from PySide6.QtGui import QPainter, Qt, QColor
from PySide6.QtWidgets import QWidget, QGridLayout, QSizePolicy, QVBoxLayout, QLineEdit, QApplication
from user_interface.control.numpad.numpad_button import NumPadButton


class NumPad(QWidget):
    # Signal to emit when a numpad button is clicked
    numpad_signal = QtCore.Signal(str)
    
    def __init__(self, parent=None, width=320, height=315, location_x=0, location_y=0, 
                 background_color=0x778D45, foreground_color=0xFFFFFF, *args, **kwargs):
        super(NumPad, self).__init__(parent)

        self.parent = parent
        self.numpad_width = width
        self.numpad_height = height
        self.location_x = location_x
        self.location_y = location_y
        self.callback_function = None
        self.current_text = ""
        
        # Set a flag to track if we're in the process of regaining focus
        # This helps prevent focus loops
        self.is_regaining_focus = False
        
        # Flag to track if we should attempt to regain focus
        self.auto_focus_enabled = True
        
        # Timer for focus regain
        self.focus_timer = QtCore.QTimer(self)
        self.focus_timer.setSingleShot(True)
        self.focus_timer.timeout.connect(self._regain_focus)
        
        # Store colors
        self.background_color = QColor(background_color)
        self.foreground_color = QColor(foreground_color)
        
        print("NumPad", self.numpad_width, self.numpad_height, self.location_x, self.location_y)
        print(f"NumPad colors: bg={background_color:x}, fg={foreground_color:x}")
        
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
        
        # Set text display colors
        text_bg_color = self.background_color.lighter(150).name()
        text_fg_color = self.foreground_color.name()
        
        self.text_display.setStyleSheet(f"""
            QLineEdit {{
                font-size: 24px;
                font-weight: bold;
                border: 2px solid {self.background_color.darker(120).name()};
                border-radius: 5px;
                background-color: {text_bg_color};
                color: {text_fg_color};
                padding: 5px;
            }}
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
        
        # Apply a stylesheet to the entire widget
        self.setStyleSheet(f"""
            NumPad {{
                background-color: {self.background_color.name()};
                border: 2px solid {self.background_color.darker(150).name()};
                border-radius: 10px;
            }}
        """)
        
        # Set focus policy to ensure the numpad gets focus
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Show the widget
        self.show()
        
        # Install event filter on the parent to capture keyboard events
        if self.parent:
            self.parent.installEventFilter(self)
        
        # Get application instance
        self.app = QApplication.instance()
        
        # Connect to application's focus changed signal
        if self.app:
            self.app.focusChanged.connect(self.on_focus_changed)
        
        # Set up a timer to focus on this widget when the form is shown
        QtCore.QTimer.singleShot(100, self.initialize_focus)

    def set_auto_focus(self, enabled):
        """Enable or disable automatic focus regaining
        
        Parameters
        ----------
        enabled : bool
            Whether to automatically regain focus when it's lost
        """
        self.auto_focus_enabled = enabled

    def initialize_focus(self):
        """Set initial focus to this widget"""
        if self.isVisible() and self.auto_focus_enabled:
            self.activateWindow()
            self.setFocus()
            self.raise_()
            print("NumPad initial focus set")
        
    def on_focus_changed(self, old, new):
        """Handle focus change events in the application
        
        Parameters
        ----------
        old : QWidget
            Widget that lost focus
        new : QWidget
            Widget that gained focus
        """
        # If auto-focus is disabled, do nothing
        if not self.auto_focus_enabled:
            return
            
        # If we're in the process of regaining focus, don't interfere
        if self.is_regaining_focus:
            return
            
        # If we lost focus to another widget
        if old is self and new is not None and new is not self:
            # Cancel any pending focus regain
            self.focus_timer.stop()
            # Start the timer to regain focus
            self.focus_timer.start(150)
            
    def _regain_focus(self):
        """Internal method to regain focus after it's been lost to another widget"""
        # If we shouldn't try to regain focus or we're not visible, do nothing
        if not self.auto_focus_enabled or not self.isVisible():
            return
            
        # Set flag to prevent focus loop
        self.is_regaining_focus = True
        
        # Make sure this widget is visible and active before trying to regain focus
        self.activateWindow()
        self.setFocus()
        self.raise_()
        print("NumPad regained focus")
        
        # Reset flag after a short delay to allow focus events to settle
        QtCore.QTimer.singleShot(200, self._reset_regain_flag)
        
    def _reset_regain_flag(self):
        """Reset the regaining focus flag after focus events have settled"""
        self.is_regaining_focus = False

    def eventFilter(self, obj, event):
        """Filter events to capture keyboard events on the parent
        
        Parameters
        ----------
        obj : QObject
            Object that sent the event
        event : QEvent
            Event that was sent
            
        Returns
        -------
        bool
            True if the event was handled, False otherwise
        """
        # If auto-focus is disabled, only filter keyboard events
        if not self.auto_focus_enabled and event.type() != QtCore.QEvent.KeyPress:
            return False
            
        # If the event is a focus event and we should regain focus
        if event.type() == QtCore.QEvent.FocusIn:
            # If another widget gained focus and we're not in the process of regaining focus
            if obj is not self and self.auto_focus_enabled and not self.is_regaining_focus:
                # Cancel any pending focus regain
                self.focus_timer.stop()
                # Start the timer to regain focus
                self.focus_timer.start(150)
                
        # If the event is a key press and it's one of our numpad keys, handle it
        elif event.type() == QtCore.QEvent.KeyPress:
            key = event.text()
            key_code = event.key()
            
            # Number keys
            if key.isdigit():
                self._on_button_clicked(key)
                return True
                
            # Enter key
            elif key_code in (Qt.Key_Return, Qt.Key_Enter):
                self._on_button_clicked('Enter')
                return True
                
            # Backspace key
            elif key_code == Qt.Key_Backspace:
                self._on_button_clicked('Backspace')
                return True
                
            # Clear - Escape key
            elif key_code == Qt.Key_Escape:
                self._on_button_clicked('Clear')
                return True
                
        # Let other events pass through
        return super(NumPad, self).eventFilter(obj, event)
        
    def keyPressEvent(self, event):
        """Handle key press events directly on this widget
        
        Parameters
        ----------
        event : QKeyEvent
            Key event
        """
        # Number keys
        key = event.text()
        key_code = event.key()
        
        if key.isdigit():
            self._on_button_clicked(key)
            event.accept()
            return
            
        # Enter key
        if key_code in (Qt.Key_Return, Qt.Key_Enter):
            self._on_button_clicked('Enter')
            event.accept()
            return
            
        # Backspace key
        if key_code == Qt.Key_Backspace:
            self._on_button_clicked('Backspace')
            event.accept()
            return
            
        # Clear - Escape key
        if key_code == Qt.Key_Escape:
            self._on_button_clicked('Clear')
            event.accept()
            return
            
        # Pass unhandled events to parent class
        super(NumPad, self).keyPressEvent(event)
        
    def hideEvent(self, event):
        """Handle hide events to disable focus regaining while hidden
        
        Parameters
        ----------
        event : QHideEvent
            Hide event
        """
        # Temporarily disable auto-focus when hidden
        self.auto_focus_enabled = False
        super(NumPad, self).hideEvent(event)
        
    def showEvent(self, event):
        """Handle show events to re-enable focus regaining
        
        Parameters
        ----------
        event : QShowEvent
            Show event
        """
        # Re-enable auto-focus when shown
        self.auto_focus_enabled = True
        super(NumPad, self).showEvent(event)
        # Schedule focus acquisition
        QtCore.QTimer.singleShot(100, self.initialize_focus)
        
    def closeEvent(self, event):
        """Handle close events to clean up event filters and connections
        
        Parameters
        ----------
        event : QCloseEvent
            Close event
        """
        # Disconnect from focus changed signal to avoid issues after closing
        try:
            self.app.focusChanged.disconnect(self.on_focus_changed)
        except:
            pass
            
        # Remove event filter from parent if we have one
        if self.parent:
            self.parent.removeEventFilter(self)
            
        # Stop any pending timers
        self.focus_timer.stop()
        
        super(NumPad, self).closeEvent(event)

    def _create_buttons(self):
        # Create all buttons and add to layout
        for row_idx, row in enumerate(self.numpad_keys):
            for col_idx, key in enumerate(row):
                button = NumPadButton(key, self)
                
                # Apply color scheme
                self._apply_button_style(button, key)
                
                # Connect the button's signal to our internal handler
                button.key_button_clicked_signal.connect(self._on_button_clicked)
                
                # Special case for Enter button - make it span across multiple columns
                if key == 'Enter':
                    self.button_layout.addWidget(button, row_idx, 0, 1, 3)
                else:
                    self.button_layout.addWidget(button, row_idx, col_idx)

    def _apply_button_style(self, button, key):
        # Base colors from the numpad settings
        base_bg = self.background_color
        base_fg = self.foreground_color
        
        # Different styling based on button type
        if key.isdigit():
            # Number buttons - make them large and prominent
            button.setStyleSheet(f"""
                QPushButton {{
                    min-width: 60px;
                    max-width: 100px;
                    min-height: 60px;
                    max-height: 100px;
                    font-size: 24px;
                    font-weight: bold;
                    font-family: Noto Sans CJK JP;
                    border: 3px solid {base_bg.darker(130).name()};
                    border-radius: 8px;
                    background-color: {base_bg.lighter(130).name()};
                    color: {base_fg.name()};
                }}
                QPushButton:pressed {{
                    background-color: {base_bg.name()};
                    color: {base_fg.name()};
                }}
            """)
        elif key == "Backspace":
            # Backspace button - distinctive styling
            button.setStyleSheet(f"""
                QPushButton {{
                    min-width: 60px;
                    max-width: 100px;
                    min-height: 60px;
                    max-height: 100px;
                    font-size: 16px;
                    font-family: Noto Sans CJK JP;
                    border: 3px solid {base_bg.darker(120).name()};
                    border-radius: 8px;
                    background-color: {QColor(255, 204, 203).name()};
                    color: black;
                }}
                QPushButton:pressed {{
                    background-color: {QColor(255, 153, 153).name()};
                    color: white;
                }}
            """)
        elif key == "Clear":
            # Clear button - distinctive styling
            button.setStyleSheet(f"""
                QPushButton {{
                    min-width: 60px;
                    max-width: 100px;
                    min-height: 60px;
                    max-height: 100px;
                    font-size: 16px;
                    font-family: Noto Sans CJK JP;
                    border: 3px solid {base_bg.darker(120).name()};
                    border-radius: 8px;
                    background-color: {QColor(255, 230, 204).name()};
                    color: black;
                }}
                QPushButton:pressed {{
                    background-color: {QColor(255, 204, 153).name()};
                    color: white;
                }}
            """)
        elif key == "Enter":
            # Enter button - make it wide and stand out
            button.setStyleSheet(f"""
                QPushButton {{
                    min-width: 100%;
                    min-height: 60px;
                    max-height: 100px;
                    font-size: 18px;
                    font-weight: bold;
                    font-family: Noto Sans CJK JP;
                    border: 3px solid {base_bg.darker(120).name()};
                    border-radius: 8px;
                    background-color: {base_bg.lighter(150).name()};
                    color: {base_fg.name()};
                }}
                QPushButton:pressed {{
                    background-color: {base_bg.name()};
                    color: {base_fg.name()};
                }}
            """)
        else:
            # Default styling for other buttons
            button.setStyleSheet(f"""
                QPushButton {{
                    min-width: 60px;
                    max-width: 100px;
                    min-height: 60px;
                    max-height: 100px;
                    font-size: 16px;
                    font-family: Noto Sans CJK JP;
                    border: 3px solid {base_bg.darker(120).name()};
                    border-radius: 8px;
                    background-color: {base_bg.lighter(120).name()};
                    color: {base_fg.name()};
                }}
                QPushButton:pressed {{
                    background-color: {base_bg.name()};
                    color: {base_fg.name()};
                }}
            """)

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
        painter.fillRect(self.rect(), self.background_color)
