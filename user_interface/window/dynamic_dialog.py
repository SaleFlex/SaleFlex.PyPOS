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

from core.logger import get_logger

logger = get_logger(__name__)
from PySide6.QtGui import QIcon, QColor, QLinearGradient, QBrush, QPalette

from user_interface.control import TextBox, Button, NumPad, PaymentList, SaleList, ComboBox, AmountTable, Label, DataGrid, Panel
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
        self._panels = {}
        
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
        
        self.setWindowTitle(settings["name"])
        self.setFixedSize(settings["width"], settings["height"])
        self._apply_gradient_background(
            settings.get('background_color', 0xFFFFFF),
            settings.get('foreground_color', 0x000000)
        )
        
        # Initialize panels dictionary
        if not hasattr(self, '_panels'):
            self._panels = {}
        
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
            elif control_type == "panel":
                self._create_panel(control_design_data)
        
        self.setUpdatesEnabled(True)
        
        # Update keyboard size and position
        self.keyboard.resize_from_parent()
        self.keyboard.raise_()
    
    def _apply_gradient_background(self, background_value: int, foreground_value: int):
        """
        Apply a subtle gradient to match BaseWindow styling.
        """
        base_color = self._int_to_qcolor(background_value, default=QColor(255, 255, 255))
        dark_color = base_color.darker(120)
        light_color = base_color.lighter(120)

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
            
            try:
                if not hasattr(panel, 'get_content_widget'):
                    return values
            except RuntimeError:
                logger.warning("[GET_PANEL_VALUES] Panel '%s' widget already deleted", panel_name)
                return values
            
            try:
                content_widget = panel.get_content_widget()
                if not content_widget:
                    return values
                
                try:
                    _ = content_widget.children()
                except RuntimeError:
                    logger.warning("[GET_PANEL_VALUES] Content widget for panel '%s' already deleted", panel_name)
                    return values
                
                for child in content_widget.findChildren(TextBox):
                    try:
                        _ = child.text()
                    except RuntimeError:
                        continue
                    
                    textbox_name = getattr(child, 'name', None) or getattr(child, '__name__', None)
                    if textbox_name:
                        field_name = textbox_name.lower()
                        values[field_name] = child.text()
            except RuntimeError as e:
                logger.warning("[GET_PANEL_VALUES] Error accessing panel '%s': %s", panel_name, e)
                return values
            except Exception as e:
                logger.warning("[GET_PANEL_VALUES] Unexpected error accessing panel '%s': %s", panel_name, e)
                return values
        
        except Exception as e:
            logger.warning("[GET_PANEL_VALUES] Error getting panel values for '%s': %s", panel_name, e)
            return values
        
        return values

    def clear(self):
        """Clear and cleanup all child widgets."""
        for item in self.children():
            if type(item) in [TextBox, Button, Label, NumPad, PaymentList, SaleList, ComboBox, AmountTable, DataGrid, Panel]:
                item.deleteLater()
                item.setParent(None)
    
    def _create_button(self, design_data):
        """Create a button control with event binding and optional PLU text."""
        # Resolve parent: panel content widget or dialog
        parent_panel = None
        if design_data.get('parent_name'):
            parent_panel = self._panels.get(design_data['parent_name'])
        parent_widget = parent_panel.get_content_widget() if parent_panel else self
        
        font_name = design_data.get("font", "Verdana")
        font_auto_height = design_data.get("font_auto_height", True)
        button = Button("", parent_widget, font_name=font_name, font_auto_height=font_auto_height)
        button.setGeometry(design_data["location_x"], design_data["location_y"],
                          design_data["width"], design_data["height"])
        button.set_color(design_data['background_color'], design_data['foreground_color'])
        button.setToolTip(design_data.get("caption", ""))
        button.setText(design_data.get("caption", ""))
        
        button_name = design_data.get("name", "")
        button.control_name = button_name
        function_name = design_data.get("function", "NONE")
        event_handler = self.app.event_distributor(function_name)
        
        if event_handler:
            payment_events = ["CASH_PAYMENT", "CREDIT_PAYMENT", "CHECK_PAYMENT", "EXCHANGE_PAYMENT",
                             "PREPAID_PAYMENT", "CHARGE_SALE_PAYMENT", "OTHER_PAYMENT", "CHANGE_PAYMENT"]
            sale_events = ["SALE_PLU_CODE", "SALE_PLU_BARCODE", "SALE_DEPARTMENT"]
            if function_name in sale_events or function_name in payment_events:
                button.clicked.connect(lambda checked=False, btn=button: event_handler(btn))
            elif function_name.startswith("NAVIGATE_TO_FORM:"):
                parts = function_name.split(':')
                if len(parts) >= 3:
                    target_form_id = parts[1]
                    transition_mode = parts[2]
                    button.clicked.connect(
                        lambda: self.app._navigate_to_form(target_form_id, transition_mode)
                    )
            elif function_name == "CLOSE_FORM":
                button.clicked.connect(self.accept)
            else:
                button.clicked.connect(event_handler)
        
        # PLU button text from product data
        if function_name in ["SALE_PLU_CODE", "SALE_PLU_BARCODE"] and button_name and button_name.upper().startswith("PLU"):
            try:
                code_or_barcode = button_name[3:]
                if function_name == "SALE_PLU_CODE":
                    products = [
                        p for p in self.app.product_data.get("Product", [])
                        if p.code == code_or_barcode and not (hasattr(p, 'is_deleted') and p.is_deleted)
                    ]
                    if products:
                        product = products[0]
                        product_name = product.short_name if product.short_name else product.name
                        button.setText(product_name)
                elif function_name == "SALE_PLU_BARCODE":
                    barcode_records = [
                        pb for pb in self.app.product_data.get("ProductBarcode", [])
                        if pb.barcode == code_or_barcode and not (hasattr(pb, 'is_deleted') and pb.is_deleted)
                    ]
                    if barcode_records:
                        product_barcode = barcode_records[0]
                        products = [
                            p for p in self.app.product_data.get("Product", [])
                            if p.id == product_barcode.fk_product_id
                        ]
                        if products:
                            product = products[0]
                            product_name = product.short_name if product.short_name else product.name
                            button.setText(product_name)
            except Exception:
                pass
        
        if font_auto_height and hasattr(button, '_adjust_font_size'):
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, lambda: button._adjust_font_size())
        
        if parent_panel:
            parent_panel.add_child_control(button)
    
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
        parent_panel = None
        if design_data.get('parent_name'):
            parent_panel = self._panels.get(design_data['parent_name'])
        parent_widget = parent_panel.get_content_widget() if parent_panel else self
        
        label = Label(parent_widget)
        label.setText(design_data.get('caption', ''))
        label.setGeometry(design_data["location_x"], design_data["location_y"],
                         design_data["width"], design_data["height"])
        
        if design_data.get('text_alignment') == "LEFT":
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        elif design_data.get('text_alignment') == "RIGHT":
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        elif design_data.get('text_alignment') == "CENTER":
            label.setAlignment(Qt.AlignCenter)
        else:
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        label.set_color(design_data.get('background_color', 0xFFFFFF),
                        design_data.get('foreground_color', 0x000000))
        
        if design_data.get('font_size'):
            from PySide6.QtGui import QFont
            font = label.font()
            font.setPointSize(int(design_data['font_size']))
            label.setFont(font)
        
        if design_data.get('caption'):
            label.setToolTip(design_data['caption'])
        
        if parent_panel:
            parent_panel.add_child_control(label)

    def _create_textbox(self, design_data):
        """Create a textbox control with optional panel parent and CurrentData loading."""
        parent_panel = None
        if design_data.get('parent_name'):
            parent_panel = self._panels.get(design_data['parent_name'])
        parent_widget = parent_panel.get_content_widget() if parent_panel else self
        
        textbox = TextBox(parent_widget)
        alignment = design_data.get('alignment', 'left').lower()
        if alignment == "left":
            textbox.setAlignment(Qt.AlignLeft)
        elif alignment == "right":
            textbox.setAlignment(Qt.AlignRight)
        elif alignment == "center":
            textbox.setAlignment(Qt.AlignCenter)
        if design_data.get('input_type') == "password":
            textbox.set_password_type()
        
        textbox_name = design_data.get('name') or design_data.get('field_name')
        textbox.__name__ = textbox_name
        textbox.name = textbox_name
        textbox.setGeometry(design_data["location_x"], design_data["location_y"],
                            design_data["width"], design_data["height"])
        textbox.set_font_size(design_data.get('font_size'))
        textbox.field_name = design_data.get('caption')
        if design_data.get('place_holder'):
            textbox.setPlaceholderText(design_data.get('place_holder'))
        textbox.set_color(design_data['background_color'], design_data['foreground_color'])
        if design_data.get('use_keyboard') or parent_panel:
            textbox.keyboard = self.keyboard
        
        if parent_panel:
            parent_panel.add_child_control(textbox)
        
        # Load from CurrentData when textbox is in a panel
        if parent_panel and getattr(parent_panel, 'name', None):
            panel_name = parent_panel.name
            if textbox_name:
                field_name = textbox_name.lower()
                parts = panel_name.lower().split('_')
                model_class_name = ''.join(word.capitalize() for word in parts)
                model_instance = None
                cache_attr_name = None
                if model_class_name == "PosSettings":
                    cache_attr_name = "pos_settings"
                elif model_class_name == "Cashier":
                    cache_attr_name = "cashier_data"
                if cache_attr_name and hasattr(self.app, cache_attr_name):
                    model_instance = getattr(self.app, cache_attr_name)
                    if model_instance and hasattr(model_instance, 'unwrap'):
                        model_instance = model_instance.unwrap()
                if not model_instance:
                    try:
                        import data_layer.model.definition as model_module
                        from data_layer.model.definition import __all__ as model_names
                        if model_class_name in model_names:
                            model_class = getattr(model_module, model_class_name)
                            instances = model_class.get_all(is_deleted=False)
                            if instances:
                                model_instance = instances[0]
                    except Exception:
                        pass
                if model_instance:
                    try:
                        value = getattr(model_instance, field_name, None)
                        if value is not None:
                            textbox.setText(str(value))
                    except Exception:
                        pass
    
    def _create_combobox(self, design_data):
        """Create a combobox control with optional panel parent and item source."""
        parent_panel = None
        if design_data.get('parent_name'):
            parent_panel = self._panels.get(design_data['parent_name'])
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
        
        items = design_data.get("items")
        if items and isinstance(items, list):
            combo.set_items([str(x) for x in items])
        else:
            from data_layer.enums import ControlName, EventName
            name_key = str(design_data.get("name", ""))
            if name_key == ControlName.CASHIER_NAME_LIST.value:
                try:
                    from data_layer.model import Cashier
                    cashiers = Cashier.get_all(is_deleted=False)
                    labels = [f"{c.user_name} ({c.name} {c.last_name})" for c in cashiers]
                    if design_data.get("function1") == EventName.LOGIN.value:
                        labels.append("SUPERVISOR")
                    combo.set_items(labels)
                except Exception:
                    combo.set_items([])
        
        if design_data.get("function"):
            combo.set_event(self.app.event_distributor(design_data["function"]))
        if design_data.get("caption"):
            combo.setToolTip(design_data["caption"])
        if design_data.get("name") is not None:
            combo.name = design_data["name"]
        if design_data.get("type_name") is not None:
            combo.type = design_data["type_name"]
        if design_data.get("function1") is not None:
            combo.function1 = design_data["function1"]
        if design_data.get("function2") is not None:
            combo.function2 = design_data["function2"]
        
        if parent_panel:
            parent_panel.add_child_control(combo)
    
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
        datagrid.set_color(background_color, foreground_color)
        
        if "font_size" in design_data:
            from PySide6.QtGui import QFont
            font = QFont("Verdana", design_data["font_size"])
            datagrid.setFont(font)
        
        if "name" in design_data:
            datagrid.name = design_data["name"]
        if "function" in design_data:
            datagrid.function = design_data["function"]
        if "caption" in design_data:
            datagrid.setToolTip(design_data["caption"])
        
        from data_layer.enums import ControlName
        name_key = str(design_data.get("name", ""))
        if name_key == ControlName.CLOSURE.value:
            try:
                from data_layer.model import Closure, Cashier
                closures = Closure.get_all(is_deleted=False)
                closures = sorted(
                    closures,
                    key=lambda c: c.closure_start_time if c.closure_start_time else c.closure_date,
                    reverse=True
                )
                datagrid.set_columns([
                    "Closure No",
                    "Date",
                    "Cashier",
                    "Gross Sales",
                    "Opening Cash",
                    "Closing Cash"
                ])
                data_rows = []
                for closure in closures:
                    cashier_name = ""
                    if closure.fk_cashier_closed_id:
                        cashier = Cashier.get_by_id(closure.fk_cashier_closed_id)
                        if cashier:
                            cashier_name = cashier.user_name or ""
                    date_str = ""
                    if closure.closure_start_time:
                        date_str = closure.closure_start_time.strftime("%Y-%m-%d %H:%M")
                    elif closure.closure_date:
                        date_str = closure.closure_date.strftime("%Y-%m-%d")
                    def _num(val):
                        return "0.00" if val is None else f"{float(val):.2f}"
                    row = [
                        str(closure.closure_number),
                        date_str,
                        cashier_name,
                        _num(closure.gross_sales_amount),
                        _num(closure.opening_cash_amount),
                        _num(closure.closing_cash_amount)
                    ]
                    data_rows.append(row)
                datagrid.set_data(data_rows)
            except Exception as e:
                import traceback
                logger.exception("Error loading closure data: %s", e)
                datagrid.set_columns(["No Data Available"])
                datagrid.set_data([])
        
        datagrid.show()

    def _create_panel(self, design_data):
        """
        Create a Panel control with scrollbar support.
        
        Args:
            design_data (dict): Design specifications for the panel
        """
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
        
        if "name" in design_data:
            panel.name = design_data["name"]
            if not hasattr(self, '_panels'):
                self._panels = {}
            self._panels[design_data["name"]] = panel
        
        panel.show()

