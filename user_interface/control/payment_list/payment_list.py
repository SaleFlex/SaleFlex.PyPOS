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
    def __init__(self, source=None, width=970, height=315, x_pos=0, y_pos=0, parent=None):
        super(PaymentList, self).__init__(parent)
        
        # Set widget properties
        self.setGeometry(x_pos, y_pos, width, height)
        self.setMinimumSize(width, height)
        self.source = source
        self.event_func = None
        
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
        
        # Add payment details to table
        self.table_widget.setItem(row_position, 0, QTableWidgetItem(payment_type))
        self.table_widget.setItem(row_position, 1, QTableWidgetItem(str(amount)))
        self.table_widget.setItem(row_position, 2, QTableWidgetItem(currency))
        self.table_widget.setItem(row_position, 3, QTableWidgetItem(str(rate)))
        
        # Calculate total
        total = amount * rate
        self.table_widget.setItem(row_position, 4, QTableWidgetItem(str(total)))
        
        return total
        
    def clear_payments(self):
        """Clear all payments from the list"""
        self.table_widget.setRowCount(0)
        
    def get_total_amount(self):
        """Calculate the total amount of all payments"""
        total = 0.0
        for row in range(self.table_widget.rowCount()):
            total += float(self.table_widget.item(row, 4).text())
        return total
