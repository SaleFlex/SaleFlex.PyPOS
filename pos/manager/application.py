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

import sys
import os
import time
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from pos.manager.current_status import CurrentStatus
from pos.manager.current_data import CurrentData
from pos.manager.event_handler import EventHandler
from user_interface.manager import Interface
from data_layer.db_manager import init_db
from data_layer.enums import FormName
from settings import env_data
from user_interface.form.about_form import AboutForm
# Model imports are now handled in CurrentData.populate_pos_data()
# Only import models that are used directly in Application class methods
from data_layer.model import Currency, Form


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
        # Create the main Qt application instance as early as possible
        # so that we can show the AboutForm during initialization
        self.app = QApplication([])
        self.app.setApplicationName("SaleFlex")

        # Show AboutForm to provide live initialization feedback
        about = AboutForm()
        about.update_message("Starting application...")
        about.show()
        self.app.processEvents()

        # Initialize parent classes to inherit their functionality
        about.update_message("Initializing application state...")
        self.app.processEvents()
        CurrentStatus.__init__(self)    # Application state management
        CurrentData.__init__(self)      # Session data management
        EventHandler.__init__(self)     # Event processing capabilities

        # Initialize database connection and create tables if needed
        about.update_message("Initializing database...")
        self.app.processEvents()
        init_db()
        
        # Initialize KeyboardSettingsLoader for virtual keyboard settings
        from data_layer.engine import Engine
        from user_interface.control.virtual_keyboard.keyboard_settings_loader import KeyboardSettingsLoader
        keyboard_engine = Engine()
        KeyboardSettingsLoader.initialize(keyboard_engine)

        # Load reference data into memory to reduce disk I/O during runtime
        # This populates pos_data with all reference models (excluding transaction/sales data)
        about.update_message("Loading reference data into memory...")
        self.app.processEvents()
        self.populate_pos_data(progress_callback=lambda msg: about.update_message(msg) or self.app.processEvents())
        
        # Load product-related data into memory to reduce disk I/O during runtime
        # This populates product_data with all product-related models
        about.update_message("Loading product data into memory...")
        self.app.processEvents()
        self.populate_product_data(progress_callback=lambda msg: about.update_message(msg) or self.app.processEvents())

        # Set application icon from settings.toml
        # Icon path is configured in settings.toml under app.icon
        about.update_message("Configuring application UI...")
        self.app.processEvents()
        from settings.settings import Settings
        icon_path = Settings().app_icon
        if icon_path and os.path.exists(icon_path):
            self.app.setWindowIcon(QIcon(icon_path))

        # Initialize the user interface manager
        # Pass self reference so the interface can access application methods
        self.interface = Interface(self)

        # Load startup form from database
        about.update_message("Loading startup form...")
        self.app.processEvents()
        self.load_startup_form()
        
        # Load current currency from PosSettings
        about.update_message("Loading currency settings...")
        self.app.processEvents()
        self.load_current_currency_from_pos_data()

        # Finalize and dispose the AboutForm
        about.update_message("Initialization complete.")
        self.app.processEvents()
        time.sleep(1)
        about.dispose()
    
    def load_current_currency_from_pos_data(self):
        """
        Load the current currency sign from PosSettings using cached pos_settings.
        
        This method loads the currency sign from the cached pos_settings attribute,
        which is more efficient than querying the database directly. The currency
        sign is stored in CurrentData.current_currency.
        """
        try:
            from data_layer.model import Currency
            
            # Use cached pos_settings (already loaded in memory, avoids database read)
            if self.pos_settings:
                settings = self.pos_settings
                if settings.fk_current_currency_id:
                    # Get currency from pos_data (already loaded in memory)
                    all_currencies = self.pos_data.get("Currency", [])
                    currency = next((c for c in all_currencies if c.id == settings.fk_current_currency_id), None)
                    
                    if currency and currency.sign:
                        self.current_currency = currency.sign
                        print(f"✓ Current currency loaded: {self.current_currency}")
                    else:
                        # Default to GBP if currency not found
                        self.current_currency = "GBP"
                        print("✓ Currency not found, defaulting to GBP")
                else:
                    # Default to GBP if not set
                    self.current_currency = "GBP"
                    print("✓ Current currency not set, defaulting to GBP")
            else:
                # Fallback: try pos_data if pos_settings not cached
                pos_settings = self.pos_data.get("PosSettings", [])
                if pos_settings and len(pos_settings) > 0:
                    settings = pos_settings[0]
                    if settings.fk_current_currency_id:
                        all_currencies = self.pos_data.get("Currency", [])
                        currency = next((c for c in all_currencies if c.id == settings.fk_current_currency_id), None)
                        if currency and currency.sign:
                            self.current_currency = currency.sign
                            print(f"✓ Current currency loaded: {self.current_currency}")
                        else:
                            self.current_currency = "GBP"
                            print("✓ Currency not found, defaulting to GBP")
                    else:
                        self.current_currency = "GBP"
                        print("✓ Current currency not set, defaulting to GBP")
                else:
                    # Default to GBP if no settings found
                    self.current_currency = "GBP"
                    print("✓ No POS settings found, defaulting to GBP")
        except Exception as e:
            print(f"Error loading current currency: {e}")
            import traceback
            traceback.print_exc()
            # Default to GBP on error
            self.current_currency = "GBP"

    def run(self):
        """
        Start the Point of Sale application.
        
        This method:
        1. Draws the initial user interface from database startup form
        2. Checks if startup form requires login
        3. If login required, shows LOGIN form first
        4. Starts the Qt event loop
        5. Exits the application when the event loop ends
        
        The startup form is loaded from the database (Form table with is_startup=True).
        If no startup form is found, it falls back to form name 'LOGIN'.
        
        Note: This method blocks until the application is closed by the user.
        """
        # Check if startup form requires login
        startup_form = None
        if self.current_form_id:
            startup_form = Form.get_by_id(self.current_form_id)
        
        # If startup form requires login and user not logged in, show LOGIN first
        if startup_form and startup_form.need_login and not self.login_succeed:
            self.interface.draw(form_name=FormName.LOGIN.name)
        elif self.current_form_id:
            # Use database form ID
            self.interface.draw(form_id=self.current_form_id)
        else:
            # Fallback to LOGIN form using FormName enum
            self.interface.draw(form_name=FormName.LOGIN.name)
        
        # Start the Qt event loop and exit with the same code when it ends
        # This is a blocking call that runs until the application is closed
        sys.exit(self.app.exec())
