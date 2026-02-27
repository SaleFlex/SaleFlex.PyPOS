"""
SaleFlex.PyPOS - Closure Manager Mixin

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

from core.logger import get_logger

logger = get_logger(__name__)

from datetime import date, datetime
from uuid import uuid4
from data_layer.model import (
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
)
from data_layer.auto_save import AutoSaveModel


class ClosureManager:
    """
    Mixin class for managing closure operations.
    
    This mixin provides methods for loading, creating, and closing closures,
    including all related summary data.
    """
    
    def load_open_closure(self):
        """
        Load the last open closure (closure_end_time is None) from database.
        
        If an open closure exists, it will be loaded with all its summary data.
        If no open closure exists, a new empty closure will be created.
        
        This method should be called at application startup after database initialization
        and after pos_data/product_data are populated.
        """
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
                    logger.info("[DEBUG] Loaded open closure: %s", open_closure.closure_unique_id)
                else:
                    # No open closure exists, create a new empty one
                    logger.debug("[DEBUG] No open closure found, creating new empty closure")
                    self.create_empty_closure()
        except Exception as e:
            logger.error("[DEBUG] Error loading open closure: %s", e)
            # On error, try to create a new empty closure
            try:
                self.create_empty_closure()
            except Exception as e2:
                logger.error("[DEBUG] Error creating empty closure: %s", e2)
    
    def _load_closure_data(self, closure_id):
        """
        Load all closure data (main record + all summaries) into self.closure dictionary.
        
        Args:
            closure_id: UUID of the closure to load
        """
        try:
            # Load main closure record using CRUD.get_by_id()
            closure = Closure.get_by_id(closure_id)
            if not closure:
                logger.error("[DEBUG] Closure not found: %s", closure_id)
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
            
            # Load all summary records using CRUD.filter_by() and find_first()
            self.closure["cashier_summaries"] = ClosureCashierSummary.filter_by(
                fk_closure_id=closure_id, is_deleted=False
            )
            
            self.closure["country_specific"] = ClosureCountrySpecific.find_first(
                fk_closure_id=closure_id, is_deleted=False
            )
            
            self.closure["currencies"] = ClosureCurrency.filter_by(
                fk_closure_id=closure_id, is_deleted=False
            )
            
            self.closure["department_summaries"] = ClosureDepartmentSummary.filter_by(
                fk_closure_id=closure_id, is_deleted=False
            )
            
            self.closure["discount_summaries"] = ClosureDiscountSummary.filter_by(
                fk_closure_id=closure_id, is_deleted=False
            )
            
            self.closure["document_type_summaries"] = ClosureDocumentTypeSummary.filter_by(
                fk_closure_id=closure_id, is_deleted=False
            )
            
            self.closure["payment_type_summaries"] = ClosurePaymentTypeSummary.filter_by(
                fk_closure_id=closure_id, is_deleted=False
            )
            
            self.closure["tip_summaries"] = ClosureTipSummary.filter_by(
                fk_closure_id=closure_id, is_deleted=False
            )
            
            self.closure["vat_summaries"] = ClosureVATSummary.filter_by(
                fk_closure_id=closure_id, is_deleted=False
            )
            
            logger.info("[DEBUG] Loaded closure data: %s cashiers, "
                  f"%s currencies, "
                  f"%s departments", len(self.closure['cashier_summaries']), len(self.closure['currencies']), len(self.closure['department_summaries']))
        except Exception as e:
            logger.error("[DEBUG] Error loading closure data: %s", e)
    
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
        from data_layer.engine import Engine
        
        try:
            # Validate required data
            if not self.pos_settings:
                logger.error("[DEBUG] Cannot create closure: pos_settings not loaded")
                return
            
            # Get store_id from pos_data["Store"]
            store_id = None
            stores = self.pos_data.get("Store", [])
            if stores:
                store_id = stores[0].id
                logger.debug("[DEBUG] Using store for closure: %s", store_id)
            else:
                logger.error("[DEBUG] Cannot create closure: no store found in pos_data")
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
                    logger.error("[DEBUG] Cannot create closure: no currency found")
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
                    logger.debug("[DEBUG] Using fallback cashier for closure: %s", cashier_id)
                else:
                    logger.warning("[DEBUG] Warning: No cashier available, closure will be created without cashier")
                    # Note: fk_cashier_opened_id is nullable=False, so we need a cashier
                    # In production, you might want to create a system cashier or handle this differently
                    return
            
            # Get next closure number (daily sequence)
            today = date.today()
            
            # Find the highest closure_number for today using Engine for complex query
            # CRUD.filter_by() doesn't support date comparison and ordering yet
            with Engine().get_session() as session:
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
            
            # Save to database using CRUD.create()
            new_closure.create()
            
            # Load the closure data into self.closure
            self._load_closure_data(new_closure.id)
            
            logger.info("[DEBUG] Created new empty closure: %s", closure_unique_id)
        except Exception as e:
            logger.error("[DEBUG] Error creating empty closure: %s", e)
    
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
        
        if not self.closure or not self.closure.get("closure"):
            logger.debug("[DEBUG] No open closure to close")
            return
        
        if not self.cashier_data:
            logger.error("[DEBUG] Cannot close closure: cashier_data not set (user not logged in)")
            return
        
        try:
            closure = self.closure["closure"]
            # Unwrap if it's an AutoSaveModel (AutoSaveModel will handle the save automatically)
            closure_unwrapped = closure.unwrap() if isinstance(closure, AutoSaveModel) else closure
            
            # Update closure with closing information
            # Use the wrapped version so AutoSaveModel can intercept and save
            closure.closure_end_time = datetime.now()
            closure.fk_cashier_closed_id = self.cashier_data.id
            
            if closing_cash_amount is not None:
                closure.closing_cash_amount = closing_cash_amount
                # Calculate cash difference
                closure.cash_difference = closing_cash_amount - closure.expected_cash_amount
            
            if description:
                closure.description = description
            
            # Save closure using CRUD.save() (AutoSaveModel already saved it, but we ensure it's saved)
            if hasattr(closure_unwrapped, 'save'):
                closure_unwrapped.save()
            
            # Save all summaries using CRUD.save() or CRUD.create()
            for summary_list_name in [
                "cashier_summaries", "currencies", "department_summaries",
                "discount_summaries", "document_type_summaries",
                "payment_type_summaries", "tip_summaries", "vat_summaries"
            ]:
                summaries = self.closure.get(summary_list_name, [])
                for summary in summaries:
                    # Unwrap if it's an AutoSaveModel
                    if isinstance(summary, AutoSaveModel):
                        summary = summary.unwrap()
                    if not summary.id:  # New record
                        closure_id = closure.id if not isinstance(closure, AutoSaveModel) else closure.unwrap().id
                        summary.fk_closure_id = closure_id
                    # Save using CRUD methods
                    if summary.id and hasattr(summary, 'save'):
                        summary.save()
                    elif not summary.id and hasattr(summary, 'create'):
                        summary.create()
            
            # Save country_specific if exists using CRUD.save() or CRUD.create()
            if self.closure.get("country_specific"):
                country_specific = self.closure["country_specific"]
                # Unwrap if it's an AutoSaveModel
                if isinstance(country_specific, AutoSaveModel):
                    country_specific = country_specific.unwrap()
                if not country_specific.id:  # New record
                    closure_id = closure.id if not isinstance(closure, AutoSaveModel) else closure.unwrap().id
                    country_specific.fk_closure_id = closure_id
                # Save using CRUD methods
                if country_specific.id and hasattr(country_specific, 'save'):
                    country_specific.save()
                elif not country_specific.id and hasattr(country_specific, 'create'):
                    country_specific.create()
            
            logger.debug("[DEBUG] Closed closure: %s", closure.closure_unique_id)
            
            # Create new empty closure
            self.create_empty_closure()
            
        except Exception as e:
            logger.error("[DEBUG] Error closing closure: %s", e)

