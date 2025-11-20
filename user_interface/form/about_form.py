"""
SaleFlex.PyPOS - About Form

This module defines the AboutForm widget which displays application
information centered on the primary screen.
"""

import os
import time
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import (
    QGuiApplication, QFont, QColor, QIcon, 
    QPainter, QLinearGradient, QBrush, QPen
)
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QSpacerItem, QSizePolicy
)
from settings.settings import Settings


class AboutForm(QWidget):
    """Professional about dialog-like form for SaleFlex.PyPOS.

    Features:
    - Fixed size 500x550 with modern design
    - Centered on the primary screen when shown
    - Gradient background with professional color scheme
    - Logo/icon display area at the top
    - Top-centered title "SaleFlex.PyPOS" with elegant typography
    - Subtitle with version text
    - Bottom-centered message area, updatable via update_message()
    - Smooth visual effects and shadows
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)

        # Window configuration
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setFixedSize(500, 550)
        self._set_window_icon()

        # Layout and widgets
        self._icon_label = QLabel(self)
        self._icon_label.setAlignment(Qt.AlignHCenter)
        self._icon_label.setFixedSize(80, 80)
        self._load_icon()

        self._title_label = QLabel("SaleFlex.PyPOS", self)
        self._title_label.setAlignment(Qt.AlignHCenter)
        self._title_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        self._title_label.setStyleSheet(
            "color: white; "
            "background: transparent; "
            "padding: 8px;"
        )

        self._version_label = QLabel(f"Version {Settings().app_version}", self)
        self._version_label.setAlignment(Qt.AlignHCenter)
        self._version_label.setFont(QFont("Segoe UI", 13))
        self._version_label.setStyleSheet(
            "color: #cbd5e1; "  # softer gray
            "background: transparent; "
            "padding: 4px; "
            "letter-spacing: 1px;"
        )

        self._message_label = QLabel("", self)
        self._message_label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        self._message_label.setFont(QFont("Segoe UI", 11))
        self._message_label.setStyleSheet(
            "color: #e2e8f0; "  # light gray-white
            "background: rgba(255, 255, 255, 0.1); "
            "padding: 12px 16px; "
            "border-radius: 8px; "
            "min-height: 40px;"
        )
        self._message_label.setWordWrap(True)
        self._message_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(32, 40, 32, 32)
        layout.setSpacing(16)

        # Top section with icon, title, and version
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        layout.addWidget(self._icon_label, alignment=Qt.AlignHCenter)
        layout.addSpacing(8)
        layout.addWidget(self._title_label, alignment=Qt.AlignHCenter)
        layout.addWidget(self._version_label, alignment=Qt.AlignHCenter)

        # Spacer to push message label to bottom
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addWidget(self._message_label)

        self.setLayout(layout)

    def _load_icon(self) -> None:
        """Load and display the application icon."""
        try:
            icon_path = Settings().app_icon
            if icon_path and os.path.exists(icon_path):
                icon = QIcon(icon_path)
                pixmap = icon.pixmap(80, 80)
                self._icon_label.setPixmap(pixmap)
        except Exception:
            # If icon fails to load, show a placeholder or hide the label
            self._icon_label.hide()

    def paintEvent(self, event) -> None:
        """Override paintEvent to draw gradient background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Create gradient from top-left to bottom-right
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(30, 58, 138))  # Deep blue
        gradient.setColorAt(0.5, QColor(37, 99, 235))  # Bright blue
        gradient.setColorAt(1, QColor(29, 78, 216))  # Medium blue

        painter.fillRect(self.rect(), QBrush(gradient))

        # Draw subtle border
        pen = QPen(QColor(255, 255, 255, 30), 1)
        painter.setPen(pen)
        painter.drawRoundedRect(1, 1, self.width() - 2, self.height() - 2, 8, 8)

    def _apply_background_theme(self) -> None:
        """No longer needed - using paintEvent for gradient."""
        pass

    def _set_window_icon(self) -> None:
        """Set the window icon from settings.toml configuration."""
        try:
            icon_path = Settings().app_icon
            if icon_path and os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except Exception:
            pass  # Silently fail if icon cannot be loaded

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


