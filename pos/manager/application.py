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

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from pos.manager.current_status import CurrentStatus
from pos.manager.current_data import CurrentData
from pos.manager.event_handler import EventHandler
from user_interface.manager import Interface
from data_layer import init_db
from settings import env_data


class Application(CurrentStatus, CurrentData, EventHandler):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        CurrentStatus.__init__(self)
        CurrentData.__init__(self)
        EventHandler.__init__(self)

        init_db()
        self.app = QApplication([])
        self.app.setApplicationName("SaleFlex")
        
        # Logo path from images folder
        logo_path = os.path.join(env_data.image_absolute_folder, "logo.png")
        # Use default icon if logo doesn't exist
        if os.path.exists(logo_path):
            self.app.setWindowIcon(QIcon(logo_path))
            
        self.interface = Interface(self)

    def run(self):
        self.interface.draw(self.current_display_type)
        sys.exit(self.app.exec())
