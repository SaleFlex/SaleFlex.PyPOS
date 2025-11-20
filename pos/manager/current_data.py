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

from data_layer.model import (
    Cashier,
    City,
    Country,
    Currency,
    CurrencyTable,
    District,
    Form,
    FormControl,
    LabelValue,
    PaymentType,
    PosSettings,
    PosVirtualKeyboard,
    ReceiptFooter,
    ReceiptHeader,
    Store,
    Table,
    Vat,
)


class CurrentData:
    """
    Session Data Manager for SaleFlex Point of Sale System.
    
    This class is responsible for holding and managing session-specific data
    that persists throughout the user's current session but is cleared when
    the application restarts or the user logs out.
    
    The class serves as a centralized data container for:
    - Current cashier information and authentication details
    - Active document/transaction data being processed
    - Cached reference data (pos_data) loaded once at startup to minimize disk I/O
    - Temporary session state that needs to be shared across components
    
    Key Features:
    - pos_data: Dictionary containing all reference data models (Cashier, City, Country,
      Currency, CurrencyTable, District, Form, FormControl, LabelValue, PaymentType,
      PosSettings, PosVirtualKeyboard, ReceiptFooter, ReceiptHeader, Store, Table, Vat)
      loaded once at application startup to avoid repeated database reads
    - Cache synchronization: When reference data is modified, pos_data cache is automatically
      updated to stay synchronized with database
    
    This class is designed to be inherited by the main Application class,
    providing session data access throughout the application lifecycle.
    
    Attributes:
        cashier_data: Information about the currently logged-in cashier (set during login)
        document_data: Current transaction/document being processed
        pos_data: Dictionary of cached reference data models (populated at startup)
        pos_settings: POS settings object (cached reference from pos_data)
        current_currency: Current currency sign (e.g., "GBP", "USD")
    
    Methods:
        populate_pos_data: Load all reference data models into pos_data cache
        update_pos_data_cache: Update cache when a model instance is modified
        refresh_pos_data_model: Reload a specific model's data from database
    """
    
    def __init__(self):
        """
        Initialize the session data container.
        
        Sets all session data attributes to None, indicating that no user
        is currently logged in and no document is being processed.
        
        These attributes will be populated when:
        - cashier_data: Set during successful login process
        - document_data: Set when starting a new transaction/document
        - pos_data: Populated after database initialization with rarely-changing
          reference data to reduce disk I/O during runtime
        - pos_settings: Loaded from pos_data after database initialization (cached)
        - current_currency: Loaded from PosSettings after database initialization
        """
        # Information about the currently logged-in cashier
        # Contains user details, permissions, and authentication status
        self.cashier_data = None
        
        # Current transaction or document being processed
        # Holds the active sale, return, or other document data
        self.document_data = None

        # Cached reference data loaded at startup (after DB init)
        # Example keys: "Cashier", "City", "Country", ...
        self.pos_data = {}
        
        # POS settings object (cached to avoid repeated database reads)
        # Will be populated from pos_data after database initialization
        self.pos_settings = None
        
        # Current currency sign (e.g., "GBP", "USD")
        # Will be loaded from PosSettings after database initialization
        self.current_currency = None
    
    def populate_pos_data(self, progress_callback=None):
        """
        Populate pos_data dictionary with reference data from database.
        
        This method loads all reference data models into memory to minimize
        disk I/O during runtime. All data is loaded once at application startup
        and cached in pos_data dictionary for fast access throughout the session.
        
        The following models are loaded:
        - Cashier: User accounts for POS operators
        - City: City master data
        - Country: Country master data
        - Currency: Currency master data
        - CurrencyTable: Currency exchange rates
        - District: District/region master data
        - Form: Dynamic form definitions
        - FormControl: Form controls (buttons, textboxes, etc.)
        - LabelValue: Label/value pairs for translations
        - PaymentType: Payment method definitions
        - PosSettings: POS system-wide settings
        - PosVirtualKeyboard: Virtual keyboard configurations
        - ReceiptFooter: Receipt footer templates
        - ReceiptHeader: Receipt header templates
        - Store: Store/outlet information
        - Table: Restaurant table management
        - Vat: VAT/tax rate definitions
        
        Args:
            progress_callback: Optional callback function(message: str) to report progress
        """
        # Define all reference data models to load (excluding transaction/sales data)
        model_classes = [
            Cashier,
            City,
            Country,
            Currency,
            CurrencyTable,
            District,
            Form,
            FormControl,
            LabelValue,
            PaymentType,
            PosSettings,
            PosVirtualKeyboard,
            ReceiptFooter,
            ReceiptHeader,
            Store,
            Table,
            Vat,
        ]
        
        # Load each model into pos_data dictionary
        for model_cls in model_classes:
            model_name = model_cls.__name__
            
            # Report progress if callback provided
            if progress_callback:
                progress_callback(f"Loading {model_name}...")
            
            try:
                # Load all records from database (excluding soft-deleted records)
                self.pos_data[model_name] = model_cls.get_all()
                
                # Special handling for PosSettings - cache first record
                if model_name == "PosSettings":
                    if self.pos_data[model_name] and len(self.pos_data[model_name]) > 0:
                        self.pos_settings = self.pos_data[model_name][0]
                        print(f"[DEBUG] PosSettings cached in pos_settings: id={self.pos_settings.id}, name={self.pos_settings.name}")
                
                print(f"[DEBUG] Loaded {len(self.pos_data[model_name])} {model_name} records")
            except Exception as e:
                # On any unexpected read error, keep an empty list
                print(f"[DEBUG] Error loading {model_name}: {e}")
                import traceback
                traceback.print_exc()
                self.pos_data[model_name] = []
        
        print(f"[DEBUG] pos_data populated with {len(self.pos_data)} model types")
    
    def update_pos_data_cache(self, model_instance):
        """
        Update pos_data cache when a model instance is created, updated, or deleted.
        
        This method ensures that pos_data cache stays synchronized with database
        changes. When a model instance is modified, this method should be called
        to update the cache accordingly.
        
        Args:
            model_instance: The model instance that was created, updated, or deleted
        """
        if not model_instance:
            return
        
        model_name = model_instance.__class__.__name__
        
        # Only update cache for models that are in pos_data
        if model_name not in self.pos_data:
            return
        
        # If instance is soft-deleted, remove from cache
        if hasattr(model_instance, 'is_deleted') and model_instance.is_deleted:
            self.pos_data[model_name] = [
                item for item in self.pos_data[model_name] 
                if item.id != model_instance.id
            ]
            print(f"[DEBUG] Removed {model_name} (id={model_instance.id}) from pos_data cache (soft-deleted)")
            return
        
        # Check if instance already exists in cache
        existing_index = None
        for i, item in enumerate(self.pos_data[model_name]):
            if item.id == model_instance.id:
                existing_index = i
                break
        
        if existing_index is not None:
            # Update existing item in cache
            self.pos_data[model_name][existing_index] = model_instance
            print(f"[DEBUG] Updated {model_name} (id={model_instance.id}) in pos_data cache")
        else:
            # Add new item to cache
            self.pos_data[model_name].append(model_instance)
            print(f"[DEBUG] Added {model_name} (id={model_instance.id}) to pos_data cache")
        
        # Special handling for PosSettings - update cached reference
        if model_name == "PosSettings" and len(self.pos_data[model_name]) > 0:
            self.pos_settings = self.pos_data[model_name][0]
            print(f"[DEBUG] Updated pos_settings cache reference")
    
    def refresh_pos_data_model(self, model_class):
        """
        Refresh a specific model's data in pos_data cache from database.
        
        This method reloads all records for a specific model from the database
        and updates the cache. Use this when you need to ensure cache is
        synchronized with database after bulk changes.
        
        Args:
            model_class: The model class to refresh (e.g., Cashier, Currency, etc.)
        """
        model_name = model_class.__name__
        
        try:
            # Reload from database
            self.pos_data[model_name] = model_class.get_all()
            
            # Special handling for PosSettings
            if model_name == "PosSettings" and len(self.pos_data[model_name]) > 0:
                self.pos_settings = self.pos_data[model_name][0]
            
            print(f"[DEBUG] Refreshed {model_name} in pos_data cache: {len(self.pos_data[model_name])} records")
        except Exception as e:
            print(f"[DEBUG] Error refreshing {model_name} in pos_data cache: {e}")
            import traceback
            traceback.print_exc()