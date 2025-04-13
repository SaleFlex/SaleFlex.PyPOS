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
