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

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView,
                             QDialog, QPushButton, QHBoxLayout, QLabel)
from PySide6.QtCore import Qt


class ItemActionPopup(QDialog):
    def __init__(self, parent=None, item_name="", background_color=0x778D45, foreground_color=0xFFFFFF):
        super(ItemActionPopup, self).__init__(parent)
        self.setWindowTitle("Item Actions")
        self.setMinimumWidth(300)
        self.setMinimumHeight(150)
        
        # Set background color
        self.setStyleSheet(f"background-color: #{background_color:06x}; color: #{foreground_color:06x};")
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Item name label
        item_label = QLabel(f"Selected item: {item_name}")
        item_label.setStyleSheet(f"font-size: 14px; color: #{foreground_color:06x};")
        layout.addWidget(item_label)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        
        # Repeat button
        self.repeat_button = QPushButton("REPEAT")
        self.repeat_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #{(background_color + 0x222222) & 0xFFFFFF:06x};
                color: #{foreground_color:06x};
                padding: 8px 16px;
                border: 1px solid #{foreground_color:06x};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #{(background_color + 0x444444) & 0xFFFFFF:06x};
            }}
        """)
        button_layout.addWidget(self.repeat_button)
        
        # Delete button
        self.delete_button = QPushButton("DELETE")
        self.delete_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #aa3333;
                color: #{foreground_color:06x};
                padding: 8px 16px;
                border: 1px solid #{foreground_color:06x};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #cc4444;
            }}
        """)
        button_layout.addWidget(self.delete_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Action result
        self.action = None
        
        # Connect signals
        self.repeat_button.clicked.connect(self.on_repeat)
        self.delete_button.clicked.connect(self.on_delete)
    
    def on_repeat(self):
        self.action = "REPEAT"
        self.accept()
    
    def on_delete(self):
        self.action = "DELETE"
        self.accept()


class SaleList(QWidget):
    def __init__(self, parent=None, width=970, height=315, location_x=0, location_y=0,
                 background_color=0x778D45, foreground_color=0xFFFFFF, *args, **kwargs):
        super(SaleList, self).__init__(parent)
        
        # Set widget properties
        self.setGeometry(location_x, location_y, width, height)
        self.setMinimumSize(width, height)
        self.parent = parent
        self.event_func = None
        
        # Apply background and foreground colors
        self.background_color = background_color
        self.foreground_color = foreground_color
        
        # Set palette for the widget
        palette = self.palette()
        palette.setColor(self.backgroundRole(), background_color)
        palette.setColor(self.foregroundRole(), foreground_color)
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        
        # Create table widget
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Product Name", "Quantity", "Unit Price", "Total"])
        
        # Set table properties
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Apply colors to table widget
        table_palette = self.table_widget.palette()
        table_palette.setColor(self.table_widget.backgroundRole(), background_color)
        table_palette.setColor(self.table_widget.foregroundRole(), foreground_color)
        self.table_widget.setPalette(table_palette)
        
        # Style the header
        header = self.table_widget.horizontalHeader()
        header_palette = header.palette()
        header_palette.setColor(header.backgroundRole(), background_color)
        header_palette.setColor(header.foregroundRole(), foreground_color)
        header.setPalette(header_palette)
        
        # Style for alternating rows
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setStyleSheet(f"""
            QTableWidget {{
                background-color: #{background_color:06x};
                color: #{foreground_color:06x};
                gridline-color: #{foreground_color:06x};
                border: 1px solid #{foreground_color:06x};
            }}
            QTableWidget::item {{
                color: #{foreground_color:06x};
            }}
            QHeaderView::section {{
                background-color: #{background_color:06x};
                color: #{foreground_color:06x};
                border: 1px solid #{foreground_color:06x};
                padding: 4px;
            }}
            QTableWidget::item:selected {{
                background-color: #{(background_color + 0x222222) & 0xFFFFFF:06x};
            }}
        """)
        
        # Connect signals
        self.table_widget.itemClicked.connect(self.on_item_clicked)
        
        # Add table to layout
        self.layout.addWidget(self.table_widget)
        
    def set_event(self, function):
        self.event_func = function
        
    def on_item_clicked(self, item):
        selected_row = item.row()
        product_name = self.table_widget.item(selected_row, 0).text()
        
        # Create and show popup dialog
        popup = ItemActionPopup(self, product_name, self.background_color, self.foreground_color)
        result = popup.exec()
        
        # If dialog was accepted and we have an event function
        if result == QDialog.Accepted and self.event_func and popup.action:
            # Pass selected row and action to event function
            self.event_func(selected_row, popup.action)
            
    def add_product(self, product_name, quantity, unit_price):
        """Add a product to the sale list"""
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)
        
        # Convert quantity and price to float to ensure proper calculation
        try:
            quantity_float = float(quantity)
            price_float = float(unit_price)
        except ValueError:
            quantity_float = 0.0
            price_float = 0.0
        
        # Calculate total
        total = quantity_float * price_float
        
        # Create items
        product_item = QTableWidgetItem(product_name)
        quantity_item = QTableWidgetItem(str(quantity_float))
        price_item = QTableWidgetItem(str(price_float))
        total_item = QTableWidgetItem(str(total))
        
        # Set items
        self.table_widget.setItem(row_position, 0, product_item)
        self.table_widget.setItem(row_position, 1, quantity_item)
        self.table_widget.setItem(row_position, 2, price_item)
        self.table_widget.setItem(row_position, 3, total_item)
        
        return total
        
    def clear_products(self):
        """Clear all products from the list"""
        self.table_widget.setRowCount(0)
        
    def get_total_amount(self):
        """Calculate the total amount of all products"""
        total = 0.0
        for row in range(self.table_widget.rowCount()):
            try:
                total += float(self.table_widget.item(row, 3).text())
            except (ValueError, TypeError):
                # Skip adding this value if it can't be converted to float
                continue
        return total
        
    def get_product_at_row(self, row):
        """Get product details at the specified row"""
        if row < 0 or row >= self.table_widget.rowCount():
            return None
            
        try:
            product_name = self.table_widget.item(row, 0).text()
            quantity = float(self.table_widget.item(row, 1).text())
            unit_price = float(self.table_widget.item(row, 2).text())
            total = float(self.table_widget.item(row, 3).text())
            
            return {
                "name": product_name,
                "quantity": quantity,
                "unit_price": unit_price,
                "total": total
            }
        except (ValueError, TypeError):
            return None
            
    def remove_product_at_row(self, row):
        """Remove product at the specified row"""
        if row >= 0 and row < self.table_widget.rowCount():
            self.table_widget.removeRow(row)
            return True
        return False
