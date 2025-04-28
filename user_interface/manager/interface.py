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

from user_interface.window import BaseWindow
from pos.data import FormType
from user_interface.design_file import Interpreter


class Interface:
    def __init__(self, app):
        self.app = app
        self.window = BaseWindow(app=self.app)

    def draw(self, form_type: FormType):
        interpreter = Interpreter(form_type)
        self.window.draw_window(interpreter.settings, interpreter.toolbar_settings, interpreter.design)
        self.window.show()
        self.window.focus_text_box()

    def redraw(self, form_type: FormType):
        self.window.clear()
        self.draw(form_type)
