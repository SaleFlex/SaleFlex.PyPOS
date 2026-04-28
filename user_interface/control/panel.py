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

from PySide6.QtWidgets import QScrollArea, QWidget
from PySide6.QtCore import Qt


class Panel(QScrollArea):
    """
    A scrollable panel control that can contain child controls.
    Designed for touch screens with scrollbar support.
    """
    def __init__(self, parent=None, width=800, height=600, location_x=0, location_y=0,
                 background_color=0xFFFFFF, foreground_color=0x000000):
        super().__init__(parent)
        
        # Set geometry
        self.setGeometry(location_x, location_y, width, height)
        
        # Create content widget that will hold child controls
        self.content_widget = QWidget()
        self.content_widget.setAutoFillBackground(True)
        
        # Set content widget as scroll area's widget
        self.setWidget(self.content_widget)
        self.setWidgetResizable(True)
        
        # Enable scrollbars - always show vertical scrollbar for touch screens
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Set scrollbar style for better touch interaction (30px width/height for easier touch)
        self.setStyleSheet("""
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 30px;
                border: 1px solid #c0c0c0;
            }
            QScrollBar::handle:vertical {
                background-color: #a0a0a0;
                min-height: 30px;
                border-radius: 10px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #808080;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                background-color: #f0f0f0;
                height: 30px;
                border: 1px solid #c0c0c0;
            }
            QScrollBar::handle:horizontal {
                background-color: #a0a0a0;
                min-width: 30px;
                border-radius: 10px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #808080;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
        
        # Store colors
        self._background_color = background_color
        self._foreground_color = foreground_color
        
        # Apply colors
        self.set_color(background_color, foreground_color)
        
        # Store child controls
        self._child_controls = []
    
    def set_color(self, background_color, foreground_color):
        """Set background and foreground colors for the panel."""
        self._background_color = background_color
        self._foreground_color = foreground_color
        
        # Set background color for content widget
        palette = self.content_widget.palette()
        palette.setColor(self.content_widget.backgroundRole(), 
                        self._color_int_to_qcolor(background_color))
        self.content_widget.setPalette(palette)
        
        # Set background color for scroll area
        palette = self.palette()
        palette.setColor(self.backgroundRole(), 
                        self._color_int_to_qcolor(background_color))
        self.setPalette(palette)
    
    def _color_int_to_qcolor(self, color_int):
        """Convert integer color to QColor."""
        from PySide6.QtGui import QColor
        r = (color_int >> 16) & 0xFF
        g = (color_int >> 8) & 0xFF
        b = color_int & 0xFF
        return QColor(r, g, b)
    
    def add_child_control(self, control):
        """Add a child control to the panel's content widget."""
        if control:
            control.setParent(self.content_widget)
            self._child_controls.append(control)
            # Update content widget size to accommodate all children
            self._update_content_size()
    
    def _update_content_size(self):
        """Update the content widget size to fit all child controls."""
        if not self._child_controls:
            return
        
        # Find the maximum x and y positions
        max_x = 0
        max_y = 0
        
        for control in self._child_controls:
            if hasattr(control, 'geometry'):
                geom = control.geometry()
                max_x = max(max_x, geom.x() + geom.width())
                max_y = max(max_y, geom.y() + geom.height())
        
        # Set minimum size for content widget
        self.content_widget.setMinimumSize(max_x + 10, max_y + 10)
    
    def get_content_widget(self):
        """Get the content widget that holds child controls."""
        return self.content_widget

