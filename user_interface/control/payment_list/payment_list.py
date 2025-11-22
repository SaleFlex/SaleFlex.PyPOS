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
from typing import Optional, Callable, List


class PaymentListData:
    """
    Data model class for individual payment entries in the payment list.
    
    This class encapsulates the essential information for each payment transaction,
    providing a structured way to store and access payment details.
    
    Attributes:
        row_number (int): Sequential row identifier for display ordering
        payment_type (str): Type/method of payment (cash, card, check, etc.)
        amount (float): Payment amount in the base currency
        payment_id (int): Unique identifier for the payment transaction
        currency (str): Currency code for the payment
        rate (float): Exchange rate applied to the payment
    """
    
    def __init__(self, row_number: int = 0, payment_type: str = "", amount: float = 0.0, 
                 payment_id: int = 0, currency: str = "", rate: float = 1.0):
        self.row_number = row_number
        self.payment_type = payment_type
        self.amount = amount
        self.payment_id = payment_id
        self.currency = currency  
        self.rate = rate


class PaymentList(QWidget):
    """
    Advanced payment list widget for Point of Sale (POS) applications.
    
    This widget provides a tabular display of payment transactions with comprehensive
    functionality for managing payment data. It supports multiple payment types,
    currency conversion, and interactive payment management.
    
    Key Features:
    - Two-column table display (Description, Amount)
    - Customizable styling with background and foreground colors
    - Event-driven architecture with configurable event handlers
    - Internal data storage for payment records
    - Automatic total calculation with currency conversion
    - Row selection tracking and navigation capabilities
    
    The widget maintains both visual representation (QTableWidget) and internal
    data structures (PaymentListData list) for efficient data management.
    """
    def __init__(self, parent=None, width=970, height=315, location_x=0, location_y=0,
                 background_color=0x778D45, foreground_color=0xFFFFFF, *args, **kwargs):
        """
        Initialize the PaymentList widget with customizable dimensions and styling.
        
        Args:
            parent: Parent widget (optional)
            width (int): Widget width in pixels (default: 970)
            height (int): Widget height in pixels (default: 315)
            location_x (int): X coordinate for widget positioning (default: 0)
            location_y (int): Y coordinate for widget positioning (default: 0)
            background_color (int): Background color as hexadecimal value (default: 0x778D45)
            foreground_color (int): Foreground color as hexadecimal value (default: 0xFFFFFF)
        """
        super(PaymentList, self).__init__(parent)
        
        # Core widget configuration
        self.setGeometry(location_x, location_y, width, height)
        self.setMinimumSize(width, height)
        self.parent = parent
        
        # Internal data storage for payment records
        self._payment_data_list: List[PaymentListData] = []
        self._selected_index: int = 0
        
        # Event handling system
        self.event_func = None
        self._event_handler1: Optional[Callable] = None
        self._event_handler2: Optional[Callable] = None
        
        # Control interface properties for system integration
        self._name: str = ""
        self._type: str = "PaymentList"
        self._function1: str = ""
        self._function2: str = ""
        
        # Color scheme configuration
        self.background_color = background_color
        self.foreground_color = foreground_color
        
        # Configure widget appearance using palette system
        palette = self.palette()
        palette.setColor(self.backgroundRole(), background_color)
        palette.setColor(self.foregroundRole(), foreground_color)
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        
        # Initialize the main layout container
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        
        # Create the primary data display table
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["Description", "Amount"])
        
        # Configure table behavior and interaction properties
        # Set column widths: Description 65%, Amount 35%
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        
        # Calculate column widths based on widget width
        # Account for borders and spacing (approximately 20 pixels)
        available_width = width - 20
        self.table_widget.setColumnWidth(0, int(available_width * 0.65))
        self.table_widget.setColumnWidth(1, int(available_width * 0.35))
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)  # Read-only table
        
        # Apply color theming to the table widget
        table_palette = self.table_widget.palette()
        table_palette.setColor(self.table_widget.backgroundRole(), background_color)
        table_palette.setColor(self.table_widget.foregroundRole(), foreground_color)
        self.table_widget.setPalette(table_palette)
        
        # Configure header styling to match overall theme
        header = self.table_widget.horizontalHeader()
        header_palette = header.palette()
        header_palette.setColor(header.backgroundRole(), background_color)
        header_palette.setColor(header.foregroundRole(), foreground_color)
        header.setPalette(header_palette)
        
        # Enable alternating row colors for better visual distinction
        self.table_widget.setAlternatingRowColors(True)
        
        # Calculate lighter background color for selected rows
        # Extract RGB components and make them lighter
        r = min(0xFF, ((background_color >> 16) & 0xFF) + 0x40)
        g = min(0xFF, ((background_color >> 8) & 0xFF) + 0x40)
        b = min(0xFF, (background_color & 0xFF) + 0x40)
        selected_bg_color = (r << 16) | (g << 8) | b
        
        # Apply comprehensive CSS styling for consistent appearance
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
                background-color: #{selected_bg_color:06x};
                color: #{foreground_color:06x};
            }}
        """)
        
        # Wire up event handling for user interactions
        self.table_widget.itemClicked.connect(self.on_item_clicked)
        
        # Integrate the table into the main widget layout
        self.layout.addWidget(self.table_widget)
    
    def resizeEvent(self, event):
        """
        Handle widget resize events to maintain column width ratios.
        
        When the widget is resized, this method recalculates column widths
        to maintain the 65%/35% ratio for Description/Amount columns.
        
        Args:
            event: QResizeEvent containing the new size information
        """
        super().resizeEvent(event)
        if self.table_widget:
            # Get current widget width
            current_width = self.width()
            # Account for borders and spacing (approximately 20 pixels)
            available_width = current_width - 20
            if available_width > 0:
                self.table_widget.setColumnWidth(0, int(available_width * 0.65))
                self.table_widget.setColumnWidth(1, int(available_width * 0.35))
    
    # Control Interface Properties (ICustomControl equivalent)
    @property
    def name(self) -> str:
        """Get the control name identifier."""
        return self._name
    
    @name.setter
    def name(self, value: str):
        """Set the control name identifier."""
        self._name = value
    
    @property
    def type(self) -> str:
        """Get the control type identifier."""
        return self._type
    
    @type.setter
    def type(self, value: str):
        """Set the control type identifier."""
        self._type = value
    
    @property
    def function1(self) -> str:
        """Get the first function name for event handling."""
        return self._function1
    
    @function1.setter
    def function1(self, value: str):
        """Set the first function name for event handling."""
        self._function1 = value
    
    @property
    def function2(self) -> str:
        """Get the second function name for event handling."""
        return self._function2
    
    @function2.setter
    def function2(self, value: str):
        """Set the second function name for event handling."""
        self._function2 = value
    
    @property
    def event_handler1(self) -> Optional[Callable]:
        """Get the first event handler callback."""
        return self._event_handler1
    
    @event_handler1.setter
    def event_handler1(self, value: Optional[Callable]):
        """Set the first event handler callback."""
        self._event_handler1 = value
    
    @property
    def event_handler2(self) -> Optional[Callable]:
        """Get the second event handler callback."""
        return self._event_handler2
    
    @event_handler2.setter
    def event_handler2(self, value: Optional[Callable]):
        """Set the second event handler callback."""
        self._event_handler2 = value

    @property
    def selected_index(self) -> int:
        """Get the currently selected row index."""
        return self._selected_index
    
    @selected_index.setter
    def selected_index(self, value: int):
        """Set the currently selected row index with bounds checking."""
        if 0 <= value < self.table_widget.rowCount():
            self._selected_index = value
            # Update visual selection in the table
            self.table_widget.selectRow(value)
        
    def set_event(self, function: Callable):
        """
        Set the primary event handler function for backward compatibility.
        
        This method maintains compatibility with existing code while providing
        a simple interface for event handling.
        
        Args:
            function: Callback function to be invoked on item selection
        """
        self.event_func = function
        
    def on_event1(self, sender, event_args):
        """
        Handle the first event using the configured event handler.
        
        This method provides a standardized event handling interface that can be
        connected to various UI interactions or external triggers.
        
        Args:
            sender: Object that triggered the event
            event_args: Event-specific arguments and data
        """
        if self._event_handler1:
            self._event_handler1(sender, event_args)
    
    def on_event2(self, sender, event_args):
        """
        Handle the second event using the configured event handler.
        
        This method provides a secondary event handling channel for complex
        interaction scenarios that require multiple event types.
        
        Args:
            sender: Object that triggered the event
            event_args: Event-specific arguments and data
        """
        if self._event_handler2:
            self._event_handler2(sender, event_args)

    def on_item_clicked(self, item):
        """
        Handle table item click events and update selection state.
        
        When a user clicks on any item in the payment table, this method:
        1. Updates the internal selected index
        2. Triggers the primary event handler if configured
        3. Maintains selection synchronization with the UI
        
        Args:
            item: QTableWidgetItem that was clicked by the user
        """
        if self.event_func:
            selected_row = item.row()
            self._selected_index = selected_row
            self.event_func(selected_row)
    
    def navigate_up(self):
        """
        Navigate to the previous row in the payment list.
        
        This method provides keyboard-like navigation functionality, allowing
        users to move selection upward through the payment entries. The selection
        wraps to ensure it stays within valid bounds.
        """
        if self.table_widget.rowCount() > 0 and self._selected_index > 0:
            self._selected_index -= 1
            self.table_widget.selectRow(self._selected_index)
            self.table_widget.scrollToItem(self.table_widget.item(self._selected_index, 0))
    
    def navigate_down(self):
        """
        Navigate to the next row in the payment list.
        
        This method provides keyboard-like navigation functionality, allowing
        users to move selection downward through the payment entries. The selection
        is bounded to prevent out-of-range access.
        """
        if (self.table_widget.rowCount() > 0 and 
            self._selected_index < self.table_widget.rowCount() - 1):
            self._selected_index += 1
            self.table_widget.selectRow(self._selected_index)
            self.table_widget.scrollToItem(self.table_widget.item(self._selected_index, 0))
    
    def add_payment(self, payment_type: str, amount: float, currency: str = "", 
                   rate: float = 1.0, payment_id: int = 0) -> float:
        """
        Add a new payment entry to the payment list.
        
        This method creates both visual table entries and internal data records
        for comprehensive payment tracking. It automatically calculates totals
        based on amount and exchange rate.
        
        Args:
            payment_type (str): Type/method of payment (e.g., "Cash", "Card")
            amount (float): Payment amount in base currency
            currency (str): Currency code (optional, defaults to empty string)
            rate (float): Exchange rate for currency conversion (default: 1.0)
            payment_id (int): Unique identifier for the payment (default: 0)
            
        Returns:
            float: Calculated total amount after currency conversion
        """
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)
        
        # Validate and convert input parameters to ensure data integrity
        try:
            amount_float = float(amount)
            rate_float = float(rate)
        except ValueError:
            amount_float = 0.0
            rate_float = 1.0
        
        # Calculate the final total amount including currency conversion
        total = amount_float * rate_float
        
        # Create internal data record for comprehensive tracking
        payment_data = PaymentListData(
            row_number=row_position + 1,
            payment_type=payment_type,
            amount=amount_float,
            payment_id=payment_id,
            currency=currency,
            rate=rate_float
        )
        self._payment_data_list.append(payment_data)
        
        # Create description: payment_type (currency)
        if currency:
            description = f"{payment_type} ({currency})"
        else:
            description = payment_type
        
        # Create table display items with proper formatting
        description_item = QTableWidgetItem(description)
        amount_item = QTableWidgetItem(f"{total:.2f}")
        
        # Populate the table row with formatted data
        self.table_widget.setItem(row_position, 0, description_item)
        self.table_widget.setItem(row_position, 1, amount_item)
        
        # Auto-select the newly added row and ensure it's visible
        self.table_widget.selectRow(row_position)
        self.table_widget.scrollToItem(self.table_widget.item(row_position, 0))
        self._selected_index = row_position
        
        return total
        
    def clear_payments(self) -> bool:
        """
        Remove all payment entries from both the display and internal storage.
        
        This method performs a complete cleanup of the payment list, clearing
        both the visual table representation and the internal data structures.
        It also resets the selection index to a safe state.
        
        Returns:
            bool: True if the operation completed successfully
        """
        # Clear internal data storage
        while len(self._payment_data_list) > 0:
            self._payment_data_list.pop()
        
        # Clear visual table display
        while self.table_widget.rowCount() > 0:
            self.table_widget.removeRow(0)
        
        # Reset selection state
        self._selected_index = 0
        
        return True
        
    def get_total_amount(self) -> float:
        """
        Calculate the total amount of all payments including currency conversions.
        
        This method sums up all payment totals from the internal data storage,
        providing an accurate total that accounts for exchange rates and
        currency conversions. It includes error handling for data integrity.
        
        Returns:
            float: Total amount of all payments in the base currency
        """
        total = 0.0
        
        # Calculate total from internal data for accuracy
        for payment_data in self._payment_data_list:
            try:
                total += payment_data.amount * payment_data.rate
            except (ValueError, TypeError, AttributeError):
                # Skip entries with invalid data, continue processing others
                continue
                
        return total
    
    def get_payment_data(self, index: int) -> Optional[PaymentListData]:
        """
        Retrieve payment data for a specific row index.
        
        This method provides access to the complete payment information
        stored internally, allowing external systems to retrieve detailed
        payment data beyond what's visible in the table.
        
        Args:
            index (int): Row index of the desired payment data
            
        Returns:
            PaymentListData: Payment data object, or None if index is invalid
        """
        if 0 <= index < len(self._payment_data_list):
            return self._payment_data_list[index]
        return None
    
    def get_payment_count(self) -> int:
        """
        Get the total number of payment entries.
        
        Returns:
            int: Number of payment entries currently stored
        """
        return len(self._payment_data_list)
    
    def get_custom_customer_form(self):
        """
        Retrieve the parent customer form for integration purposes.
        
        This method attempts to navigate the widget hierarchy to find
        the parent customer form, enabling integration with larger
        application workflows.
        
        Returns:
            Parent customer form object if found, None otherwise
        """
        try:
            # Navigate up the widget hierarchy to find the parent form
            parent_widget = self.parent
            while parent_widget is not None:
                # Look for specific form types or naming patterns
                if hasattr(parent_widget, 'add_payment') or hasattr(parent_widget, 'customer_form'):
                    return parent_widget
                parent_widget = parent_widget.parent if hasattr(parent_widget, 'parent') else None
        except Exception:
            # Return None if navigation fails to prevent crashes
            pass
        
        return None
