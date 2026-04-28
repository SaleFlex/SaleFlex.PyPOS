"""
SaleFlex.PyPOS - Point of Sale Application
Copyright (C) 2025-2026 Mousavi.Tech

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from PySide6.QtWidgets import QTabWidget, QWidget
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt


class TabControl(QTabWidget):
    """
    A tab control widget for organizing content into multiple tabs.

    Designed for touch screens with large, readable tabs. Supports
    dynamic tab creation and consistent styling across the POS UI.
    """

    def __init__(self, parent=None, width=800, height=600,
                 location_x=0, location_y=0,
                 background_color=0xFFFFFF, foreground_color=0x000000,
                 font_size=14):
        super().__init__(parent)

        self.setGeometry(location_x, location_y, width, height)
        # ClickFocus lets the tab bar process mouse events normally;
        # Qt.NoFocus can prevent tab switching in some PySide6 builds.
        self.setFocusPolicy(Qt.ClickFocus)

        self._background_color = background_color
        self._foreground_color = foreground_color
        self._font_size = font_size

        self.setFont(QFont("Verdana", font_size))
        self.set_color(background_color, foreground_color)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_tab(self, widget: QWidget, title: str) -> int:
        """
        Add a widget as a new tab.

        Args:
            widget: The widget to display inside the tab.
            title:  Tab label text.

        Returns:
            Index of the newly added tab.
        """
        return self.addTab(widget, title)

    def set_color(self, background_color: int, foreground_color: int):
        """
        Apply background / foreground colours and a touch-friendly tab bar style.

        Args:
            background_color: RGB integer, e.g. 0x2F4F4F
            foreground_color: RGB integer, e.g. 0xFFFFFF
        """
        self._background_color = background_color
        self._foreground_color = foreground_color

        bg = f"#{background_color:06X}"
        fg = f"#{foreground_color:06X}"
        tab_bg = f"#{self._darken(background_color, 0.75):06X}"
        tab_sel = f"#{self._lighten(background_color, 1.3):06X}"
        tab_border = f"#{self._darken(background_color, 0.5):06X}"

        style = f"""
            QTabWidget::pane {{
                background-color: {bg};
                border: 2px solid {tab_border};
                border-radius: 4px;
            }}
            QTabBar::tab {{
                background-color: {tab_bg};
                color: {fg};
                padding: 10px 20px;
                margin-right: 2px;
                border: 1px solid {tab_border};
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                min-width: 120px;
                font-size: {self._font_size}px;
            }}
            QTabBar::tab:selected {{
                background-color: {tab_sel};
                color: {fg};
                border-bottom: 2px solid {tab_sel};
                font-weight: bold;
            }}
            QTabBar::tab:hover {{
                background-color: {self._lighten_hex(background_color, 1.15)};
            }}
            QWidget#tab_page {{
                background-color: {bg};
            }}
        """
        self.setStyleSheet(style)

    def get_current_tab_index(self) -> int:
        """Return the currently active tab index."""
        return self.currentIndex()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _darken(color: int, factor: float) -> int:
        r = int(((color >> 16) & 0xFF) * factor)
        g = int(((color >> 8) & 0xFF) * factor)
        b = int((color & 0xFF) * factor)
        return (max(0, r) << 16) | (max(0, g) << 8) | max(0, b)

    @staticmethod
    def _lighten(color: int, factor: float) -> int:
        r = min(255, int(((color >> 16) & 0xFF) * factor))
        g = min(255, int(((color >> 8) & 0xFF) * factor))
        b = min(255, int((color & 0xFF) * factor))
        return (r << 16) | (g << 8) | b

    def _lighten_hex(self, color: int, factor: float) -> str:
        return f"#{self._lighten(color, factor):06X}"
