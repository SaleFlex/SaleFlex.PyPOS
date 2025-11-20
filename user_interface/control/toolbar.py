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

