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

import os
import sys

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QToolBar
from PySide6.QtGui import QFont, Qt, QIcon

from settings import env_data


class ToolBar(QToolBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFont(QFont("Verdana", 20))
        self.setMovable(False)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setIconSize(QSize(32, 32))
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    def add_event(self, **kwargs):
        if "back_function" in kwargs and "back_function_caption" in kwargs and "back_function_image" in kwargs:
            if kwargs["back_function_image"] == "":
                self.addAction(kwargs["back_function_caption"], kwargs["back_function"])
            else:
                image_path = os.path.join(env_data.image_absolute_folder, kwargs["back_function_image"])
                self.addAction(QIcon(image_path), kwargs["back_function_caption"], kwargs["back_function"])

