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

from decimal import Decimal, InvalidOperation
from typing import Optional, Dict, Any
from data_layer.enums.event_name import EventName
from data_layer.model.definition.transaction_status import TransactionStatus
from data_layer.model.definition.transaction_payment_temp import TransactionPaymentTemp
from data_layer.model.definition.transaction_change_temp import TransactionChangeTemp
from pos.exceptions import PaymentError, InvalidAmountError, PaymentAlreadyCompleteError



from core.logger import get_logger

logger = get_logger(__name__)

class PaymentService:
    """
    Payment business logic service.
    
    This service contains the business logic for processing payments including:
    - Payment processing with button name parsing
    - Change calculation and recording
    - Document completion checking
    - Closure updates
    
    All payment calculations and business rules are handled here, separate from
    event handlers to improve code organization and reusability.
    """
    
    @staticmethod
    def _safe_decimal(value) -> Decimal:
        """
        Safely convert a value to Decimal.
        
        Handles None, string, int, float, and Decimal types.
        Returns Decimal('0') if conversion fails.
        
        Args:
            value: Value to convert (can be None, str, int, float, Decimal)
        
        Returns:
            Decimal: Converted value, or Decimal('0') if conversion fails
        """
        if value is None:
            return Decimal('0')
        
        if isinstance(value, Decimal):
            return value
        
        try:
            # Try direct conversion first
            if isinstance(value, (int, float)):
                return Decimal(str(value))
            
            # For string values, strip whitespace
            if isinstance(value, str):
                value = value.strip()
                if not value or value.lower() in ['none', 'null', '']:
                    return Decimal('0')
                return Decimal(value)
            
            # For other types, try string conversion
            return Decimal(str(value))
            
        except (ValueError, InvalidOperation, TypeError):
            logger.warning("[PAYMENT_SERVICE] Warning: Could not convert %s (%s) to Decimal, using 0", value, type(value))
            return Decimal('0')
    
    @staticmethod
    def calculate_payment_amount(button_name: str, remaining_amount: Decimal, payment_type: str) -> Decimal:
        """
        Calculate payment amount based on button name and payment type.
        
        Button name parsing rules:
        - PAYMENT prefix: Pay remaining balance
        - CASH prefix: Pay specific amount (number after CASH divided by 100)
        - Otherwise: Pay remaining balance
        
        Payment type rules:
        - CASH_PAYMENT, CHECK_PAYMENT, EXCHANGE_PAYMENT: Exact button amount
        - CREDIT_PAYMENT, PREPAID_PAYMENT, CHARGE_SALE_PAYMENT, OTHER_PAYMENT: 
          Min(button_amount, remaining_balance)
        
        Args:
            button_name: Button control name
            remaining_amount: Remaining balance to be paid
            payment_type: Payment type string (CASH_PAYMENT, CREDIT_PAYMENT, etc.)
        
        Returns:
            Decimal: Calculated payment amount
        """
        payment_amount = Decimal('0')
        
        if button_name.upper().startswith("PAYMENT"):
            # PAYMENT prefix: pay remaining balance
            payment_amount = remaining_amount
        elif button_name.upper().startswith("CASH"):
            # CASH prefix: extract amount from button name
            # Remove "CASH" prefix and parse number (divide by 100)
            amount_str = button_name[4:]  # Remove "CASH" (4 characters)
            try:
                amount_value = int(amount_str)
                payment_amount = Decimal(str(amount_value)) / Decimal('100')
            except (ValueError, IndexError):
                raise InvalidAmountError(f"Invalid CASH button name format: {button_name}")
        else:
            # No special prefix: pay remaining balance
            payment_amount = remaining_amount
        
        # For certain payment types, limit payment to remaining balance
        if payment_type in [EventName.CREDIT_PAYMENT.value, EventName.PREPAID_PAYMENT.value,
                           EventName.CHARGE_SALE_PAYMENT.value, EventName.OTHER_PAYMENT.value]:
            if payment_amount > remaining_amount:
                payment_amount = remaining_amount
        
        return payment_amount
    
    @staticmethod
    def process_payment(document_data: Dict[str, Any], payment_type: str, 
                       button_name: str = "") -> tuple[bool, Optional[TransactionPaymentTemp], Optional[str]]:
        """
        Process a payment and create TransactionPaymentTemp record.
        
        Args:
            document_data: Document data dictionary with head and payments
            payment_type: Payment type string (CASH_PAYMENT, CREDIT_PAYMENT, etc.)
            button_name: Optional button control name for amount calculation
        
        Returns:
            tuple: (success, payment_temp, error_message)
        """
        if not document_data or not document_data.get("head"):
            return False, None, "No active document"
        
        try:
            head_temp = document_data["head"]
            
            # Calculate remaining balance (use safe decimal conversion)
            total_amount = PaymentService._safe_decimal(head_temp.total_amount)
            total_payment = PaymentService._safe_decimal(head_temp.total_payment_amount)
            remaining_amount = total_amount - total_payment
            
            if remaining_amount <= 0:
                return False, None, "Document already fully paid"
            
            # Calculate payment amount
            try:
                payment_amount = PaymentService.calculate_payment_amount(
                    button_name, remaining_amount, payment_type
                )
            except (PaymentError, InvalidAmountError) as e:
                return False, None, str(e)
            
            if payment_amount <= 0:
                raise InvalidAmountError("Payment amount must be greater than zero")
            
            # Get next line number for payment
            payments = document_data.get("payments", [])
            line_no = len(payments) + 1
            
            # Create payment record
            payment_temp = TransactionPaymentTemp()
            payment_temp.fk_transaction_head_id = head_temp.id
            payment_temp.line_no = line_no
            payment_temp.payment_type = payment_type
            payment_temp.payment_total = payment_amount
            payment_temp.currency_code = head_temp.base_currency or "GBP"
            payment_temp.currency_total = payment_amount
            payment_temp.currency_exchange_rate = Decimal('1.0')
            payment_temp.payment_status = "approved"
            
            # Save payment record
            payment_temp.create()
            
            # Add to document_data
            if "payments" not in document_data:
                document_data["payments"] = []
            document_data["payments"].append(payment_temp)
            
            # Update head_temp total_payment_amount (use safe decimal conversion)
            current_payment = PaymentService._safe_decimal(head_temp.total_payment_amount)
            head_temp.total_payment_amount = current_payment + payment_amount
            try:
                head_temp.save()
            except Exception as save_err:
                # Log but do not abort: the in-memory value is already updated,
                # and mark_document_complete() will persist the final state.
                logger.warning(
                    "[PAYMENT_SERVICE] head_temp.save() failed (will retry on completion): %s",
                    save_err
                )
            
            return True, payment_temp, None
            
        except (PaymentError, InvalidAmountError) as e:
            return False, None, str(e)
        except Exception as e:
            logger.error("[PAYMENT_SERVICE] Unexpected error during payment processing: %s", e)
            return False, None, f"Error processing payment: {str(e)}"
    
    @staticmethod
    def calculate_change(document_data: Dict[str, Any]) -> Decimal:
        """
        Calculate change amount for a document.
        
        Change = total_payment_amount - total_amount
        
        Args:
            document_data: Document data dictionary with head
        
        Returns:
            Decimal: Change amount (can be negative if underpaid)
        """
        if not document_data or not document_data.get("head"):
            return Decimal('0')
        
        head_temp = document_data["head"]
        total_payment = PaymentService._safe_decimal(head_temp.total_payment_amount)
        total_amount = PaymentService._safe_decimal(head_temp.total_amount)
        change_amount = total_payment - total_amount
        return change_amount
    
    @staticmethod
    def record_change(document_data: Dict[str, Any]) -> tuple[bool, Optional[TransactionChangeTemp], Optional[str]]:
        """
        Record change amount in TransactionChangeTemp if change is positive.
        
        Args:
            document_data: Document data dictionary with head and changes
        
        Returns:
            tuple: (success, change_temp, error_message)
        """
        if not document_data or not document_data.get("head"):
            return False, None, "No active document"
        
        try:
            head_temp = document_data["head"]
            
            # Calculate change amount
            change_amount = PaymentService.calculate_change(document_data)
            
            # Only record if change is positive
            if change_amount > 0:
                # Get next line number for change
                changes = document_data.get("changes", [])
                line_no = len(changes) + 1
                
                # Create change record
                change_temp = TransactionChangeTemp()
                change_temp.fk_transaction_head_id = head_temp.id
                change_temp.line_no = line_no
                change_temp.change_amount = change_amount
                change_temp.currency = head_temp.base_currency or "GBP"
                
                # Save change record
                change_temp.create()
                
                # Add to document_data
                if "changes" not in document_data:
                    document_data["changes"] = []
                document_data["changes"].append(change_temp)
                
                # Update head_temp total_change_amount
                head_temp.total_change_amount = change_amount
                try:
                    head_temp.save()
                except Exception as save_err:
                    logger.warning(
                        "[PAYMENT_SERVICE] head_temp.save() in record_change failed "
                        "(non-fatal): %s", save_err
                    )
                
                return True, change_temp, None
            else:
                return False, None, f"No change due (change_amount: {change_amount})"
            
        except Exception as e:
            return False, None, f"Error recording change: {str(e)}"
    
    @staticmethod
    def is_document_complete(document_data: Dict[str, Any]) -> bool:
        """
        Check if document is fully paid and ready for completion.
        
        Document is complete when:
        total_amount = total_payment_amount - total_change_amount
        
        Args:
            document_data: Document data dictionary with head
        
        Returns:
            bool: True if document is complete, False otherwise
        """
        if not document_data or not document_data.get("head"):
            return False
        
        try:
            head_temp = document_data["head"]
            
            total_amount = PaymentService._safe_decimal(head_temp.total_amount)
            total_payment = PaymentService._safe_decimal(head_temp.total_payment_amount)
            total_change = PaymentService._safe_decimal(head_temp.total_change_amount)
            
            # Document is complete when: total_amount = total_payment - total_change
            # Use small tolerance for floating point comparison
            difference = abs(total_amount - (total_payment - total_change))
            is_complete = difference < Decimal('0.01')
            
            # Debug logging
            logger.debug("[PAYMENT_SERVICE] Document completion check:")
            logger.debug("  total_amount: %s", total_amount)
            logger.debug("  total_payment: %s", total_payment)
            logger.debug("  total_change: %s", total_change)
            logger.debug("  difference: %s", difference)
            logger.debug("  is_complete: %s", is_complete)
            
            return is_complete
            
        except Exception as e:
            logger.error("[PAYMENT_SERVICE] Error checking document completion: %s", e)
            return False
    
    @staticmethod
    def mark_document_complete(document_data: Dict[str, Any]) -> bool:
        """
        Mark document as complete by updating transaction status.
        
        Args:
            document_data: Document data dictionary with head
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not document_data or not document_data.get("head"):
            return False
        
        try:
            head_temp = document_data["head"]
            
            # Mark document as complete
            head_temp.transaction_status = TransactionStatus.COMPLETED.value
            head_temp.is_closed = True
            head_temp.save()
            
            logger.info("[PAYMENT_SERVICE] Document marked as complete: %s",
                        getattr(head_temp, 'transaction_unique_id', head_temp.id))
            return True
            
        except Exception as e:
            logger.error("[PAYMENT_SERVICE] mark_document_complete failed: %s", e)
            return False
    
    @staticmethod
    def update_closure_for_completion(closure: Dict[str, Any], document_data: Dict[str, Any]) -> bool:
        """
        Update closure with transaction totals when document is completed.
        
        Args:
            closure: Closure dictionary with closure instance
            document_data: Document data dictionary with head and payments
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not closure or not closure.get("closure"):
            return False
        
        if not document_data or not document_data.get("head"):
            return False
        
        try:
            closure_instance = closure["closure"]
            head_temp = document_data["head"]
            
            # Update closure totals (use safe decimal conversion)
            closure_instance.total_document_count += 1
            
            head_total = PaymentService._safe_decimal(head_temp.total_amount)
            head_vat = PaymentService._safe_decimal(head_temp.total_vat_amount)
            head_discount = PaymentService._safe_decimal(head_temp.total_discount_amount)
            head_tip = PaymentService._safe_decimal(head_temp.tip_amount)
            head_payment = PaymentService._safe_decimal(head_temp.total_payment_amount)
            
            closure_gross = PaymentService._safe_decimal(closure_instance.gross_sales_amount)
            closure_net = PaymentService._safe_decimal(closure_instance.net_sales_amount)
            closure_tax = PaymentService._safe_decimal(closure_instance.total_tax_amount)
            closure_discount = PaymentService._safe_decimal(closure_instance.total_discount_amount)
            closure_tip = PaymentService._safe_decimal(closure_instance.total_tip_amount)
            closure_cash = PaymentService._safe_decimal(closure_instance.closing_cash_amount)
            closure_paid = PaymentService._safe_decimal(closure_instance.paid_in_total)
            
            closure_instance.gross_sales_amount = closure_gross + head_total
            closure_instance.net_sales_amount = closure_net + (head_total - head_vat)
            closure_instance.total_tax_amount = closure_tax + head_vat
            closure_instance.total_discount_amount = closure_discount + head_discount
            closure_instance.total_tip_amount = closure_tip + head_tip
            closure_instance.valid_transaction_count += 1
            
            # Calculate cash payments total
            cash_total = Decimal('0')
            payment_count = 0
            if document_data.get("payments"):
                for payment in document_data["payments"]:
                    payment_count += 1
                    if payment.payment_type == EventName.CASH_PAYMENT.value:
                        cash_total += PaymentService._safe_decimal(payment.payment_total)
            
            closure_instance.closing_cash_amount = closure_cash + cash_total
            closure_instance.paid_in_count += payment_count
            closure_instance.paid_in_total = closure_paid + head_payment
            
            closure_instance.save()
            
            return True
            
        except Exception as e:
            logger.error("[PAYMENT_SERVICE] Error updating closure: %s", e)
            return False
    
    @staticmethod
    def copy_temp_to_permanent(document_data: Dict[str, Any]) -> bool:
        """
        Copy all temp models to permanent models.
        
        Args:
            document_data: Document data dictionary with all temp models
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            from data_layer.model.definition.transaction_head import TransactionHead
            from data_layer.model.definition.transaction_payment import TransactionPayment
            from data_layer.model.definition.transaction_change import TransactionChange
            from uuid import uuid4
            
            if not document_data or not document_data.get("head"):
                return False
            
            head_temp = document_data["head"]
            
            # Copy head
            head = TransactionHead()
            for key in head_temp.__table__.columns.keys():
                if hasattr(head_temp, key):
                    setattr(head, key, getattr(head_temp, key))
            head.id = uuid4()
            head.create()
            
            # Copy payments
            if document_data.get("payments"):
                for pay_temp in document_data["payments"]:
                    pay = TransactionPayment()
                    for key in pay_temp.__table__.columns.keys():
                        if hasattr(pay_temp, key):
                            if key == "fk_transaction_head_id":
                                setattr(pay, key, head.id)
                            else:
                                setattr(pay, key, getattr(pay_temp, key))
                    pay.id = uuid4()
                    pay.create()
            
            # Copy changes
            if document_data.get("changes"):
                for change_temp in document_data["changes"]:
                    change = TransactionChange()
                    for key in change_temp.__table__.columns.keys():
                        if hasattr(change_temp, key):
                            if key == "fk_transaction_head_id":
                                setattr(change, key, head.id)
                            else:
                                setattr(change, key, getattr(change_temp, key))
                    change.id = uuid4()
                    change.create()
            
            return True
            
        except Exception as e:
            logger.error("[PAYMENT_SERVICE] Error copying temp to permanent: %s", e)
            return False

