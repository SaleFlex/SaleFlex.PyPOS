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

from user_interface.control import TextBox, Button, ToolBar, StatusBar, NumPad, PaymentList, SaleList
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

            if control_design_data["type"] == "numpad":
                self._create_numpad(control_design_data)

            if control_design_data["type"] == "payment_list":
                self._create_payment_list(control_design_data)

            if control_design_data["type"] == "sale_list":
                self._create_sale_list(control_design_data)

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
            if type(item) in [TextBox, Button, ToolBar, StatusBar, NumPad, PaymentList, SaleList]:
                print(type(item), item)
                item.deleteLater()
                item.setParent(None)
        self.hide()

    def _create_button(self, design_data):
        print(design_data)
        button = Button(design_data["caption"], self)
        button.setGeometry(design_data["location_x"], design_data["location_y"],
                           design_data["width"], design_data["height"])

        button.set_color(design_data['background_color'], design_data['foreground_color'])
        button.setToolTip(design_data["caption"])
        button.clicked.connect(self.app.event_distributor(design_data["function"]))

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


