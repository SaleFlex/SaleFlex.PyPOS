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
from PySide6.QtGui import QIcon, QColor, QLinearGradient, QBrush, QPalette

from user_interface.control import TextBox, Button, ToolBar, StatusBar, NumPad, PaymentList, SaleList, ComboBox, AmountTable, Label, DataGrid, Panel
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
        self.setWindowTitle(settings["name"])
        self.move(0, 0)
        self.setFixedSize(settings["width"], settings["height"])
        self._apply_gradient_background(
            settings.get('background_color', 0xFFFFFF),
            settings.get('foreground_color', 0x000000)
        )

        if settings["toolbar"]:
            self._create_toolbar(toolbar_settings)
        if settings["statusbar"]:
            self._create_status_bar()

        # Initialize panels dictionary
        if not hasattr(self, '_panels'):
            self._panels = {}

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

            if control_design_data["type"] == "panel":
                self._create_panel(control_design_data)

        self.setUpdatesEnabled(True)

        self.keyboard.resize_from_parent()
        self.keyboard.raise_()

    def _apply_gradient_background(self, background_value: int, foreground_value: int):
        """
        Apply a subtle gradient using the provided base colors.

        Creates a vertical gradient that starts slightly darker than the base
        color, transitions through the original tone, and ends slightly lighter.
        This keeps the existing color scheme but adds depth to the form surface.
        """
        base_color = self._int_to_qcolor(background_value, default=QColor(255, 255, 255))
        dark_color = base_color.darker(120)   # ~20% darker
        light_color = base_color.lighter(120) # ~20% lighter

        gradient = QLinearGradient(0, 0, 0, self.height() or 1)
        gradient.setColorAt(0.0, dark_color)
        gradient.setColorAt(0.5, base_color)
        gradient.setColorAt(1.0, light_color)

        palette = self.palette()
        palette.setBrush(QPalette.Window, QBrush(gradient))
        palette.setColor(QPalette.WindowText, self._int_to_qcolor(foreground_value, default=QColor(0, 0, 0)))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    @staticmethod
    def _int_to_qcolor(value, default: QColor):
        """Safely convert an integer RGB value to QColor."""
        try:
            rgb = int(value)
        except (TypeError, ValueError):
            return default

        rgb = max(0, min(0xFFFFFF, rgb))
        r = (rgb >> 16) & 0xFF
        g = (rgb >> 8) & 0xFF
        b = rgb & 0xFF
        return QColor(r, g, b)

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
    
    def get_panel_textbox_values(self, panel_name):
        """
        Get all textbox values from a specific panel.
        
        Args:
            panel_name (str): Name of the panel (e.g., "POS_SETTINGS")
            
        Returns:
            dict: Dictionary mapping field names (lowercase) to textbox values
        """
        values = {}
        try:
            if not hasattr(self, '_panels'):
                return values
            
            panel = self._panels.get(panel_name)
            if not panel:
                return values
            
            # Check if panel widget is still valid
            try:
                # Try to access panel to check if it's still valid
                if not hasattr(panel, 'get_content_widget'):
                    return values
            except RuntimeError:
                # Widget already deleted
                print(f"[GET_PANEL_VALUES] ⚠ Panel '{panel_name}' widget already deleted")
                return values
            
            # Get all textboxes from panel's content widget
            try:
                content_widget = panel.get_content_widget()
                if not content_widget:
                    return values
                
                # Check if content widget is still valid
                try:
                    # Try to access widget to check if it's still valid
                    _ = content_widget.children()
                except RuntimeError:
                    # Widget already deleted
                    print(f"[GET_PANEL_VALUES] ⚠ Content widget for panel '{panel_name}' already deleted")
                    return values
                
                for child in content_widget.findChildren(TextBox):
                    try:
                        # Check if child widget is still valid
                        _ = child.text()
                    except RuntimeError:
                        # Widget already deleted, skip it
                        continue
                    
                    # Get textbox name (uppercase in DB, convert to lowercase for model attribute)
                    # Try both __name__ and name attributes
                    textbox_name = getattr(child, 'name', None) or getattr(child, '__name__', None)
                    if textbox_name:
                        # Convert uppercase name to lowercase for model attribute
                        # Textbox names are uppercase (e.g., "POS_NO_IN_STORE")
                        # Model attributes are lowercase (e.g., "pos_no_in_store")
                        field_name = textbox_name.lower()
                        values[field_name] = child.text()
            except RuntimeError as e:
                # Widget already deleted
                print(f"[GET_PANEL_VALUES] ⚠ Error accessing panel '{panel_name}': {e}")
                return values
            except Exception as e:
                print(f"[GET_PANEL_VALUES] ⚠ Unexpected error accessing panel '{panel_name}': {e}")
                return values
        
        except Exception as e:
            print(f"[GET_PANEL_VALUES] ⚠ Error getting panel values for '{panel_name}': {e}")
            return values
        
        return values

    def clear(self):
        for item in self.children():
            print(item)
            if type(item) in [TextBox, Button, Label, ToolBar, StatusBar, NumPad, PaymentList, SaleList, ComboBox, AmountTable, DataGrid, Panel]:
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
        
        # Check if this control belongs to a panel
        parent_panel = None
        if 'parent_name' in design_data and design_data['parent_name']:
            parent_panel = self._panels.get(design_data['parent_name'])
        
        # Use panel's content widget as parent if available, otherwise use window
        parent_widget = parent_panel.get_content_widget() if parent_panel else self
        
        # Get font name from design_data, default to "Verdana"
        font_name = design_data.get("font", "Verdana")
        # Get font_auto_height setting from design_data, default to True
        font_auto_height = design_data.get("font_auto_height", True)
        # Create button with empty text first, then set geometry, then set text
        # This ensures button dimensions are set before font adjustment
        button = Button("", parent_widget, font_name=font_name, font_auto_height=font_auto_height)
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
            
            # Special handling for sale and payment events: pass button object to handler
            # Use default parameter to avoid closure issues
            payment_events = ["CASH_PAYMENT", "CREDIT_PAYMENT", "CHECK_PAYMENT", "EXCHANGE_PAYMENT", 
                             "PREPAID_PAYMENT", "CHARGE_SALE_PAYMENT", "OTHER_PAYMENT", "CHANGE_PAYMENT"]
            sale_events = ["SALE_PLU_CODE", "SALE_PLU_BARCODE", "SALE_DEPARTMENT"] 
            if function_name in sale_events or function_name in payment_events:
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
        
        # Add to panel if parent exists
        if parent_panel:
            parent_panel.add_child_control(button)
        
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
        # Check if this control belongs to a panel
        parent_panel = None
        if 'parent_name' in design_data and design_data['parent_name']:
            parent_panel = self._panels.get(design_data['parent_name'])
        
        # Use panel's content widget as parent if available, otherwise use window
        parent_widget = parent_panel.get_content_widget() if parent_panel else self
        
        label = Label(parent_widget)
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
        
        # Add to panel if parent exists
        if parent_panel:
            parent_panel.add_child_control(label)

    def _create_textbox(self, design_data):
        print(design_data)
        # Check if this control belongs to a panel
        parent_panel = None
        if 'parent_name' in design_data and design_data['parent_name']:
            parent_panel = self._panels.get(design_data['parent_name'])
        
        # Use panel's content widget as parent if available, otherwise use window
        parent_widget = parent_panel.get_content_widget() if parent_panel else self
        
        textbox = TextBox(parent_widget)
        if design_data.get('alignment') == "left":
            textbox.setAlignment(Qt.AlignLeft)
        elif design_data.get('alignment') == "right":
            textbox.setAlignment(Qt.AlignRight)
        elif design_data.get('alignment') == "center":
            textbox.setAlignment(Qt.AlignCenter)
        if design_data.get('input_type') == "password":
            textbox.set_password_type()
        # Store textbox name for identification (used in save operations)
        textbox_name = design_data.get('name') or design_data.get('field_name')
        textbox.__name__ = textbox_name
        textbox.name = textbox_name  # Also store as name attribute for easier access
        textbox.setGeometry(design_data["location_x"], design_data["location_y"],
                            design_data["width"], design_data["height"])
        textbox.set_font_size(design_data.get('font_size'))
        textbox.filed_name = design_data.get('caption')
        if design_data.get('place_holder'):
            textbox.setPlaceholderText(design_data.get('place_holder'))
        textbox.set_color(design_data['background_color'], design_data['foreground_color'])
        # Set keyboard for textbox - always enable for panel textboxes or if use_keyboard is True
        if design_data.get('use_keyboard') or parent_panel:
            textbox.keyboard = self.keyboard
        
        # Add to panel if parent exists
        if parent_panel:
            parent_panel.add_child_control(textbox)
        
        # Load data from CurrentData if this textbox belongs to a panel
        # Panel name matches model name (e.g., "POS_SETTINGS" -> PosSettings, "CASHIER" -> Cashier)
        if parent_panel and hasattr(parent_panel, 'name') and parent_panel.name:
            panel_name = parent_panel.name
            textbox_name = design_data.get('name', '')
            
            if textbox_name:
                # Get field name from textbox name (uppercase in DB, convert to lowercase for model attribute)
                # Textbox name is uppercase (e.g., "POS_NO_IN_STORE", "USER_NAME") 
                # Model attribute is lowercase (e.g., "pos_no_in_store", "user_name")
                field_name = textbox_name.lower()
                
                # Convert panel name to model class name
                # Panel name is uppercase (e.g., "POS_SETTINGS", "CASHIER")
                # Model class name is PascalCase (e.g., "PosSettings", "Cashier")
                parts = panel_name.lower().split('_')
                model_class_name = ''.join(word.capitalize() for word in parts)
                
                # Try to get model instance from CurrentData cache
                model_instance = None
                cache_attr_name = None
                
                # Check common cache attributes
                if model_class_name == "PosSettings":
                    cache_attr_name = "pos_settings"
                elif model_class_name == "Cashier":
                    cache_attr_name = "cashier_data"
                
                if cache_attr_name and hasattr(self.app, cache_attr_name):
                    model_instance = getattr(self.app, cache_attr_name)
                    if model_instance:
                        # Unwrap if it's an AutoSaveModel
                        if hasattr(model_instance, 'unwrap'):
                            model_instance = model_instance.unwrap()
                
                # If not in cache, try to get from model class
                if not model_instance:
                    try:
                        from data_layer.model.definition import __all__ as model_names
                        import data_layer.model.definition as model_module
                        
                        if model_class_name in model_names:
                            model_class = getattr(model_module, model_class_name)
                            # Try to get first instance from database
                            instances = model_class.get_all(is_deleted=False)
                            if instances and len(instances) > 0:
                                model_instance = instances[0]
                    except Exception as e:
                        print(f"[LOAD_DATA] Error loading model class {model_class_name}: {e}")
                
                # Load value from model instance
                if model_instance:
                    try:
                        value = getattr(model_instance, field_name, None)
                        if value is not None:
                            # Convert to string for textbox
                            textbox.setText(str(value))
                            print(f"[LOAD_DATA] Loaded {field_name} = {value} into textbox '{textbox_name}' (panel: {panel_name}, model: {model_class_name})")
                    except Exception as e:
                        print(f"[LOAD_DATA] Error loading {field_name} from {model_class_name}: {e}")
                        import traceback
                        traceback.print_exc()

    def _create_combobox(self, design_data):
        print(design_data)
        # Check if this control belongs to a panel
        parent_panel = None
        if 'parent_name' in design_data and design_data['parent_name']:
            parent_panel = self._panels.get(design_data['parent_name'])
        
        # Use panel's content widget as parent if available, otherwise use window
        parent_widget = parent_panel.get_content_widget() if parent_panel else self
        
        width = design_data.get("width", 240)
        height = design_data.get("height", 44)
        background_color = design_data.get("background_color", 0xFFFFFF)
        foreground_color = design_data.get("foreground_color", 0x000000)

        combo = ComboBox(parent_widget,
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
        
        # Add to panel if parent exists
        if parent_panel:
            parent_panel.add_child_control(combo)

    def _create_toolbar(self, design_data):
        print(design_data)
        tools = ToolBar()
        if "button" in design_data and "back" in design_data["button"]:
            tools.add_event(back_function_caption=design_data["button"]["back"]["caption"],
                            back_function_image=design_data["button"]["back"]["image"],
                            back_function=self.app.event_distributor("BACK"))
        self.addToolBar(tools)

    def _create_status_bar(self):
        statusbar = StatusBar(app=self.app)
        self.setStatusBar(statusbar)
        # Store reference for manual updates
        self.statusbar = statusbar

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

    def _create_panel(self, design_data):
        """
        Create a Panel control with scrollbar support.
        
        Args:
            design_data (dict): Design specifications for the panel
        """
        print("="*80)
        print(f"Creating panel: {design_data}")
        print("="*80)
        
        width = design_data.get("width", 800)
        height = design_data.get("height", 600)
        background_color = design_data.get("background_color", 0xFFFFFF)
        foreground_color = design_data.get("foreground_color", 0x000000)
        
        panel = Panel(
            self,
            width=width,
            height=height,
            location_x=design_data.get("location_x", 0),
            location_y=design_data.get("location_y", 0),
            background_color=background_color,
            foreground_color=foreground_color
        )
        
        # Store panel reference by name for child controls
        if "name" in design_data:
            panel.name = design_data["name"]
            # Store panel in a dictionary for child controls to find their parent
            if not hasattr(self, '_panels'):
                self._panels = {}
            self._panels[design_data["name"]] = panel
        
        panel.show()


