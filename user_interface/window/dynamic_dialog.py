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

import os
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from user_interface.control import TextBox, Button, NumPad, PaymentList, SaleList, ComboBox, AmountTable, Label, DataGrid
from user_interface.control import VirtualKeyboard


class DynamicDialog(QDialog):
    """
    Dynamic modal dialog that renders forms from database definitions.
    
    This class creates modal dialogs that display forms defined in the database,
    using the same rendering logic as BaseWindow but in a modal context.
    """
    
    def __init__(self, app, parent=None):
        """
        Initialize the dynamic dialog.
        
        Args:
            app: The main application instance
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.app = app
        self.keyboard = VirtualKeyboard(source=None, parent=self)
        self.payment_list = None
        self.sale_list = None
        self.amount_table = None
        
        # Make dialog modal and frameless
        self.setModal(True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        
        # Set window icon from settings
        self._set_window_icon()
    
    def _set_window_icon(self):
        """Set the window icon from settings.toml configuration."""
        try:
            from settings.settings import Settings
            icon_path = Settings().app_icon
            if icon_path and os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except Exception:
            pass  # Silently fail if icon cannot be loaded
    
    def draw_window(self, settings: dict, toolbar_settings: dict, design: list):
        """
        Draw the dialog content based on design specifications.
        
        Args:
            settings (dict): Form settings (size, colors, etc.)
            toolbar_settings (dict): Toolbar configuration (not used in dialogs)
            design (list): List of control designs to render
        """
        self.setUpdatesEnabled(False)
        
        # Set window properties
        p = self.palette()
        p.setColor(self.backgroundRole(), settings['background_color'])
        p.setColor(self.foregroundRole(), settings['foreground_color'])
        self.setPalette(p)
        
        self.setWindowTitle(settings["name"])
        self.setFixedSize(settings["width"], settings["height"])
        
        # Render all controls
        for control_design_data in design:
            control_type = control_design_data["type"]
            
            if control_type == "textbox":
                self._create_textbox(control_design_data)
            elif control_type == "button":
                self._create_button(control_design_data)
            elif control_type == "label":
                self._create_label(control_design_data)
            elif control_type == "numpad":
                self._create_numpad(control_design_data)
            elif control_type == "paymentlist":
                self._create_payment_list(control_design_data)
            elif control_type == "saleslist":
                self._create_sale_list(control_design_data)
            elif control_type == "amountstable":
                self._create_amount_table(control_design_data)
            elif control_type == "combobox":
                self._create_combobox(control_design_data)
            elif control_type == "datagrid":
                self._create_datagrid(control_design_data)
        
        self.setUpdatesEnabled(True)
        
        # Update keyboard size and position
        self.keyboard.resize_from_parent()
        self.keyboard.raise_()
    
    def focus_text_box(self):
        """Set focus to the first textbox found."""
        for item in self.children():
            if type(item) is TextBox:
                item.setFocus()
                break
    
    def get_textbox_values(self):
        """
        Get all textbox values.
        
        Returns:
            dict: Dictionary of field_name -> value pairs
        """
        values = {}
        for item in self.children():
            if type(item) is TextBox:
                values[item.__name__] = item.text()
        return values
    
    def clear(self):
        """Clear and cleanup all child widgets."""
        for item in self.children():
            if type(item) in [TextBox, Button, Label, NumPad, PaymentList, SaleList, ComboBox, AmountTable, DataGrid]:
                item.deleteLater()
                item.setParent(None)
    
    def _create_button(self, design_data):
        """Create a button control."""
        button = Button(design_data["caption"], self)
        button.setGeometry(design_data["location_x"], design_data["location_y"],
                           design_data["width"], design_data["height"])
        
        button.set_color(design_data['background_color'], design_data['foreground_color'])
        button.setToolTip(design_data["caption"])
        
        # Connect button to event handler
        function_name = design_data.get("function", "NONE")
        
        # Special handling for form navigation
        if function_name.startswith("NAVIGATE_TO_FORM:"):
            # Parse navigation command: NAVIGATE_TO_FORM:<form_id>:<transition_mode>
            parts = function_name.split(':')
            if len(parts) >= 3:
                target_form_id = parts[1]
                transition_mode = parts[2]
                button.clicked.connect(
                    lambda: self.app._navigate_to_form(target_form_id, transition_mode)
                )
        elif function_name == "CLOSE_FORM":
            # Close button for dialog
            button.clicked.connect(self.accept)
        else:
            # Regular event handler
            button.clicked.connect(self.app.event_distributor(function_name))
    
    def _create_numpad(self, design_data):
        """Create a numpad control."""
        # Use width and height directly from database/design_data
        # NumPad now handles dynamic sizing internally
        width = design_data.get("width", 300)
        height = design_data.get("height", 350)
        
        background_color = design_data.get("background_color", 0x778D45)
        foreground_color = design_data.get("foreground_color", 0xFFFFFF)
        
        numpad = NumPad(self,
                        width=width,
                        height=height,
                        location_x=design_data["location_x"],
                        location_y=design_data["location_y"],
                        background_color=background_color,
                        foreground_color=foreground_color)
        
        numpad.setToolTip(design_data.get("caption", ""))
        numpad.set_event(self.app.event_distributor(design_data.get("function", "NONE")))
    
    def _create_payment_list(self, design_data):
        """Create a payment list control."""
        width = design_data.get("width", 970)
        height = design_data.get("height", 315)
        background_color = design_data.get("background_color", 0x778D45)
        foreground_color = design_data.get("foreground_color", 0xFFFFFF)
        location_x = design_data.get("location_x", 10)
        location_y = design_data.get("location_y", 100)
        
        self.payment_list = PaymentList(self,
                        width=width,
                        height=height,
                        location_x=location_x,
                        location_y=location_y,
                        background_color=background_color,
                        foreground_color=foreground_color)
        
        if "function" in design_data and design_data["function"]:
            self.payment_list.set_event(self.app.event_distributor(design_data["function"]))
    
    def _create_sale_list(self, design_data):
        """Create a sale list control."""
        width = design_data.get("width", 970)
        height = design_data.get("height", 315)
        background_color = design_data.get("background_color", 0x778D45)
        foreground_color = design_data.get("foreground_color", 0xFFFFFF)
        location_x = design_data.get("location_x", 10)
        location_y = design_data.get("location_y", 100)
        
        self.sale_list = SaleList(self,
                        width=width,
                        height=height,
                        location_x=location_x,
                        location_y=location_y,
                        background_color=background_color,
                        foreground_color=foreground_color)
        
        if "function" in design_data and design_data["function"]:
            self.sale_list.set_event(self.app.event_distributor(design_data["function"]))
    
    def _create_amount_table(self, design_data):
        """Create an amount table control."""
        width = design_data.get("width", 250)
        height = design_data.get("height", 200)
        background_color = design_data.get("background_color", 0x778D45)
        foreground_color = design_data.get("foreground_color", 0xFFFFFF)
        location_x = design_data.get("location_x", 1)
        location_y = design_data.get("location_y", 1)
        
        self.amount_table = AmountTable(self,
                        width=width,
                        height=height,
                        location_x=location_x,
                        location_y=location_y,
                        background_color=background_color,
                        foreground_color=foreground_color)
        
        if "function" in design_data and design_data["function"]:
            self.amount_table.set_event(self.app.event_distributor(design_data["function"]))
    
    def _create_label(self, design_data):
        """Create a label control."""
        label = Label(self)
        label.setText(design_data.get('caption', ''))
        label.setGeometry(design_data["location_x"], design_data["location_y"],
                         design_data["width"], design_data["height"])
        
        # Set text alignment
        if design_data.get('text_alignment') == "LEFT":
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        elif design_data.get('text_alignment') == "RIGHT":
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        elif design_data.get('text_alignment') == "CENTER":
            label.setAlignment(Qt.AlignCenter)
        else:
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Set colors
        label.set_color(design_data.get('background_color', 0xFFFFFF), 
                       design_data.get('foreground_color', 0x000000))
        
        # Set font size if specified
        if design_data.get('font_size'):
            from PySide6.QtGui import QFont
            font = label.font()
            font.setPointSize(int(design_data['font_size']))
            label.setFont(font)
        
        # Set tooltip
        if design_data.get('caption'):
            label.setToolTip(design_data['caption'])

    def _create_textbox(self, design_data):
        """Create a textbox control."""
        textbox = TextBox(self)
        
        # Set alignment
        alignment = design_data.get('alignment', 'left').lower()
        if alignment == "left":
            textbox.setAlignment(Qt.AlignLeft)
        elif alignment == "right":
            textbox.setAlignment(Qt.AlignRight)
        elif alignment == "center":
            textbox.setAlignment(Qt.AlignCenter)
        
        # Set input type
        if design_data.get('input_type') == "password":
            textbox.set_password_type()
        
        # Set properties
        textbox.__name__ = design_data.get('field_name')
        textbox.setGeometry(design_data["location_x"], design_data["location_y"],
                            design_data["width"], design_data["height"])
        textbox.set_font_size(design_data.get('font_size', 12))
        textbox.filed_name = design_data.get('caption')
        
        if design_data.get('place_holder'):
            textbox.setPlaceholderText(design_data.get('place_holder'))
        
        textbox.set_color(design_data['background_color'], design_data['foreground_color'])
        
        if design_data.get('use_keyboard', False):
            textbox.keyboard = self.keyboard
    
    def _create_combobox(self, design_data):
        """Create a combobox control."""
        width = design_data.get("width", 240)
        height = design_data.get("height", 44)
        background_color = design_data.get("background_color", 0xFFFFFF)
        foreground_color = design_data.get("foreground_color", 0x000000)
        
        combo = ComboBox(self,
                         width=width,
                         height=height,
                         location_x=design_data.get("location_x", 0),
                         location_y=design_data.get("location_y", 0),
                         background_color=background_color,
                         foreground_color=foreground_color,
                         font_size=design_data.get("font_size", 20))
        
        # Populate items
        items = design_data.get("items")
        if items and isinstance(items, list):
            combo.set_items([str(x) for x in items])
        else:
            # Auto-populate by known names
            name_key = str(design_data.get("name", "")).upper()
            if name_key == "CASHIER_NAME_LIST":
                try:
                    from data_layer.model import Cashier
                    cashiers = Cashier.get_all(is_deleted=False)
                    # Format: "username (name lastname)" for better identification
                    labels = [f"{c.user_name} ({c.name} {c.last_name})" for c in cashiers]
                    if str(design_data.get("function1", "")).upper() == "LOGIN":
                        labels.append("SUPERVISOR")
                    combo.set_items(labels)
                except Exception:
                    combo.set_items([])
        
        # Optional event hookup
        if "function" in design_data and design_data["function"]:
            combo.set_event(self.app.event_distributor(design_data["function"]))
        
        # Set metadata
        if "caption" in design_data:
            combo.setToolTip(design_data["caption"])
        if "name" in design_data:
            combo.name = design_data["name"]
        if "type_name" in design_data:
            combo.type = design_data["type_name"]
        if "function1" in design_data:
            combo.function1 = design_data["function1"]
        if "function2" in design_data:
            combo.function2 = design_data["function2"]
    
    def _create_datagrid(self, design_data):
        """
        Create a DataGrid control for displaying tabular data.
        
        Args:
            design_data (dict): Design specifications for the datagrid
        """
        width = design_data.get("width", 600)
        height = design_data.get("height", 400)
        background_color = design_data.get("background_color", 0xFFFFFF)
        foreground_color = design_data.get("foreground_color", 0x000000)
        
        datagrid = DataGrid(self)
        datagrid.setGeometry(
            design_data.get("location_x", 0),
            design_data.get("location_y", 0),
            width,
            height
        )
        
        # Apply colors
        datagrid.set_color(background_color, foreground_color)
        
        # Set font size if provided
        if "font_size" in design_data:
            from PySide6.QtGui import QFont
            font = QFont("Verdana", design_data["font_size"])
            datagrid.setFont(font)
        
        # Store metadata
        if "name" in design_data:
            datagrid.name = design_data["name"]
        if "function" in design_data:
            datagrid.function = design_data["function"]
        if "caption" in design_data:
            datagrid.setToolTip(design_data["caption"])
        
        # Auto-populate data if this is the CLOSURE DATAGRID
        from data_layer.enums import ControlName
        name_key = str(design_data.get("name", ""))
        
        if name_key == ControlName.DATAGRID.value:
            # Load closure data from database
            try:
                from data_layer.model import Closure
                closures = Closure.get_all(is_deleted=False)
                
                # Set column headers
                datagrid.set_columns([
                    "Closure No", 
                    "Date", 
                    "Cashier", 
                    "Total Sales", 
                    "Cash", 
                    "Credit Card"
                ])
                
                # Prepare data rows
                data_rows = []
                for closure in closures:
                    row = [
                        str(closure.closure_no),
                        closure.date_create.strftime("%Y-%m-%d %H:%M") if closure.date_create else "",
                        closure.cashier.user_name if closure.cashier else "",
                        f"{closure.total_amount:.2f}" if closure.total_amount else "0.00",
                        f"{closure.cash_amount:.2f}" if closure.cash_amount else "0.00",
                        f"{closure.credit_card_amount:.2f}" if closure.credit_card_amount else "0.00"
                    ]
                    data_rows.append(row)
                
                # Set data
                datagrid.set_data(data_rows)
                
            except Exception as e:
                print(f"Error loading closure data: {e}")
                # Set empty data on error
                datagrid.set_columns(["No Data Available"])
                datagrid.set_data([])
        
        datagrid.show()

