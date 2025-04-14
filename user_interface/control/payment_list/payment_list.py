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

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt


class PaymentList(QWidget):
    def __init__(self, parent=None, width=970, height=315, location_x=0, location_y=0,
                 background_color=0x778D45, foreground_color=0xFFFFFF, *args, **kwargs):
        super(PaymentList, self).__init__(parent)
        
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
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["Payment Type", "Amount", "Currency", "Rate", "Total"])
        
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
        if self.event_func:
            selected_row = item.row()
            self.event_func(selected_row)
            
    def add_payment(self, payment_type, amount, currency, rate=1.0):
        """Add a payment to the payment list"""
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)
        
        # Convert amount and rate to float to ensure proper calculation
        try:
            amount_float = float(amount)
            rate_float = float(rate)
        except ValueError:
            amount_float = 0.0
            rate_float = 1.0
        
        # Create items with styling
        payment_type_item = QTableWidgetItem(payment_type)
        amount_item = QTableWidgetItem(str(amount_float))
        currency_item = QTableWidgetItem(currency)
        rate_item = QTableWidgetItem(str(rate_float))
        total_item = QTableWidgetItem(str(amount_float * rate_float))
        
        # Calculate total
        total = amount_float * rate_float
        
        # Set items with consistent styling
        self.table_widget.setItem(row_position, 0, payment_type_item)
        self.table_widget.setItem(row_position, 1, amount_item)
        self.table_widget.setItem(row_position, 2, currency_item)
        self.table_widget.setItem(row_position, 3, rate_item)
        self.table_widget.setItem(row_position, 4, total_item)
        
        return total
        
    def clear_payments(self):
        """Clear all payments from the list"""
        self.table_widget.setRowCount(0)
        
    def get_total_amount(self):
        """Calculate the total amount of all payments"""
        total = 0.0
        for row in range(self.table_widget.rowCount()):
            try:
                total += float(self.table_widget.item(row, 4).text())
            except (ValueError, TypeError):
                # Skip adding this value if it can't be converted to float
                continue
        return total
