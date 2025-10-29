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

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor


class DataGrid(QTableWidget):
    """
    A custom DataGrid control for displaying tabular data.
    Supports dynamic column and row management with customizable styling.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFont(QFont("Verdana", 10))
        
        # Set default properties
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Read-only by default
        
        # Set header properties
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setVisible(False)
        
        # Apply default styling
        self._apply_default_style()
    
    def _apply_default_style(self):
        """Apply default styling to the DataGrid"""
        style = """
            QTableWidget {
                background-color: #FFFFFF;
                color: #000000;
                border: 2px solid #888888;
                border-radius: 4px;
                gridline-color: #CCCCCC;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #EEEEEE;
            }
            QTableWidget::item:selected {
                background-color: #4682B4;
                color: #FFFFFF;
            }
            QTableWidget::item:hover {
                background-color: #E0E0E0;
            }
            QHeaderView::section {
                background-color: #2F4F4F;
                color: #FFFFFF;
                padding: 10px;
                border: 1px solid #1C1C1C;
                font-weight: bold;
                font-size: 11px;
            }
            QTableWidget::item:alternate {
                background-color: #F5F5F5;
            }
        """
        self.setStyleSheet(style)
    
    def set_color(self, background_color, foreground_color):
        """
        Set custom colors for the DataGrid
        
        Args:
            background_color: Background color as integer (hex)
            foreground_color: Foreground color as integer (hex)
        """
        if background_color is None:
            background_color = 0xFFFFFF
        if foreground_color is None:
            foreground_color = 0x000000
            
        style = f"""
            QTableWidget {{
                background-color: #{background_color:06X};
                color: #{foreground_color:06X};
                border: 2px solid #{self._darken_color(background_color, 0.7):06X};
                border-radius: 4px;
                gridline-color: #{self._darken_color(background_color, 0.85):06X};
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #{self._darken_color(background_color, 0.9):06X};
            }}
            QTableWidget::item:selected {{
                background-color: #4682B4;
                color: #FFFFFF;
            }}
            QTableWidget::item:hover {{
                background-color: #{self._lighten_color(background_color, 0.95):06X};
            }}
            QHeaderView::section {{
                background-color: #2F4F4F;
                color: #FFFFFF;
                padding: 10px;
                border: 1px solid #1C1C1C;
                font-weight: bold;
                font-size: 11px;
            }}
            QTableWidget::item:alternate {{
                background-color: #{self._lighten_color(background_color, 0.97):06X};
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
        r = min(255, int(((color >> 16) & 0xFF) / factor))
        g = min(255, int(((color >> 8) & 0xFF) / factor))
        b = min(255, int((color & 0xFF) / factor))
        return (r << 16) | (g << 8) | b
    
    def set_columns(self, columns):
        """
        Set the column headers for the DataGrid
        
        Args:
            columns: List of column names (strings)
        """
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)
    
    def set_data(self, data):
        """
        Set the data for the DataGrid
        
        Args:
            data: List of lists, where each inner list represents a row
                 Example: [['ID', 'Name', 'Amount'], ['1', 'John', '100.00']]
        """
        if not data:
            self.setRowCount(0)
            return
        
        self.setRowCount(len(data))
        
        for row_idx, row_data in enumerate(data):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(row_idx, col_idx, item)
    
    def add_row(self, row_data):
        """
        Add a single row to the DataGrid
        
        Args:
            row_data: List of cell values for the new row
        """
        row_position = self.rowCount()
        self.insertRow(row_position)
        
        for col_idx, cell_data in enumerate(row_data):
            item = QTableWidgetItem(str(cell_data))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setItem(row_position, col_idx, item)
    
    def clear_data(self):
        """Clear all data from the DataGrid"""
        self.setRowCount(0)
    
    def get_selected_row(self):
        """
        Get the currently selected row data
        
        Returns:
            List of cell values from the selected row, or None if no selection
        """
        selected_items = self.selectedItems()
        if not selected_items:
            return None
        
        row = selected_items[0].row()
        row_data = []
        for col in range(self.columnCount()):
            item = self.item(row, col)
            row_data.append(item.text() if item else '')
        
        return row_data
    
    def get_selected_row_index(self):
        """
        Get the index of the currently selected row
        
        Returns:
            Row index (int) or -1 if no selection
        """
        selected_items = self.selectedItems()
        if not selected_items:
            return -1
        
        return selected_items[0].row()
    
    def set_event(self, function):
        """
        Set a click/selection event handler for the DataGrid
        
        Args:
            function: Callback function to be called when a row is selected
        """
        self.itemSelectionChanged.connect(function)

