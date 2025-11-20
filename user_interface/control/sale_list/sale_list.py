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
from PySide6.QtGui import QFont, QColor
from typing import List, Optional, Dict, Any


class SalesData:
    """
    Data model representing a single item in the sales list.
    
    This class stores all information about a transaction row including
    product details, pricing, quantities, and transaction metadata.
    """
    def __init__(self):
        # Row identification and ordering
        self.row_number: int = 0                    # Sequential row number in the display
        self.reference_id: int = 0                  # Database reference ID for this transaction
        
        # Transaction categorization
        self.transaction_type: str = ""             # Type: "PLU", "DEPARTMENT", "SUBTOTAL", "TOTAL", "DISCOUNT"
        self.transaction: str = ""                  # Display name: "Sale", "Return", "Subtotal", etc.
        
        # Product information
        self.name_of_product: str = ""              # Product name displayed to user
        self.barcode: str = ""                      # Product barcode if available
        self.plu_no: str = ""                       # Product lookup number
        self.department_no: int = 0                 # Department classification number
        self.id: int = 0                            # Internal product ID
        
        # Quantity and pricing
        self.quantity: float = 0.0                  # Actual quantity (numeric value)
        self.unit_quantity: str = ""                # Formatted quantity for display
        self.unit: int = 1                          # Unit type (piece, weight, etc.)
        self.price: float = 0.0                     # Unit price
        self.total_amount: float = 0.0              # Total price (quantity × unit price)
        
        # Transaction state and discounts
        self.is_canceled: bool = False              # Whether this row has been canceled/deleted
        self.discount_surcharge_datamodel_list: List[Any] = None  # Associated discounts and surcharges
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the SalesData object to a dictionary format.
        
        Returns:
            Dict containing all sales data properties as key-value pairs.
            Useful for serialization, debugging, and data export.
        """
        return {
            'row_number': self.row_number,
            'reference_id': self.reference_id,
            'transaction_type': self.transaction_type,
            'transaction': self.transaction,
            'name_of_product': self.name_of_product,
            'quantity': self.quantity,
            'unit': self.unit,
            'price': self.price,
            'total_amount': self.total_amount,
            'barcode': self.barcode,
            'department_no': self.department_no,
            'plu_no': self.plu_no,
            'id': self.id,
            'unit_quantity': self.unit_quantity,
            'is_canceled': self.is_canceled
        }


class ItemActionPopup(QDialog):
    """
    Modal dialog that appears when user clicks on a sales list item.
    
    Provides three action buttons:
    - REPEAT: Increase quantity of selected item by 1
    - CANCEL: Close dialog without taking any action
    - DELETE: Remove or cancel the selected item
    """
    def __init__(self, parent=None, item_name="", background_color=0x778D45, foreground_color=0xFFFFFF):
        """
        Initialize the action popup dialog.
        
        Args:
            parent: Parent widget (usually the SaleList)
            item_name: Name of the selected item to display
            background_color: Background color in hex format
            foreground_color: Text/foreground color in hex format
        """
        super(ItemActionPopup, self).__init__(parent)
        self.setWindowTitle("Item Actions")
        self.setMinimumWidth(300)
        self.setMinimumHeight(150)
        
        # Apply color theme to the dialog
        self.setStyleSheet(f"background-color: #{background_color:06x}; color: #{foreground_color:06x};")
        
        # Create main vertical layout for the dialog
        layout = QVBoxLayout(self)
        
        # Display the selected item name at the top
        item_label = QLabel(f"Selected item: {item_name}")
        item_label.setStyleSheet(f"font-size: 14px; color: #{foreground_color:06x};")
        layout.addWidget(item_label)
        
        # Create horizontal layout for action buttons
        button_layout = QHBoxLayout()
        
        # Create REPEAT button - increases item quantity by 1
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
        
        # Create CANCEL button - closes dialog without action
        self.cancel_button = QPushButton("CANCEL")
        self.cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #cc6600;
                color: #{foreground_color:06x};
                padding: 8px 16px;
                border: 1px solid #{foreground_color:06x};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #dd7711;
            }}
        """)
        button_layout.addWidget(self.cancel_button)
        
        # Create DELETE button - removes or cancels the item
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
        
        # Add button layout to main layout and finalize dialog setup
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Store the user's selected action (initially None)
        self.action = None
        
        # Connect button click events to their respective handlers
        self.repeat_button.clicked.connect(self.on_repeat)
        self.cancel_button.clicked.connect(self.on_cancel)
        self.delete_button.clicked.connect(self.on_delete)
    
    def on_repeat(self):
        """Handle REPEAT button click - sets action and closes dialog."""
        self.action = "REPEAT"
        self.accept()
    
    def on_cancel(self):
        """Handle CANCEL button click - sets action and closes dialog."""
        self.action = "CANCEL"
        self.accept()
    
    def on_delete(self):
        """Handle DELETE button click - sets action and closes dialog."""
        self.action = "DELETE"
        self.accept()


class SaleList(QWidget):
    """
    Advanced sales list widget for Point of Sale (POS) applications.
    
    Features:
    - Multi-column table display with products, quantities, prices, and totals
    - Interactive popup for item actions (repeat, cancel, delete)
    - Support for different transaction types (products, subtotals, discounts)
    - Automatic subtotal calculations and updates
    - Row cancellation with visual strikethrough effects
    - Keyboard navigation and selection tracking
    """
    def __init__(self, parent=None, width=970, height=315, location_x=0, location_y=0,
                 background_color=0x778D45, foreground_color=0xFFFFFF, *args, **kwargs):
        """
        Initialize the SaleList widget.
        
        Args:
            parent: Parent widget
            width: Widget width in pixels
            height: Widget height in pixels
            location_x: X position for widget placement
            location_y: Y position for widget placement
            background_color: Background color in hex format (default: 0x778D45)
            foreground_color: Text/foreground color in hex format (default: 0xFFFFFF)
        """
        super(SaleList, self).__init__(parent)
        
        # Configure widget size and position
        self.setGeometry(location_x, location_y, width, height)
        self.setMinimumSize(width, height)
        self.parent = parent
        
        # Event handling callback function (set by external code)
        self.event_func = None
        
        # Core data storage for all sales list items
        self.custom_sales_data_list: List[SalesData] = []
        
        # Track currently selected row index for navigation
        self.selected_index: int = 0
        
        # Store color scheme for consistent theming
        self.background_color = background_color
        self.foreground_color = foreground_color
        
        # Apply color palette to the widget
        palette = self.palette()
        palette.setColor(self.backgroundRole(), background_color)
        palette.setColor(self.foregroundRole(), foreground_color)
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        
        # Create main layout container
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for full widget usage
        self.setLayout(self.layout)
        
        # Create the main table widget with comprehensive column structure
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(9)
        self.table_widget.setHorizontalHeaderLabels([
            "Row #",        # Sequential row number
            "Ref ID",       # Database reference ID (hidden from display)
            "Type",         # Transaction type (PLU, DEPARTMENT, etc.)
            "Transaction",  # Transaction description (Sale, Return, etc.)
            "Product Name", # Product or item name
            "Unit Qty",     # Formatted quantity display
            "Unit",         # Unit type
            "Price",        # Unit price
            "Total"         # Total amount (quantity × price)
        ])
        
        # Define column indices as constants for maintainable code
        self.COL_ROW_NUMBER = 0        # Row numbering column
        self.COL_REFERENCE_ID = 1      # Database reference column
        self.COL_TRANSACTION_TYPE = 2  # Transaction type column
        self.COL_TRANSACTION = 3       # Transaction name column
        self.COL_NAME_OF_PRODUCT = 4   # Product name column
        self.COL_UNIT_QUANTITY = 5     # Quantity display column
        self.COL_UNIT = 6              # Unit type column
        self.COL_PRICE = 7             # Unit price column
        self.COL_TOTAL_AMOUNT = 8      # Total amount column
        
        # Hide Ref ID column from display (kept in data for background operations)
        self.table_widget.setColumnHidden(self.COL_REFERENCE_ID, True)
        
        # Configure table behavior and appearance
        header = self.table_widget.horizontalHeader()
        
        # Set fixed widths for small columns (must be set before resize mode)
        self.table_widget.setColumnWidth(self.COL_ROW_NUMBER, 50)        # Row # - small
        self.table_widget.setColumnWidth(self.COL_TRANSACTION_TYPE, 60)   # Type - small
        self.table_widget.setColumnWidth(self.COL_TRANSACTION, 80)       # Transaction - medium-small
        self.table_widget.setColumnWidth(self.COL_UNIT_QUANTITY, 70)     # Unit Qty - medium-small
        self.table_widget.setColumnWidth(self.COL_UNIT, 50)               # Unit - small
        self.table_widget.setColumnWidth(self.COL_PRICE, 90)              # Price - medium
        self.table_widget.setColumnWidth(self.COL_TOTAL_AMOUNT, 90)       # Total - medium
        
        # Set resize modes: Fixed for small/medium columns
        header.setSectionResizeMode(self.COL_ROW_NUMBER, QHeaderView.Fixed)
        header.setSectionResizeMode(self.COL_TRANSACTION_TYPE, QHeaderView.Fixed)
        header.setSectionResizeMode(self.COL_TRANSACTION, QHeaderView.Fixed)
        header.setSectionResizeMode(self.COL_UNIT_QUANTITY, QHeaderView.Fixed)
        header.setSectionResizeMode(self.COL_UNIT, QHeaderView.Fixed)
        header.setSectionResizeMode(self.COL_PRICE, QHeaderView.Fixed)
        header.setSectionResizeMode(self.COL_TOTAL_AMOUNT, QHeaderView.Fixed)
        
        # Set Product Name to stretch (takes all remaining space - largest column)
        header.setSectionResizeMode(self.COL_NAME_OF_PRODUCT, QHeaderView.Stretch)
        
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)               # Select entire rows, not individual cells
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)               # Prevent direct cell editing
        
        # Apply color theme to the table widget
        table_palette = self.table_widget.palette()
        table_palette.setColor(self.table_widget.backgroundRole(), background_color)
        table_palette.setColor(self.table_widget.foregroundRole(), foreground_color)
        self.table_widget.setPalette(table_palette)
        
        # Style the table header with matching colors
        header = self.table_widget.horizontalHeader()
        header_palette = header.palette()
        header_palette.setColor(header.backgroundRole(), background_color)
        header_palette.setColor(header.foregroundRole(), foreground_color)
        header.setPalette(header_palette)
        
        # Calculate lightened color for selected row (for better readability)
        def lighten_color(color):
            """Lighten color for selected row"""
            r = (color >> 16) & 0xFF
            g = (color >> 8) & 0xFF
            b = color & 0xFF
            r = min(255, r + 60)
            g = min(255, g + 60)
            b = min(255, b + 60)
            return (r << 16) | (g << 8) | b
        
        selected_bg_color = lighten_color(background_color)
        
        # Enable alternating row colors and apply comprehensive styling
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
                background-color: #{selected_bg_color:06x};
                color: #{foreground_color:06x};
            }}
        """)
        
        # Connect table click events to the item action handler
        self.table_widget.itemClicked.connect(self.on_item_clicked)
        
        # Add the configured table to the main layout
        self.layout.addWidget(self.table_widget)
        
    def set_event(self, function):
        """
        Set the external event handler function.
        
        Args:
            function: Callback function that will be called when popup actions occur.
                     Function signature should be: func(row_index, action_string)
        """
        self.event_func = function
        
    def on_item_clicked(self, item):
        """
        Handle table item click events by showing the action popup dialog.
        
        When a user clicks on any item in the table, this method:
        1. Updates the selected row index
        2. Extracts the product name for display
        3. Shows the ItemActionPopup dialog
        4. Processes the user's selected action (REPEAT, CANCEL, DELETE)
        5. Calls external event handler if configured
        
        Args:
            item: QTableWidgetItem that was clicked
        """
        selected_row = item.row()
        self.selected_index = selected_row  # Track the currently selected row
        
        # Extract product name from the clicked row for popup display
        product_name_item = self.table_widget.item(selected_row, self.COL_NAME_OF_PRODUCT)
        product_name = product_name_item.text() if product_name_item else "Unknown Product"
        
        # Create and display the action selection popup
        popup = ItemActionPopup(self, product_name, self.background_color, self.foreground_color)
        result = popup.exec()
        
        # Notify external event handler if one is registered and an action was selected
        if result == QDialog.Accepted and self.event_func and popup.action:
            self.event_func(selected_row, popup.action)
            
        # Process the selected action internally
        if result == QDialog.Accepted and popup.action:
            if popup.action == "DELETE":
                self.delete_transaction(selected_row)
            elif popup.action == "CANCEL":
                # Cancel button just closes the popup - no further action required
                pass
            elif popup.action == "REPEAT":
                self.repeat_transaction(selected_row)
            
    def add_product(self, product_name, quantity, unit_price, **kwargs):
        """
        Add a product to the sales list (simplified interface for backward compatibility).
        
        This is a convenience method that creates a SalesData object with default values
        and delegates to add_sale_with_data() for the actual insertion.
        
        Args:
            product_name: Display name of the product
            quantity: Quantity being purchased (will be converted to float)
            unit_price: Price per unit (will be converted to float)
            **kwargs: Optional parameters including:
                - reference_id: Database reference ID
                - barcode: Product barcode
                - plu_no: Product lookup number
                - department_no: Department classification
                - id: Internal product ID
        
        Returns:
            bool: True if product was added successfully, False otherwise
        """
        # Create new sales data object with provided information
        custom_sales_data = SalesData()
        
        # Set core product information
        custom_sales_data.name_of_product = product_name
        custom_sales_data.quantity = float(quantity)
        custom_sales_data.price = float(unit_price)
        custom_sales_data.total_amount = custom_sales_data.quantity * custom_sales_data.price
        
        # Set default transaction properties
        custom_sales_data.transaction = "Sale"      # Default to sale transaction
        custom_sales_data.transaction_type = kwargs.get('transaction_type', "PLU")  # Default to PLU (product lookup) type
        custom_sales_data.unit_quantity = str(custom_sales_data.quantity)
        
        # Apply optional parameters from keyword arguments
        custom_sales_data.reference_id = kwargs.get('reference_id', 0)
        custom_sales_data.barcode = kwargs.get('barcode', "")
        custom_sales_data.plu_no = kwargs.get('plu_no', "")
        custom_sales_data.department_no = kwargs.get('department_no', 0)
        custom_sales_data.id = kwargs.get('id', 0)
        
        # Delegate to the comprehensive add method
        return self.add_sale_with_data(custom_sales_data)
    
    def add_sale_with_data(self, custom_sales_data: SalesData) -> bool:
        """
        Add a sales item using a complete SalesData object.
        
        This is the comprehensive method for adding items to the sales list.
        It handles row numbering, data storage, table insertion, and UI updates.
        
        Args:
            custom_sales_data: Complete SalesData object with all transaction details
            
        Returns:
            bool: True if the item was added successfully, False if an error occurred
        """
        try:
            # Automatically assign the next sequential row number
            if len(self.custom_sales_data_list) == 0:
                custom_sales_data.row_number = 1  # First row starts at 1
            else:
                # Calculate next row number based on the last table entry
                last_row_item = self.table_widget.item(self.table_widget.rowCount() - 1, self.COL_ROW_NUMBER)
                if last_row_item:
                    custom_sales_data.row_number = int(last_row_item.text()) + 1
                else:
                    # Fallback to data list length + 1
                    custom_sales_data.row_number = len(self.custom_sales_data_list) + 1
            
            # Store the sales data in our internal list for later reference
            self.custom_sales_data_list.append(custom_sales_data)
            
            # Create a new row in the table widget
            row_index = self.table_widget.rowCount()
            self.table_widget.insertRow(row_index)
            
            # Populate all table columns with data from the SalesData object
            self.table_widget.setItem(row_index, self.COL_ROW_NUMBER, 
                                    QTableWidgetItem(str(custom_sales_data.row_number)))
            self.table_widget.setItem(row_index, self.COL_REFERENCE_ID, 
                                    QTableWidgetItem(str(custom_sales_data.reference_id)))
            self.table_widget.setItem(row_index, self.COL_TRANSACTION_TYPE, 
                                    QTableWidgetItem(custom_sales_data.transaction_type))
            self.table_widget.setItem(row_index, self.COL_TRANSACTION, 
                                    QTableWidgetItem(custom_sales_data.transaction))
            self.table_widget.setItem(row_index, self.COL_NAME_OF_PRODUCT, 
                                    QTableWidgetItem(custom_sales_data.name_of_product))
            self.table_widget.setItem(row_index, self.COL_UNIT_QUANTITY, 
                                    QTableWidgetItem(custom_sales_data.unit_quantity))
            
            # Handle different column displays based on transaction type
            if custom_sales_data.transaction_type == "SUBTOTAL":
                # Subtotal rows don't show unit or price information - only total
                self.table_widget.setItem(row_index, self.COL_UNIT, QTableWidgetItem(""))
                self.table_widget.setItem(row_index, self.COL_PRICE, QTableWidgetItem(""))
            else:
                # Regular product rows show unit and price information
                self.table_widget.setItem(row_index, self.COL_UNIT, 
                                        QTableWidgetItem(str(custom_sales_data.unit)))
                self.table_widget.setItem(row_index, self.COL_PRICE, 
                                        QTableWidgetItem(f"{custom_sales_data.price:.2f}"))
            
            # Always show the total amount (formatted to 2 decimal places)
            self.table_widget.setItem(row_index, self.COL_TOTAL_AMOUNT, 
                                    QTableWidgetItem(f"{custom_sales_data.total_amount:.2f}"))
            
            # Update UI state: select the new row and ensure it's visible
            self.table_widget.selectRow(row_index)
            self.table_widget.scrollToItem(self.table_widget.item(row_index, 0))
            self.selected_index = row_index
            
            return True
            
        except Exception as e:
            # Log error and return failure status
            print(f"Error adding sale: {e}")
            return False
    
    def add_subtotal(self, total_price: float = None) -> bool:
        """
        Add a subtotal line to the sales list.
        
        A subtotal line displays the sum of all non-canceled product amounts.
        It appears as a special row type with no unit or price information.
        
        Args:
            total_price: Optional pre-calculated total. If None, will be calculated
                        automatically from current non-canceled products.
        
        Returns:
            bool: True if subtotal was added successfully, False if table is empty
                  or a subtotal already exists as the last row.
        """
        # Don't add subtotal to empty tables
        if self.table_widget.rowCount() == 0:
            return False
            
        # Prevent duplicate subtotals by checking if last row is already a subtotal
        last_transaction_item = self.table_widget.item(self.table_widget.rowCount() - 1, self.COL_TRANSACTION)
        if last_transaction_item and last_transaction_item.text() == "Subtotal":
            return False
        
        # Auto-calculate subtotal if not provided
        if total_price is None:
            total_price = self.calculate_subtotal()
            
        # Create subtotal entry with special formatting
        custom_sales_data = SalesData()
        custom_sales_data.transaction_type = "SUBTOTAL"
        custom_sales_data.transaction = "Subtotal"
        custom_sales_data.name_of_product = "SUBTOTAL"
        custom_sales_data.total_amount = total_price
        custom_sales_data.price = 0.0         # Subtotals don't display unit prices
        custom_sales_data.unit = 0            # Subtotals don't display units
        custom_sales_data.unit_quantity = ""  # Subtotals don't display quantities
        
        return self.add_sale_with_data(custom_sales_data)
    
    def calculate_subtotal(self) -> float:
        """
        Calculate the current subtotal from all active (non-canceled) product rows.
        
        This method sums the total_amount of all items that are:
        - Product transactions (PLU or DEPARTMENT type)
        - Not marked as canceled
        
        Returns:
            float: Sum of all active product totals
        """
        subtotal = 0.0
        for data in self.custom_sales_data_list:
            # Only include actual products that haven't been canceled
            if data.transaction_type in ["PLU", "DEPARTMENT"] and not data.is_canceled:
                subtotal += data.total_amount
        return subtotal
    
    def update_subtotals(self):
        """
        Update all existing subtotal rows with recalculated values.
        
        This method is called after product modifications (add, delete, repeat)
        to ensure subtotal rows always reflect the current product totals.
        It also ensures subtotal rows maintain their special formatting.
        """
        for i, data in enumerate(self.custom_sales_data_list):
            if data.transaction_type == "SUBTOTAL":
                # Recalculate the subtotal based on current active products
                new_subtotal = self.calculate_subtotal()
                data.total_amount = new_subtotal
                
                # Update the table display if the row exists
                if i < self.table_widget.rowCount():
                    self.table_widget.setItem(i, self.COL_TOTAL_AMOUNT, 
                                            QTableWidgetItem(f"{new_subtotal:.2f}"))
                    # Ensure subtotal rows don't show price/unit information
                    self.table_widget.setItem(i, self.COL_PRICE, QTableWidgetItem(""))
                    self.table_widget.setItem(i, self.COL_UNIT, QTableWidgetItem(""))
                    self.table_widget.setItem(i, self.COL_UNIT_QUANTITY, QTableWidgetItem(""))
    
    def delete_transaction(self, row_index: int) -> bool:
        """
        Handle delete action based on row type.
        
        This method implements smart deletion behavior:
        - For product rows: Apply strikethrough formatting and mark as canceled
        - For non-product rows: Remove the row completely from the table
        
        After deleting products, subtotals are automatically updated to reflect
        the change in active product totals.
        
        Args:
            row_index: Index of the row to delete
            
        Returns:
            bool: True if deletion was successful, False if row index is invalid
                  or an error occurred
        """
        try:
            # Validate row index
            if row_index < 0 or row_index >= self.table_widget.rowCount():
                return False
            
            # Determine appropriate action based on row type
            if row_index < len(self.custom_sales_data_list):
                row_data = self.custom_sales_data_list[row_index]
                
                # Product rows: cancel with strikethrough (soft delete)
                if row_data.transaction_type in ["PLU", "DEPARTMENT"]:
                    success = self.cancel_transaction(row_index)
                    if success:
                        # Recalculate subtotals since product was removed from calculations
                        self.update_subtotals()
                    return success
                else:
                    # Non-product rows: remove completely (hard delete)
                    return self.remove_product_at_row(row_index)
            else:
                # Fallback for rows not in data list: remove from table
                return self.remove_product_at_row(row_index)
                
        except Exception as e:
            print(f"Error deleting transaction: {e}")
            return False
    
    def add_discount_by_amount_line(self, discount_amount: float, product_name: str = "") -> bool:
        """
        Add a discount line with a fixed amount reduction.
        
        Creates a discount entry that shows a negative amount, reducing the total.
        If no product name is provided, uses the name from the last product in the list.
        
        Args:
            discount_amount: Amount to discount (will be shown as negative)
            product_name: Optional product name to associate with discount
            
        Returns:
            bool: True if discount was added successfully
        """
        custom_sales_data = SalesData()
        custom_sales_data.transaction_type = "DISCOUNT"
        custom_sales_data.transaction = "DISC. AMT"
        
        if not product_name and len(self.custom_sales_data_list) > 0:
            product_name = self.custom_sales_data_list[-1].name_of_product
            custom_sales_data.row_number = self.custom_sales_data_list[-1].row_number
        
        custom_sales_data.name_of_product = product_name
        custom_sales_data.total_amount = -discount_amount  # Negative for discount
        
        return self.add_sale_with_data(custom_sales_data)
    
    def add_discount_by_percent_line(self, discount_percent: float, discount_result: float, product_name: str = "") -> bool:
        """
        Add a discount line with percentage-based reduction.
        
        Creates a discount entry showing both the percentage and calculated discount amount.
        The discount percentage is displayed in the unit quantity column, and the
        calculated discount amount is shown as a negative total.
        
        Args:
            discount_percent: Percentage of discount applied
            discount_result: Calculated discount amount (will be shown as negative)
            product_name: Optional product name to associate with discount
            
        Returns:
            bool: True if discount was added successfully
        """
        custom_sales_data = SalesData()
        custom_sales_data.transaction_type = "DISCOUNT"
        custom_sales_data.transaction = "DISC. %"
        
        if not product_name and len(self.custom_sales_data_list) > 0:
            product_name = self.custom_sales_data_list[-1].name_of_product
            custom_sales_data.row_number = self.custom_sales_data_list[-1].row_number
        
        custom_sales_data.name_of_product = product_name
        custom_sales_data.unit_quantity = f"%{discount_percent}"
        custom_sales_data.total_amount = -discount_result  # Negative for discount
        
        return self.add_sale_with_data(custom_sales_data)
        
    def clear_products(self):
        """
        Clear all items from the sales list.
        
        This method removes all products, subtotals, discounts, and other items
        from both the internal data storage and the table display. It also resets
        the selected row index to 0.
        
        Returns:
            bool: Always returns True to indicate successful clearing
        """
        self.custom_sales_data_list.clear()  # Clear internal data storage
        self.table_widget.setRowCount(0)     # Remove all rows from table display
        self.selected_index = 0              # Reset selection tracking
        return True
        
    def get_total_amount(self):
        """
        Calculate the grand total of all rows in the sales list.
        
        This method sums up ALL total amounts from every row in the table,
        including products, subtotals, discounts, etc. It's different from
        calculate_subtotal() which only includes active products.
        
        Returns:
            float: Sum of all row totals, or 0.0 if no valid totals found
        """
        total = 0.0
        for row in range(self.table_widget.rowCount()):
            try:
                # Attempt to parse the total amount from each row
                amount_text = self.table_widget.item(row, self.COL_TOTAL_AMOUNT).text()
                total += float(amount_text)
            except (ValueError, TypeError, AttributeError):
                # Skip rows with invalid or missing total values
                continue
        return total
        
    def get_product_at_row(self, row):
        """Get product details at the specified row"""
        if row < 0 or row >= self.table_widget.rowCount():
            return None
            
        try:
            # Get from CustomSalesData if available
            if row < len(self.custom_sales_data_list):
                return self.custom_sales_data_list[row].to_dict()
            
            # Fallback to reading from table
            product_name = self.table_widget.item(row, self.COL_NAME_OF_PRODUCT).text()
            quantity_text = self.table_widget.item(row, self.COL_UNIT_QUANTITY).text()
            unit_price = float(self.table_widget.item(row, self.COL_PRICE).text())
            total = float(self.table_widget.item(row, self.COL_TOTAL_AMOUNT).text())
            
            return {
                "name": product_name,
                "quantity": quantity_text,
                "unit_price": unit_price,
                "total": total
            }
        except (ValueError, TypeError):
            return None
            
    def remove_product_at_row(self, row):
        """Remove product at the specified row"""
        if row >= 0 and row < self.table_widget.rowCount():
            # Remove from data list if exists
            if row < len(self.custom_sales_data_list):
                self.custom_sales_data_list.pop(row)
            
            # Remove from table
            self.table_widget.removeRow(row)
            
            # Update selected index
            if self.selected_index >= row and self.selected_index > 0:
                self.selected_index -= 1
                
            return True
        return False
    
    def get_selected_sale(self) -> Optional[Dict[str, Any]]:
        """Get selected sale data - equivalent to C# iGetSelectedSale"""
        try:
            if self.table_widget.currentRow() >= 0:
                selected_row = self.table_widget.currentRow()
                return self.get_product_at_row(selected_row)
        except Exception as e:
            print(f"Error getting selected sale: {e}")
        return None
    
    def get_last_sale(self) -> Optional[Dict[str, Any]]:
        """Get last sale data - equivalent to C# iGetLastSale"""
        try:
            if self.table_widget.rowCount() > 0:
                row_index = self.table_widget.rowCount() - 1
                
                # Skip canceled rows (similar to C# logic)
                while row_index >= 0:
                    row_data = self.get_product_at_row(row_index)
                    if row_data and not row_data.get('is_canceled', False):
                        return row_data
                    row_index -= 1
                    
        except Exception as e:
            print(f"Error getting last sale: {e}")
        return None
    
    def cancel_transaction(self, row_index: int) -> bool:
        """Cancel transaction - equivalent to C# bCancelTransaction"""
        try:
            if row_index < 0 or row_index >= self.table_widget.rowCount():
                return False
            
            # Get row number to cancel all related rows
            row_number_item = self.table_widget.item(row_index, self.COL_ROW_NUMBER)
            if not row_number_item:
                return False
                
            row_number = int(row_number_item.text())
            
            # Cancel all rows with the same row number
            for row in range(self.table_widget.rowCount()):
                current_row_item = self.table_widget.item(row, self.COL_ROW_NUMBER)
                if current_row_item and int(current_row_item.text()) == row_number:
                    self._apply_canceled_style(row)
                    
                    # Mark as canceled in data
                    if row < len(self.custom_sales_data_list):
                        self.custom_sales_data_list[row].is_canceled = True
            
            return True
            
        except Exception as e:
            print(f"Error canceling transaction: {e}")
            return False
    
    def repeat_transaction(self, row_index: int) -> bool:
        """
        Increase the quantity of a product row by 1.
        
        This method implements the "repeat" functionality by:
        1. Incrementing the product quantity by 1
        2. Recalculating the total amount (quantity × unit price)
        3. Updating the table display with new values
        4. Refreshing all subtotal calculations
        
        Only works on product rows (PLU/DEPARTMENT) that are not canceled.
        
        Args:
            row_index: Index of the row to repeat
            
        Returns:
            bool: True if quantity was successfully increased, False if row is invalid,
                  not a product, or already canceled
        """
        try:
            # Validate row index
            if row_index < 0 or row_index >= self.table_widget.rowCount():
                return False
            
            # Get the sales data for this row
            if row_index < len(self.custom_sales_data_list):
                current_data = self.custom_sales_data_list[row_index]
            else:
                return False
            
            # Only allow repeat on actual product rows
            if current_data.transaction_type not in ["PLU", "DEPARTMENT"]:
                return False
            
            # Don't repeat canceled items
            if current_data.is_canceled:
                return False
            
            # Increment quantity by 1
            current_data.quantity += 1.0
            
            # Recalculate total amount based on new quantity
            current_data.total_amount = current_data.quantity * current_data.price
            
            # Format quantity display appropriately
            if current_data.transaction_type == "PLU" and current_data.quantity < 1.0:
                # Show decimal quantities with 3 decimal places for weights
                current_data.unit_quantity = f"{current_data.quantity:.3f}"
            else:
                # Show whole numbers or decimals as appropriate
                current_data.unit_quantity = str(int(current_data.quantity) if current_data.quantity.is_integer() else current_data.quantity)
            
            # Update the table display with recalculated values
            self.table_widget.setItem(row_index, self.COL_UNIT_QUANTITY, 
                                    QTableWidgetItem(current_data.unit_quantity))
            self.table_widget.setItem(row_index, self.COL_TOTAL_AMOUNT, 
                                    QTableWidgetItem(f"{current_data.total_amount:.2f}"))
            
            # Recalculate subtotals since product total changed
            self.update_subtotals()
            
            # Force table refresh to ensure changes are visible
            self.table_widget.update()
            
            return True
            
        except Exception as e:
            print(f"Error repeating transaction: {e}")
            return False
    
    def error_correction(self, row_index: int) -> bool:
        """
        Apply error correction to a specific row.
        
        This method marks a row as corrected by applying strikethrough formatting
        and setting its canceled status. Unlike delete_transaction, this method
        is specifically for error correction scenarios.
        
        Args:
            row_index: Index of the row to mark as error-corrected
            
        Returns:
            bool: True if error correction was applied successfully
        """
        try:
            if row_index < 0 or row_index >= self.table_widget.rowCount():
                return False
                
            self._apply_canceled_style(row_index)
            
            # Mark as canceled in data
            if row_index < len(self.custom_sales_data_list):
                self.custom_sales_data_list[row_index].is_canceled = True
            
            return True
            
        except Exception as e:
            print(f"Error in error correction: {e}")
            return False
    
    def _apply_canceled_style(self, row_index: int):
        """Apply canceled/strikethrough style to a row"""
        try:
            # Create strikethrough font
            font = QFont()
            font.setStrikeOut(True)
            
            # Apply gray colors and strikethrough to all cells in row
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row_index, col)
                if item:
                    item.setBackground(QColor(211, 211, 211))  # Light gray
                    item.setForeground(QColor(245, 245, 245))  # White smoke
                    item.setFont(font)
                    
        except Exception as e:
            print(f"Error applying canceled style: {e}")
    
    def move_selection_up(self):
        """
        Move the selection up by one row.
        
        This method provides keyboard navigation support by moving the selection
        to the previous row and ensuring it's visible in the table view.
        Does nothing if already at the top row or table is empty.
        """
        if self.table_widget.rowCount() > 0 and self.selected_index > 0:
            self.selected_index -= 1                                               # Update internal tracking
            self.table_widget.selectRow(self.selected_index)                      # Update table selection
            self.table_widget.scrollToItem(self.table_widget.item(self.selected_index, 0))  # Ensure visibility
    
    def move_selection_down(self):
        """
        Move the selection down by one row.
        
        This method provides keyboard navigation support by moving the selection
        to the next row and ensuring it's visible in the table view.
        Does nothing if already at the bottom row or table is empty.
        """
        if self.table_widget.rowCount() > 0 and self.selected_index < self.table_widget.rowCount() - 1:
            self.selected_index += 1                                               # Update internal tracking
            self.table_widget.selectRow(self.selected_index)                      # Update table selection
            self.table_widget.scrollToItem(self.table_widget.item(self.selected_index, 0))  # Ensure visibility
