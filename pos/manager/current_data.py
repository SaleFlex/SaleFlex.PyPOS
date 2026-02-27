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

from data_layer.auto_save import AutoSaveModel, AutoSaveDict, AutoSaveDescriptor
from pos.manager.document_manager import DocumentManager
from pos.manager.cache_manager import CacheManager
from pos.manager.closure_manager import ClosureManager



from core.logger import get_logger

logger = get_logger(__name__)

class CurrentData(DocumentManager, CacheManager, ClosureManager):
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
    
    The class uses mixin pattern to organize functionality:
    - DocumentManager: Manages document/transaction operations
    - CacheManager: Manages POS and product data caching
    - ClosureManager: Manages closure operations
    
    Attributes:
        cashier_data: Information about the currently logged-in cashier (set during login)
        document_data: Dictionary containing current transaction/document being processed with all temp models
        pending_documents_data: List of dictionaries containing pending documents (is_pending=True)
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
        (Inherited from DocumentManager)
        create_empty_document: Create a new empty document with all transaction temp models initialized
        load_incomplete_document: Load the last incomplete document from database
        load_pending_documents: Load all pending documents (is_pending=True) from database
        complete_document: Complete the current document by copying all temp models to permanent models
        set_document_pending: Set the current document as pending (suspended) or resume it
        
        (Inherited from CacheManager)
        populate_pos_data: Load all reference data models into pos_data cache
        populate_product_data: Load all product-related models into product_data cache
        update_pos_data_cache: Update cache when a model instance is modified
        refresh_pos_data_model: Reload a specific model's data from database
        update_product_data_cache: Update product_data cache when a model instance is modified
        refresh_product_data_model: Reload a specific product model's data from database
        
        (Inherited from ClosureManager)
        load_open_closure: Load the last open closure from database or create empty one
        create_empty_closure: Create a new empty closure with all summary structures
        close_closure: Close the current open closure and create a new empty one
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
        
        Note: During initialization, _skip_autosave flag is set to True to allow
        direct assignment to private attributes without triggering database saves.
        """
        # Enable skip autosave during initialization
        self._skip_autosave = True
        
        # Initialize private attributes directly (no database save during init)
        self._cashier_data = None
        self._document_data = None
        self._pending_documents_data = []
        self._pos_data = {}
        self._pos_settings = None
        self._current_currency = None
        self._product_data = {}
        self._closure = None
        
        # Disable skip autosave after initialization
        self._skip_autosave = False
    
    # Save callback functions for each attribute
    def _save_cashier_data(self, value):
        """Save cashier_data to database"""
        if not value:
            return True
        
        # Use CRUD.save() method which handles lazy engine initialization
        if hasattr(value, 'save'):
            return value.save()
        return True
    
    def _save_document_data(self, value):
        """Save document_data (all temp models) to database"""
        if not value:
            return True
        
        # Unwrap if it's an AutoSaveDict
        if isinstance(value, AutoSaveDict):
            unwrapped = value.unwrap()
        elif isinstance(value, dict):
            unwrapped = value
        else:
            return True
        
        try:
            # Save head using CRUD.save()
            head = unwrapped.get("head")
            if head:
                # Unwrap if it's an AutoSaveModel
                if isinstance(head, AutoSaveModel):
                    head = head.unwrap()
                if hasattr(head, 'save'):
                    head.save()
            
            # Save all related temp models using CRUD.save()
            for model_list_name in ["products", "payments", "discounts", "departments", 
                                   "deliveries", "kitchen_orders", "loyalty", "notes",
                                   "refunds", "surcharges", "taxes", "tips"]:
                models = unwrapped.get(model_list_name, [])
                for model in models:
                    if model:
                        # Unwrap if it's an AutoSaveModel
                        if isinstance(model, AutoSaveModel):
                            model = model.unwrap()
                        if hasattr(model, 'save'):
                            model.save()
            
            # Save fiscal if exists using CRUD.save()
            fiscal = unwrapped.get("fiscal")
            if fiscal:
                # Unwrap if it's an AutoSaveModel
                if isinstance(fiscal, AutoSaveModel):
                    fiscal = fiscal.unwrap()
                if hasattr(fiscal, 'save'):
                    fiscal.save()
            
            return True
        except Exception as e:
            logger.error("[DEBUG] Error saving document_data: %s", e)
            return False
    
    def _save_pending_documents_data(self, value):
        """Save pending_documents_data to database"""
        if not isinstance(value, list):
            return True
        
        # Each pending document is saved individually via document_data save logic
        # This is mainly for consistency, but pending documents are typically
        # saved when they are created/modified, not when the list changes
        return True
    
    def _save_pos_data(self, value):
        """Save pos_data dictionary to database"""
        if not isinstance(value, dict):
            return True
        
        try:
            # Save all models in pos_data using CRUD.save()
            for model_list in value.values():
                if isinstance(model_list, list):
                    for model in model_list:
                        if model and hasattr(model, 'save'):
                            model.save()
            return True
        except Exception as e:
            logger.error("[DEBUG] Error saving pos_data: %s", e)
            return False
    
    def _save_pos_settings(self, value):
        """Save pos_settings to database"""
        if not value:
            return True
        
        # Use CRUD.save() method which handles lazy engine initialization
        if hasattr(value, 'save'):
            return value.save()
        return True
    
    def _save_product_data(self, value):
        """Save product_data dictionary to database"""
        if not isinstance(value, dict):
            return True
        
        try:
            # Save all models in product_data using CRUD.save()
            for model_list in value.values():
                if isinstance(model_list, list):
                    for model in model_list:
                        if model and hasattr(model, 'save'):
                            model.save()
            return True
        except Exception as e:
            logger.error("[DEBUG] Error saving product_data: %s", e)
            return False
    
    def _save_closure(self, value):
        """Save closure dictionary to database"""
        if not value:
            return True
        
        # Unwrap if it's an AutoSaveDict
        if isinstance(value, AutoSaveDict):
            unwrapped = value.unwrap()
        elif isinstance(value, dict):
            unwrapped = value
        else:
            return True
        
        try:
            # Save main closure record using CRUD.save()
            closure = unwrapped.get("closure")
            if closure:
                # Unwrap if it's an AutoSaveModel
                if isinstance(closure, AutoSaveModel):
                    closure = closure.unwrap()
                if hasattr(closure, 'save'):
                    closure.save()
            
            # Save all summaries using CRUD.save() or CRUD.create()
            for summary_list_name in [
                "cashier_summaries", "currencies", "department_summaries",
                "discount_summaries", "document_type_summaries",
                "payment_type_summaries", "tip_summaries", "vat_summaries"
            ]:
                summaries = unwrapped.get(summary_list_name, [])
                for summary in summaries:
                    if summary:
                        # Unwrap if it's an AutoSaveModel
                        if isinstance(summary, AutoSaveModel):
                            summary = summary.unwrap()
                        # Set foreign key if new record
                        if not summary.id and closure:
                            closure_id = closure.id if not isinstance(closure, AutoSaveModel) else closure.unwrap().id
                            summary.fk_closure_id = closure_id
                        # Save using CRUD methods
                        if summary.id and hasattr(summary, 'save'):
                            summary.save()
                        elif not summary.id and hasattr(summary, 'create'):
                            summary.create()
            
            # Save country_specific if exists using CRUD.save() or CRUD.create()
            country_specific = unwrapped.get("country_specific")
            if country_specific:
                # Unwrap if it's an AutoSaveModel
                if isinstance(country_specific, AutoSaveModel):
                    country_specific = country_specific.unwrap()
                # Set foreign key if new record
                if not country_specific.id and closure:
                    closure_id = closure.id if not isinstance(closure, AutoSaveModel) else closure.unwrap().id
                    country_specific.fk_closure_id = closure_id
                # Save using CRUD methods
                if country_specific.id and hasattr(country_specific, 'save'):
                    country_specific.save()
                elif not country_specific.id and hasattr(country_specific, 'create'):
                    country_specific.create()
            
            return True
        except Exception as e:
            logger.error("[DEBUG] Error saving closure: %s", e)
            return False
    
    # Property definitions with auto-save descriptors
    cashier_data = AutoSaveDescriptor('_cashier_data', lambda obj, val: obj._save_cashier_data(val))
    document_data = AutoSaveDescriptor('_document_data', lambda obj, val: obj._save_document_data(val))
    pending_documents_data = AutoSaveDescriptor('_pending_documents_data', lambda obj, val: obj._save_pending_documents_data(val))
    pos_data = AutoSaveDescriptor('_pos_data', lambda obj, val: obj._save_pos_data(val))
    pos_settings = AutoSaveDescriptor('_pos_settings', lambda obj, val: obj._save_pos_settings(val))
    product_data = AutoSaveDescriptor('_product_data', lambda obj, val: obj._save_product_data(val))
    closure = AutoSaveDescriptor('_closure', lambda obj, val: obj._save_closure(val))
