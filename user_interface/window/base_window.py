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

from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Qt

from user_interface.control import TextBox, Button, ToolBar, StatusBar, NumPad, PaymentList, SaleList, ComboBox, AmountTable, Label
from user_interface.control import VirtualKeyboard


class BaseWindow(QMainWindow):
    def __init__(self, app):
        super().__init__(parent=None)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.app = app

        self.keyboard = VirtualKeyboard(source=None, parent=self)

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
            if type(item) in [TextBox, Button, Label, ToolBar, StatusBar, NumPad, PaymentList, SaleList, ComboBox, AmountTable]:
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
        
        button = Button(design_data["caption"], self)
        button.setGeometry(design_data["location_x"], design_data["location_y"],
                           design_data["width"], design_data["height"])

        button.set_color(design_data['background_color'], design_data['foreground_color'])
        button.setToolTip(design_data["caption"])
        
        # Get the event handler function
        function_name = design_data.get("function")
        print(f"Calling event_distributor with: '{function_name}'")
        
        event_handler = self.app.event_distributor(function_name)
        print(f"Event handler retrieved: {event_handler}")
        print(f"Event handler type: {type(event_handler)}")
        
        if event_handler:
            print(f"✓ Connecting button '{design_data.get('caption')}' to event handler: {event_handler.__name__}")
            button.clicked.connect(event_handler)
        else:
            print(f"✗ WARNING: No event handler found for function: '{function_name}'")
        print("="*80)

    def _create_numpad(self, design_data):
        print(design_data)
        
        # Ensure numpad has appropriate size to fit all buttons
        width = design_data.get("width", 300)
        height = design_data.get("height", 350)
        
        # Make sure width and height are sufficient for a numpad
        if width < 250:
            width = 300
        if height < 300:
            height = 350
        
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


