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
    CashierPerformanceMetrics,
    CashierPerformanceTarget,
    CashierTransactionMetrics,
    CashierWorkBreak,
    CashierWorkSession,
    City,
    Closure,
    ClosureCashierSummary,
    ClosureCountrySpecific,
    ClosureCurrency,
    ClosureDepartmentSummary,
    ClosureDiscountSummary,
    ClosureDocumentTypeSummary,
    ClosurePaymentTypeSummary,
    ClosureTipSummary,
    ClosureVATSummary,
    Country,
    CountryRegion,
    Currency,
    CurrencyTable,
    DepartmentMainGroup,
    DepartmentSubGroup,
    District,
    Form,
    FormControl,
    LabelValue,
    PaymentType,
    PosSettings,
    PosVirtualKeyboard,
    Product,
    ProductAttribute,
    ProductBarcode,
    ProductBarcodeMask,
    ProductManufacturer,
    ProductUnit,
    ProductVariant,
    ReceiptFooter,
    ReceiptHeader,
    Store,
    Table,
    Vat,
    Warehouse,
    WarehouseLocation,
    WarehouseProductStock,
    WarehouseStockAdjustment,
    WarehouseStockMovement,
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
    - pos_data: Dictionary containing all reference data models (Cashier, CashierPerformanceMetrics,
      CashierPerformanceTarget, CashierTransactionMetrics, CashierWorkBreak, CashierWorkSession,
      City, Country, CountryRegion, District, Form, FormControl, LabelValue, PaymentType, PosSettings,
      PosVirtualKeyboard, ReceiptFooter, ReceiptHeader, Store, Table) loaded once at
      application startup to avoid repeated database reads
    - product_data: Dictionary containing product-related models (Currency, CurrencyTable, Vat,
      DepartmentMainGroup, DepartmentSubGroup, Product, ProductAttribute, ProductBarcode,
      ProductBarcodeMask, ProductManufacturer, ProductUnit, ProductVariant, Warehouse,
      WarehouseLocation, WarehouseProductStock, WarehouseStockAdjustment, WarehouseStockMovement)
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
        closure: Dictionary containing current open closure data with all summaries:
            - closure: Closure instance (main closure record)
            - cashier_summaries: List[ClosureCashierSummary]
            - country_specific: ClosureCountrySpecific or None
            - currencies: List[ClosureCurrency]
            - department_summaries: List[ClosureDepartmentSummary]
            - discount_summaries: List[ClosureDiscountSummary]
            - document_type_summaries: List[ClosureDocumentTypeSummary]
            - payment_type_summaries: List[ClosurePaymentTypeSummary]
            - tip_summaries: List[ClosureTipSummary]
            - vat_summaries: List[ClosureVATSummary]
    
    Methods:
        populate_pos_data: Load all reference data models into pos_data cache
        populate_product_data: Load all product-related models into product_data cache
        update_pos_data_cache: Update cache when a model instance is modified
        refresh_pos_data_model: Reload a specific model's data from database
        update_product_data_cache: Update product_data cache when a model instance is modified
        refresh_product_data_model: Reload a specific product model's data from database
        load_open_closure: Load the last open closure from database or create empty one
        create_empty_closure: Create a new empty closure with all summary structures
        close_closure: Close the current open closure and create a new empty one
        _load_closure_data: Internal method to load all closure data into self.closure
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
        
        # Cached product-related data loaded at startup (after DB init)
        # Example keys: "Product", "ProductBarcode", "DepartmentMainGroup", ...
        self.product_data = {}
        
        # Current active closure data (open closure until closed)
        # Dictionary structure:
        # {
        #     "closure": Closure instance (main closure record),
        #     "cashier_summaries": List[ClosureCashierSummary],
        #     "country_specific": ClosureCountrySpecific or None,
        #     "currencies": List[ClosureCurrency],
        #     "department_summaries": List[ClosureDepartmentSummary],
        #     "discount_summaries": List[ClosureDiscountSummary],
        #     "document_type_summaries": List[ClosureDocumentTypeSummary],
        #     "payment_type_summaries": List[ClosurePaymentTypeSummary],
        #     "tip_summaries": List[ClosureTipSummary],
        #     "vat_summaries": List[ClosureVATSummary]
        # }
        # Will be populated at application startup with the last open closure
        # (closure_end_time is None) or a new empty closure if none exists
        self.closure = None
    
    def populate_pos_data(self, progress_callback=None):
        """
        Populate pos_data dictionary with reference data from database.
        
        This method loads all reference data models into memory to minimize
        disk I/O during runtime. All data is loaded once at application startup
        and cached in pos_data dictionary for fast access throughout the session.
        
        The following models are loaded:
        - Cashier: User accounts for POS operators
        - CashierPerformanceMetrics: Cashier performance metrics and statistics
        - CashierPerformanceTarget: Cashier performance targets and goals
        - CashierTransactionMetrics: Transaction-level performance metrics
        - CashierWorkBreak: Cashier break records and tracking
        - CashierWorkSession: Cashier work session records
        - City: City master data
        - Country: Country master data
        - CountryRegion: Sub-country regions (states, provinces, special economic zones)
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
        
        Args:
            progress_callback: Optional callback function(message: str) to report progress
        """
        # Define all reference data models to load (excluding transaction/sales data)
        model_classes = [
            Cashier,
            CashierPerformanceMetrics,
            CashierPerformanceTarget,
            CashierTransactionMetrics,
            CashierWorkBreak,
            CashierWorkSession,
            City,
            Country,
            CountryRegion,
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
    
    def populate_product_data(self, progress_callback=None):
        """
        Populate product_data dictionary with product-related data from database.
        
        This method loads all product-related models into memory to minimize
        disk I/O during runtime. All data is loaded once at application startup
        and cached in product_data dictionary for fast access throughout the session.
        
        The following models are loaded:
        - Currency: Currency master data
        - CurrencyTable: Currency exchange rates
        - DepartmentMainGroup: Main department groups
        - DepartmentSubGroup: Sub department groups
        - Product: Product master data
        - ProductAttribute: Product attributes
        - ProductBarcode: Product barcode mappings
        - ProductBarcodeMask: Barcode mask definitions
        - ProductManufacturer: Manufacturer information
        - ProductUnit: Product unit definitions
        - ProductVariant: Product variants
        - Vat: VAT/tax rate definitions
        - Warehouse: Warehouse master data
        - WarehouseLocation: Warehouse location data
        - WarehouseProductStock: Product stock levels by warehouse
        - WarehouseStockAdjustment: Stock adjustment records
        - WarehouseStockMovement: Stock movement records
        
        Args:
            progress_callback: Optional callback function(message: str) to report progress
        """
        # Define all product-related models to load
        model_classes = [
            Currency,
            CurrencyTable,
            DepartmentMainGroup,
            DepartmentSubGroup,
            Product,
            ProductAttribute,
            ProductBarcode,
            ProductBarcodeMask,
            ProductManufacturer,
            ProductUnit,
            ProductVariant,
            Vat,
            Warehouse,
            WarehouseLocation,
            WarehouseProductStock,
            WarehouseStockAdjustment,
            WarehouseStockMovement,
        ]
        
        # Load each model into product_data dictionary
        for model_cls in model_classes:
            model_name = model_cls.__name__
            
            # Report progress if callback provided
            if progress_callback:
                progress_callback(f"Loading {model_name}...")
            
            try:
                # Load all records from database (excluding soft-deleted records)
                self.product_data[model_name] = model_cls.get_all()
                
                print(f"[DEBUG] Loaded {len(self.product_data[model_name])} {model_name} records")
            except Exception as e:
                # On any unexpected read error, keep an empty list
                print(f"[DEBUG] Error loading {model_name}: {e}")
                import traceback
                traceback.print_exc()
                self.product_data[model_name] = []
        
        print(f"[DEBUG] product_data populated with {len(self.product_data)} model types")
    
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
            model_class: The model class to refresh (e.g., Cashier, Form, etc.)
                        Note: Currency, CurrencyTable, and Vat are now in product_data
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
    
    def update_product_data_cache(self, model_instance):
        """
        Update product_data cache when a model instance is created, updated, or deleted.
        
        This method ensures that product_data cache stays synchronized with database
        changes. When a model instance is modified, this method should be called
        to update the cache accordingly.
        
        Args:
            model_instance: The model instance that was created, updated, or deleted
        """
        if not model_instance:
            return
        
        model_name = model_instance.__class__.__name__
        
        # Only update cache for models that are in product_data
        if model_name not in self.product_data:
            return
        
        # If instance is soft-deleted, remove from cache
        if hasattr(model_instance, 'is_deleted') and model_instance.is_deleted:
            self.product_data[model_name] = [
                item for item in self.product_data[model_name] 
                if item.id != model_instance.id
            ]
            print(f"[DEBUG] Removed {model_name} (id={model_instance.id}) from product_data cache (soft-deleted)")
            return
        
        # Check if instance already exists in cache
        existing_index = None
        for i, item in enumerate(self.product_data[model_name]):
            if item.id == model_instance.id:
                existing_index = i
                break
        
        if existing_index is not None:
            # Update existing item in cache
            self.product_data[model_name][existing_index] = model_instance
            print(f"[DEBUG] Updated {model_name} (id={model_instance.id}) in product_data cache")
        else:
            # Add new item to cache
            self.product_data[model_name].append(model_instance)
            print(f"[DEBUG] Added {model_name} (id={model_instance.id}) to product_data cache")
    
    def refresh_product_data_model(self, model_class):
        """
        Refresh a specific model's data in product_data cache from database.
        
        This method reloads all records for a specific model from the database
        and updates the cache. Use this when you need to ensure cache is
        synchronized with database after bulk changes.
        
        Args:
            model_class: The model class to refresh (e.g., Product, ProductBarcode, etc.)
        """
        model_name = model_class.__name__
        
        try:
            # Reload from database
            self.product_data[model_name] = model_class.get_all()
            
            print(f"[DEBUG] Refreshed {model_name} in product_data cache: {len(self.product_data[model_name])} records")
        except Exception as e:
            print(f"[DEBUG] Error refreshing {model_name} in product_data cache: {e}")
            import traceback
            traceback.print_exc()
    
    def load_open_closure(self):
        """
        Load the last open closure (closure_end_time is None) from database.
        
        If an open closure exists, it will be loaded with all its summary data.
        If no open closure exists, a new empty closure will be created.
        
        This method should be called at application startup after database initialization
        and after pos_data/product_data are populated.
        """
        from datetime import date, datetime
        from data_layer.engine import Engine
        
        try:
            # Query for the last open closure (closure_end_time is None)
            with Engine().get_session() as session:
                open_closure = session.query(Closure).filter(
                    Closure.closure_end_time.is_(None),
                    Closure.is_deleted == False
                ).order_by(
                    Closure.closure_start_time.desc()
                ).first()
                
                if open_closure:
                    # Load closure with all summary data
                    self._load_closure_data(open_closure.id)
                    print(f"[DEBUG] Loaded open closure: {open_closure.closure_unique_id}")
                else:
                    # No open closure exists, create a new empty one
                    print("[DEBUG] No open closure found, creating new empty closure")
                    self.create_empty_closure()
        except Exception as e:
            print(f"[DEBUG] Error loading open closure: {e}")
            import traceback
            traceback.print_exc()
            # On error, try to create a new empty closure
            try:
                self.create_empty_closure()
            except Exception as e2:
                print(f"[DEBUG] Error creating empty closure: {e2}")
                import traceback
                traceback.print_exc()
    
    def _load_closure_data(self, closure_id):
        """
        Load all closure data (main record + all summaries) into self.closure dictionary.
        
        Args:
            closure_id: UUID of the closure to load
        """
        from data_layer.engine import Engine
        
        try:
            with Engine().get_session() as session:
                # Load main closure record
                closure = session.query(Closure).filter_by(id=closure_id).first()
                if not closure:
                    print(f"[DEBUG] Closure not found: {closure_id}")
                    return
                
                # Initialize closure dictionary
                self.closure = {
                    "closure": closure,
                    "cashier_summaries": [],
                    "country_specific": None,
                    "currencies": [],
                    "department_summaries": [],
                    "discount_summaries": [],
                    "document_type_summaries": [],
                    "payment_type_summaries": [],
                    "tip_summaries": [],
                    "vat_summaries": []
                }
                
                # Load all summary records
                self.closure["cashier_summaries"] = session.query(ClosureCashierSummary).filter_by(
                    fk_closure_id=closure_id, is_deleted=False
                ).all()
                
                self.closure["country_specific"] = session.query(ClosureCountrySpecific).filter_by(
                    fk_closure_id=closure_id, is_deleted=False
                ).first()
                
                self.closure["currencies"] = session.query(ClosureCurrency).filter_by(
                    fk_closure_id=closure_id, is_deleted=False
                ).all()
                
                self.closure["department_summaries"] = session.query(ClosureDepartmentSummary).filter_by(
                    fk_closure_id=closure_id, is_deleted=False
                ).all()
                
                self.closure["discount_summaries"] = session.query(ClosureDiscountSummary).filter_by(
                    fk_closure_id=closure_id, is_deleted=False
                ).all()
                
                self.closure["document_type_summaries"] = session.query(ClosureDocumentTypeSummary).filter_by(
                    fk_closure_id=closure_id, is_deleted=False
                ).all()
                
                self.closure["payment_type_summaries"] = session.query(ClosurePaymentTypeSummary).filter_by(
                    fk_closure_id=closure_id, is_deleted=False
                ).all()
                
                self.closure["tip_summaries"] = session.query(ClosureTipSummary).filter_by(
                    fk_closure_id=closure_id, is_deleted=False
                ).all()
                
                self.closure["vat_summaries"] = session.query(ClosureVATSummary).filter_by(
                    fk_closure_id=closure_id, is_deleted=False
                ).all()
                
                print(f"[DEBUG] Loaded closure data: {len(self.closure['cashier_summaries'])} cashiers, "
                      f"{len(self.closure['currencies'])} currencies, "
                      f"{len(self.closure['department_summaries'])} departments")
        except Exception as e:
            print(f"[DEBUG] Error loading closure data: {e}")
            import traceback
            traceback.print_exc()
    
    def create_empty_closure(self):
        """
        Create a new empty closure with all summary structures initialized to empty.
        
        The closure will have:
        - closure_date: Today's date
        - closure_start_time: Current datetime
        - closure_end_time: None (open closure)
        - All other fields set to default/zero values
        
        This method requires:
        - pos_settings to be loaded (for fk_pos_id)
        - pos_data to contain Store (for fk_store_id - uses first store from pos_data["Store"])
        - product_data to contain Currency (for fk_base_currency_id)
        
        Note: If cashier_data is not set, the closure will be created but fk_cashier_opened_id
        will need to be set later (e.g., after login). For now, we'll use the first cashier
        from pos_data as a fallback, or leave it unset if no cashiers exist.
        """
        from datetime import date, datetime
        from uuid import uuid4
        from data_layer.engine import Engine
        
        try:
            # Validate required data
            if not self.pos_settings:
                print("[DEBUG] Cannot create closure: pos_settings not loaded")
                return
            
            # Get store_id from pos_data["Store"]
            store_id = None
            stores = self.pos_data.get("Store", [])
            if stores:
                store_id = stores[0].id
                print(f"[DEBUG] Using store for closure: {store_id}")
            else:
                print("[DEBUG] Cannot create closure: no store found in pos_data")
                return
            
            # Get base currency from pos_settings
            base_currency_id = None
            if self.pos_settings.fk_current_currency_id:
                base_currency_id = self.pos_settings.fk_current_currency_id
            else:
                # Fallback: get first currency from product_data
                currencies = self.product_data.get("Currency", [])
                if currencies:
                    base_currency_id = currencies[0].id
                else:
                    print("[DEBUG] Cannot create closure: no currency found")
                    return
            
            # Get cashier ID (use current cashier if logged in, otherwise use first cashier as fallback)
            cashier_id = None
            if self.cashier_data:
                cashier_id = self.cashier_data.id
            else:
                # Fallback: get first cashier from pos_data
                cashiers = self.pos_data.get("Cashier", [])
                if cashiers:
                    cashier_id = cashiers[0].id
                    print(f"[DEBUG] Using fallback cashier for closure: {cashier_id}")
                else:
                    print("[DEBUG] Warning: No cashier available, closure will be created without cashier")
                    # Note: fk_cashier_opened_id is nullable=False, so we need a cashier
                    # In production, you might want to create a system cashier or handle this differently
                    return
            
            # Get next closure number (daily sequence)
            today = date.today()
            with Engine().get_session() as session:
                # Find the highest closure_number for today
                max_closure = session.query(Closure).filter(
                    Closure.closure_date == today,
                    Closure.is_deleted == False
                ).order_by(Closure.closure_number.desc()).first()
                
                next_closure_number = 1
                if max_closure:
                    next_closure_number = max_closure.closure_number + 1
                
                # Create unique ID
                closure_unique_id = f"{today.strftime('%Y%m%d')}-{next_closure_number:04d}"
                
                # Create new closure record
                new_closure = Closure()
                new_closure.id = uuid4()
                new_closure.closure_unique_id = closure_unique_id
                new_closure.closure_number = next_closure_number
                new_closure.fk_store_id = store_id
                new_closure.fk_pos_id = self.pos_settings.id
                new_closure.closure_date = today
                new_closure.closure_start_time = datetime.now()
                new_closure.closure_end_time = None  # Open closure
                new_closure.fk_base_currency_id = base_currency_id
                new_closure.fk_cashier_opened_id = cashier_id
                new_closure.fk_cashier_closed_id = cashier_id  # Will be updated when closed
                
                # All numeric fields default to 0 (handled by model defaults)
                
                # Save to database
                session.add(new_closure)
                session.commit()
                
                # Load the closure data into self.closure
                self._load_closure_data(new_closure.id)
                
                print(f"[DEBUG] Created new empty closure: {closure_unique_id}")
        except Exception as e:
            print(f"[DEBUG] Error creating empty closure: {e}")
            import traceback
            traceback.print_exc()
    
    def close_closure(self, closing_cash_amount=None, description=None):
        """
        Close the current open closure.
        
        This method:
        1. Sets closure_end_time to current datetime
        2. Sets fk_cashier_closed_id to current cashier
        3. Updates closing_cash_amount if provided
        4. Saves all closure data to database
        5. Creates a new empty closure
        
        Args:
            closing_cash_amount: Optional closing cash amount (if None, uses expected_cash_amount)
            description: Optional description/notes for the closure
        """
        from datetime import datetime
        from data_layer.engine import Engine
        
        if not self.closure or not self.closure.get("closure"):
            print("[DEBUG] No open closure to close")
            return
        
        if not self.cashier_data:
            print("[DEBUG] Cannot close closure: cashier_data not set (user not logged in)")
            return
        
        try:
            closure = self.closure["closure"]
            
            # Update closure with closing information
            closure.closure_end_time = datetime.now()
            closure.fk_cashier_closed_id = self.cashier_data.id
            
            if closing_cash_amount is not None:
                closure.closing_cash_amount = closing_cash_amount
                # Calculate cash difference
                closure.cash_difference = closing_cash_amount - closure.expected_cash_amount
            
            if description:
                closure.description = description
            
            # Save closure and all summaries to database
            with Engine().get_session() as session:
                # Merge closure (it might have been modified)
                session.merge(closure)
                
                # Save all summaries
                for summary_list_name in [
                    "cashier_summaries", "currencies", "department_summaries",
                    "discount_summaries", "document_type_summaries",
                    "payment_type_summaries", "tip_summaries", "vat_summaries"
                ]:
                    summaries = self.closure.get(summary_list_name, [])
                    for summary in summaries:
                        if summary.id:  # Existing record
                            session.merge(summary)
                        else:  # New record
                            summary.fk_closure_id = closure.id
                            session.add(summary)
                
                # Save country_specific if exists
                if self.closure.get("country_specific"):
                    country_specific = self.closure["country_specific"]
                    if country_specific.id:  # Existing record
                        session.merge(country_specific)
                    else:  # New record
                        country_specific.fk_closure_id = closure.id
                        session.add(country_specific)
                
                session.commit()
            
            print(f"[DEBUG] Closed closure: {closure.closure_unique_id}")
            
            # Create new empty closure
            self.create_empty_closure()
            
        except Exception as e:
            print(f"[DEBUG] Error closing closure: {e}")
            import traceback
            traceback.print_exc()