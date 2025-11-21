"""
SaleFlex.PyPOS - Cache Manager Mixin

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
    TransactionDiscountType,
    TransactionDocumentType,
    TransactionSequence,
    Vat,
    Warehouse,
    WarehouseLocation,
    WarehouseProductStock,
    WarehouseStockAdjustment,
    WarehouseStockMovement,
)


class CacheManager:
    """
    Mixin class for managing POS and Product data caches.
    
    This mixin provides methods for populating, updating, and refreshing
    cached reference data to minimize database I/O during runtime.
    """
    
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
        - TransactionDiscountType: Transaction discount type definitions
        - TransactionDocumentType: Transaction document type definitions
        - TransactionSequence: Transaction sequence number generators
        
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
            TransactionDiscountType,
            TransactionDocumentType,
            TransactionSequence,
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

