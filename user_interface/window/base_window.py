"""
SaleFlex.PyPOS - Point of Sale Application

Copyright (c) 2025-2026 Ferhat Mousavi

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

from core.logger import get_logger

logger = get_logger(__name__)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QColor, QLinearGradient, QBrush, QPalette

from user_interface.control import TextBox, CheckBox, Button, ToolBar, StatusBar, NumPad, PaymentList, SaleList, ComboBox, AmountTable, Label, DataGrid, Panel, TabControl
from user_interface.control import VirtualKeyboard


class BaseWindow(QMainWindow):
    def __init__(self, app):
        super().__init__(parent=None)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.app = app

        self.keyboard = VirtualKeyboard(source=None, parent=self)
        # Explicitly hide so Qt's showChildren does not auto-show the keyboard
        # when the window is first displayed (resizeEvent makes it 970×315 and
        # blocks mouse events on the upper portion of the window).
        self.keyboard.hide()

        # Dual-function button registry — populated during draw_window
        self._dual_function_buttons = []
        self._func_mode_active = False

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

    def _reset_all_dual_buttons_to_primary(self):
        """After any dual-function action, return every dual button to state 1 (caption1)."""
        self._func_mode_active = False
        for btn in self._dual_function_buttons:
            btn.reset_to_primary_state()

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

        # Always reset panels/tab dictionaries at the start of each draw so stale
        # references from a previous form do not leak into the new one.
        self._panels = {}
        self._tab_controls = {}
        self._tab_pages = {}   # str(tab_id) → QWidget (tab page)
        self._dual_function_buttons = []
        self._func_mode_active = False

        for control_design_data in design:
            if control_design_data["type"] == "textbox":
                self._create_textbox(control_design_data)

            if control_design_data["type"] == "checkbox":
                self._create_checkbox(control_design_data)

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

            if control_design_data["type"] == "tabcontrol":
                self._create_tab_control(control_design_data)

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
        Get field values from a panel: textbox strings and checkbox true/false strings.
        
        Args:
            panel_name (str): Name of the panel (e.g., "POS_SETTINGS")
            
        Returns:
            dict: Field name (lowercase) -> value (str; checkboxes as "true"/"false")
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
                logger.warning("[GET_PANEL_VALUES] Panel '%s' widget already deleted", panel_name)
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
                    logger.warning("[GET_PANEL_VALUES] Content widget for panel '%s' already deleted", panel_name)
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
                
                for child in content_widget.findChildren(CheckBox):
                    try:
                        _ = child.isChecked()
                    except RuntimeError:
                        continue
                    cb_name = getattr(child, 'name', None) or getattr(child, '__name__', None)
                    if cb_name:
                        field_name = cb_name.lower()
                        values[field_name] = "true" if child.isChecked() else "false"
            except RuntimeError as e:
                # Widget already deleted
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
        """Clear all child controls and hide the window."""
        # Clean up Panel children (parented to panel.content_widget, not the window).
        if hasattr(self, '_panels'):
            for panel in list(self._panels.values()):
                try:
                    for child in list(panel._child_controls):
                        try:
                            child.blockSignals(True)
                            child.setParent(None)
                            child.deleteLater()
                        except RuntimeError:
                            pass
                    panel._child_controls.clear()
                except RuntimeError:
                    pass
            self._panels.clear()

        # Clean up tab-page widgets (parented to TabControl, not the window directly).
        if hasattr(self, '_tab_pages'):
            self._tab_pages.clear()
        if hasattr(self, '_tab_controls'):
            self._tab_controls.clear()

        for item in list(self.children()):
            if type(item) in [TextBox, CheckBox, Button, Label, ToolBar, StatusBar, NumPad, PaymentList, SaleList, ComboBox, AmountTable, DataGrid, Panel, TabControl]:
                try:
                    item.blockSignals(True)
                    item.setParent(None)
                    item.deleteLater()
                except RuntimeError:
                    pass
        self.hide()

    def _create_button(self, design_data):
        # Resolve parent: panel content widget or window
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
        
        function_name = design_data.get("function")
        function2_name = design_data.get("function2")
        caption2 = design_data.get("caption2")
        event_handler = self.app.event_distributor(function_name)

        # Special event categories that pass the button object to the handler
        payment_events = ["CASH_PAYMENT", "CREDIT_PAYMENT", "CHECK_PAYMENT", "EXCHANGE_PAYMENT",
                         "PREPAID_PAYMENT", "CHARGE_SALE_PAYMENT", "OTHER_PAYMENT", "CHANGE_PAYMENT"]
        sale_events = ["SALE_PLU_CODE", "SALE_PLU_BARCODE", "SALE_DEPARTMENT"]
        quantity_events = ["INPUT_QUANTITY", "PLU_INQUIRY"]

        # Dual-function mode: requires function2, caption2, and function1 must not be a
        # sale/PLU event (those buttons derive their text from product data, not caption1)
        is_dual_function = (
            bool(function2_name) and bool(caption2)
            and function_name not in sale_events
        )

        if is_dual_function:
            handler2 = self.app.event_distributor(function2_name)
            caption1 = design_data.get("caption", "")
            button.setup_dual_function(
                caption1,
                caption2,
                event_handler,
                handler2,
                after_action_reset=self._reset_all_dual_buttons_to_primary,
            )
            self._dual_function_buttons.append(button)
        elif button_name == "FUNC":
            # FUNC switches labels only; clicks on dual buttons never toggle captions.
            # Each press flips all dual-function buttons between state 1 and state 2.
            def _func_click(checked=False, win=self):
                win._func_mode_active = not win._func_mode_active
                for btn in win._dual_function_buttons:
                    btn.toggle_state()
            button.clicked.connect(_func_click)
        elif event_handler:
            # Special handling for sale and payment events: pass button object to handler
            # Use default parameter to avoid closure issues
            if function_name in sale_events or function_name in payment_events or function_name in quantity_events:
                button.clicked.connect(lambda checked=False, btn=button: event_handler(btn))
            else:
                button.clicked.connect(event_handler)

        # Hide admin-only buttons for non-administrator users
        if function_name == "ADD_NEW_CASHIER":
            logged_in_cashier = getattr(self.app, 'cashier_data', None)
            if logged_in_cashier and hasattr(logged_in_cashier, 'unwrap'):
                logged_in_cashier = logged_in_cashier.unwrap()
            is_admin = getattr(logged_in_cashier, 'is_administrator', False) if logged_in_cashier else False
            if not is_admin:
                button.hide()

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
                        pass  # Button text set to product name
                    else:
                        pass  # No product found for code
                
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
                            pass  # Button text set to product name
                        else:
                            pass  # Product not found for barcode's product id
                    else:
                        pass  # No product_barcode found for barcode
            except Exception:
                pass
        
        # Trigger font adjustment after button is fully created and sized (only if font_auto_height is True)
        # Use QTimer to ensure button dimensions are set
        if font_auto_height:
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, lambda: button._adjust_font_size() if hasattr(button, '_adjust_font_size') else None)
        
        # Add to panel if parent exists
        if parent_panel:
            parent_panel.add_child_control(button)

    def _create_numpad(self, design_data):
        
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
        # Wire the form function to the Enter-only callback so individual digit
        # presses do NOT accidentally trigger sale/lookup events.
        # set_event (regular callback) is left unset for the numpad in the SALE
        # form; other forms that need per-key callbacks can override this.
        numpad.set_enter_event(self.app.event_distributor(design_data["function"]))

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
        # Ensure sale list has appropriate dimensions
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
        # Resolve parent: panel content widget or window
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
        # Resolve parent: panel content widget or window
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
        textbox.field_name = design_data.get('caption')
        if design_data.get('place_holder'):
            textbox.setPlaceholderText(design_data.get('place_holder'))
        textbox.set_color(design_data['background_color'], design_data['foreground_color'])
        # Set keyboard for textbox - always enable for panel textboxes or if use_keyboard is True
        if design_data.get('use_keyboard') or parent_panel:
            textbox.keyboard = self.keyboard

        # If form_control_function1 is set (and not NONE), wire ENTER key to trigger that event
        function_name = design_data.get('function')
        if function_name and function_name.upper() != 'NONE':
            enter_handler = self.app.event_distributor(function_name)
            if enter_handler:
                textbox.enter_function = enter_handler

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
                    # Prefer editing_cashier (set when entering the cashier management form)
                    # so that admin changes are reflected when selecting different cashiers
                    editing = getattr(self.app, '_editing_cashier', None)
                    cache_attr_name = None
                    model_instance = editing or getattr(self.app, 'cashier_data', None)
                    if model_instance and hasattr(model_instance, 'unwrap'):
                        model_instance = model_instance.unwrap()
                
                if cache_attr_name and hasattr(self.app, cache_attr_name):
                    model_instance = getattr(self.app, cache_attr_name)
                    if model_instance:
                        # Unwrap if it's an AutoSaveModel
                        if hasattr(model_instance, 'unwrap'):
                            model_instance = model_instance.unwrap()
                
                # If not in cache, try loyalty settings rows or first DB row
                if not model_instance:
                    if model_class_name in ("LoyaltyProgram", "LoyaltyProgramPolicy", "LoyaltyRedemptionPolicy"):
                        try:
                            from pos.service.loyalty_settings_model import get_settings_form_loyalty_instance
                            model_instance = get_settings_form_loyalty_instance(model_class_name)
                        except Exception as e:
                            logger.error("[LOAD_DATA] Error loading loyalty settings model %s: %s", model_class_name, e)
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
                        logger.error("[LOAD_DATA] Error loading model class %s: %s", model_class_name, e)
                
                # Load value from model instance
                if model_instance:
                    try:
                        value = getattr(model_instance, field_name, None)
                        if value is not None:
                            # Convert to string for textbox
                            textbox.setText(str(value))
                            logger.debug("[LOAD_DATA] Loaded %s = %s into textbox '%s' (panel: %s, model: %s)", field_name, value, textbox_name, panel_name, model_class_name)
                    except Exception as e:
                        logger.error("[LOAD_DATA] Error loading %s from %s: %s", field_name, model_class_name, e)
                    
                    # Read-only rules for Cashier panel:
                    # - Logged-in admin (is_administrator==True) -> all fields editable
                    # - Non-admin logged-in cashier              -> only password editable, rest read-only
                    if model_class_name == "Cashier":
                        logged_in_cashier = getattr(self.app, 'cashier_data', None)
                        if logged_in_cashier and hasattr(logged_in_cashier, 'unwrap'):
                            logged_in_cashier = logged_in_cashier.unwrap()
                        is_logged_in_admin = getattr(logged_in_cashier, 'is_administrator', False) if logged_in_cashier else False
                        is_password_field = design_data.get('input_type') == 'password'
                        if not is_logged_in_admin and not is_password_field:
                            textbox.setReadOnly(True)
                            textbox.setStyleSheet(
                                textbox.styleSheet() +
                                "QLineEdit { background-color: #D3D3D3; color: #555555; }"
                            )

    def _create_checkbox(self, design_data):
        parent_panel = None
        if 'parent_name' in design_data and design_data['parent_name']:
            parent_panel = self._panels.get(design_data['parent_name'])
        parent_widget = parent_panel.get_content_widget() if parent_panel else self

        checkbox = CheckBox(parent_widget)
        cb_name = design_data.get('name') or design_data.get('field_name')
        checkbox.__name__ = cb_name
        checkbox.name = cb_name
        checkbox.setGeometry(
            design_data["location_x"],
            design_data["location_y"],
            design_data["width"],
            design_data["height"],
        )
        checkbox.set_font_size(design_data.get('font_size'))
        checkbox.field_name = design_data.get('caption', '')
        if design_data.get('caption'):
            checkbox.setText(design_data['caption'])
        checkbox.set_color(
            design_data.get('background_color', 0xFFFFFF),
            design_data.get('foreground_color', 0x000000),
        )
        if parent_panel:
            parent_panel.add_child_control(checkbox)

        if parent_panel and hasattr(parent_panel, 'name') and parent_panel.name and cb_name:
            panel_name = parent_panel.name
            field_name = cb_name.lower()
            parts = panel_name.lower().split('_')
            model_class_name = ''.join(word.capitalize() for word in parts)
            model_instance = None
            cache_attr_name = None
            if model_class_name == "PosSettings":
                cache_attr_name = "pos_settings"
            elif model_class_name == "Cashier":
                editing = getattr(self.app, '_editing_cashier', None)
                cache_attr_name = None
                model_instance = editing or getattr(self.app, 'cashier_data', None)
                if model_instance and hasattr(model_instance, 'unwrap'):
                    model_instance = model_instance.unwrap()
            if cache_attr_name and hasattr(self.app, cache_attr_name):
                model_instance = getattr(self.app, cache_attr_name)
                if model_instance and hasattr(model_instance, 'unwrap'):
                    model_instance = model_instance.unwrap()
            if not model_instance:
                if model_class_name in ("LoyaltyProgram", "LoyaltyProgramPolicy", "LoyaltyRedemptionPolicy"):
                    try:
                        from pos.service.loyalty_settings_model import get_settings_form_loyalty_instance
                        model_instance = get_settings_form_loyalty_instance(model_class_name)
                    except Exception as e:
                        logger.error("[LOAD_DATA] Error loading loyalty settings model %s: %s", model_class_name, e)
            if not model_instance:
                try:
                    from data_layer.model.definition import __all__ as model_names
                    import data_layer.model.definition as model_module
                    if model_class_name in model_names:
                        model_class = getattr(model_module, model_class_name)
                        instances = model_class.get_all(is_deleted=False)
                        if instances and len(instances) > 0:
                            model_instance = instances[0]
                except Exception as e:
                    logger.error("[LOAD_DATA] Error loading model class %s: %s", model_class_name, e)
            if model_instance:
                try:
                    value = getattr(model_instance, field_name, None)
                    checkbox.setChecked(bool(value) if value is not None else False)
                except Exception as e:
                    logger.error("[LOAD_DATA] Error loading %s from %s: %s", field_name, model_class_name, e)
                if model_class_name == "Cashier":
                    logged_in_cashier = getattr(self.app, 'cashier_data', None)
                    if logged_in_cashier and hasattr(logged_in_cashier, 'unwrap'):
                        logged_in_cashier = logged_in_cashier.unwrap()
                    is_logged_in_admin = getattr(logged_in_cashier, 'is_administrator', False) if logged_in_cashier else False
                    if not is_logged_in_admin and field_name in ('is_administrator', 'is_active'):
                        checkbox.setEnabled(False)

    def _create_combobox(self, design_data):
        # Resolve parent: panel content widget or window
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
            
            elif name_key == ControlName.CASHIER_MGMT_LIST.value:
                try:
                    from data_layer.model import Cashier
                    logged_in = getattr(self.app, 'cashier_data', None)
                    if logged_in and hasattr(logged_in, 'unwrap'):
                        logged_in = logged_in.unwrap()
                    is_admin = logged_in.is_administrator if logged_in else False
                    cashiers = Cashier.get_all(is_deleted=False) if is_admin else (
                        [logged_in] if logged_in else []
                    )
                    labels = [f"{c.user_name} ({c.name} {c.last_name})" for c in cashiers]
                    # Block signals during population to prevent spurious SELECT_CASHIER events
                    combo.blockSignals(True)
                    combo.set_items(labels)
                    # Pre-select the current editing cashier
                    editing = getattr(self.app, '_editing_cashier', None)
                    if editing:
                        target = f"{editing.user_name} ({editing.name} {editing.last_name})"
                        idx = labels.index(target) if target in labels else 0
                        combo.setCurrentIndex(idx)
                    combo.blockSignals(False)
                except Exception:
                    combo.blockSignals(False)
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

        If ``design_data`` contains a ``tab_id`` key the grid is parented to the
        corresponding tab-page ``QWidget`` (looked up in ``self._tab_pages``).
        Otherwise it is parented directly to the window.

        Args:
            design_data (dict): Design specifications for the datagrid
        """
        width = design_data.get("width", 600)
        height = design_data.get("height", 400)
        background_color = design_data.get("background_color", 0xFFFFFF)
        foreground_color = design_data.get("foreground_color", 0x000000)

        # Determine parent widget (tab page or window)
        parent_widget = self
        tab_id = design_data.get("tab_id")
        if tab_id and hasattr(self, "_tab_pages"):
            tab_page = self._tab_pages.get(tab_id)
            if tab_page:
                parent_widget = tab_page

        datagrid = DataGrid(parent_widget)
        # If the parent tab page has a layout, add the DataGrid to it so it
        # stretches to fill the page.  Otherwise fall back to absolute geometry.
        if parent_widget is not self and parent_widget.layout() is not None:
            parent_widget.layout().addWidget(datagrid)
        else:
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
        
        # Auto-populate data if this is the CLOSURE datagrid (from data_layer.model.definition.closure)
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
                closure_ids = []
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
                        if val is None:
                            return "0.00"
                        return f"{float(val):.2f}"

                    row = [
                        str(closure.closure_number),
                        date_str,
                        cashier_name,
                        _num(closure.gross_sales_amount),
                        _num(closure.opening_cash_amount),
                        _num(closure.closing_cash_amount)
                    ]
                    data_rows.append(row)
                    closure_ids.append(str(closure.id))

                datagrid.set_data(data_rows)
                datagrid._closure_ids = closure_ids

            except Exception as e:
                import traceback
                logger.exception("Error loading closure data: %s", e)
                datagrid.set_columns(["No Data Available"])
                datagrid.set_data([])
                datagrid._closure_ids = []

        elif name_key == ControlName.CLOSURE_DETAIL_GRID.value:
            self._populate_closure_detail_grid(datagrid)

        elif name_key == ControlName.CLOSURE_RECEIPTS_DATAGRID.value:
            self._populate_closure_receipts_grid(datagrid)

        elif name_key == ControlName.CLOSURE_RECEIPT_DETAIL_GRID.value:
            self._populate_closure_receipt_detail_grid(datagrid)

        elif name_key == ControlName.CLOSURE_RECEIPT_ITEMS_GRID.value:
            self._populate_closure_receipt_items_grid(datagrid)

        elif name_key == ControlName.SUSPENDED_SALES_DATAGRID.value:
            try:
                cols, data_rows = self.app.get_suspended_market_receipt_rows()
                datagrid.set_columns(cols)
                datagrid.set_data(data_rows)
                datagrid.setColumnHidden(0, True)
            except Exception as e:
                logger.exception("Error loading suspended sales list: %s", e)
                datagrid.set_columns(["No Data Available"])
                datagrid.set_data([])

        elif name_key == ControlName.PRODUCT_LIST_DATAGRID.value:
            # Start with column headers only; rows are populated by PRODUCT_SEARCH event
            datagrid.set_columns(["Code", "Name", "Short Name", "Sale Price", "Stock"])
            datagrid.set_data([])
            datagrid._product_ids = []

        elif name_key == ControlName.PRODUCT_INFO_GRID.value:
            self._populate_product_info_grid(datagrid)

        elif name_key == ControlName.PRODUCT_BARCODE_GRID.value:
            self._populate_product_barcode_grid(datagrid)

        elif name_key == ControlName.PRODUCT_ATTRIBUTE_GRID.value:
            self._populate_product_attribute_grid(datagrid)

        elif name_key == ControlName.PRODUCT_VARIANT_GRID.value:
            self._populate_product_variant_grid(datagrid)

        datagrid.show()

    # ------------------------------------------------------------------ #
    # Product-detail grid helpers                                         #
    # ------------------------------------------------------------------ #

    def _get_current_product(self):
        """Return the Product for ``self.app.current_product_id``, or None."""
        product_id = getattr(self.app, "current_product_id", None)
        if not product_id:
            return None
        try:
            from uuid import UUID as _UUID
            from data_layer.model import Product
            # SQLAlchemy's UUID column type requires a uuid.UUID object, not a plain
            # string, otherwise it fails with 'str has no attribute .hex'.
            if isinstance(product_id, str):
                product_id = _UUID(product_id)
            return Product.get_by_id(product_id)
        except Exception as exc:
            logger.exception("[PRODUCT_DETAIL] Error loading product: %s", exc)
            return None

    def _populate_product_info_grid(self, datagrid):
        """Fill the Product-Info tab grid with key/value rows."""
        product = self._get_current_product()
        datagrid.set_columns(["Field", "Value"])
        if not product:
            datagrid.set_data([])
            return
        try:
            from data_layer.model import ProductUnit, ProductManufacturer

            from uuid import UUID as _UUID

            def _to_uuid(val):
                if val is None:
                    return None
                return _UUID(str(val)) if not isinstance(val, _UUID) else val

            unit = None
            if getattr(product, "fk_product_unit_id", None):
                unit = ProductUnit.get_by_id(_to_uuid(product.fk_product_unit_id))

            # The FK column on Product is fk_manufacturer_id (not fk_product_manufacturer_id)
            mfr = None
            if getattr(product, "fk_manufacturer_id", None):
                mfr = ProductManufacturer.get_by_id(_to_uuid(product.fk_manufacturer_id))

            def _fmt(val):
                if val is None:
                    return ""
                try:
                    return f"{float(val):.2f}"
                except (TypeError, ValueError):
                    return str(val)

            rows = [
                ["Code",           product.code or ""],
                ["Name",           product.name or ""],
                ["Short Name",     product.short_name or ""],
                ["Sale Price",     _fmt(product.sale_price)],
                ["Purchase Price", _fmt(product.purchase_price)],
                ["Stock",          str(product.stock) if product.stock is not None else ""],
                ["Min Stock",      str(product.min_stock) if product.min_stock is not None else ""],
                ["Max Stock",      str(product.max_stock) if product.max_stock is not None else ""],
                ["Unit",           unit.name if unit else ""],
                ["Manufacturer",   mfr.name if mfr else ""],
            ]
            datagrid.set_data(rows)
        except Exception as exc:
            logger.exception("[PRODUCT_INFO_GRID] Error loading data: %s", exc)
            datagrid.set_data([])

    def _populate_product_barcode_grid(self, datagrid):
        """Fill the Barcodes tab grid."""
        product = self._get_current_product()
        datagrid.set_columns(["Barcode", "Old Barcode", "Purchase Price", "Sale Price"])
        if not product:
            datagrid.set_data([])
            return
        try:
            from data_layer.model import ProductBarcode
            barcodes = [b for b in ProductBarcode.get_all(is_deleted=False)
                        if str(b.fk_product_id) == str(product.id)]
            rows = [
                [
                    b.barcode or "",
                    b.old_barcode or "",
                    f"{float(b.purchase_price):.2f}" if b.purchase_price else "",
                    f"{float(b.sale_price):.2f}" if b.sale_price else "",
                ]
                for b in barcodes
            ]
            datagrid.set_data(rows)
        except Exception as exc:
            logger.exception("[PRODUCT_BARCODE_GRID] Error loading data: %s", exc)
            datagrid.set_data([])

    def _populate_product_attribute_grid(self, datagrid):
        """Fill the Attributes tab grid."""
        product = self._get_current_product()
        datagrid.set_columns(["Attribute", "Value", "Category", "Unit"])
        if not product:
            datagrid.set_data([])
            return
        try:
            from data_layer.model import ProductAttribute
            attrs = [a for a in ProductAttribute.get_all(is_deleted=False)
                     if str(a.fk_product_id) == str(product.id)]
            attrs.sort(key=lambda a: (a.display_order or 0, a.attribute_name or ""))
            rows = [
                [
                    a.display_name or a.attribute_name or "",
                    a.attribute_value or "",
                    a.category or "",
                    a.unit or "",
                ]
                for a in attrs
            ]
            datagrid.set_data(rows)
        except Exception as exc:
            logger.exception("[PRODUCT_ATTRIBUTE_GRID] Error loading data: %s", exc)
            datagrid.set_data([])

    def _populate_product_variant_grid(self, datagrid):
        """Fill the Variants tab grid."""
        product = self._get_current_product()
        datagrid.set_columns(["Name", "Code", "Color", "Size", "Additional Info"])
        if not product:
            datagrid.set_data([])
            return
        try:
            from data_layer.model import ProductVariant
            variants = [v for v in ProductVariant.get_all(is_deleted=False)
                        if str(v.fk_product_id) == str(product.id)]
            rows = [
                [
                    v.variant_name or "",
                    v.variant_code or "",
                    v.color or "",
                    v.size or "",
                    v.additional_info or "",
                ]
                for v in variants
            ]
            datagrid.set_data(rows)
        except Exception as exc:
            logger.exception("[PRODUCT_VARIANT_GRID] Error loading data: %s", exc)
            datagrid.set_data([])

    def _create_panel(self, design_data):
        """
        Create a Panel control with scrollbar support.

        If ``design_data`` contains ``tab_id``, parent the panel to that tab page
        (SETTING / PRODUCT_DETAIL / CUSTOMER_DETAIL pattern).
        """
        width = design_data.get("width", 800)
        height = design_data.get("height", 600)
        background_color = design_data.get("background_color", 0xFFFFFF)
        foreground_color = design_data.get("foreground_color", 0x000000)

        parent_widget = self
        tab_id = design_data.get("tab_id")
        if tab_id and hasattr(self, "_tab_pages"):
            tab_page = self._tab_pages.get(tab_id)
            if tab_page:
                parent_widget = tab_page

        panel = Panel(
            parent_widget,
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
            self._panels[design_data["name"]] = panel  # noqa: always reset in draw_window

        if parent_widget is not self and parent_widget.layout() is not None:
            parent_widget.layout().addWidget(panel)

        panel.show()

    def _create_tab_control(self, design_data):
        """
        Create a TabControl widget and populate its tab pages from DB definitions.

        Tab page ``QWidget`` instances are stored in ``self._tab_pages`` keyed by
        their ``form_control_tab.id`` (string) so that child controls added in
        subsequent ``_create_*`` calls can look up the correct parent widget.

        Each tab page is given a ``QVBoxLayout`` so child DataGrids fill it
        automatically without needing explicit geometry.

        Args:
            design_data (dict): Design specifications from the form renderer.
                                Expects a ``tabs`` list produced by
                                ``DynamicFormRenderer._load_tabs_for_control``.
        """
        from PySide6.QtWidgets import QWidget, QVBoxLayout

        width = design_data.get("width", 900)
        height = design_data.get("height", 500)
        background_color = design_data.get("background_color", 0x2F4F4F)
        foreground_color = design_data.get("foreground_color", 0xFFFFFF)
        font_size = int(design_data.get("font_size", 12))

        tab_ctrl = TabControl(
            self,
            width=width,
            height=height,
            location_x=design_data.get("location_x", 0),
            location_y=design_data.get("location_y", 0),
            background_color=background_color,
            foreground_color=foreground_color,
            font_size=font_size,
        )

        ctrl_name = design_data.get("name", "")
        if ctrl_name:
            tab_ctrl.name = ctrl_name
            if not hasattr(self, "_tab_controls"):
                self._tab_controls = {}
            self._tab_controls[ctrl_name] = tab_ctrl

        if not hasattr(self, "_tab_pages"):
            self._tab_pages = {}

        # Create one QWidget page per FormControlTab definition
        for tab_info in sorted(design_data.get("tabs", []), key=lambda t: t["tab_index"]):
            page = QWidget()
            page.setObjectName(f"tab_page_{tab_info['tab_index']}")
            # Use a layout so the child DataGrid stretches to fill the page
            layout = QVBoxLayout(page)
            layout.setContentsMargins(2, 2, 2, 2)
            layout.setSpacing(0)
            tab_ctrl.add_tab(page, tab_info["tab_title"])
            if tab_info.get("id"):
                self._tab_pages[tab_info["id"]] = page

        tab_ctrl.show()

    # ------------------------------------------------------------------ #
    # Closure-detail / receipts grid helpers                              #
    # ------------------------------------------------------------------ #

    def _populate_closure_detail_grid(self, datagrid):
        """
        Fill the CLOSURE_DETAIL datagrid with key/value rows for the closure
        identified by ``self.app.current_closure_id``.
        """
        datagrid.set_columns(["Field", "Value"])
        closure_id = getattr(self.app, "current_closure_id", None)
        if not closure_id:
            datagrid.set_data([])
            return
        try:
            from uuid import UUID as _UUID
            from data_layer.model import Closure, Cashier

            if isinstance(closure_id, str):
                closure_id = _UUID(closure_id)
            closure = Closure.get_by_id(closure_id)
            if not closure:
                datagrid.set_data([])
                return

            def _num(val):
                if val is None:
                    return "0.00"
                try:
                    return f"{float(val):.2f}"
                except (TypeError, ValueError):
                    return str(val)

            opened_by = ""
            if getattr(closure, "fk_cashier_opened_id", None):
                c = Cashier.get_by_id(closure.fk_cashier_opened_id)
                if c:
                    opened_by = c.user_name or ""

            closed_by = ""
            if getattr(closure, "fk_cashier_closed_id", None):
                c = Cashier.get_by_id(closure.fk_cashier_closed_id)
                if c:
                    closed_by = c.user_name or ""

            start_str = ""
            if closure.closure_start_time:
                start_str = closure.closure_start_time.strftime("%Y-%m-%d %H:%M:%S")
            end_str = ""
            if closure.closure_end_time:
                end_str = closure.closure_end_time.strftime("%Y-%m-%d %H:%M:%S")

            rows = [
                ["Closure No",              str(closure.closure_number or "")],
                ["Unique ID",               closure.closure_unique_id or ""],
                ["Date",                    str(closure.closure_date or "")],
                ["Start Time",              start_str],
                ["End Time",                end_str],
                ["Opened By",               opened_by],
                ["Closed By",               closed_by],
                ["Total Documents",         str(closure.total_document_count or 0)],
                ["Valid Transactions",       str(closure.valid_transaction_count or 0)],
                ["Cancelled Transactions",  str(closure.canceled_transaction_count or 0)],
                ["Return Transactions",     str(closure.return_transaction_count or 0)],
                ["Suspended Transactions",  str(closure.suspended_transaction_count or 0)],
                ["Gross Sales",             _num(closure.gross_sales_amount)],
                ["Net Sales",               _num(closure.net_sales_amount)],
                ["Total Tax",               _num(closure.total_tax_amount)],
                ["Total Discount",          _num(closure.total_discount_amount)],
                ["Total Tip",               _num(closure.total_tip_amount)],
                ["Opening Cash",            _num(closure.opening_cash_amount)],
                ["Closing Cash",            _num(closure.closing_cash_amount)],
                ["Expected Cash",           _num(closure.expected_cash_amount)],
                ["Cash Difference",         _num(closure.cash_difference)],
            ]
            datagrid.set_data(rows)
        except Exception as exc:
            logger.exception("[CLOSURE_DETAIL_GRID] Error: %s", exc)
            datagrid.set_data([])

    def _populate_closure_receipts_grid(self, datagrid):
        """
        Fill the CLOSURE_RECEIPTS datagrid with transaction heads that belong to
        the closure identified by ``self.app.current_closure_id``.

        Also stores the ordered receipt UUID list as ``datagrid._receipt_ids``.
        """
        datagrid.set_columns([
            "Receipt No", "Date/Time", "Type", "Total", "Payment", "Change", "Status"
        ])
        closure_id = getattr(self.app, "current_closure_id", None)
        if not closure_id:
            datagrid.set_data([])
            datagrid._receipt_ids = []
            return
        try:
            from uuid import UUID as _UUID
            from data_layer.model import Closure, TransactionHead

            if isinstance(closure_id, str):
                closure_id = _UUID(closure_id)
            closure = Closure.get_by_id(closure_id)
            if not closure:
                datagrid.set_data([])
                datagrid._receipt_ids = []
                return

            heads = TransactionHead.filter_by(
                closure_number=closure.closure_number,
                is_deleted=False,
            ) or []
            heads = sorted(
                heads,
                key=lambda h: h.transaction_date_time if h.transaction_date_time else h.receipt_number,
                reverse=False,
            )

            def _num(val):
                if val is None:
                    return "0.00"
                try:
                    return f"{float(val):.2f}"
                except (TypeError, ValueError):
                    return str(val)

            data_rows = []
            receipt_ids = []
            for head in heads:
                dt_str = ""
                if head.transaction_date_time:
                    dt_str = head.transaction_date_time.strftime("%Y-%m-%d %H:%M")
                data_rows.append([
                    str(head.receipt_number or ""),
                    dt_str,
                    head.document_type or "",
                    _num(head.total_amount),
                    _num(head.total_payment_amount),
                    _num(head.total_change_amount),
                    head.transaction_status or "",
                ])
                receipt_ids.append(str(head.id))

            datagrid.set_data(data_rows)
            datagrid._receipt_ids = receipt_ids
        except Exception as exc:
            logger.exception("[CLOSURE_RECEIPTS_GRID] Error: %s", exc)
            datagrid.set_data([])
            datagrid._receipt_ids = []

    def _populate_closure_receipt_detail_grid(self, datagrid):
        """
        Fill the upper CLOSURE_RECEIPT_DETAIL_GRID with key/value header rows for
        the receipt (TransactionHead) identified by ``self.app.current_receipt_id``.
        Only receipt-level summary fields are shown here; line items are in the
        separate CLOSURE_RECEIPT_ITEMS_GRID below.

        Uses a direct session query to avoid detached-object UUID comparison issues.
        """
        datagrid.set_columns(["Field", "Value"])
        receipt_id = getattr(self.app, "current_receipt_id", None)
        if not receipt_id:
            datagrid.set_data([])
            return
        try:
            from data_layer.engine import Engine
            from data_layer.model.definition.transaction_head import TransactionHead

            def _num(val):
                if val is None:
                    return "0.00"
                try:
                    return f"{float(val):.2f}"
                except (TypeError, ValueError):
                    return str(val)

            from uuid import UUID as _UUID
            receipt_uuid = _UUID(str(receipt_id)) if not isinstance(receipt_id, _UUID) else receipt_id
            engine = Engine()
            with engine.get_session() as session:
                head = session.query(TransactionHead).filter(
                    TransactionHead.id == receipt_uuid
                ).first()

                if not head:
                    datagrid.set_data([])
                    return

                dt_str = head.transaction_date_time.strftime("%Y-%m-%d %H:%M:%S") if head.transaction_date_time else ""

                rows = [
                    ["Receipt No",      str(head.receipt_number or "")],
                    ["Unique ID",       head.transaction_unique_id or ""],
                    ["Date/Time",       dt_str],
                    ["Document Type",   head.document_type or ""],
                    ["Trans. Type",     head.transaction_type or ""],
                    ["Status",          head.transaction_status or ""],
                    ["Closure No",      str(head.closure_number or "")],
                    ["Currency",        head.base_currency or ""],
                    ["Total Amount",    _num(head.total_amount)],
                    ["Tax Amount",      _num(head.total_vat_amount)],
                    ["Discount",        _num(head.total_discount_amount)],
                    ["Surcharge",       _num(head.total_surcharge_amount)],
                    ["Payment Total",   _num(head.total_payment_amount)],
                    ["Change",          _num(head.total_change_amount)],
                    ["Tip",             _num(head.tip_amount)],
                ]

            datagrid.set_data(rows)
        except Exception as exc:
            logger.exception("[CLOSURE_RECEIPT_DETAIL_GRID] Error: %s", exc)
            datagrid.set_data([])

    def _populate_closure_receipt_items_grid(self, datagrid):
        """
        Fill the lower CLOSURE_RECEIPT_ITEMS_GRID with the sold line items
        (TransactionProduct rows) for the receipt identified by
        ``self.app.current_receipt_id``.

        Columns: #, Product, Code, Qty, Unit, Unit Price, Discount, VAT%, Total, Status
        Cancelled lines (is_cancel=True) are still shown but marked as "CANCELLED".

        Uses a direct session query with the receipt UUID as a string to avoid
        detached-object UUID comparison issues.
        """
        datagrid.set_columns([
            "#", "Product", "Code", "Qty", "Unit",
            "Unit Price", "Discount", "VAT%", "Total", "Status"
        ])
        receipt_id = getattr(self.app, "current_receipt_id", None)
        if not receipt_id:
            datagrid.set_data([])
            return
        try:
            from data_layer.engine import Engine
            from data_layer.model.definition.transaction_head import TransactionHead
            from data_layer.model.definition.transaction_product import TransactionProduct

            def _num(val, decimals=2):
                if val is None:
                    return "0.00"
                try:
                    return f"{float(val):.{decimals}f}"
                except (TypeError, ValueError):
                    return str(val)

            from uuid import UUID as _UUID
            from data_layer.model.definition.transaction_head import TransactionHead
            from data_layer.model.definition.transaction_head_temp import TransactionHeadTemp
            from data_layer.model.definition.transaction_product_temp import TransactionProductTemp
            receipt_uuid = _UUID(str(receipt_id)) if not isinstance(receipt_id, _UUID) else receipt_id
            engine = Engine()
            with engine.get_session() as session:
                # Primary: permanent transaction_product table
                products = (
                    session.query(TransactionProduct)
                    .filter(
                        TransactionProduct.fk_transaction_head_id == receipt_uuid,
                        TransactionProduct.is_deleted != True,
                    )
                    .order_by(TransactionProduct.line_no)
                    .all()
                )

                # Fallback: temp table using receipt_number + closure_number to find the
                # matching temp head (permanent finalization creates a new UUID for the head
                # so the FK in temp products points to the original temp head ID)
                if not products:
                    perm_head = session.query(TransactionHead).filter(
                        TransactionHead.id == receipt_uuid
                    ).first()
                    if perm_head:
                        temp_head = session.query(TransactionHeadTemp).filter(
                            TransactionHeadTemp.receipt_number == perm_head.receipt_number,
                            TransactionHeadTemp.closure_number == perm_head.closure_number,
                        ).first()
                        if temp_head:
                            products = (
                                session.query(TransactionProductTemp)
                                .filter(
                                    TransactionProductTemp.fk_transaction_head_id == temp_head.id,
                                    TransactionProductTemp.is_deleted != True,
                                )
                                .order_by(TransactionProductTemp.line_no)
                                .all()
                            )

                data_rows = []
                for prod in products:
                    status = "CANCELLED" if getattr(prod, "is_cancel", False) else "OK"
                    data_rows.append([
                        str(prod.line_no or ""),
                        prod.product_name or "",
                        prod.product_code or "",
                        _num(prod.quantity, 3),
                        prod.unit_of_measure or "EA",
                        _num(prod.unit_price),
                        _num(prod.unit_discount),
                        _num(prod.vat_rate, 1),
                        _num(prod.total_price),
                        status,
                    ])

            datagrid.set_data(data_rows)
        except Exception as exc:
            logger.exception("[CLOSURE_RECEIPT_ITEMS_GRID] Error: %s", exc)
            datagrid.set_data([])

