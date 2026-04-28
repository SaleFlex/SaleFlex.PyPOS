"""
SaleFlex.PyPOS - Point of Sale Application
Copyright (C) 2025-2026 Mousavi.Tech

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from decimal import Decimal
from typing import Optional

from data_layer.enums import FormName
from data_layer.enums.event_name import EventName
from pos.peripherals import get_default_cash_drawer, get_default_pos_printer
from pos.peripherals.hooks import sync_line_display_from_document, sync_line_display_payment
from pos.service.payment_service import PaymentService



from core.logger import get_logger

logger = get_logger(__name__)


def _unwrap_head(head):
    from data_layer.auto_save import AutoSaveModel

    if isinstance(head, AutoSaveModel):
        return head.unwrap()
    return head


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

    def _can_open_payment_form(self) -> tuple[bool, str]:
        """
        PAYMENT screen is only for an open, payable sale document.

        Returns:
            (True, "") if opening is allowed, else (False, user-facing Turkish message).
        """
        from data_layer.auto_save import AutoSaveModel
        from data_layer.model.definition.transaction_status import TransactionStatus

        if not self.document_data or not self.document_data.get("head"):
            return False, "Açık fiş yok. Satış ekranında kalem ekleyip tekrar deneyin."

        head = self.document_data["head"]
        if isinstance(head, AutoSaveModel):
            head = head.unwrap()

        if getattr(head, "is_closed", False):
            return False, "Bu fiş kapatılmış; ödeme ekranı açılamaz."

        st = getattr(head, "transaction_status", None)
        if st == TransactionStatus.COMPLETED.value:
            return False, "Bu fiş tamamlanmış; ödeme ekranı açılamaz."
        if st == TransactionStatus.CANCELLED.value:
            return False, "Bu fiş iptal edilmiş; ödeme ekranı açılamaz."

        total_amt = PaymentService._safe_decimal(getattr(head, "total_amount", 0))
        if total_amt <= 0:
            return False, "Ödeme alınacak tutar yok. Önce satışa kalem ekleyin."

        if PaymentService.remaining_balance(self.document_data) <= 0:
            return False, "Fiş tutarı tamamen tahsil edilmiş."

        return True, ""

    def _payment_event(self):
        """
        Open the PAYMENT form (full-screen payment entry).

        Used from the SALE form's dual CREDIT CARD button (FUNC → PAYMENT caption).
        BACK returns to SALE via form history.

        Returns:
            bool: True if navigation succeeded, False if not authenticated or no payable receipt.
        """
        if not self.login_succeed:
            self._logout()
            return False

        ok, message = self._can_open_payment_form()
        if not ok:
            logger.info("[PAYMENT] PAYMENT form blocked: %s", message)
            win = self.interface.window if hasattr(self, "interface") else None
            if win:
                try:
                    from user_interface.form.message_form import MessageForm

                    MessageForm.show_error(win, "Ödeme ekranı", message)
                except Exception:
                    pass
            return False

        self.current_form_type = FormName.PAYMENT
        self.interface.redraw(form_name=FormName.PAYMENT.name)
        logger.info("[PAYMENT] Opened PAYMENT form")
        return True
    
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
        logger.debug("Payment detail - functionality to be implemented")
        return False
    
    # ==================== CASH PAYMENT EVENTS ====================

    def _cash_opens_drawer_without_payment(self) -> bool:
        """
        True when CASH should only kick the drawer (log) and not call PaymentService.

        The session almost always has a TransactionHeadTemp after startup or after a
        completed sale (pre-created empty document), so "no head" is not enough.
        We treat "no document to pay" as: missing head, or zero balance with no
        payments recorded (empty / zero ticket).
        """
        if not self.document_data or not self.document_data.get("head"):
            return True
        head = _unwrap_head(self.document_data["head"])
        total = PaymentService._safe_decimal(getattr(head, "total_amount", 0))
        paid = PaymentService._safe_decimal(getattr(head, "total_payment_amount", 0))
        balance = total - paid
        if balance > 0:
            return False
        if paid == 0:
            return True
        return False

    def _cash_payment_event(self, button=None, key=None):
        """
        Handle cash payment processing.

        If the button name has no digit suffix (e.g. button name is "PAYMENT_CASH"),
        the current numpad value is read and used as the tendered amount.
        The numpad value represents the amount in the currency's minor unit
        (e.g. 10000 → £100.00 for GBP with 2 decimal places).

        For preset buttons like "CASH2000" (£20.00) the digit-encoded amount is
        used and the numpad is ignored.

        Parameters:
            button: Optional button object with control_name
            key: Optional parameter from numpad input

        Returns:
            bool: True if cash payment processed successfully, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False

        if self.current_form_type in (FormName.SALE, FormName.PAYMENT) and self._cash_opens_drawer_without_payment():
            get_default_cash_drawer().open_drawer("CASH_PAYMENT_no_open_sale_or_nothing_to_pay")
            return True

        numpad_value = self._read_numpad_payment_amount(button)
        return self._process_payment(EventName.CASH_PAYMENT.value, button, numpad_value)
    
    # ==================== ELECTRONIC PAYMENT EVENTS ====================
    
    def _credit_payment_event(self, button=None, key=None):
        """
        Handle credit card payment processing.

        If the button has no digit-encoded amount, reads the numpad value as the
        tendered amount (same minor-unit convention as cash: 10000 → £100.00).

        Parameters:
            button: Optional button object with control_name
            key: Optional parameter from numpad input

        Returns:
            bool: True if credit payment processed successfully, False otherwise
        """
        if not self.login_succeed:
            self._logout()
            return False

        numpad_value = self._read_numpad_payment_amount(button)
        return self._process_payment(EventName.CREDIT_PAYMENT.value, button, numpad_value)
    
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

        numpad_value = self._read_numpad_payment_amount(button)
        return self._process_payment(EventName.CHECK_PAYMENT.value, button, numpad_value)
    
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

        numpad_value = self._read_numpad_payment_amount(button)
        return self._process_payment(EventName.EXCHANGE_PAYMENT.value, button, numpad_value)
    
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

        numpad_value = self._read_numpad_payment_amount(button)
        return self._process_payment(EventName.PREPAID_PAYMENT.value, button, numpad_value)
    
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

        numpad_value = self._read_numpad_payment_amount(button)
        return self._process_payment(EventName.CHARGE_SALE_PAYMENT.value, button, numpad_value)
    
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

        numpad_value = self._read_numpad_payment_amount(button)
        return self._process_payment(EventName.OTHER_PAYMENT.value, button, numpad_value)

    def _read_numpad_loyalty_points(self) -> Optional[int]:
        """Whole loyalty points from numpad (not converted with currency decimal places)."""
        try:
            window = self.interface.window if hasattr(self, "interface") else None
            if not window:
                return None
            from user_interface.control.numpad.numpad import NumPad

            numpads = window.findChildren(NumPad)
            if not numpads:
                return None
            numpad = numpads[0]
            numpad_text = numpad.get_text()
            numpad.set_text("")
            if not numpad_text or not numpad_text.strip():
                return None
            raw_value = int(numpad_text)
            return raw_value if raw_value > 0 else None
        except (ValueError, TypeError):
            return None
        except Exception as e:
            logger.error("[PAYMENT] Error reading numpad loyalty points: %s", e)
            return None

    def _bonus_payment_event(self, button=None, key=None):
        """
        Apply loyalty points as a document discount (``discount_type=LOYALTY``).
        Cashier enters whole points on the numpad, then presses BONUS.
        """
        if not self.login_succeed:
            self._logout()
            return False

        if not self.document_data or not self.document_data.get("head"):
            return False

        pts = self._read_numpad_loyalty_points()
        if pts is None:
            msg = "Enter the number of points on the numpad (whole points), then press BONUS."
            win = self.interface.window if hasattr(self, "interface") else None
            if win and self.current_form_type == FormName.PAYMENT:
                try:
                    from user_interface.form.message_form import MessageForm

                    MessageForm.show_info(win, "Loyalty", msg)
                except Exception:
                    pass
            logger.info("[PAYMENT] BONUS blocked: %s", msg)
            return False

        from pos.service.loyalty_redemption_service import LoyaltyRedemptionService

        dp = LoyaltyRedemptionService._decimal_places_from_app(self)
        ok, err = LoyaltyRedemptionService.apply_points_redemption(
            self.document_data, pts, decimal_places=dp
        )
        if not ok:
            logger.error("[PAYMENT] BONUS: %s", err)
            win = self.interface.window if hasattr(self, "interface") else None
            if win:
                try:
                    from user_interface.form.message_form import MessageForm

                    MessageForm.show_info(win, "Loyalty", err or "Could not apply points.")
                except Exception:
                    pass
            return False

        try:
            window = self.interface.window if hasattr(self, "interface") else None
            if window and self.document_data.get("head"):
                from pos.service.sale_service import SaleService

                if hasattr(window, "sale_list") and window.sale_list:
                    SaleService.update_sale_list_from_document(
                        window.sale_list,
                        self.document_data,
                        getattr(self, "pos_data", None),
                    )
                if hasattr(window, "amount_table") and window.amount_table:
                    SaleService.update_amount_table_from_document(
                        window.amount_table, self.document_data["head"]
                    )
            if self.current_form_type in (FormName.SALE, FormName.PAYMENT):
                from pos.peripherals.hooks import sync_line_display_from_document

                sync_line_display_from_document(self, self.document_data)
        except Exception as exc:
            logger.error("[PAYMENT] BONUS UI refresh: %s", exc)

        self._check_and_complete_document()
        return True

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
            logger.debug("[PAYMENT] No active document for change calculation")
            return False
        
        try:
            # Use PaymentService to record change
            success, change_temp, error_message = PaymentService.record_change(self.document_data)
            
            if success:
                logger.debug("[PAYMENT] Change recorded: %s %s", change_temp.change_amount, change_temp.currency)
                
                # Update UI controls
                self._update_payment_ui("CHANGE", change_temp.change_amount)
                
                # Check if document is complete and complete it
                self._check_and_complete_document()
            else:
                logger.error("[PAYMENT] %s", error_message)
            
            return success
            
        except Exception as e:
            logger.error("[PAYMENT] Error processing change payment: %s", e)
            return False
    
    def _read_numpad_payment_amount(self, button=None):
        """
        Read the numpad value and convert it to a Decimal payment amount.

        Only returns a value when the button does NOT have a digit-encoded amount
        in its name (i.e. the button is a generic CASH/CREDIT button, not e.g.
        CASH2000).  The numpad value is divided by 10^decimal_places to convert
        from minor units to the currency's major unit.

        The numpad is cleared after reading regardless of whether a valid amount
        was found.

        Parameters:
            button: Optional button widget

        Returns:
            Decimal | None: Parsed amount, or None if not applicable / empty
        """
        try:
            # Detect preset buttons (have a digit suffix like CASH2000)
            button_name = ""
            if button and hasattr(button, 'control_name'):
                button_name = button.control_name or ""

            name_upper = button_name.upper()
            # Only skip the numpad for preset denomination buttons
            # (e.g. CASH2000, CASH5000, CASH10000).
            # Generic buttons like PAYMENT_CASH, PAYMENT_CREDIT, CASH (no digits)
            # should use the numpad value when one is entered.
            has_preset_amount = (
                name_upper.startswith("CASH") and len(name_upper) > 4 and name_upper[4:].isdigit()
            )
            if has_preset_amount:
                return None

            # Find current window and numpad
            window = self.interface.window if hasattr(self, 'interface') else None
            if not window:
                return None

            from user_interface.control.numpad.numpad import NumPad
            numpads = window.findChildren(NumPad)
            if not numpads:
                return None
            numpad = numpads[0]

            numpad_text = numpad.get_text()
            if not numpad_text or not numpad_text.strip():
                return None

            try:
                raw_value = int(numpad_text)
            except ValueError:
                numpad.set_text("")
                return None

            # Clear numpad after reading
            numpad.set_text("")

            # Determine decimal places from current currency
            decimal_places = 2
            try:
                current_currency_sign = self.current_currency if hasattr(self, 'current_currency') and self.current_currency else "GBP"
                if hasattr(self, 'product_data') and self.product_data:
                    all_currencies = self.product_data.get("Currency", [])
                    currency = next((c for c in all_currencies if c.sign == current_currency_sign and not c.is_deleted), None)
                    if currency and currency.decimal_places is not None:
                        decimal_places = currency.decimal_places
            except Exception:
                pass

            divisor = 10 ** decimal_places
            from decimal import Decimal
            amount = Decimal(str(raw_value)) / Decimal(str(divisor))
            logger.debug("[PAYMENT] Numpad payment amount: %s (raw=%s / %s)", amount, raw_value, divisor)
            return amount

        except Exception as e:
            logger.error("[PAYMENT] Error reading numpad payment amount: %s", e)
            return None

    def _process_payment(self, payment_type, button=None, numpad_value=None):
        """
        Process a payment based on payment type, button information and optional numpad amount.

        Parameters:
            payment_type:  Payment type string (CASH_PAYMENT, CREDIT_PAYMENT, etc.)
            button:        Optional button object with control_name attribute
            numpad_value:  Optional Decimal amount read from the numpad

        Returns:
            bool: True if payment processed successfully, False otherwise
        """
        if not self.document_data or not self.document_data.get("head"):
            logger.debug("[PAYMENT] No active document")
            return False
        
        try:
            # Get button name if button is provided
            button_name = ""
            if button and hasattr(button, 'control_name'):
                button_name = button.control_name or ""
            
            default_to_remaining = self.current_form_type != FormName.PAYMENT

            # Use PaymentService to process payment
            success, payment_temp, error_message = PaymentService.process_payment(
                self.document_data,
                payment_type,
                button_name,
                numpad_value,
                default_to_remaining_balance=default_to_remaining,
            )

            if not success:
                logger.error("[PAYMENT] %s", error_message)
                if (
                    self.current_form_type == FormName.PAYMENT
                    and error_message
                    and self.interface.window
                ):
                    try:
                        from user_interface.form.message_form import MessageForm

                        MessageForm.show_info(
                            self.interface.window,
                            "Payment",
                            error_message,
                        )
                    except Exception:
                        pass
                return False
            
            # Update UI controls
            self._update_payment_ui(payment_type, payment_temp.payment_total)
            
            logger.debug("[PAYMENT] Payment recorded: %s %s (%s)", payment_temp.payment_total, payment_temp.currency_code, payment_type)
            
            # Check if change is needed (payment exceeds total)
            change_amount = PaymentService.calculate_change(self.document_data)
            if change_amount > 0:
                logger.debug("[PAYMENT] Change needed: %s", change_amount)
                # Check if change_payment button exists in the current window
                has_change_button = self._has_change_payment_button()
                
                if has_change_button:
                    # Change button exists - just inform user, don't record change automatically
                    logger.debug("[PAYMENT] Change payment button found. User should click change button to record change.")
                    # Don't complete document yet - wait for change button click
                else:
                    # No change button - show info message and record change when OK is clicked
                    logger.debug("[PAYMENT] No change payment button found, showing MessageForm for change amount: %s", change_amount)
                    self._show_change_info_and_record(change_amount)
                    # _show_change_info_and_record will handle document completion after change is recorded
                    return True
            else:
                # No change needed - check if document is complete and complete it if so
                self._check_and_complete_document()
            
            return True
            
        except Exception as e:
            logger.error("[PAYMENT] Error processing payment: %s", e)
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
            if window:
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
                    if self.document_data and self.document_data.get("head"):
                        from pos.service.sale_service import SaleService

                        SaleService.update_amount_table_from_document(
                            window.amount_table, self.document_data["head"]
                        )

            if self.current_form_type in (FormName.SALE, FormName.PAYMENT):
                sync_line_display_payment(self, self.document_data, Decimal(str(payment_amount)))

        except Exception as e:
            logger.error("[PAYMENT] Error updating UI: %s", e)
    
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

            return_to_payment_screen = self.current_form_type == FormName.PAYMENT
            
            # Mark document as complete
            if not PaymentService.mark_document_complete(self.document_data):
                logger.error("[PAYMENT] Failed to mark document as complete")
                return False
            
            # Update closure
            if self.closure:
                PaymentService.update_closure_for_completion(self.closure, self.document_data)
            
            # Copy temp models to permanent models
            PaymentService.copy_temp_to_permanent(self.document_data)

            get_default_pos_printer().print_sale_document(self.document_data)
            
            # Increment receipt number AFTER copying to permanent so the next
            # document gets a fresh number.
            self._increment_receipt_number()
            
            # Reset document_data so the next sale starts fresh
            self.document_data = None
            
            # Clear UI controls
            self._clear_sale_screen_controls()
            
            logger.info("[PAYMENT] Document completed successfully")

            get_default_cash_drawer().open_drawer("document_completed")

            # Immediately create the next empty document so the cashier can
            # start the next sale without any additional action.
            new_doc = self.create_empty_document()
            if new_doc:
                logger.info("[PAYMENT] New empty document ready for next sale")
            else:
                logger.warning("[PAYMENT] Could not pre-create next empty document")

            if return_to_payment_screen:
                self.interface.redraw(form_name=FormName.SALE.name, skip_history_update=True)
                # Drop the SALE entry stacked when PAYMENT opened, same as BACK would.
                self.prepare_navigation_return_from_payment_form()

            if self.current_form_type == FormName.SALE:
                sync_line_display_from_document(self, self.document_data)

            return True
            
        except Exception as e:
            logger.error("[PAYMENT] Error checking document completion: %s", e)
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
                logger.debug("[PAYMENT] PaymentList cleared")
            
            # Clear AmountTable if it exists
            if hasattr(window, 'amount_table') and window.amount_table:
                window.amount_table.clear()
                logger.debug("[PAYMENT] AmountTable cleared")
            
            # Clear SaleList if it exists
            if hasattr(window, 'sale_list') and window.sale_list:
                window.sale_list.clear_products()
                logger.debug("[PAYMENT] SaleList cleared")
                
        except Exception as e:
            logger.error("[PAYMENT] Error clearing sale screen controls: %s", e)
    
    def _increment_receipt_number(self):
        """Increment receipt number sequence."""
        try:
            if not self.pos_data or "TransactionSequence" not in self.pos_data:
                logger.error("[PAYMENT] TransactionSequence not found in pos_data")
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
                logger.debug("[PAYMENT] Receipt number incremented to: %s", receipt_seq.value)
            else:
                logger.error("[PAYMENT] ReceiptNumber sequence not found")
                
        except Exception as e:
            logger.error("[PAYMENT] Error incrementing receipt number: %s", e)
    
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
                logger.debug("[PAYMENT] No current_form_id found, assuming no change button")
                return False
            
            # Check form controls from database
            from data_layer.model import FormControl
            
            form_controls = FormControl.filter_by(
                fk_form_id=app.current_form_id,
                is_deleted=False,
                is_visible=True
            )
            
            logger.debug("[PAYMENT] Checking %s form controls for CHANGE_PAYMENT function", len(form_controls))
            
            for control in form_controls:
                if control.form_control_function1 == EventName.CHANGE_PAYMENT.value:
                    logger.debug("[PAYMENT] Found CHANGE_PAYMENT button: %s", control.name)
                    return True
            
            logger.debug("[PAYMENT] No CHANGE_PAYMENT button found in form controls")
            return False
            
        except Exception as e:
            logger.error("[PAYMENT] Error checking for change payment button: %s", e)
            # On error, assume no button exists so MessageForm will be shown
            return False
    
    def _show_change_info_and_record(self, change_amount):
        """
        Show info message about change amount and record change when OK is clicked.
        
        Parameters:
            change_amount: Change amount as Decimal
        """
        logger.debug("[PAYMENT] _show_change_info_and_record called with change_amount: %s", change_amount)
        try:
            # Get current window
            window = self.interface.window if hasattr(self, 'interface') else None
            if not window:
                logger.debug("[PAYMENT] No window found for showing change info")
                return
            
            logger.debug("[PAYMENT] Window found: %s", window)
            
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
                logger.debug("[PAYMENT] OK clicked, recording change: %s", change_amount)
                change_success, change_temp, change_error = PaymentService.record_change(self.document_data)
                if change_success:
                    logger.debug("[PAYMENT] Change recorded: %s %s", change_temp.change_amount, change_temp.currency)
                    
                    # Update UI controls
                    self._update_payment_ui("CHANGE", change_temp.change_amount)
                    
                    # Check if document is complete and complete it if so
                    self._check_and_complete_document()
                else:
                    logger.error("[PAYMENT] Error recording change: %s", change_error)
            
        except Exception as e:
            logger.error("[PAYMENT] Error showing change info: %s", e)
    
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
        logger.debug("Suspend payment - functionality to be implemented")
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
        logger.debug("Back payment - functionality to be implemented")
        return False 