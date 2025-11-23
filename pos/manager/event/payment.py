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

from decimal import Decimal
from data_layer.enums.event_name import EventName
from pos.service.payment_service import PaymentService


class PaymentEvent:
    """
    Payment Event Handler for POS transaction payment processing.
    
    This class handles all payment-related events including:
    - Various payment methods (cash, credit, check, etc.)
    - Payment validation and processing
    - Change calculation and dispensing
    - Payment suspension and recovery
    - Payment details and receipts
    
    All methods require valid authentication and active transaction.
    Methods handle payment validation, processing, and completion
    according to POS business rules and regulations.
    """
    
    # ==================== GENERAL PAYMENT EVENTS ====================
    
    def _payment_event(self):
        """
        Handle general payment processing selection.
        
        Displays payment method selection interface and routes
        to appropriate specific payment handler based on user choice.
        
        Process:
        1. Verify transaction total is ready for payment
        2. Display payment method selection interface
        3. Handle payment method selection
        4. Route to specific payment processor
        
        Returns:
            bool: True if payment selection successful, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
            
        # TODO: Implement payment method selection interface
        print("Payment method selection - functionality to be implemented")
        return False
    
    def _payment_detail_event(self):
        """
        Handle payment detail display and management.
        
        Shows detailed breakdown of payment amounts, methods used,
        change due, and payment status for current transaction.
        
        Returns:
            bool: True if payment details displayed successfully, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
            
        # TODO: Implement payment detail display
        print("Payment detail - functionality to be implemented")
        return False
    
    # ==================== CASH PAYMENT EVENTS ====================
    
    def _cash_payment_event(self, button=None, key=None):
        """
        Handle cash payment processing.
        
        Processes cash payment with change calculation and validation.
        Handles cash drawer opening and change dispensing.
        
        Process:
        1. Get cash amount tendered from input or button name
        2. Validate amount is sufficient for transaction total
        3. Calculate change due
        4. Open cash drawer
        5. Record payment and complete transaction
        6. Print receipt if required
        
        Parameters:
            button: Optional button object with control_name and form_control_function1
            key: Optional parameter from numpad input
        
        Returns:
            bool: True if cash payment processed successfully, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
        
        return self._process_payment(EventName.CASH_PAYMENT.value, button)
    
    # ==================== ELECTRONIC PAYMENT EVENTS ====================
    
    def _credit_payment_event(self, button=None, key=None):
        """
        Handle credit card payment processing.
        
        Processes credit card transactions through payment gateway,
        handles authorization, and manages transaction completion.
        
        Process:
        1. Initiate credit card reader/input
        2. Get card information (number, expiry, CVV)
        3. Send authorization request to payment processor
        4. Handle authorization response
        5. Complete transaction or handle decline
        6. Print receipt with signature line if required
        
        Parameters:
            button: Optional button object with control_name and form_control_function1
            key: Optional parameter from numpad input
        
        Returns:
            bool: True if credit payment processed successfully, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
        
        return self._process_payment(EventName.CREDIT_PAYMENT.value, button)
    
    def _check_payment_event(self, button=None, key=None):
        """
        Handle check payment processing.
        
        Processes personal or business check payments with
        validation and fraud prevention measures.
        
        Process:
        1. Get check information (number, amount, bank details)
        2. Validate check amount matches transaction total
        3. Perform check verification if available
        4. Record check payment details
        5. Complete transaction
        6. Store check information for deposit
        
        Parameters:
            button: Optional button object with control_name and form_control_function1
            key: Optional parameter from numpad input
        
        Returns:
            bool: True if check payment processed successfully, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
        
        return self._process_payment(EventName.CHECK_PAYMENT.value, button)
    
    # ==================== ALTERNATIVE PAYMENT EVENTS ====================
    
    def _exchange_payment_event(self, button=None):
        """
        Handle exchange/trade-in payment processing.
        
        Processes payments where goods are exchanged for other goods
        or applied as credit toward purchase.
        
        Parameters:
            button: Optional button object with control_name and form_control_function1
        
        Returns:
            bool: True if exchange payment processed successfully, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
        
        return self._process_payment(EventName.EXCHANGE_PAYMENT.value, button)
    
    def _prepaid_payment_event(self, button=None, key=None):
        """
        Handle prepaid card or voucher payment processing.
        
        Processes payments using prepaid cards, gift cards,
        or store credit vouchers.
        
        Process:
        1. Read prepaid card/voucher information
        2. Validate card status and available balance
        3. Deduct payment amount from card balance
        4. Complete transaction or handle insufficient funds
        5. Update card balance and transaction records
        
        Parameters:
            button: Optional button object with control_name and form_control_function1
            key: Optional parameter from numpad input
        
        Returns:
            bool: True if prepaid payment processed successfully, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
        
        return self._process_payment(EventName.PREPAID_PAYMENT.value, button)
    
    def _charge_sale_payment_event(self, button=None):
        """
        Handle charge sale payment processing.
        
        Processes payments where amount is charged to customer account
        for later billing (house accounts, corporate accounts).
        
        Parameters:
            button: Optional button object with control_name and form_control_function1
        
        Returns:
            bool: True if charge sale processed successfully, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
        
        return self._process_payment(EventName.CHARGE_SALE_PAYMENT.value, button)
    
    def _other_payment_event(self, button=None, key=None):
        """
        Handle other/miscellaneous payment methods.
        
        Processes alternative payment methods not covered by
        standard payment types (mobile payments, digital wallets, etc.).
        
        Parameters:
            button: Optional button object with control_name and form_control_function1
            key: Optional parameter from numpad input
        
        Returns:
            bool: True if other payment processed successfully, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
        
        return self._process_payment(EventName.OTHER_PAYMENT.value, button)
    
    def _change_payment_event(self, button=None):
        """
        Handle change payment calculation and recording.
        
        Calculates change amount when payment exceeds transaction total
        and records it in TransactionChangeTemp. After recording change,
        completes the document.
        
        Parameters:
            button: Optional button object (name not important for this event)
        
        Returns:
            bool: True if change payment processed successfully, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
        
        if not self.document_data or not self.document_data.get("head"):
            print("[PAYMENT] No active document for change calculation")
            return False
        
        try:
            # Use PaymentService to record change
            success, change_temp, error_message = PaymentService.record_change(self.document_data)
            
            if success:
                print(f"[PAYMENT] Change recorded: {change_temp.change_amount} {change_temp.currency}")
                
                # Update UI controls
                self._update_payment_ui("CHANGE", change_temp.change_amount)
                
                # Check if document is complete and complete it
                self._check_and_complete_document()
            else:
                print(f"[PAYMENT] {error_message}")
            
            return success
            
        except Exception as e:
            print(f"[PAYMENT] Error processing change payment: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _process_payment(self, payment_type, button=None):
        """
        Process a payment based on payment type and button information.
        
        Handles payment button name parsing:
        - PAYMENT prefix: Pay remaining balance
        - CASH prefix: Pay specific amount (number after CASH divided by 100)
        
        Parameters:
            payment_type: Payment type string (CASH_PAYMENT, CREDIT_PAYMENT, etc.)
            button: Optional button object with control_name attribute
        
        Returns:
            bool: True if payment processed successfully, False otherwise
        """
        if not self.document_data or not self.document_data.get("head"):
            print("[PAYMENT] No active document")
            return False
        
        try:
            # Get button name if button is provided
            button_name = ""
            if button and hasattr(button, 'control_name'):
                button_name = button.control_name or ""
            
            # Use PaymentService to process payment
            success, payment_temp, error_message = PaymentService.process_payment(
                self.document_data, payment_type, button_name
            )
            
            if not success:
                print(f"[PAYMENT] {error_message}")
                return False
            
            # Update UI controls
            self._update_payment_ui(payment_type, payment_temp.payment_total)
            
            print(f"[PAYMENT] Payment recorded: {payment_temp.payment_total} {payment_temp.currency_code} ({payment_type})")
            
            # Check if change is needed (payment exceeds total)
            change_amount = PaymentService.calculate_change(self.document_data)
            if change_amount > 0:
                print(f"[PAYMENT] Change needed: {change_amount}")
                # Check if change_payment button exists in the current window
                has_change_button = self._has_change_payment_button()
                
                if has_change_button:
                    # Change button exists - just inform user, don't record change automatically
                    print(f"[PAYMENT] Change payment button found. User should click change button to record change.")
                    # Don't complete document yet - wait for change button click
                else:
                    # No change button - show info message and record change when OK is clicked
                    print(f"[PAYMENT] No change payment button found, showing MessageForm for change amount: {change_amount}")
                    self._show_change_info_and_record(change_amount)
                    # _show_change_info_and_record will handle document completion after change is recorded
                    return True
            else:
                # No change needed - check if document is complete and complete it if so
                self._check_and_complete_document()
            
            return True
            
        except Exception as e:
            print(f"[PAYMENT] Error processing payment: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _update_payment_ui(self, payment_type, payment_amount):
        """
        Update PaymentList and AmountTable UI controls after payment.
        
        Parameters:
            payment_type: Payment type string
            payment_amount: Payment amount as Decimal
        """
        try:
            # Get current window
            window = self.interface.window if hasattr(self, 'interface') else None
            if not window:
                return
            
            # Update PaymentList if it exists
            if hasattr(window, 'payment_list') and window.payment_list:
                payment_list = window.payment_list
                # Get currency from document
                currency = "GBP"
                if self.document_data and self.document_data.get("head"):
                    currency = self.document_data["head"].base_currency or "GBP"
                
                # Add payment to list
                payment_list.add_payment(
                    payment_type=payment_type,
                    amount=float(payment_amount),
                    currency=currency,
                    rate=1.0,
                    payment_id=len(payment_list._payment_data_list)
                )
            
            # Update AmountTable if it exists
            if hasattr(window, 'amount_table') and window.amount_table:
                amount_table = window.amount_table
                if self.document_data and self.document_data.get("head"):
                    head_temp = self.document_data["head"]
                    
                    # Update payment amount
                    from decimal import Decimal
                    amount_table.receipt_total_payment = Decimal(str(head_temp.total_payment_amount))
                    
                    # Update balance
                    remaining = Decimal(str(head_temp.total_amount)) - Decimal(str(head_temp.total_payment_amount))
                    amount_table._set_amount_value(amount_table.BALANCE_AMOUNT_ROW, remaining)
                    
        except Exception as e:
            print(f"[PAYMENT] Error updating UI: {e}")
            import traceback
            traceback.print_exc()
    
    def _check_and_complete_document(self):
        """
        Check if document is fully paid and complete it if so.
        
        Document is complete when:
        total_amount = total_payment_amount - total_change_amount
        """
        if not self.document_data or not self.document_data.get("head"):
            return False
        
        try:
            # Use PaymentService to check if document is complete
            if not PaymentService.is_document_complete(self.document_data):
                return False
            
            # Mark document as complete
            if not PaymentService.mark_document_complete(self.document_data):
                return False
            
            # Update closure
            if self.closure:
                PaymentService.update_closure_for_completion(self.closure, self.document_data)
            
            # Increment receipt number
            self._increment_receipt_number()
            
            # Copy temp models to permanent models
            PaymentService.copy_temp_to_permanent(self.document_data)
            
            # Reset document_data
            self.document_data = None
            
            # Clear UI controls
            self._clear_sale_screen_controls()
            
            print("[PAYMENT] Document completed successfully")
            return True
            
        except Exception as e:
            print(f"[PAYMENT] Error checking document completion: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _clear_sale_screen_controls(self):
        """
        Clear all sale screen UI controls after document completion.
        
        Clears PaymentList, AmountTable, and SaleList controls.
        """
        try:
            # Get current window
            window = self.interface.window if hasattr(self, 'interface') else None
            if not window:
                return
            
            # Clear PaymentList if it exists
            if hasattr(window, 'payment_list') and window.payment_list:
                window.payment_list.clear_payments()
                print("[PAYMENT] PaymentList cleared")
            
            # Clear AmountTable if it exists
            if hasattr(window, 'amount_table') and window.amount_table:
                window.amount_table.clear()
                print("[PAYMENT] AmountTable cleared")
            
            # Clear SaleList if it exists
            if hasattr(window, 'sale_list') and window.sale_list:
                window.sale_list.clear_products()
                print("[PAYMENT] SaleList cleared")
                
        except Exception as e:
            print(f"[PAYMENT] Error clearing sale screen controls: {e}")
            import traceback
            traceback.print_exc()
    
    def _increment_receipt_number(self):
        """Increment receipt number sequence."""
        try:
            if not self.pos_data or "TransactionSequence" not in self.pos_data:
                print("[PAYMENT] TransactionSequence not found in pos_data")
                return
            
            sequences = self.pos_data["TransactionSequence"]
            receipt_seq = None
            
            for seq in sequences:
                if seq.name == "ReceiptNumber":
                    receipt_seq = seq
                    break
            
            if receipt_seq:
                receipt_seq.value += 1
                receipt_seq.save()
                print(f"[PAYMENT] Receipt number incremented to: {receipt_seq.value}")
            else:
                print("[PAYMENT] ReceiptNumber sequence not found")
                
        except Exception as e:
            print(f"[PAYMENT] Error incrementing receipt number: {e}")
            import traceback
            traceback.print_exc()
    
    def _has_change_payment_button(self):
        """
        Check if current window has a button with CHANGE_PAYMENT function.
        
        Returns:
            bool: True if change payment button exists, False otherwise
        """
        try:
            # Get current form_id from app
            app = self.interface.app if hasattr(self, 'interface') and hasattr(self.interface, 'app') else None
            if not app or not hasattr(app, 'current_form_id') or not app.current_form_id:
                print("[PAYMENT] No current_form_id found, assuming no change button")
                return False
            
            # Check form controls from database
            from data_layer.model import FormControl
            
            form_controls = FormControl.filter_by(
                fk_form_id=app.current_form_id,
                is_deleted=False,
                is_visible=True
            )
            
            print(f"[PAYMENT] Checking {len(form_controls)} form controls for CHANGE_PAYMENT function")
            
            for control in form_controls:
                if control.form_control_function1 == EventName.CHANGE_PAYMENT.value:
                    print(f"[PAYMENT] Found CHANGE_PAYMENT button: {control.name}")
                    return True
            
            print("[PAYMENT] No CHANGE_PAYMENT button found in form controls")
            return False
            
        except Exception as e:
            print(f"[PAYMENT] Error checking for change payment button: {e}")
            import traceback
            traceback.print_exc()
            # On error, assume no button exists so MessageForm will be shown
            return False
    
    def _show_change_info_and_record(self, change_amount):
        """
        Show info message about change amount and record change when OK is clicked.
        
        Parameters:
            change_amount: Change amount as Decimal
        """
        print(f"[PAYMENT] _show_change_info_and_record called with change_amount: {change_amount}")
        try:
            # Get current window
            window = self.interface.window if hasattr(self, 'interface') else None
            if not window:
                print("[PAYMENT] No window found for showing change info")
                return
            
            print(f"[PAYMENT] Window found: {window}")
            
            # Get currency from document
            currency = "GBP"
            if self.document_data and self.document_data.get("head"):
                currency = self.document_data["head"].base_currency or "GBP"
            
            # Format change amount
            change_str = f"{change_amount:.2f} {currency}"
            
            # Get message from LabelValue or use default
            from data_layer.model import LabelValue
            
            message_line1 = f"Change Amount: {change_str}"
            message_line2 = "Please give change to customer."
            
            try:
                label_values = LabelValue.filter_by(key="ChangeAmount", culture_info="en-GB", is_deleted=False)
                if label_values and len(label_values) > 0:
                    message_template = label_values[0].value
                    message_line1 = message_template.replace("{amount}", change_str)
            except Exception:
                pass  # Use default message
            
            # Show info message
            from user_interface.form.message_form import MessageForm
            result = MessageForm.show_info(window, message_line1, message_line2)
            
            # When OK is clicked, record change
            if result == "OK":
                print(f"[PAYMENT] OK clicked, recording change: {change_amount}")
                change_success, change_temp, change_error = PaymentService.record_change(self.document_data)
                if change_success:
                    print(f"[PAYMENT] Change recorded: {change_temp.change_amount} {change_temp.currency}")
                    
                    # Update UI controls
                    self._update_payment_ui("CHANGE", change_temp.change_amount)
                    
                    # Check if document is complete and complete it if so
                    self._check_and_complete_document()
                else:
                    print(f"[PAYMENT] Error recording change: {change_error}")
            
        except Exception as e:
            print(f"[PAYMENT] Error showing change info: {e}")
            import traceback
            traceback.print_exc()
    
    # ==================== PAYMENT MANAGEMENT EVENTS ====================
    
    def _suspend_payment_event(self):
        """
        Handle payment suspension for later completion.
        
        Suspends current transaction payment process, saving
        transaction state for later retrieval and completion.
        
        Process:
        1. Validate transaction is ready for suspension
        2. Save current transaction state
        3. Generate suspension ticket/reference
        4. Clear current transaction from active state
        5. Reset to new transaction mode
        
        Returns:
            bool: True if payment suspended successfully, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
            
        # TODO: Implement payment suspension logic
        print("Suspend payment - functionality to be implemented")
        return False
    
    def _back_payment_event(self):
        """
        Handle return to previous payment step or method.
        
        Allows user to go back in payment process to change
        payment method or modify payment amounts.
        
        Returns:
            bool: True if payment back navigation successful, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False
            
        # TODO: Implement payment navigation back logic
        print("Back payment - functionality to be implemented")
        return False 