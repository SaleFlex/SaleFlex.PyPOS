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
from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from user_interface.control import TextBox, Button, ToolBar, StatusBar, NumPad, PaymentList, SaleList, ComboBox, AmountTable, Label, DataGrid
from user_interface.control import VirtualKeyboard


class BaseWindow(QMainWindow):
    def __init__(self, app):
        super().__init__(parent=None)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.app = app

        self.keyboard = VirtualKeyboard(source=None, parent=self)
        
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
        self.setUpdatesEnabled(False)
        p = self.palette()
        p.setColor(self.backgroundRole(), settings['background_color'])
        p.setColor(self.foregroundRole(), settings['foreground_color'])
        self.setPalette(p)

        self.setWindowTitle(settings["name"])
        self.move(0, 0)
        self.setFixedSize(settings["width"], settings["height"])

        if settings["toolbar"]:
            self._create_toolbar(toolbar_settings)
        if settings["statusbar"]:
            self._create_status_bar()

        for control_design_data in design:
            if control_design_data["type"] == "textbox":
                self._create_textbox(control_design_data)

            if control_design_data["type"] == "button":
                self._create_button(control_design_data)

            if control_design_data["type"] == "label":
                self._create_label(control_design_data)

            if control_design_data["type"] == "numpad":
                self._create_numpad(control_design_data)

            if control_design_data["type"] == "paymentlist":
                self._create_payment_list(control_design_data)

            if control_design_data["type"] == "saleslist":
                self._create_sale_list(control_design_data)

            if control_design_data["type"] == "amountstable":
                self._create_amount_table(control_design_data)

            if control_design_data["type"] == "combobox":
                self._create_combobox(control_design_data)

            if control_design_data["type"] == "datagrid":
                self._create_datagrid(control_design_data)

        self.setUpdatesEnabled(True)

        self.keyboard.resize_from_parent()
        self.keyboard.raise_()

    def focus_text_box(self):
        for item in self.children():
            if type(item) is TextBox:
                item.setFocus()
                break

    def get_textbox_values(self):
        values = {}
        for item in self.children():
            if type(item) is TextBox:
                values[item.__name__] = item.text()
        return values

    def clear(self):
        for item in self.children():
            print(item)
            if type(item) in [TextBox, Button, Label, ToolBar, StatusBar, NumPad, PaymentList, SaleList, ComboBox, AmountTable, DataGrid]:
                print(type(item), item)
                item.deleteLater()
                item.setParent(None)
        self.hide()

    def _create_button(self, design_data):
        print("="*80)
        print(f"Creating button: {design_data}")
        print(f"Button caption: {design_data.get('caption')}")
        print(f"Button function value from DB: '{design_data.get('function')}'")
        print(f"Button function type: {type(design_data.get('function'))}")
        
        # Get font name from design_data, default to "Verdana"
        font_name = design_data.get("font", "Verdana")
        # Get font_auto_height setting from design_data, default to True
        font_auto_height = design_data.get("font_auto_height", True)
        # Create button with empty text first, then set geometry, then set text
        # This ensures button dimensions are set before font adjustment
        button = Button("", self, font_name=font_name, font_auto_height=font_auto_height)
        button.setGeometry(design_data["location_x"], design_data["location_y"],
                           design_data["width"], design_data["height"])

        button.set_color(design_data['background_color'], design_data['foreground_color'])
        button.setToolTip(design_data["caption"])
        
        # Set button text after geometry is set - this will trigger font adjustment
        button.setText(design_data["caption"])
        
        # Store button metadata for event handling
        button_name = design_data.get("name", "")
        button.control_name = button_name  # Store control name for SALE_PLU_CODE handling
        
        # Get the event handler function
        function_name = design_data.get("function")
        print(f"Calling event_distributor with: '{function_name}'")
        
        event_handler = self.app.event_distributor(function_name)
        print(f"Event handler retrieved: {event_handler}")
        print(f"Event handler type: {type(event_handler)}")
        
        if event_handler:
            print(f"✓ Connecting button '{design_data.get('caption')}' to event handler: {event_handler.__name__}")
            
            # Special handling for SALE_PLU_CODE, SALE_PLU_BARCODE, and SALE_DEPARTMENT: pass button object to handler
            # Use default parameter to avoid closure issues
            if function_name in ["SALE_PLU_CODE", "SALE_PLU_BARCODE", "SALE_DEPARTMENT"]:
                button.clicked.connect(lambda checked=False, btn=button: event_handler(btn))
            else:
                button.clicked.connect(event_handler)
        else:
            print(f"✗ WARNING: No event handler found for function: '{function_name}'")
        
        # Set button text based on product information for PLU buttons
        if function_name in ["SALE_PLU_CODE", "SALE_PLU_BARCODE"] and button_name and button_name.upper().startswith("PLU"):
            try:
                # Extract code/barcode from button name (remove "PLU" prefix)
                code_or_barcode = button_name[3:]  # Remove first 3 characters "PLU"
                
                if function_name == "SALE_PLU_CODE":
                    # Find product by code from product_data cache
                    products = [
                        p for p in self.app.product_data.get("Product", [])
                        if p.code == code_or_barcode and not (hasattr(p, 'is_deleted') and p.is_deleted)
                    ]
                    if products and len(products) > 0:
                        product = products[0]
                        product_name = product.short_name if product.short_name else product.name
                        button.setText(product_name)
                        print(f"[BUTON] SALE_PLU_CODE: Set button text to '{product_name}' for code '{code_or_barcode}'")
                    else:
                        print(f"[BUTON] SALE_PLU_CODE: No product found with code '{code_or_barcode}'")
                
                elif function_name == "SALE_PLU_BARCODE":
                    # Find product_barcode by barcode from product_data cache, then get product
                    barcode_records = [
                        pb for pb in self.app.product_data.get("ProductBarcode", [])
                        if pb.barcode == code_or_barcode and not (hasattr(pb, 'is_deleted') and pb.is_deleted)
                    ]
                    if barcode_records and len(barcode_records) > 0:
                        product_barcode = barcode_records[0]
                        # Find product by id from product_data cache
                        products = [
                            p for p in self.app.product_data.get("Product", [])
                            if p.id == product_barcode.fk_product_id
                        ]
                        if products and len(products) > 0:
                            product = products[0]
                            product_name = product.short_name if product.short_name else product.name
                            button.setText(product_name)
                            print(f"[BUTON] SALE_PLU_BARCODE: Set button text to '{product_name}' for barcode '{code_or_barcode}'")
                        else:
                            print(f"[BUTON] SALE_PLU_BARCODE: Product not found with id '{product_barcode.fk_product_id}'")
                    else:
                        print(f"[BUTON] SALE_PLU_BARCODE: No product_barcode found with barcode '{code_or_barcode}'")
            except Exception as e:
                print(f"[BUTON] Error setting button text for PLU button: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Trigger font adjustment after button is fully created and sized (only if font_auto_height is True)
        # Use QTimer to ensure button dimensions are set
        if font_auto_height:
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, lambda: button._adjust_font_size() if hasattr(button, '_adjust_font_size') else None)
        
        print("="*80)

    def _create_numpad(self, design_data):
        print(design_data)
        
        # Use width and height directly from database/design_data
        # NumPad now handles dynamic sizing internally
        width = design_data.get("width", 300)
        height = design_data.get("height", 350)
        
        # Get background and foreground colors from design data
        background_color = design_data.get("background_color", 0x778D45)
        foreground_color = design_data.get("foreground_color", 0xFFFFFF)
        
        numpad = NumPad(self,
                        width=width,
                        height=height,
                        location_x=design_data["location_x"],
                        location_y=design_data["location_y"],
                        background_color=background_color,
                        foreground_color=foreground_color)

        numpad.setToolTip(design_data["caption"])
        numpad.set_event(self.app.event_distributor(design_data["function"]))

    def _create_payment_list(self, design_data):
        # Ensure payment list has appropriate dimensions
        width = design_data.get("width", 970)
        height = design_data.get("height", 315)

        # Get background and foreground colors from design data
        background_color = design_data.get("background_color", 0x778D45)
        foreground_color = design_data.get("foreground_color", 0xFFFFFF)

        location_x = design_data.get("location_x", 10)
        location_y = design_data.get("location_y", 100)

        # Create the payment list widget
        self.payment_list = PaymentList(self,
                        width=width,
                        height=height,
                        location_x=location_x,
                        location_y=location_y,
                        background_color=background_color,
                        foreground_color=foreground_color)
        
        # Set the event handler if specified
        if "function" in design_data:
            self.payment_list.set_event(self.app.event_distributor(design_data["function"]))

    def _create_sale_list(self, design_data):
        # Ensure payment list has appropriate dimensions
        width = design_data.get("width", 970)
        height = design_data.get("height", 315)

        # Get background and foreground colors from design data
        background_color = design_data.get("background_color", 0x778D45)
        foreground_color = design_data.get("foreground_color", 0xFFFFFF)

        location_x = design_data.get("location_x", 10)
        location_y = design_data.get("location_y", 100)

        # Create the payment list widget
        self.sale_list = SaleList(self,
                        width=width,
                        height=height,
                        location_x=location_x,
                        location_y=location_y,
                        background_color=background_color,
                        foreground_color=foreground_color)

        # Set the event handler if specified
        if "function" in design_data:
            self.sale_list.set_event(self.app.event_distributor(design_data["function"]))

    def _create_amount_table(self, design_data):
        # Ensure amount table has appropriate dimensions
        width = design_data.get("width", 250)
        height = design_data.get("height", 200)

        # Get background and foreground colors from design data
        background_color = design_data.get("background_color", 0x778D45)
        foreground_color = design_data.get("foreground_color", 0xFFFFFF)

        location_x = design_data.get("location_x", 1)
        location_y = design_data.get("location_y", 1)

        # Create the amount table widget
        self.amount_table = AmountTable(self,
                        width=width,
                        height=height,
                        location_x=location_x,
                        location_y=location_y,
                        background_color=background_color,
                        foreground_color=foreground_color)

        # Set the event handler if specified
        if "function" in design_data:
            self.amount_table.set_event(self.app.event_distributor(design_data["function"]))

    def _create_label(self, design_data):
        print(design_data)
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
        print(design_data)
        textbox = TextBox(self)
        if design_data.get('alignment') == "left":
            textbox.setAlignment(Qt.AlignLeft)
        elif design_data.get('alignment') == "right":
            textbox.setAlignment(Qt.AlignRight)
        elif design_data.get('alignment') == "center":
            textbox.setAlignment(Qt.AlignCenter)
        if design_data.get('input_type') == "password":
            textbox.set_password_type()
        textbox.__name__ = design_data.get('field_name')
        textbox.setGeometry(design_data["location_x"], design_data["location_y"],
                            design_data["width"], design_data["height"])
        textbox.set_font_size(design_data.get('font_size'))
        textbox.filed_name = design_data.get('caption')
        if design_data.get('place_holder'):
            textbox.setPlaceholderText(design_data.get('place_holder'))
        textbox.set_color(design_data['background_color'], design_data['foreground_color'])
        if design_data['use_keyboard']:
            textbox.keyboard = self.keyboard

    def _create_combobox(self, design_data):
        print(design_data)
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

        # Populate items: either static list or by special name
        items = design_data.get("items")
        if items and isinstance(items, list):
            combo.set_items([str(x) for x in items])
        else:
            # Auto-populate by known names (e.g., CASHIER_NAME_LIST)
            from data_layer.enums import ControlName, EventName
            name_key = str(design_data.get("name", ""))
            
            if name_key == ControlName.CASHIER_NAME_LIST.value:
                try:
                    from data_layer.model import Cashier
                    cashiers = Cashier.get_all(is_deleted=False)
                    # Format: "username (name lastname)" for better identification
                    labels = [f"{c.user_name} ({c.name} {c.last_name})" for c in cashiers]
                    # Add SUPERVISOR option if function1 is LOGIN event
                    if design_data.get("function1") == EventName.LOGIN.value:
                        labels.append("SUPERVISOR")
                    combo.set_items(labels)
                except Exception:
                    combo.set_items([])

        # Optional event hookup
        if "function" in design_data:
            combo.set_event(self.app.event_distributor(design_data["function"]))

        # Set tooltip and store metadata
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

    def _create_toolbar(self, design_data):
        print(design_data)
        tools = ToolBar()
        if "button" in design_data and "back" in design_data["button"]:
            tools.add_event(back_function_caption=design_data["button"]["back"]["caption"],
                            back_function_image=design_data["button"]["back"]["image"],
                            back_function=self.app.event_distributor("BACK"))
        self.addToolBar(tools)

    def _create_status_bar(self):
        statusbar = StatusBar()
        self.setStatusBar(statusbar)

    def _create_datagrid(self, design_data):
        """
        Create a DataGrid control for displaying tabular data.
        
        Args:
            design_data (dict): Design specifications for the datagrid
        """
        print("="*80)
        print(f"Creating datagrid: {design_data}")
        print("="*80)
        
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


