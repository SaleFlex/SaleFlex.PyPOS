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

from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QFont


class Button(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFont(QFont("Verdana", 20))
        
    def set_color(self, background_color, foreground_color):
        # 3D appearance with gradient and border effect
        style = f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #{background_color:06X},
                    stop:0.5 #{self._darken_color(background_color, 0.85):06X},
                    stop:1 #{self._darken_color(background_color, 0.7):06X});
                color: #{foreground_color:06X};
                border: 2px solid #{self._darken_color(background_color, 0.5):06X};
                border-radius: 6px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #{self._lighten_color(background_color, 1.15):06X},
                    stop:0.5 #{background_color:06X},
                    stop:1 #{self._darken_color(background_color, 0.75):06X});
                border: 2px solid #{self._darken_color(background_color, 0.4):06X};
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #{self._darken_color(background_color, 0.6):06X},
                    stop:0.5 #{self._darken_color(background_color, 0.75):06X},
                    stop:1 #{self._darken_color(background_color, 0.85):06X});
                border: 2px solid #{self._darken_color(background_color, 0.3):06X};
                padding-top: 7px;
                padding-left: 7px;
            }}
            QPushButton:disabled {{
                background: #CCCCCC;
                color: #888888;
                border: 2px solid #999999;
            }}
        """
        self.setStyleSheet(style)

    def _darken_color(self, color, factor):
        """Darken the color by factor"""
        r = int(((color >> 16) & 0xFF) * factor)
        g = int(((color >> 8) & 0xFF) * factor)
        b = int((color & 0xFF) * factor)
        return (r << 16) | (g << 8) | b
    
    def _lighten_color(self, color, factor):
        """Lighten the color by factor"""
        r = min(255, int(((color >> 16) & 0xFF) * factor))
        g = min(255, int(((color >> 8) & 0xFF) * factor))
        b = min(255, int((color & 0xFF) * factor))
        return (r << 16) | (g << 8) | b

    def set_event(self, function):
        self.click()

