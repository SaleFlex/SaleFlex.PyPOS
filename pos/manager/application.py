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
from data_layer.db_manager import init_db
from settings import env_data


class Application(CurrentStatus, CurrentData, EventHandler):
    """
    Main Application class for SaleFlex Point of Sale System.
    
    This class implements the Singleton design pattern to ensure only one instance
    of the application exists throughout the program lifecycle. It inherits from
    three manager classes to provide comprehensive functionality:
    
    - CurrentStatus: Manages application state (login status, current forms, document states)
    - CurrentData: Holds session-specific data (document content, cashier information, etc.)
    - EventHandler: Processes user interface events and business logic
    
    The class is responsible for:
    - Database initialization
    - Qt Application setup and configuration
    - User interface management
    - Application lifecycle control
    """
    
    # Class variable to store the singleton instance
    __instance = None

    def __new__(cls, *args, **kwargs):
        """
        Singleton pattern implementation.
        
        Ensures only one instance of the Application class can exist.
        If an instance already exists, returns the existing instance.
        
        Returns:
            Application: The singleton instance of the Application class
        """
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        """
        Initialize the POS Application.
        
        Performs the following initialization steps:
        1. Initialize parent classes (CurrentStatus, CurrentData, EventHandler)
        2. Initialize the database connection and schema
        3. Create and configure the Qt Application instance
        4. Set application branding (name and icon)
        5. Initialize the user interface manager
        
        The initialization follows a specific order to ensure all dependencies
        are properly set up before the interface is created.
        """
        # Initialize parent classes to inherit their functionality
        CurrentStatus.__init__(self)    # Application state management
        CurrentData.__init__(self)      # Session data management  
        EventHandler.__init__(self)     # Event processing capabilities

        # Initialize database connection and create tables if needed
        init_db()
        
        # Create the main Qt application instance
        # Empty list means no command line arguments are passed
        self.app = QApplication([])
        
        # Set the application name (appears in window titles and system menus)
        self.app.setApplicationName("SaleFlex")
        
        # Set application icon if logo file exists
        # Logo path is constructed from the images folder in design_files
        logo_path = os.path.join(env_data.image_absolute_folder, "logo.png")
        
        # Only set the icon if the logo file actually exists to avoid errors
        if os.path.exists(logo_path):
            self.app.setWindowIcon(QIcon(logo_path))
            
        # Initialize the user interface manager
        # Pass self reference so the interface can access application methods
        self.interface = Interface(self)

    def run(self):
        """
        Start the Point of Sale application.
        
        This method:
        1. Draws the initial user interface based on current form type
        2. Starts the Qt event loop
        3. Exits the application when the event loop ends
        
        The current_form_type is inherited from CurrentStatus and determines
        which form (login, sale, configuration, etc.) to display initially.
        
        Note: This method blocks until the application is closed by the user.
        """
        # Draw the initial interface (typically the login form)
        self.interface.draw(self.current_form_type)
        
        # Start the Qt event loop and exit with the same code when it ends
        # This is a blocking call that runs until the application is closed
        sys.exit(self.app.exec())
