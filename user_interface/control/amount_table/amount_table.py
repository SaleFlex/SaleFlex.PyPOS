"""
SaleFlex.PyPOS - Point of Sale Application

Copyright (c) 2025 Ferhat Mousavi

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

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from decimal import Decimal, InvalidOperation
from typing import Optional, Callable


class AmountTable(QWidget):
    """
    Custom widget that displays various transaction amounts in a table format.
    Uses QTableWidget to show amounts in rows with labels and values.
    Similar to the C# CustomAmountsTable control.
    """
    
    # Table row indices for easy access
    SALES_AMOUNT_ROW = 0
    DISCOUNT_AMOUNT_ROW = 1
    NET_AMOUNT_ROW = 2
    PAYMENT_AMOUNT_ROW = 3
    BALANCE_AMOUNT_ROW = 4
    
    def __init__(self, parent=None, width=300, height=213, location_x=0, location_y=0,
                 background_color=0x778D45, foreground_color=0xFFFFFF, *args, **kwargs):
        """
        Initialize the AmountTable control with specified parameters.
        
        Args:
            parent: Parent widget
            width: Widget width in pixels
            height: Widget height in pixels
            location_x: X coordinate position
            location_y: Y coordinate position
            background_color: Background color as hex integer
            foreground_color: Foreground color as hex integer
        """
        super().__init__(parent)
        
        # Set widget properties
        self.setGeometry(location_x, location_y, width, height)
        self.setFixedSize(width, height)  # Make size fixed
        self.parent = parent
        self.event_func = None
        
        # Initialize member variables
        self._function1_name = ""
        self._name = ""
        self._type = ""
        self._function1 = ""
        self._function2 = ""
        self._event_handler1: Optional[Callable] = None
        self._event_handler2: Optional[Callable] = None
        
        # Store color values
        self.background_color = background_color
        self.foreground_color = foreground_color
        
        # Initialize the table
        self._init_table()
        
        # Apply colors to the table
        self._apply_colors()
        
    def _init_table(self):
        """Initialize the table widget and setup layout."""
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        
        # Create table widget
        self.table_widget = QTableWidget(5, 2, self)  # 5 rows, 2 columns
        
        # Set column headers
        self.table_widget.setHorizontalHeaderLabels(["Description", "Amount"])
        
        # Set row data
        self._setup_table_rows()
        
        # Configure table appearance
        self._configure_table_appearance()
        
        # Add table to layout
        self.layout.addWidget(self.table_widget)
    
    def _setup_table_rows(self):
        """Setup the table rows with labels and initial values."""
        # Row labels and initial values
        rows_data = [
            ("Sales Amount:", "0.00"),
            ("Discount Amount:", "0.00"),
            ("Net Amount:", "0.00"),
            ("Payment Amount:", "0.00"),
            ("Balance Amount:", "0.00")
        ]
        
        # Set default font
        font = QFont("Verdana", 10)
        
        # Set bold font for Balance Amount row
        bold_font = QFont("Verdana", 12, QFont.Bold)
        
        for row, (label, value) in enumerate(rows_data):
            # Use bold font for Balance Amount row
            current_font = bold_font if row == self.BALANCE_AMOUNT_ROW else font
            
            # Create label item (left column)
            label_item = QTableWidgetItem(label)
            label_item.setFont(current_font)
            label_item.setFlags(Qt.ItemIsEnabled)  # Make it read-only
            self.table_widget.setItem(row, 0, label_item)
            
            # Create value item (right column)
            value_item = QTableWidgetItem(value)
            value_item.setFont(current_font)
            value_item.setTextAlignment(Qt.AlignCenter)
            value_item.setFlags(Qt.ItemIsEnabled)  # Make it read-only
            self.table_widget.setItem(row, 1, value_item)
    
    def _configure_table_appearance(self):
        """Configure the table's visual appearance."""
        # Hide row headers (numbers)
        self.table_widget.verticalHeader().setVisible(False)
        
        # Set column widths
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Description column
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Amount column stretches
        
        # Make table completely non-interactive
        self.table_widget.setSelectionMode(QTableWidget.NoSelection)
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_widget.setFocusPolicy(Qt.NoFocus)  # No focus
        self.table_widget.setEnabled(True)  # Keep enabled for display but non-clickable
        self.table_widget.setAlternatingRowColors(True)
        
        # Disable sorting
        self.table_widget.setSortingEnabled(False)
        
        # Disable context menu
        self.table_widget.setContextMenuPolicy(Qt.NoContextMenu)
        
        # Set row heights
        for row in range(5):
            self.table_widget.setRowHeight(row, 35)
    
    def _apply_colors(self):
        """Apply background and foreground colors to the table."""
        # Apply colors to the widget itself
        palette = self.palette()
        palette.setColor(self.backgroundRole(), self.background_color)
        palette.setColor(self.foregroundRole(), self.foreground_color)
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        
        # Style the table with colors
        self.table_widget.setStyleSheet(f"""
            QTableWidget {{
                gridline-color: #cccccc;
                background-color: #{self.background_color:06x};
                color: #{self.foreground_color:06x};
                border: 1px solid #cccccc;
                selection-background-color: transparent;
                selection-color: #{self.foreground_color:06x};
            }}
            QTableWidget::item {{
                padding: 5px;
                border-bottom: 1px solid #eeeeee;
                background-color: #{self.background_color:06x};
                color: #{self.foreground_color:06x};
            }}
            QTableWidget::item:hover {{
                background-color: #{self.background_color:06x};
                color: #{self.foreground_color:06x};
            }}
            QHeaderView::section {{
                background-color: #{self.background_color - 0x111111:06x};
                color: #{self.foreground_color:06x};
                padding: 5px;
                border: 1px solid #cccccc;
                font-weight: bold;
            }}
        """)
    

    
    def _set_amount_value(self, row: int, value: Decimal):
        """
        Set the amount value for a specific row.
        
        Args:
            row: Row index
            value: Amount value to set
        """
        formatted_value = f"{value:,.2f}"
        item = self.table_widget.item(row, 1)
        if item:
            item.setText(formatted_value)
            
            # Apply bold font for Balance Amount row
            if row == self.BALANCE_AMOUNT_ROW:
                bold_font = QFont("Verdana", 12, QFont.Bold)
                item.setFont(bold_font)
    
    def _get_amount_value(self, row: int) -> Decimal:
        """
        Get the amount value from a specific row.
        
        Args:
            row: Row index
            
        Returns:
            Decimal: The amount value, or 0 if conversion fails
        """
        item = self.table_widget.item(row, 1)
        if item:
            try:
                return Decimal(item.text().replace(',', ''))
            except (InvalidOperation, ValueError):
                pass
        return Decimal('0')
    
    # Properties for accessing and setting amounts
    @property
    def receipt_total_price(self) -> Decimal:
        """
        Get the total receipt price.
        
        Returns:
            Decimal: The total price, or 0 if conversion fails
        """
        return self._get_amount_value(self.SALES_AMOUNT_ROW)
    
    @receipt_total_price.setter
    def receipt_total_price(self, value: Decimal):
        """
        Set the total receipt price and update related fields.
        
        Args:
            value: The total price to set
        """
        self._set_amount_value(self.SALES_AMOUNT_ROW, value)
        self._set_amount_value(self.NET_AMOUNT_ROW, value)  # Net amount equals sales amount
        
        # Update balance (total - payment)
        payment_amount = self._get_amount_value(self.PAYMENT_AMOUNT_ROW)
        balance = value - payment_amount
        self._set_amount_value(self.BALANCE_AMOUNT_ROW, balance)
        
        # Update custom customer form if available
        custom_form = self._get_custom_customer_form()
        if custom_form and hasattr(custom_form, 'receipt_total_price'):
            custom_form.receipt_total_price = value
    
    @property
    def receipt_total_payment(self) -> Decimal:
        """
        Get the total payment amount.
        
        Returns:
            Decimal: The total payment, or 0 if conversion fails
        """
        return self._get_amount_value(self.PAYMENT_AMOUNT_ROW)
    
    @receipt_total_payment.setter
    def receipt_total_payment(self, value: Decimal):
        """
        Set the total payment amount and update balance.
        
        Args:
            value: The payment amount to set
        """
        self._set_amount_value(self.PAYMENT_AMOUNT_ROW, value)
        
        # Update balance (total - payment)
        total_amount = self._get_amount_value(self.NET_AMOUNT_ROW)
        balance = total_amount - value
        self._set_amount_value(self.BALANCE_AMOUNT_ROW, balance)
        
        # Update custom customer form if available
        custom_form = self._get_custom_customer_form()
        if custom_form and hasattr(custom_form, 'receipt_total_payment'):
            custom_form.receipt_total_payment = value
    
    @property
    def discount_total_amount(self) -> Decimal:
        """
        Get the total discount amount.
        
        Returns:
            Decimal: The discount amount, or 0 if conversion fails
        """
        return self._get_amount_value(self.DISCOUNT_AMOUNT_ROW)
    
    @discount_total_amount.setter
    def discount_total_amount(self, value: Decimal):
        """
        Set the total discount amount.
        
        Args:
            value: The discount amount to set
        """
        self._set_amount_value(self.DISCOUNT_AMOUNT_ROW, value)
        
        # Update custom customer form if available
        custom_form = self._get_custom_customer_form()
        if custom_form and hasattr(custom_form, 'discount_total_amount'):
            custom_form.discount_total_amount = value
    
    @property
    def surcharge_total_amount(self) -> Decimal:
        """
        Get the total surcharge amount.
        Currently returns 0 as surcharge is not implemented.
        
        Returns:
            Decimal: Always returns 0
        """
        return Decimal('0')
    
    @surcharge_total_amount.setter
    def surcharge_total_amount(self, value: Decimal):
        """
        Set the total surcharge amount.
        Currently not implemented, but updates custom form if available.
        
        Args:
            value: The surcharge amount to set
        """
        # Surcharge functionality is not implemented in the original C# code
        # Update custom customer form if available
        custom_form = self._get_custom_customer_form()
        if custom_form and hasattr(custom_form, 'surcharge_total_amount'):
            custom_form.surcharge_total_amount = value
    
    # Control interface properties
    @property
    def name(self) -> str:
        """Get the control name."""
        return self._name
    
    @name.setter
    def name(self, value: str):
        """Set the control name."""
        self._name = value
    
    @property
    def type(self) -> str:
        """Get the control type."""
        return self._type
    
    @type.setter
    def type(self, value: str):
        """Set the control type."""
        self._type = value
    
    @property
    def function1(self) -> str:
        """Get the first function name."""
        return self._function1
    
    @function1.setter
    def function1(self, value: str):
        """Set the first function name."""
        self._function1 = value
    
    @property
    def function2(self) -> str:
        """Get the second function name."""
        return self._function2
    
    @function2.setter
    def function2(self, value: str):
        """Set the second function name."""
        self._function2 = value
    
    @property
    def event_handler1(self) -> Optional[Callable]:
        """Get the first event handler."""
        return self._event_handler1
    
    @event_handler1.setter
    def event_handler1(self, value: Optional[Callable]):
        """Set the first event handler."""
        self._event_handler1 = value
    
    @property
    def event_handler2(self) -> Optional[Callable]:
        """Get the second event handler."""
        return self._event_handler2
    
    @event_handler2.setter
    def event_handler2(self, value: Optional[Callable]):
        """Set the second event handler."""
        self._event_handler2 = value
    
    def on_event1(self, sender, event_args):
        """
        Handle the first event.
        
        Args:
            sender: Event sender object
            event_args: Event arguments
        """
        if self._event_handler1:
            self._event_handler1(sender, event_args)
    
    def on_event2(self, sender, event_args):
        """
        Handle the second event.
        
        Args:
            sender: Event sender object
            event_args: Event arguments
        """
        if self._event_handler2:
            self._event_handler2(sender, event_args)
    
    def _get_custom_customer_form(self):
        """
        Get the custom customer form from the parent hierarchy.
        
        Returns:
            Custom customer form if found, None otherwise
        """
        try:
            # Traverse up the parent hierarchy to find the custom form
            parent = self.parent()
            while parent:
                if hasattr(parent, 'custom_customer_form'):
                    return parent.custom_customer_form
                parent = parent.parent()
        except Exception:
            # Handle any exceptions during parent traversal
            pass
        
        return None
    
    def clear(self) -> bool:
        """
        Clear all amount values and reset to zero.
        
        Returns:
            bool: True if clearing was successful
        """
        self.receipt_total_price = Decimal('0')
        self.receipt_total_payment = Decimal('0')
        self.discount_total_amount = Decimal('0')
        self.surcharge_total_amount = Decimal('0')
        
        # Clear custom customer form if available
        custom_form = self._get_custom_customer_form()
        if custom_form and hasattr(custom_form, 'clear'):
            custom_form.clear()
        
        return True
    
    def update_and_refresh_form_controls(self):
        """Update and refresh all child controls."""
        self.table_widget.update()
        for child in self.findChildren(QWidget):
            child.update()
    
    def set_color(self, background_color: int, foreground_color: int):
        """
        Set the background and foreground colors of the control.
        
        Args:
            background_color: Background color as integer
            foreground_color: Foreground color as integer
        """
        self.background_color = background_color
        self.foreground_color = foreground_color
        self._apply_colors()
    
    def set_event(self, function: Callable):
        """
        Set the main event function for the control.
        
        Args:
            function: Function to be called on events
        """
        self._event_handler1 = function 