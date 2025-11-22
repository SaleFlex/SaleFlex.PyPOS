"""
SaleFlex.PyPOS - Document Manager Mixin

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

from datetime import datetime
from uuid import uuid4
from data_layer.model import (
    TransactionHead,
    TransactionHeadTemp,
    TransactionProduct,
    TransactionProductTemp,
    TransactionPayment,
    TransactionPaymentTemp,
    TransactionDiscount,
    TransactionDiscountTemp,
    TransactionDepartment,
    TransactionDepartmentTemp,
    TransactionDelivery,
    TransactionDeliveryTemp,
    TransactionKitchenOrder,
    TransactionKitchenOrderTemp,
    TransactionLoyalty,
    TransactionLoyaltyTemp,
    TransactionNote,
    TransactionNoteTemp,
    TransactionFiscal,
    TransactionFiscalTemp,
    TransactionRefund,
    TransactionRefundTemp,
    TransactionSurcharge,
    TransactionSurchargeTemp,
    TransactionTax,
    TransactionTaxTemp,
    TransactionTip,
    TransactionTipTemp,
    TransactionChange,
    TransactionChangeTemp,
)
from data_layer.model.definition.transaction_status import TransactionStatus, TransactionType
from data_layer.auto_save import AutoSaveModel


class DocumentManager:
    """
    Mixin class for managing documents/transactions.
    
    This mixin provides methods for creating, loading, completing, and managing
    transaction documents. It handles both temporary (Temp) and permanent models.
    """
    
    def create_empty_document(self):
        """
        Create a new empty document with all transaction temp models initialized.
        
        This method creates a fresh document structure with:
        - TransactionHeadTemp initialized with default values:
          * document_type: From CurrentStatus.document_type property
          * transaction_type: From CurrentStatus.document_type property (mapped to TransactionType)
          * transaction_status: TransactionStatus.DRAFT
          * closure_number: TransactionSequence with name="ClosureNumber"
          * receipt_number: TransactionSequence with name="ReceiptNumber"
          * fk_store_id: First Store from pos_data
        - All other temp models initialized as empty lists or None
        
        This method should be called when starting a new transaction.
        """
        try:
            # Validate required data
            if not self.pos_settings:
                print("[DEBUG] Cannot create document: pos_settings not loaded")
                return None
            
            # Get document_type from CurrentStatus.document_type property
            # CurrentStatus.document_type is a DocumentType enum, convert to string
            from pos.data import DocumentType
            current_doc_type = self.document_type if hasattr(self, 'document_type') else DocumentType.FISCAL_RECEIPT
            
            # Convert enum to string - use name attribute for enum
            if isinstance(current_doc_type, DocumentType):
                document_type = current_doc_type.name
            elif hasattr(current_doc_type, 'name'):
                document_type = current_doc_type.name
            else:
                document_type = str(current_doc_type)
            
            print(f"[DEBUG] CurrentStatus.document_type: {current_doc_type}, converted to: {document_type}")
            
            # Get transaction_type from CurrentStatus.document_type property
            # Map DocumentType to TransactionType (default to SALE)
            transaction_type = TransactionType.SALE.value
            if current_doc_type == DocumentType.RETURN_SLIP:
                transaction_type = TransactionType.RETURN.value
            elif current_doc_type == DocumentType.ELECTRONIC_RECEIPT:
                transaction_type = TransactionType.SALE.value
            # Add more mappings as needed
            
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
            
            # batch_number is the same as closure_number
            batch_number = closure_number
            
            # Get store_id from pos_data["Store"]
            store_id = None
            stores = self.pos_data.get("Store", [])
            if stores:
                store_id = stores[0].id
            else:
                print("[DEBUG] Cannot create document: no store found in pos_data")
                return None
            
            # Get customer_id - try to find "Walk-in Customer" or use first customer, or create default
            customer_id = None
            from data_layer.model import Customer
            from data_layer.engine import Engine
            
            # Try to find "Walk-in Customer" or "Anonymous Customer"
            with Engine().get_session() as session:
                walk_in_customer = session.query(Customer).filter(
                    Customer.name.ilike("%walk-in%") | Customer.name.ilike("%anonymous%"),
                    Customer.is_deleted == False
                ).first()
                
                if walk_in_customer:
                    customer_id = walk_in_customer.id
                    print(f"[DEBUG] Using walk-in customer: {walk_in_customer.name}")
                else:
                    # Try to get first customer
                    first_customer = session.query(Customer).filter(
                        Customer.is_deleted == False
                    ).first()
                    
                    if first_customer:
                        customer_id = first_customer.id
                        print(f"[DEBUG] Using first customer: {first_customer.name}")
                    else:
                        # Create default walk-in customer
                        default_customer = Customer(
                            name="Walk-in",
                            last_name="Customer",
                            description="Default walk-in customer for POS transactions"
                        )
                        # Set audit fields if cashier_data exists
                        if hasattr(self, 'cashier_data') and self.cashier_data:
                            default_customer.fk_cashier_create_id = self.cashier_data.id
                            default_customer.fk_cashier_update_id = self.cashier_data.id
                        default_customer.create()
                        customer_id = default_customer.id
                        print(f"[DEBUG] Created default walk-in customer: {customer_id}")
            
            if not customer_id:
                print("[DEBUG] Cannot create document: failed to get or create customer")
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
            head.transaction_type = transaction_type
            head.transaction_status = TransactionStatus.DRAFT.value
            head.fk_store_id = store_id
            head.fk_customer_id = customer_id
            head.closure_number = closure_number
            head.receipt_number = receipt_number
            head.batch_number = batch_number
            head.is_closed = False
            head.is_pending = False
            head.is_cancel = False
            
            # Initialize document_data structure
            self.document_data = {
                "head": head,
                "products": [],
                "payments": [],
                "discounts": [],
                "departments": [],
                "deliveries": [],
                "kitchen_orders": [],
                "loyalty": [],
                "notes": [],
                "fiscal": None,
                "refunds": [],
                "surcharges": [],
                "taxes": [],
                "tips": [],
                "changes": []
            }
            
            print(f"[DEBUG] Created new empty document: {transaction_unique_id}")
            print(f"[DEBUG] Document type: {document_type}, Transaction type: {transaction_type}, Receipt number: {receipt_number}")
            print(f"[DEBUG] head.document_type: {head.document_type}, head.transaction_type: {head.transaction_type}, head.receipt_number: {head.receipt_number}")
            
            # Update StatusBar if available
            self._update_statusbar()
            
            return self.document_data
            
        except Exception as e:
            print(f"[DEBUG] Error creating empty document: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _update_statusbar(self):
        """Update StatusBar if available in current window"""
        try:
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            if app:
                # Find the active window
                active_window = app.activeWindow()
                print(f"[DEBUG] _update_statusbar: active_window={active_window}")
                if active_window and hasattr(active_window, 'statusbar'):
                    statusbar = active_window.statusbar
                    print(f"[DEBUG] _update_statusbar: Found statusbar, calling update_info_label")
                    if statusbar and hasattr(statusbar, 'update_info_label'):
                        statusbar.update_info_label()
                else:
                    # Try to find statusbar in all windows
                    all_windows = app.allWindows()
                    print(f"[DEBUG] _update_statusbar: Checking {len(all_windows)} windows for statusbar")
                    for window in all_windows:
                        if hasattr(window, 'statusbar'):
                            statusbar = window.statusbar
                            print(f"[DEBUG] _update_statusbar: Found statusbar in window {window}, calling update_info_label")
                            if statusbar and hasattr(statusbar, 'update_info_label'):
                                statusbar.update_info_label()
                                break
        except Exception as e:
            # Print error for debugging
            print(f"[DEBUG] _update_statusbar error: {e}")
            import traceback
            traceback.print_exc()
            pass
    
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
            # Use Engine for complex query with multiple conditions and ordering
            # CRUD.filter_by() doesn't support complex queries yet
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
                self._load_document_data(incomplete_head.id)
                
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
            
            # Use Engine for complex query with ordering
            # CRUD.filter_by() doesn't support ordering yet
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
                    doc_data = self._load_document_data_dict(head.id)
                    if doc_data:
                        self.pending_documents_data.append(doc_data)
                
                print(f"[DEBUG] Loaded {len(self.pending_documents_data)} pending documents")
                
        except Exception as e:
            print(f"[DEBUG] Error loading pending documents: {e}")
            import traceback
            traceback.print_exc()
            self.pending_documents_data = []
    
    def _load_document_data(self, head_id):
        """
        Load all transaction temp models for a given transaction head ID.
        Populates self.document_data with the loaded data.
        
        Args:
            head_id: UUID of the TransactionHeadTemp
        """
        try:
            # Load head using CRUD.get_by_id()
            head = TransactionHeadTemp.get_by_id(head_id)
            if not head:
                print(f"[DEBUG] Transaction head not found: {head_id}")
                return
            
            # Load related models using CRUD.filter_by()
            # Initialize document_data structure
            self.document_data = {
                "head": head,
                "products": TransactionProductTemp.filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ),
                "payments": TransactionPaymentTemp.filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ),
                "discounts": TransactionDiscountTemp.filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ),
                "departments": TransactionDepartmentTemp.filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ),
                "deliveries": TransactionDeliveryTemp.filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ),
                "kitchen_orders": TransactionKitchenOrderTemp.filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ),
                "loyalty": TransactionLoyaltyTemp.filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ),
                "notes": TransactionNoteTemp.filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ),
                "fiscal": TransactionFiscalTemp.find_first(
                    fk_transaction_head_id=head_id, is_deleted=False
                ),
                "refunds": TransactionRefundTemp.filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ),
                "surcharges": TransactionSurchargeTemp.filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ),
                "taxes": TransactionTaxTemp.filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ),
                "tips": TransactionTipTemp.filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                )
            }
            
        except Exception as e:
            print(f"[DEBUG] Error loading document data: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_document_data_dict(self, head_id):
        """
        Load all transaction temp models for a given transaction head ID.
        Returns a dictionary with the loaded data (does not modify self.document_data).
        
        Args:
            head_id: UUID of the TransactionHeadTemp
            
        Returns:
            Dictionary with document data structure or None if head not found
        """
        try:
            # Load head using CRUD.get_by_id()
            head = TransactionHeadTemp.get_by_id(head_id)
            if not head:
                return None
            
            # Load related models using CRUD.filter_by()
            # Return document data dictionary
            return {
                "head": head,
                "products": TransactionProductTemp.filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ),
                "payments": TransactionPaymentTemp.filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ),
                "discounts": TransactionDiscountTemp.filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ),
                "departments": TransactionDepartmentTemp.filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ),
                "deliveries": TransactionDeliveryTemp.filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ),
                "kitchen_orders": TransactionKitchenOrderTemp.filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ),
                "loyalty": TransactionLoyaltyTemp.filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ),
                "notes": TransactionNoteTemp.filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ),
                "fiscal": TransactionFiscalTemp.find_first(
                    fk_transaction_head_id=head_id, is_deleted=False
                ),
                "refunds": TransactionRefundTemp.filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ),
                "surcharges": TransactionSurchargeTemp.filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ),
                "taxes": TransactionTaxTemp.filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ),
                "tips": TransactionTipTemp.filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                ),
                "changes": TransactionChangeTemp.filter_by(
                    fk_transaction_head_id=head_id, is_deleted=False
                )
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
        if not self.document_data or not self.document_data.get("head"):
            print("[DEBUG] No document to complete")
            return False
        
        try:
            # Unwrap if it's an AutoSaveModel
            head_temp = self.document_data["head"]
            if isinstance(head_temp, AutoSaveModel):
                head_temp = head_temp.unwrap()
            
            # Update head_temp status
            if is_cancel:
                head_temp.transaction_status = TransactionStatus.CANCELLED.value
                head_temp.is_cancel = True
                if cancel_reason:
                    head_temp.cancel_reason = cancel_reason
            else:
                head_temp.transaction_status = TransactionStatus.COMPLETED.value
            
            head_temp.is_closed = True
            
            # Save updated head_temp using CRUD.save()
            head_temp.save()
            
            # Copy head_temp to TransactionHead
            head = TransactionHead()
            # Copy all fields from head_temp
            for key in head_temp.__table__.columns.keys():
                if hasattr(head_temp, key):
                    setattr(head, key, getattr(head_temp, key))
            head.id = uuid4()  # New ID for permanent record
            
            # Create permanent head using CRUD.create()
            head.create()
            
            # Copy all related temp models to permanent models
            # Store mapping of temp IDs to permanent IDs for foreign key updates
            product_id_map = {}  # temp_id -> permanent_id
            payment_id_map = {}  # temp_id -> permanent_id
            total_id_map = {}    # temp_id -> permanent_id
            
            # Products
            for prod_temp in self.document_data.get("products", []):
                # Unwrap if it's an AutoSaveModel
                if isinstance(prod_temp, AutoSaveModel):
                    prod_temp = prod_temp.unwrap()
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
                # Create using CRUD.create()
                prod.create()
            
            # Payments
            for pay_temp in self.document_data.get("payments", []):
                # Unwrap if it's an AutoSaveModel
                if isinstance(pay_temp, AutoSaveModel):
                    pay_temp = pay_temp.unwrap()
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
                # Create using CRUD.create()
                pay.create()
            
            # Departments
            for dept_temp in self.document_data.get("departments", []):
                # Unwrap if it's an AutoSaveModel
                if isinstance(dept_temp, AutoSaveModel):
                    dept_temp = dept_temp.unwrap()
                dept = TransactionDepartment()
                temp_id = dept_temp.id
                for key in dept_temp.__table__.columns.keys():
                    if hasattr(dept_temp, key):
                        if key == "fk_transaction_head_id":
                            setattr(dept, key, head.id)
                        else:
                            setattr(dept, key, getattr(dept_temp, key))
                dept.id = uuid4()
                total_id_map[temp_id] = dept.id
                # Create using CRUD.create()
                dept.create()
            
            # Discounts
            for disc_temp in self.document_data.get("discounts", []):
                # Unwrap if it's an AutoSaveModel
                if isinstance(disc_temp, AutoSaveModel):
                    disc_temp = disc_temp.unwrap()
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
                        elif key == "fk_transaction_department_id" and getattr(disc_temp, key):
                            # Map temp department ID to permanent department ID
                            setattr(disc, key, total_id_map.get(getattr(disc_temp, key)))
                        elif key == "fk_transaction_total_id":  # Handle old field name for backward compatibility
                            # Map to new field name
                            if getattr(disc_temp, key):
                                setattr(disc, "fk_transaction_department_id", total_id_map.get(getattr(disc_temp, key)))
                        else:
                            setattr(disc, key, getattr(disc_temp, key))
                disc.id = uuid4()
                # Create using CRUD.create()
                disc.create()
            
            # Deliveries
            for del_temp in self.document_data.get("deliveries", []):
                # Unwrap if it's an AutoSaveModel
                if isinstance(del_temp, AutoSaveModel):
                    del_temp = del_temp.unwrap()
                del_rec = TransactionDelivery()
                for key in del_temp.__table__.columns.keys():
                    if hasattr(del_temp, key):
                        if key == "fk_transaction_head_id":
                            setattr(del_rec, key, head.id)
                        else:
                            setattr(del_rec, key, getattr(del_temp, key))
                del_rec.id = uuid4()
                # Create using CRUD.create()
                del_rec.create()
            
            # Kitchen Orders
            for ko_temp in self.document_data.get("kitchen_orders", []):
                # Unwrap if it's an AutoSaveModel
                if isinstance(ko_temp, AutoSaveModel):
                    ko_temp = ko_temp.unwrap()
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
                # Create using CRUD.create()
                ko.create()
            
            # Loyalty
            for loy_temp in self.document_data.get("loyalty", []):
                # Unwrap if it's an AutoSaveModel
                if isinstance(loy_temp, AutoSaveModel):
                    loy_temp = loy_temp.unwrap()
                loy = TransactionLoyalty()
                for key in loy_temp.__table__.columns.keys():
                    if hasattr(loy_temp, key):
                        if key == "fk_transaction_head_id":
                            setattr(loy, key, head.id)
                        else:
                            setattr(loy, key, getattr(loy_temp, key))
                loy.id = uuid4()
                # Create using CRUD.create()
                loy.create()
            
            # Notes
            for note_temp in self.document_data.get("notes", []):
                # Unwrap if it's an AutoSaveModel
                if isinstance(note_temp, AutoSaveModel):
                    note_temp = note_temp.unwrap()
                note = TransactionNote()
                for key in note_temp.__table__.columns.keys():
                    if hasattr(note_temp, key):
                        if key == "fk_transaction_head_id":
                            setattr(note, key, head.id)
                        else:
                            setattr(note, key, getattr(note_temp, key))
                note.id = uuid4()
                # Create using CRUD.create()
                note.create()
            
            # Fiscal
            if self.document_data.get("fiscal"):
                fiscal_temp = self.document_data["fiscal"]
                # Unwrap if it's an AutoSaveModel
                if isinstance(fiscal_temp, AutoSaveModel):
                    fiscal_temp = fiscal_temp.unwrap()
                fiscal = TransactionFiscal()
                for key in fiscal_temp.__table__.columns.keys():
                    if hasattr(fiscal_temp, key):
                        if key == "fk_transaction_head_id":
                            setattr(fiscal, key, head.id)
                        else:
                            setattr(fiscal, key, getattr(fiscal_temp, key))
                fiscal.id = uuid4()
                # Create using CRUD.create()
                fiscal.create()
            
            # Refunds
            for ref_temp in self.document_data.get("refunds", []):
                # Unwrap if it's an AutoSaveModel
                if isinstance(ref_temp, AutoSaveModel):
                    ref_temp = ref_temp.unwrap()
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
                # Create using CRUD.create()
                ref.create()
            
            # Surcharges
            for sur_temp in self.document_data.get("surcharges", []):
                # Unwrap if it's an AutoSaveModel
                if isinstance(sur_temp, AutoSaveModel):
                    sur_temp = sur_temp.unwrap()
                sur = TransactionSurcharge()
                for key in sur_temp.__table__.columns.keys():
                    if hasattr(sur_temp, key):
                        if key == "fk_transaction_head_id":
                            setattr(sur, key, head.id)
                        else:
                            setattr(sur, key, getattr(sur_temp, key))
                sur.id = uuid4()
                # Create using CRUD.create()
                sur.create()
            
            # Taxes
            for tax_temp in self.document_data.get("taxes", []):
                # Unwrap if it's an AutoSaveModel
                if isinstance(tax_temp, AutoSaveModel):
                    tax_temp = tax_temp.unwrap()
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
                # Create using CRUD.create()
                tax.create()
            
            # Tips
            for tip_temp in self.document_data.get("tips", []):
                # Unwrap if it's an AutoSaveModel
                if isinstance(tip_temp, AutoSaveModel):
                    tip_temp = tip_temp.unwrap()
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
                # Create using CRUD.create()
                tip.create()
            
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
        if not self.document_data or not self.document_data.get("head"):
            print("[DEBUG] No document to set pending")
            return False
        
        try:
            head = self.document_data["head"]
            # Unwrap if it's an AutoSaveModel (AutoSaveModel will handle the save automatically)
            if isinstance(head, AutoSaveModel):
                head.is_pending = is_pending
                if is_pending:
                    head.transaction_status = TransactionStatus.PENDING.value
                else:
                    head.transaction_status = TransactionStatus.ACTIVE.value
                # AutoSaveModel automatically saves on attribute change
            else:
                # Fallback: manual save if not wrapped
                head.is_pending = is_pending
                if is_pending:
                    head.transaction_status = TransactionStatus.PENDING.value
                else:
                    head.transaction_status = TransactionStatus.ACTIVE.value
                # Save to database using CRUD.save()
                if hasattr(head, 'save'):
                    head.save()
            
            print(f"[DEBUG] Document {'suspended' if is_pending else 'resumed'}: {head.transaction_unique_id}")
            return True
            
        except Exception as e:
            print(f"[DEBUG] Error setting document pending: {e}")
            import traceback
            traceback.print_exc()
            return False

