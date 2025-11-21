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
    TransactionDelivery,
    TransactionDeliveryTemp,
    TransactionDiscount,
    TransactionDiscountTemp,
    TransactionDiscountType,
    TransactionDocumentType,
    TransactionFiscal,
    TransactionFiscalTemp,
    TransactionHead,
    TransactionHeadTemp,
    TransactionKitchenOrder,
    TransactionKitchenOrderTemp,
    TransactionLoyalty,
    TransactionLoyaltyTemp,
    TransactionNote,
    TransactionNoteTemp,
    TransactionPayment,
    TransactionPaymentTemp,
    TransactionProduct,
    TransactionProductTemp,
    TransactionRefund,
    TransactionRefundTemp,
    TransactionSequence,
    TransactionSurcharge,
    TransactionSurchargeTemp,
    TransactionTax,
    TransactionTaxTemp,
    TransactionTip,
    TransactionTipTemp,
    TransactionTotal,
    TransactionTotalTemp,
    Vat,
    Warehouse,
    WarehouseLocation,
    WarehouseProductStock,
    WarehouseStockAdjustment,
    WarehouseStockMovement,
)
from data_layer.model.definition.transaction_status import TransactionStatus, TransactionType


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
        create_empty_document: Create a new empty document with all transaction temp models initialized
        load_incomplete_document: Load the last incomplete document from database
        load_pending_documents: Load all pending documents (is_pending=True) from database
        complete_document: Complete the current document by copying all temp models to permanent models
        set_document_pending: Set the current document as pending (suspended) or resume it
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
        # Dictionary structure containing all transaction temp models:
        # {
        #     "head": TransactionHeadTemp instance (main transaction header),
        #     "products": List[TransactionProductTemp],
        #     "payments": List[TransactionPaymentTemp],
        #     "discounts": List[TransactionDiscountTemp],
        #     "totals": List[TransactionTotalTemp],
        #     "deliveries": List[TransactionDeliveryTemp],
        #     "kitchen_orders": List[TransactionKitchenOrderTemp],
        #     "loyalty": List[TransactionLoyaltyTemp],
        #     "notes": List[TransactionNoteTemp],
        #     "fiscal": TransactionFiscalTemp or None,
        #     "refunds": List[TransactionRefundTemp],
        #     "surcharges": List[TransactionSurchargeTemp],
        #     "taxes": List[TransactionTaxTemp],
        #     "tips": List[TransactionTipTemp]
        # }
        # Will be populated when starting a new transaction or loading an incomplete one
        self.document_data = None
        
        # List of pending documents (is_pending = True)
        # Each item is a dictionary with the same structure as document_data
        # Used in restaurant mode for managing suspended orders/tables
        # Will be populated at application startup with all pending transactions
        self.pending_documents_data = []

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
    
    def create_empty_document(self):
        """
        Create a new empty document with all transaction temp models initialized.
        
        This method creates a fresh document structure with:
        - TransactionHeadTemp initialized with default values:
          * document_type: First TransactionDocumentType record
          * transaction_type: TransactionType.SALE
          * transaction_status: TransactionStatus.DRAFT
          * closure_number: TransactionSequence with name="ClosureNumber"
          * receipt_number: TransactionSequence with name="ReceiptNumber"
          * fk_store_id: First Store from pos_data
        - All other temp models initialized as empty lists or None
        
        This method should be called when starting a new transaction.
        """
        from datetime import datetime
        from uuid import uuid4
        from data_layer.engine import Engine
        
        try:
            # Validate required data
            if not self.pos_settings:
                print("[DEBUG] Cannot create document: pos_settings not loaded")
                return None
            
            # Get document_type from TransactionDocumentType (first record)
            document_types = self.pos_data.get("TransactionDocumentType", [])
            if not document_types:
                print("[DEBUG] Cannot create document: no TransactionDocumentType found")
                return None
            document_type = document_types[0].name
            
            # Get closure_number from TransactionSequence
            closure_number = 1
            sequences = self.pos_data.get("TransactionSequence", [])
            for seq in sequences:
                if seq.name == "ClosureNumber":
                    closure_number = seq.value
                    break
            
            # Get receipt_number from TransactionSequence
            receipt_number = 1
            for seq in sequences:
                if seq.name == "ReceiptNumber":
                    receipt_number = seq.value
                    break
            
            # Get store_id from pos_data["Store"]
            store_id = None
            stores = self.pos_data.get("Store", [])
            if stores:
                store_id = stores[0].id
            else:
                print("[DEBUG] Cannot create document: no store found in pos_data")
                return None
            
            # Get pos_id from pos_settings (use pos_no_in_store as pos_id is Integer)
            pos_id = self.pos_settings.pos_no_in_store if hasattr(self.pos_settings, 'pos_no_in_store') else 1
            
            # Generate unique transaction ID
            transaction_unique_id = f"{datetime.now().strftime('%Y%m%d')}-{receipt_number:06d}"
            
            # Create new TransactionHeadTemp
            head = TransactionHeadTemp()
            head.id = uuid4()
            head.transaction_unique_id = transaction_unique_id
            head.pos_id = pos_id
            head.transaction_date_time = datetime.now()
            head.document_type = document_type
            head.transaction_type = TransactionType.SALE.value
            head.transaction_status = TransactionStatus.DRAFT.value
            head.fk_store_id = store_id
            head.closure_number = closure_number
            head.receipt_number = receipt_number
            head.is_closed = False
            head.is_pending = False
            head.is_cancel = False
            
            # Initialize document_data structure
            self.document_data = {
                "head": head,
                "products": [],
                "payments": [],
                "discounts": [],
                "totals": [],
                "deliveries": [],
                "kitchen_orders": [],
                "loyalty": [],
                "notes": [],
                "fiscal": None,
                "refunds": [],
                "surcharges": [],
                "taxes": [],
                "tips": []
            }
            
            print(f"[DEBUG] Created new empty document: {transaction_unique_id}")
            return self.document_data
            
        except Exception as e:
            print(f"[DEBUG] Error creating empty document: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def load_incomplete_document(self):
        """
        Load the last incomplete document from database.
        
        An incomplete document is one where:
        - is_closed = False
        - is_pending = False
        - is_cancel = False
        
        This method should be called at application startup to resume
        any transaction that was in progress when the application closed.
        
        Returns:
            True if document was loaded, False otherwise
        """
        from data_layer.engine import Engine
        
        try:
            with Engine().get_session() as session:
                # Find the last incomplete transaction
                incomplete_head = session.query(TransactionHeadTemp).filter(
                    TransactionHeadTemp.is_closed == False,
                    TransactionHeadTemp.is_pending == False,
                    TransactionHeadTemp.is_cancel == False,
                    TransactionHeadTemp.is_deleted == False
                ).order_by(
                    TransactionHeadTemp.transaction_date_time.desc()
                ).first()
                
                if not incomplete_head:
                    print("[DEBUG] No incomplete document found")
                    return False
                
                # Load all related temp models
                self._load_document_data(incomplete_head.id, session)
                
                print(f"[DEBUG] Loaded incomplete document: {incomplete_head.transaction_unique_id}")
                return True
                
        except Exception as e:
            print(f"[DEBUG] Error loading incomplete document: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_pending_documents(self):
        """
        Load all pending documents (is_pending = True) from database.
        
        This method loads all pending transactions into self.pending_documents_data.
        Each pending document is a dictionary with the same structure as document_data.
        
        This method should be called at application startup.
        """
        from data_layer.engine import Engine
        
        try:
            self.pending_documents_data = []
            
            with Engine().get_session() as session:
                # Find all pending transactions
                pending_heads = session.query(TransactionHeadTemp).filter(
                    TransactionHeadTemp.is_pending == True,
                    TransactionHeadTemp.is_deleted == False
                ).order_by(
                    TransactionHeadTemp.transaction_date_time.desc()
                ).all()
                
                for head in pending_heads:
                    # Load document data for this pending transaction
                    doc_data = self._load_document_data_dict(head.id, session)
                    if doc_data:
                        self.pending_documents_data.append(doc_data)
                
                print(f"[DEBUG] Loaded {len(self.pending_documents_data)} pending documents")
                
        except Exception as e:
            print(f"[DEBUG] Error loading pending documents: {e}")
            import traceback
            traceback.print_exc()
            self.pending_documents_data = []
    
    def _load_document_data(self, head_id, session):
        """
        Load all transaction temp models for a given transaction head ID.
        Populates self.document_data with the loaded data.
        
        Args:
            head_id: UUID of the TransactionHeadTemp
            session: SQLAlchemy session
        """
        try:
            # Load head
            head = session.query(TransactionHeadTemp).filter_by(id=head_id).first()
            if not head:
                print(f"[DEBUG] Transaction head not found: {head_id}")
                return
            
            # Initialize document_data structure
            self.document_data = {
                "head": head,
                "products": session.query(TransactionProductTemp).filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ).all(),
                "payments": session.query(TransactionPaymentTemp).filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ).all(),
                "discounts": session.query(TransactionDiscountTemp).filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ).all(),
                "totals": session.query(TransactionTotalTemp).filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ).all(),
                "deliveries": session.query(TransactionDeliveryTemp).filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ).all(),
                "kitchen_orders": session.query(TransactionKitchenOrderTemp).filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ).all(),
                "loyalty": session.query(TransactionLoyaltyTemp).filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ).all(),
                "notes": session.query(TransactionNoteTemp).filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ).all(),
                "fiscal": session.query(TransactionFiscalTemp).filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ).first(),
                "refunds": session.query(TransactionRefundTemp).filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ).all(),
                "surcharges": session.query(TransactionSurchargeTemp).filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ).all(),
                "taxes": session.query(TransactionTaxTemp).filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ).all(),
                "tips": session.query(TransactionTipTemp).filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ).all()
            }
            
        except Exception as e:
            print(f"[DEBUG] Error loading document data: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_document_data_dict(self, head_id, session):
        """
        Load all transaction temp models for a given transaction head ID.
        Returns a dictionary with the loaded data (does not modify self.document_data).
        
        Args:
            head_id: UUID of the TransactionHeadTemp
            session: SQLAlchemy session
            
        Returns:
            Dictionary with document data structure or None if head not found
        """
        try:
            # Load head
            head = session.query(TransactionHeadTemp).filter_by(id=head_id).first()
            if not head:
                return None
            
            # Return document data dictionary
            return {
                "head": head,
                "products": session.query(TransactionProductTemp).filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ).all(),
                "payments": session.query(TransactionPaymentTemp).filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ).all(),
                "discounts": session.query(TransactionDiscountTemp).filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ).all(),
                "totals": session.query(TransactionTotalTemp).filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ).all(),
                "deliveries": session.query(TransactionDeliveryTemp).filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ).all(),
                "kitchen_orders": session.query(TransactionKitchenOrderTemp).filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ).all(),
                "loyalty": session.query(TransactionLoyaltyTemp).filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ).all(),
                "notes": session.query(TransactionNoteTemp).filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ).all(),
                "fiscal": session.query(TransactionFiscalTemp).filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ).first(),
                "refunds": session.query(TransactionRefundTemp).filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ).all(),
                "surcharges": session.query(TransactionSurchargeTemp).filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ).all(),
                "taxes": session.query(TransactionTaxTemp).filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ).all(),
                "tips": session.query(TransactionTipTemp).filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ).all()
            }
            
        except Exception as e:
            print(f"[DEBUG] Error loading document data dict: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def complete_document(self, is_cancel=False, cancel_reason=None):
        """
        Complete the current document by copying all temp models to permanent models.
        
        This method:
        1. Updates TransactionHeadTemp:
           - Sets transaction_status to COMPLETED (or CANCELLED if is_cancel=True)
           - Sets is_closed = True
           - Sets is_cancel = True if is_cancel parameter is True
        2. Copies all temp models to their permanent counterparts
        3. Saves everything to database
        4. Resets document_data to None
        
        Args:
            is_cancel: If True, marks transaction as cancelled
            cancel_reason: Optional reason for cancellation
        """
        from datetime import datetime
        from uuid import uuid4
        from data_layer.engine import Engine
        
        if not self.document_data or not self.document_data.get("head"):
            print("[DEBUG] No document to complete")
            return False
        
        try:
            head_temp = self.document_data["head"]
            
            # Update head_temp status
            if is_cancel:
                head_temp.transaction_status = TransactionStatus.CANCELLED.value
                head_temp.is_cancel = True
                if cancel_reason:
                    head_temp.cancel_reason = cancel_reason
            else:
                head_temp.transaction_status = TransactionStatus.COMPLETED.value
            
            head_temp.is_closed = True
            
            with Engine().get_session() as session:
                # Save updated head_temp
                session.merge(head_temp)
                
                # Copy head_temp to TransactionHead
                head = TransactionHead()
                # Copy all fields from head_temp
                for key in head_temp.__table__.columns.keys():
                    if hasattr(head_temp, key):
                        setattr(head, key, getattr(head_temp, key))
                head.id = uuid4()  # New ID for permanent record
                
                session.add(head)
                session.flush()  # Get the new head.id
                
                # Copy all related temp models to permanent models
                # Store mapping of temp IDs to permanent IDs for foreign key updates
                product_id_map = {}  # temp_id -> permanent_id
                payment_id_map = {}  # temp_id -> permanent_id
                total_id_map = {}    # temp_id -> permanent_id
                
                # Products
                for prod_temp in self.document_data.get("products", []):
                    prod = TransactionProduct()
                    temp_id = prod_temp.id
                    for key in prod_temp.__table__.columns.keys():
                        if hasattr(prod_temp, key):
                            if key == "fk_transaction_head_id":
                                setattr(prod, key, head.id)
                            else:
                                setattr(prod, key, getattr(prod_temp, key))
                    prod.id = uuid4()
                    product_id_map[temp_id] = prod.id
                    session.add(prod)
                
                # Payments
                for pay_temp in self.document_data.get("payments", []):
                    pay = TransactionPayment()
                    temp_id = pay_temp.id
                    for key in pay_temp.__table__.columns.keys():
                        if hasattr(pay_temp, key):
                            if key == "fk_transaction_head_id":
                                setattr(pay, key, head.id)
                            else:
                                setattr(pay, key, getattr(pay_temp, key))
                    pay.id = uuid4()
                    payment_id_map[temp_id] = pay.id
                    session.add(pay)
                
                # Totals
                for total_temp in self.document_data.get("totals", []):
                    total = TransactionTotal()
                    temp_id = total_temp.id
                    for key in total_temp.__table__.columns.keys():
                        if hasattr(total_temp, key):
                            if key == "fk_transaction_head_id":
                                setattr(total, key, head.id)
                            else:
                                setattr(total, key, getattr(total_temp, key))
                    total.id = uuid4()
                    total_id_map[temp_id] = total.id
                    session.add(total)
                
                # Discounts
                for disc_temp in self.document_data.get("discounts", []):
                    disc = TransactionDiscount()
                    for key in disc_temp.__table__.columns.keys():
                        if hasattr(disc_temp, key):
                            if key == "fk_transaction_head_id":
                                setattr(disc, key, head.id)
                            elif key == "fk_transaction_product_id" and getattr(disc_temp, key):
                                # Map temp product ID to permanent product ID
                                setattr(disc, key, product_id_map.get(getattr(disc_temp, key)))
                            elif key == "fk_transaction_payment_id" and getattr(disc_temp, key):
                                # Map temp payment ID to permanent payment ID
                                setattr(disc, key, payment_id_map.get(getattr(disc_temp, key)))
                            elif key == "fk_transaction_total_id" and getattr(disc_temp, key):
                                # Map temp total ID to permanent total ID
                                setattr(disc, key, total_id_map.get(getattr(disc_temp, key)))
                            else:
                                setattr(disc, key, getattr(disc_temp, key))
                    disc.id = uuid4()
                    session.add(disc)
                
                # Deliveries
                for del_temp in self.document_data.get("deliveries", []):
                    del_rec = TransactionDelivery()
                    for key in del_temp.__table__.columns.keys():
                        if hasattr(del_temp, key):
                            if key == "fk_transaction_head_id":
                                setattr(del_rec, key, head.id)
                            else:
                                setattr(del_rec, key, getattr(del_temp, key))
                    del_rec.id = uuid4()
                    session.add(del_rec)
                
                # Kitchen Orders
                for ko_temp in self.document_data.get("kitchen_orders", []):
                    ko = TransactionKitchenOrder()
                    for key in ko_temp.__table__.columns.keys():
                        if hasattr(ko_temp, key):
                            if key == "fk_transaction_head_id":
                                setattr(ko, key, head.id)
                            elif key == "fk_transaction_product_id" and getattr(ko_temp, key):
                                # Map temp product ID to permanent product ID
                                setattr(ko, key, product_id_map.get(getattr(ko_temp, key)))
                            else:
                                setattr(ko, key, getattr(ko_temp, key))
                    ko.id = uuid4()
                    session.add(ko)
                
                # Loyalty
                for loy_temp in self.document_data.get("loyalty", []):
                    loy = TransactionLoyalty()
                    for key in loy_temp.__table__.columns.keys():
                        if hasattr(loy_temp, key):
                            if key == "fk_transaction_head_id":
                                setattr(loy, key, head.id)
                            else:
                                setattr(loy, key, getattr(loy_temp, key))
                    loy.id = uuid4()
                    session.add(loy)
                
                # Notes
                for note_temp in self.document_data.get("notes", []):
                    note = TransactionNote()
                    for key in note_temp.__table__.columns.keys():
                        if hasattr(note_temp, key):
                            if key == "fk_transaction_head_id":
                                setattr(note, key, head.id)
                            else:
                                setattr(note, key, getattr(note_temp, key))
                    note.id = uuid4()
                    session.add(note)
                
                # Fiscal
                if self.document_data.get("fiscal"):
                    fiscal_temp = self.document_data["fiscal"]
                    fiscal = TransactionFiscal()
                    for key in fiscal_temp.__table__.columns.keys():
                        if hasattr(fiscal_temp, key):
                            if key == "fk_transaction_head_id":
                                setattr(fiscal, key, head.id)
                            else:
                                setattr(fiscal, key, getattr(fiscal_temp, key))
                    fiscal.id = uuid4()
                    session.add(fiscal)
                
                # Refunds
                for ref_temp in self.document_data.get("refunds", []):
                    ref = TransactionRefund()
                    for key in ref_temp.__table__.columns.keys():
                        if hasattr(ref_temp, key):
                            if key == "fk_transaction_head_id":
                                setattr(ref, key, head.id)
                            elif key == "fk_transaction_product_id" and getattr(ref_temp, key):
                                # Map temp product ID to permanent product ID
                                setattr(ref, key, product_id_map.get(getattr(ref_temp, key)))
                            else:
                                setattr(ref, key, getattr(ref_temp, key))
                    ref.id = uuid4()
                    session.add(ref)
                
                # Surcharges
                for sur_temp in self.document_data.get("surcharges", []):
                    sur = TransactionSurcharge()
                    for key in sur_temp.__table__.columns.keys():
                        if hasattr(sur_temp, key):
                            if key == "fk_transaction_head_id":
                                setattr(sur, key, head.id)
                            else:
                                setattr(sur, key, getattr(sur_temp, key))
                    sur.id = uuid4()
                    session.add(sur)
                
                # Taxes
                for tax_temp in self.document_data.get("taxes", []):
                    tax = TransactionTax()
                    for key in tax_temp.__table__.columns.keys():
                        if hasattr(tax_temp, key):
                            if key == "fk_transaction_head_id":
                                setattr(tax, key, head.id)
                            elif key == "fk_transaction_product_id" and getattr(tax_temp, key):
                                # Map temp product ID to permanent product ID
                                setattr(tax, key, product_id_map.get(getattr(tax_temp, key)))
                            else:
                                setattr(tax, key, getattr(tax_temp, key))
                    tax.id = uuid4()
                    session.add(tax)
                
                # Tips
                for tip_temp in self.document_data.get("tips", []):
                    tip = TransactionTip()
                    for key in tip_temp.__table__.columns.keys():
                        if hasattr(tip_temp, key):
                            if key == "fk_transaction_head_id":
                                setattr(tip, key, head.id)
                            elif key == "fk_transaction_payment_id" and getattr(tip_temp, key):
                                # Map temp payment ID to permanent payment ID
                                setattr(tip, key, payment_id_map.get(getattr(tip_temp, key)))
                            else:
                                setattr(tip, key, getattr(tip_temp, key))
                    tip.id = uuid4()
                    session.add(tip)
                
                session.commit()
            
            print(f"[DEBUG] Completed document: {head_temp.transaction_unique_id}")
            
            # Reset document_data
            self.document_data = None
            
            return True
            
        except Exception as e:
            print(f"[DEBUG] Error completing document: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def set_document_pending(self, is_pending=True):
        """
        Set the current document as pending (suspended) or resume it.
        
        Args:
            is_pending: True to suspend, False to resume
        """
        from data_layer.engine import Engine
        
        if not self.document_data or not self.document_data.get("head"):
            print("[DEBUG] No document to set pending")
            return False
        
        try:
            head = self.document_data["head"]
            head.is_pending = is_pending
            
            if is_pending:
                head.transaction_status = TransactionStatus.PENDING.value
            else:
                head.transaction_status = TransactionStatus.ACTIVE.value
            
            # Save to database
            with Engine().get_session() as session:
                session.merge(head)
                session.commit()
            
            print(f"[DEBUG] Document {'suspended' if is_pending else 'resumed'}: {head.transaction_unique_id}")
            return True
            
        except Exception as e:
            print(f"[DEBUG] Error setting document pending: {e}")
            import traceback
            traceback.print_exc()
            return False
    
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