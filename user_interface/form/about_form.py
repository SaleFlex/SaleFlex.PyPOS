"""
SaleFlex.PyPOS - About Form

This module defines the AboutForm widget which displays application
information centered on the primary screen.
"""

import time
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QGuiApplication, QFont, QColor, QPalette
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSpacerItem, QSizePolicy
from settings.settings import Settings


class AboutForm(QWidget):
    """Simple about dialog-like form for SaleFlex.PyPOS.

    Features:
    - Fixed size 425x425
    - Centered on the primary screen when shown
    - Top-centered title "SaleFlex.PyPOS"
    - Subtitle with version text "version 1.0.0b1"
    - Bottom-centered message area, updatable via update_message()
    - Background color between blue and navy for overall look
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)

        # Window configuration
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setFixedSize(425, 425)
        self._apply_background_theme()

        # Layout and widgets
        self._title_label = QLabel("SaleFlex.PyPOS", self)
        self._title_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self._title_label.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self._title_label.setStyleSheet("color: white;")

        self._version_label = QLabel(f"version {Settings().app_version}", self)
        self._version_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self._version_label.setFont(QFont("Segoe UI", 12))
        self._version_label.setStyleSheet("color: #e5e7eb;")  # light gray for contrast

        self._message_label = QLabel("", self)
        self._message_label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        self._message_label.setFont(QFont("Segoe UI", 11))
        self._message_label.setStyleSheet("color: white;")
        self._message_label.setWordWrap(True)
        self._message_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(8)

        layout.addWidget(self._title_label, alignment=Qt.AlignHCenter)
        layout.addWidget(self._version_label, alignment=Qt.AlignHCenter)

        # Spacer to push message label to bottom
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addWidget(self._message_label)

        self.setLayout(layout)

    def _apply_background_theme(self) -> None:
        """Apply a blue-navy background theme suitable for the app branding."""
        # Choose a color between blue and navy
        background = QColor(30, 58, 138)  # approx. hex #1E3A8A
        foreground = QColor("white")

        palette = QPalette(self.palette())
        palette.setColor(QPalette.Window, background)
        palette.setColor(QPalette.WindowText, foreground)
        self.setAutoFillBackground(True)
        self.setPalette(palette)

    # Public API
    def show(self) -> None:  # type: ignore[override]
        """Show the form centered on the primary screen."""
        self._center_on_primary_screen()
        super().show()

    def hide(self) -> None:  # type: ignore[override]
        """Hide the form."""
        super().hide()

    def dispose(self) -> None:
        """Dispose the form and release resources.

        This method hides the form, detaches it from its parent to break
        parent->child ownership, and schedules safe deletion via
        deleteLater(). Ensure you also drop all Python references to allow
        garbage collection of the Python wrapper.
        """
        self.hide()
        self.setParent(None)
        self.deleteLater()

    def update_message(self, message: str) -> None:
        """Update the bottom-centered message text.

        Args:
            message: Text to display in the message area.
        """
        self._message_label.setText(message or "")
        # Ensure message is immediately visible and pause very briefly
        self._message_label.repaint()
        QGuiApplication.processEvents()
        time.sleep(0.1)

    # Helpers
    def _center_on_primary_screen(self) -> None:
        """Center the window within the primary screen geometry."""
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return
        screen_geometry: QRect = screen.geometry()
        x = screen_geometry.x() + (screen_geometry.width() - self.width()) // 2
        y = screen_geometry.y() + (screen_geometry.height() - self.height()) // 2
        self.move(x, y)


