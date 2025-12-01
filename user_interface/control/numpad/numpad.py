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
        
        # Calculate dynamic dimensions based on numpad size
        self._calculate_dynamic_dimensions()
        
        # Set position and size
        self.setGeometry(location_x, location_y, width, height)
        
        # Create main layout with dynamic spacing and margins
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(self.dynamic_spacing)
        self.main_layout.setContentsMargins(self.dynamic_margin, self.dynamic_margin, 
                                           self.dynamic_margin, self.dynamic_margin)
        
        # Create text display with dynamic height
        self.text_display = QLineEdit(self)
        self.text_display.setAlignment(Qt.AlignRight)
        self.text_display.setReadOnly(True)
        self.text_display.setMinimumHeight(self.text_display_height)
        self.text_display.setMaximumHeight(self.text_display_height)
        
        # Set text display colors with dynamic font size
        text_bg_color = self.background_color.lighter(150).name()
        text_fg_color = self.foreground_color.name()
        
        self.text_display.setStyleSheet(f"""
            QLineEdit {{
                font-size: {self.text_font_size}px;
                font-weight: bold;
                border: {max(1, int(self.dynamic_margin * 0.4))}px solid {self.background_color.darker(120).name()};
                border-radius: {max(3, int(self.dynamic_margin))}px;
                background-color: {text_bg_color};
                color: {text_fg_color};
                padding: {max(2, int(self.dynamic_margin))}px;
            }}
        """)
        self.main_layout.addWidget(self.text_display)
        
        # Create grid layout for buttons with dynamic spacing
        self.button_layout = QGridLayout()
        self.button_layout.setSpacing(self.button_spacing)
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

    def _calculate_dynamic_dimensions(self):
        """Calculate dynamic dimensions based on numpad width and height"""
        # Base dimensions for reference (320x315)
        base_width = 320
        base_height = 315
        
        # Calculate scale factors
        width_scale = self.numpad_width / base_width
        height_scale = self.numpad_height / base_height
        # Use average scale for proportional sizing
        scale = (width_scale + height_scale) / 2
        
        # Dynamic margins (proportional to size, minimum 3px)
        self.dynamic_margin = max(3, int(5 * scale))
        
        # Dynamic spacing between elements (proportional to size, minimum 3px)
        self.dynamic_spacing = max(3, int(10 * scale))
        
        # Button spacing (proportional to size, minimum 2px)
        self.button_spacing = max(2, int(5 * scale))
        
        # Calculate available space for buttons
        available_width = self.numpad_width - (2 * self.dynamic_margin)
        available_height = self.numpad_height - (2 * self.dynamic_margin)
        
        # Text display takes approximately 15-20% of height
        self.text_display_height = max(30, int(available_height * 0.15))
        
        # Available height for button grid
        button_grid_height = available_height - self.text_display_height - self.dynamic_spacing
        
        # Number of rows (5 rows: 3 number rows + 1 row with Clear/0/Backspace + 1 Enter row)
        num_rows = 5
        
        # Number of columns (3 columns for most rows)
        num_cols = 3
        
        # Calculate button dimensions
        # Account for spacing between buttons: (num_cols - 1) * button_spacing
        button_width = max(30, int((available_width - (num_cols - 1) * self.button_spacing) / num_cols))
        
        # Account for spacing between rows: (num_rows - 1) * button_spacing
        button_height = max(25, int((button_grid_height - (num_rows - 1) * self.button_spacing) / num_rows))
        
        # Store button dimensions
        self.button_width = button_width
        self.button_height = button_height
        
        # Calculate font sizes based on button size
        # Base font sizes for reference (button size ~80px)
        base_button_size = 80
        base_number_font = 24
        base_action_font = 16
        base_enter_font = 18
        base_text_font = 24
        
        # Scale font sizes proportionally to button size
        font_scale = min(button_height, button_width) / base_button_size
        self.number_font_size = max(12, int(base_number_font * font_scale))
        self.action_font_size = max(10, int(base_action_font * font_scale))
        self.enter_font_size = max(12, int(base_enter_font * font_scale))
        self.text_font_size = max(14, int(base_text_font * scale))
        
        print(f"Dynamic dimensions calculated:")
        print(f"  Scale: {scale:.2f}")
        print(f"  Margin: {self.dynamic_margin}px")
        print(f"  Spacing: {self.dynamic_spacing}px")
        print(f"  Button spacing: {self.button_spacing}px")
        print(f"  Text display height: {self.text_display_height}px")
        print(f"  Button size: {self.button_width}x{self.button_height}px")
        print(f"  Font sizes - Number: {self.number_font_size}px, Action: {self.action_font_size}px, Enter: {self.enter_font_size}px, Text: {self.text_font_size}px")

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
                # Pass button dimensions to NumPadButton
                button = NumPadButton(key, self, 
                                     button_width=self.button_width,
                                     button_height=self.button_height,
                                     number_font_size=self.number_font_size,
                                     action_font_size=self.action_font_size,
                                     enter_font_size=self.enter_font_size)
                
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
        base_bg = self.background_color
        base_fg = self.foreground_color
        font_family = "Noto Sans CJK JP"

        border_width = max(1, int(min(self.button_width, self.button_height) * 0.04))
        border_radius = max(4, int(min(self.button_width, self.button_height) * 0.1))
        border_color = base_bg.darker(130)

        base_color = base_bg.lighter(120)
        hover_color = base_bg.lighter(145)
        pressed_color = base_bg
        text_color = base_fg
        font_size = self.action_font_size
        font_weight = "normal"
        min_width = self.button_width
        max_width = self.button_width
        min_height = self.button_height
        max_height = self.button_height

        if key.isdigit():
            font_size = self.number_font_size
            font_weight = "bold"
            base_color = base_bg.lighter(130)
            hover_color = base_bg.lighter(165)
            pressed_color = base_bg
        elif key == "Backspace":
            font_size = self.action_font_size
            font_weight = "bold"
            base_color = QColor(255, 204, 203)
            hover_color = QColor(base_color).lighter(110)
            pressed_color = QColor(base_color).darker(125)
            text_color = QColor(0, 0, 0)
            border_color = QColor(base_color).darker(130)
        elif key == "Clear":
            font_size = self.action_font_size
            font_weight = "bold"
            base_color = QColor(255, 230, 204)
            hover_color = QColor(base_color).lighter(110)
            pressed_color = QColor(base_color).darker(120)
            text_color = QColor(0, 0, 0)
            border_color = QColor(base_color).darker(130)
        elif key == "Enter":
            font_size = self.enter_font_size
            font_weight = "bold"
            base_color = base_bg.lighter(150)
            hover_color = base_bg.lighter(185)
            pressed_color = base_bg
            border_color = base_bg.darker(120)
            min_width = self.button_width * 3 + (self.button_spacing * 2)
            max_width = None  # allow the layout to stretch the button across the row
        else:
            # Default fallback styling
            base_color = base_bg.lighter(125)
            hover_color = base_bg.lighter(150)
            pressed_color = base_bg

        button.apply_visual_profile(
            base_bg=base_color,
            hover_bg=hover_color,
            pressed_bg=pressed_color,
            text_color=text_color,
            border_color=border_color,
            border_radius=border_radius,
            border_width=border_width,
            font_family=font_family,
            font_size=font_size,
            font_weight=font_weight,
            min_width=int(min_width) if min_width is not None else None,
            max_width=int(max_width) if max_width is not None else None,
            min_height=int(min_height) if min_height is not None else None,
            max_height=int(max_height) if max_height is not None else None,
        )

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
        """Override resize event to recalculate dimensions and update layout
        
        Parameters
        ----------
        event : QtCore.QEvent
            Resize event
        """
        # Update dimensions if size changed
        new_width = event.size().width()
        new_height = event.size().height()
        
        if new_width != self.numpad_width or new_height != self.numpad_height:
            self.numpad_width = new_width
            self.numpad_height = new_height
            
            # Recalculate dynamic dimensions
            self._calculate_dynamic_dimensions()
            
            # Update layout spacing and margins
            self.main_layout.setSpacing(self.dynamic_spacing)
            self.main_layout.setContentsMargins(self.dynamic_margin, self.dynamic_margin, 
                                               self.dynamic_margin, self.dynamic_margin)
            
            # Update text display
            self.text_display.setMinimumHeight(self.text_display_height)
            self.text_display.setMaximumHeight(self.text_display_height)
            self.text_display.setStyleSheet(f"""
                QLineEdit {{
                    font-size: {self.text_font_size}px;
                    font-weight: bold;
                    border: {max(1, int(self.dynamic_margin * 0.4))}px solid {self.background_color.darker(120).name()};
                    border-radius: {max(3, int(self.dynamic_margin))}px;
                    background-color: {self.background_color.lighter(150).name()};
                    color: {self.foreground_color.name()};
                    padding: {max(2, int(self.dynamic_margin))}px;
                }}
            """)
            
            # Update button spacing
            self.button_layout.setSpacing(self.button_spacing)
            
            # Update button styles
            for row_idx, row in enumerate(self.numpad_keys):
                for col_idx, key in enumerate(row):
                    item = self.button_layout.itemAtPosition(row_idx, col_idx)
                    if item:
                        button = item.widget()
                        if button:
                            self._apply_button_style(button, key)
        
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
