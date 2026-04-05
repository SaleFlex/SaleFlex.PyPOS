"""
SaleFlex.PyPOS - Point of Sale Application

Copyright (c) 2025-2026 Ferhat Mousavi

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
