"""
SaleFlex.PyPOS - Message Form

This module defines the MessageForm widget which displays messages
with different modes: error, info, question, and confirmation.
"""

from PySide6.QtCore import Qt, QRect, Signal
from PySide6.QtGui import (
    QGuiApplication, QFont, QColor, QPainter, QLinearGradient, QBrush, QPen
)
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy
)
from data_layer.model import LabelValue


class MessageForm(QWidget):
    """
    Message dialog form with 4 modes:
    - ERROR: Red background, yellow text, OK button only
    - INFO: Green background, white text, OK button only
    - QUESTION: White background, black text, YES/NO buttons
    - CONFIRMATION: Blue background, white text, ACCEPT/REJECT buttons
    """
    
    # Signal emitted when user clicks a button
    button_clicked = Signal(str)  # Emits "OK", "YES", "NO", "ACCEPT", or "REJECT"
    
    MODE_ERROR = "ERROR"
    MODE_INFO = "INFO"
    MODE_QUESTION = "QUESTION"
    MODE_CONFIRMATION = "CONFIRMATION"
    
    def __init__(self, parent: QWidget | None = None, mode: str = MODE_INFO, 
                 message_line1: str = "", message_line2: str = "") -> None:
        super().__init__(parent=parent)
        
        self.mode = mode
        self.message_line1 = message_line1
        self.message_line2 = message_line2
        
        # Window configuration
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setFixedSize(500, 300)
        
        # Create UI elements
        self._create_ui()
        
        # Apply mode-specific styling
        self._apply_mode_styling()
        
    def _create_ui(self):
        """Create UI elements."""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(32, 24, 32, 24)
        main_layout.setSpacing(16)
        
        # Message labels (2 lines)
        self._message_label1 = QLabel(self.message_line1, self)
        self._message_label1.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self._message_label1.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self._message_label1.setWordWrap(True)
        self._message_label1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self._message_label2 = QLabel(self.message_line2, self)
        self._message_label2.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self._message_label2.setFont(QFont("Segoe UI", 12))
        self._message_label2.setWordWrap(True)
        self._message_label2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(16)
        
        # Create buttons based on mode
        self._buttons = []
        if self.mode == self.MODE_ERROR or self.mode == self.MODE_INFO:
            # OK button only
            ok_button = self._create_button("OK")
            button_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
            button_layout.addWidget(ok_button)
            button_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
            self._buttons.append(ok_button)
        elif self.mode == self.MODE_QUESTION:
            # YES/NO buttons
            yes_button = self._create_button("YES")
            no_button = self._create_button("NO")
            button_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
            button_layout.addWidget(yes_button)
            button_layout.addWidget(no_button)
            button_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
            self._buttons.extend([yes_button, no_button])
        elif self.mode == self.MODE_CONFIRMATION:
            # ACCEPT/REJECT buttons
            accept_button = self._create_button("ACCEPT")
            reject_button = self._create_button("REJECT")
            button_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
            button_layout.addWidget(accept_button)
            button_layout.addWidget(reject_button)
            button_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
            self._buttons.extend([accept_button, reject_button])
        
        # Add widgets to main layout
        main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        main_layout.addWidget(self._message_label1)
        main_layout.addWidget(self._message_label2)
        main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def _create_button(self, button_text: str) -> QPushButton:
        """Create a button with label from LabelValue table."""
        # Get button text from LabelValue table
        try:
            label_value = LabelValue.filter_by(key=button_text, culture_info="en-GB", is_deleted=False)
            if label_value and len(label_value) > 0:
                display_text = label_value[0].value
            else:
                display_text = button_text  # Fallback to button_text
        except Exception:
            display_text = button_text  # Fallback on error
        
        button = QPushButton(display_text, self)
        button.setFixedSize(120, 40)
        button.setFont(QFont("Segoe UI", 11, QFont.Bold))
        
        # Connect button click
        button.clicked.connect(lambda: self._on_button_clicked(button_text))
        
        return button
    
    def _on_button_clicked(self, button_text: str):
        """Handle button click."""
        self.button_clicked.emit(button_text)
        self.hide()
    
    def _apply_mode_styling(self):
        """Apply styling based on mode."""
        if self.mode == self.MODE_ERROR:
            # Red background, yellow text
            self._message_label1.setStyleSheet("color: #FFD700; background: transparent; padding: 8px;")
            self._message_label2.setStyleSheet("color: #FFD700; background: transparent; padding: 8px;")
            for button in self._buttons:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #FFD700;
                        color: #8B0000;
                        border: 2px solid #8B0000;
                        border-radius: 6px;
                    }
                    QPushButton:hover {
                        background-color: #FFA500;
                    }
                    QPushButton:pressed {
                        background-color: #FF8C00;
                    }
                """)
        elif self.mode == self.MODE_INFO:
            # Green background, white text
            self._message_label1.setStyleSheet("color: white; background: transparent; padding: 8px;")
            self._message_label2.setStyleSheet("color: white; background: transparent; padding: 8px;")
            for button in self._buttons:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: white;
                        color: #006400;
                        border: 2px solid white;
                        border-radius: 6px;
                    }
                    QPushButton:hover {
                        background-color: #F0F0F0;
                    }
                    QPushButton:pressed {
                        background-color: #E0E0E0;
                    }
                """)
        elif self.mode == self.MODE_QUESTION:
            # White background, black text
            self._message_label1.setStyleSheet("color: black; background: transparent; padding: 8px;")
            self._message_label2.setStyleSheet("color: black; background: transparent; padding: 8px;")
            for button in self._buttons:
                if button.text() == self._get_label_value("YES"):
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: #4CAF50;
                            color: white;
                            border: 2px solid #4CAF50;
                            border-radius: 6px;
                        }
                        QPushButton:hover {
                            background-color: #45a049;
                        }
                        QPushButton:pressed {
                            background-color: #3d8b40;
                        }
                    """)
                else:
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: #f44336;
                            color: white;
                            border: 2px solid #f44336;
                            border-radius: 6px;
                        }
                        QPushButton:hover {
                            background-color: #da190b;
                        }
                        QPushButton:pressed {
                            background-color: #c1170a;
                        }
                    """)
        elif self.mode == self.MODE_CONFIRMATION:
            # Blue background, white text
            self._message_label1.setStyleSheet("color: white; background: transparent; padding: 8px;")
            self._message_label2.setStyleSheet("color: white; background: transparent; padding: 8px;")
            for button in self._buttons:
                if button.text() == self._get_label_value("ACCEPT"):
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: white;
                            color: #1976D2;
                            border: 2px solid white;
                            border-radius: 6px;
                        }
                        QPushButton:hover {
                            background-color: #F0F0F0;
                        }
                        QPushButton:pressed {
                            background-color: #E0E0E0;
                        }
                    """)
                else:
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: #FF5252;
                            color: white;
                            border: 2px solid #FF5252;
                            border-radius: 6px;
                        }
                        QPushButton:hover {
                            background-color: #FF1744;
                        }
                        QPushButton:pressed {
                            background-color: #D50000;
                        }
                    """)
    
    def _get_label_value(self, key: str) -> str:
        """Get label value from database."""
        try:
            label_value = LabelValue.filter_by(key=key, culture_info="en-GB", is_deleted=False)
            if label_value and len(label_value) > 0:
                return label_value[0].value
        except Exception:
            pass
        return key  # Fallback to key
    
    def paintEvent(self, event) -> None:
        """Override paintEvent to draw background based on mode."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create gradient based on mode
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        
        if self.mode == self.MODE_ERROR:
            # Red gradient
            gradient.setColorAt(0, QColor(220, 20, 60))  # Crimson
            gradient.setColorAt(0.5, QColor(178, 34, 34))  # Firebrick
            gradient.setColorAt(1, QColor(139, 0, 0))  # Dark red
        elif self.mode == self.MODE_INFO:
            # Green gradient
            gradient.setColorAt(0, QColor(34, 139, 34))  # Forest green
            gradient.setColorAt(0.5, QColor(0, 128, 0))  # Green
            gradient.setColorAt(1, QColor(0, 100, 0))  # Dark green
        elif self.mode == self.MODE_QUESTION:
            # White background
            gradient.setColorAt(0, QColor(255, 255, 255))
            gradient.setColorAt(1, QColor(245, 245, 245))
        elif self.mode == self.MODE_CONFIRMATION:
            # Blue gradient
            gradient.setColorAt(0, QColor(30, 58, 138))  # Deep blue
            gradient.setColorAt(0.5, QColor(37, 99, 235))  # Bright blue
            gradient.setColorAt(1, QColor(29, 78, 216))  # Medium blue
        
        painter.fillRect(self.rect(), QBrush(gradient))
        
        # Draw subtle border
        border_color = QColor(255, 255, 255, 50) if self.mode != self.MODE_QUESTION else QColor(200, 200, 200, 100)
        pen = QPen(border_color, 2)
        painter.setPen(pen)
        painter.drawRoundedRect(2, 2, self.width() - 4, self.height() - 4, 8, 8)
    
    def show(self) -> None:  # type: ignore[override]
        """Show the form centered on the primary screen."""
        self._center_on_primary_screen()
        super().show()
    
    def _center_on_primary_screen(self):
        """Center the window within the primary screen geometry."""
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return
        screen_geometry: QRect = screen.geometry()
        x = screen_geometry.x() + (screen_geometry.width() - self.width()) // 2
        y = screen_geometry.y() + (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
    
    @staticmethod
    def show_error(parent: QWidget, message_line1: str, message_line2: str = "") -> str:
        """
        Show error message dialog.
        
        Returns:
            str: Button clicked ("OK")
        """
        from PySide6.QtWidgets import QApplication
        
        form = MessageForm(parent, MessageForm.MODE_ERROR, message_line1, message_line2)
        result = [None]
        
        def on_button_clicked(button_text: str):
            result[0] = button_text
        
        form.button_clicked.connect(on_button_clicked)
        form.setWindowModality(Qt.ApplicationModal)
        form.show()
        
        # Wait for user interaction (modal-like behavior)
        app = QApplication.instance()
        while result[0] is None and form.isVisible():
            app.processEvents()
        
        form.close()
        return result[0] if result[0] else "OK"
    
    @staticmethod
    def show_info(parent: QWidget, message_line1: str, message_line2: str = "") -> str:
        """
        Show info message dialog.
        
        Returns:
            str: Button clicked ("OK")
        """
        from PySide6.QtWidgets import QApplication
        
        form = MessageForm(parent, MessageForm.MODE_INFO, message_line1, message_line2)
        result = [None]
        
        def on_button_clicked(button_text: str):
            result[0] = button_text
        
        form.button_clicked.connect(on_button_clicked)
        form.setWindowModality(Qt.ApplicationModal)
        form.show()
        
        # Wait for user interaction
        app = QApplication.instance()
        while result[0] is None and form.isVisible():
            app.processEvents()
        
        form.close()
        return result[0] if result[0] else "OK"
    
    @staticmethod
    def show_question(parent: QWidget, message_line1: str, message_line2: str = "") -> str:
        """
        Show question dialog.
        
        Returns:
            str: Button clicked ("YES" or "NO")
        """
        from PySide6.QtWidgets import QApplication
        
        form = MessageForm(parent, MessageForm.MODE_QUESTION, message_line1, message_line2)
        result = [None]
        
        def on_button_clicked(button_text: str):
            result[0] = button_text
        
        form.button_clicked.connect(on_button_clicked)
        form.setWindowModality(Qt.ApplicationModal)
        form.show()
        
        # Wait for user interaction
        app = QApplication.instance()
        while result[0] is None and form.isVisible():
            app.processEvents()
        
        form.close()
        return result[0] if result[0] else "NO"
    
    @staticmethod
    def show_confirmation(parent: QWidget, message_line1: str, message_line2: str = "") -> str:
        """
        Show confirmation dialog.
        
        Returns:
            str: Button clicked ("ACCEPT" or "REJECT")
        """
        from PySide6.QtWidgets import QApplication
        
        form = MessageForm(parent, MessageForm.MODE_CONFIRMATION, message_line1, message_line2)
        result = [None]
        
        def on_button_clicked(button_text: str):
            result[0] = button_text
        
        form.button_clicked.connect(on_button_clicked)
        form.setWindowModality(Qt.ApplicationModal)
        form.show()
        
        # Wait for user interaction
        app = QApplication.instance()
        while result[0] is None and form.isVisible():
            app.processEvents()
        
        form.close()
        return result[0] if result[0] else "REJECT"

