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

from typing import List, Optional, Callable, Sequence

from PySide6.QtWidgets import QComboBox, QSizePolicy
from PySide6.QtGui import QFont, QIcon


class ComboBox(QComboBox):
    """
    Custom ComboBox control aligned with project conventions.

    Key features:
    - Fixed (non-editable) dropdown with owner-style theming
    - Optional item icons
    - Event wiring compatible with existing event distributor pattern
    - Control interface attributes (name, type, function1/2, event handlers)
    - Utility method to reset selection like original C# control
    """

    def __init__(self, parent=None, width: int = 240, height: int = 44,
                 location_x: int = 0, location_y: int = 0,
                 background_color: int = 0xFFFFFF, foreground_color: int = 0x000000,
                 font_size: int = 20, *args, **kwargs):
        super().__init__(parent)

        # Visuals
        self.setGeometry(location_x, location_y, width, height)
        # Enforce explicit size even when placed into layouts
        self.setFixedSize(width, height)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFont(QFont("Verdana", font_size))
        self.setEditable(False)
        self._apply_color(background_color, foreground_color)

        # Control interface properties (ICustomControl equivalent)
        self._name: str = ""
        self._type: str = "ComboBox"
        self._function1: str = ""
        self._function2: str = ""
        self._event_handler1: Optional[Callable] = None
        self._event_handler2: Optional[Callable] = None

        # Backward-compat primary event
        self.event_func: Optional[Callable] = None

        # Wire selection commit to default handler
        self.currentIndexChanged.connect(self._on_selection_changed)

    # ----- Styling -----
    def _apply_color(self, background_color: int, foreground_color: int):
        # Precompute hex colors
        bg = f"{background_color:06x}"
        fg = f"{foreground_color:06x}"
        sel = f"{((background_color + 0x222222) & 0xFFFFFF):06x}"
        hover = f"{((background_color + 0x333333) & 0xFFFFFF):06x}"
        selected = f"{((background_color + 0x444444) & 0xFFFFFF):06x}"

        # Style both the combo and its popup view
        self.setStyleSheet(
            f"""
            QComboBox {{
                background-color: #{bg};
                color: #{fg};
                border: 1px solid #{fg};
                border-radius: 4px;
                padding: 4px 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #{bg};
                color: #{fg};
                selection-background-color: #{sel};
                selection-color: #{fg};
                border: 1px solid #{fg};
                outline: 0; /* remove thin focus line */
            }}
            QComboBox QAbstractItemView::item {{
                padding: 6px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: #{hover};
                color: #{fg};
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: #{selected};
                color: #{fg};
            }}
            """
        )

    def set_color(self, background_color: int, foreground_color: int):
        self._apply_color(background_color, foreground_color)

    # ----- Data population -----
    def set_items(self, items: Sequence[str]):
        self.clear()
        if items:
            self.addItems(list(items))
            self.setCurrentIndex(0)

    def set_items_with_icons(self, items: Sequence[str], icons: Sequence[QIcon | str]):
        self.clear()
        icon_list: List[QIcon] = []
        for icon in icons:
            if isinstance(icon, QIcon):
                icon_list.append(icon)
            else:
                icon_list.append(QIcon(str(icon)))
        for idx, text in enumerate(items):
            if idx < len(icon_list):
                self.addItem(icon_list[idx], text)
            else:
                self.addItem(text)
        if self.count() > 0:
            self.setCurrentIndex(0)

    # ----- Event model parity -----
    def set_event(self, function: Callable):
        # Backward compatible single event assignment
        self.event_func = function

    def _on_selection_changed(self, index: int):
        # Primary event
        if self.event_func:
            try:
                self.event_func(index)
            except Exception:
                pass
        # Extended event model
        if self._event_handler1:
            try:
                self._event_handler1(self, index)
            except Exception:
                pass

    # ----- Utility (C# parity) -----
    def b_reset_combobox_items(self) -> bool:
        if self.count() > 0:
            self.setCurrentIndex(0)
            return True
        return False

    # ----- Properties (ICustomControl parity) -----
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, value: str):
        self._type = value

    @property
    def function1(self) -> str:
        return self._function1

    @function1.setter
    def function1(self, value: str):
        self._function1 = value

    @property
    def function2(self) -> str:
        return self._function2

    @function2.setter
    def function2(self, value: str):
        self._function2 = value

    @property
    def event_handler1(self) -> Optional[Callable]:
        return self._event_handler1

    @event_handler1.setter
    def event_handler1(self, value: Optional[Callable]):
        self._event_handler1 = value

    @property
    def event_handler2(self) -> Optional[Callable]:
        return self._event_handler2

    @event_handler2.setter
    def event_handler2(self, value: Optional[Callable]):
        self._event_handler2 = value



