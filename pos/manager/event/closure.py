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
from datetime import date, datetime
from collections import defaultdict

from core.logger import get_logger
from data_layer.engine import Engine

logger = get_logger(__name__)
from data_layer.model import (
    TransactionHead,
    TransactionSequence,
    TransactionPayment,
    TransactionTax,
    TransactionDiscount,
    TransactionDepartment,
    TransactionTip,
    TransactionDocumentType,
    TransactionDiscountType,
    Closure,
    ClosureVATSummary,
    ClosureTipSummary,
    ClosureDiscountSummary,
    ClosurePaymentTypeSummary,
    ClosureDocumentTypeSummary,
    ClosureDepartmentSummary,
    ClosureCurrency,
    ClosureCashierSummary,
    PaymentType,
    Currency,
    Vat,
)
from data_layer.model.definition.transaction_status import (
    TransactionStatus,
    TransactionType,
)


class ClosureEvent:
    """
    Closure Event Handler for end-of-day operations.

    This class handles end-of-day closure operations including:
    - Daily sales closing
    - Cash drawer reconciliation
    - Financial reporting
    - Transaction finalization
    - Z-report generation

    All methods follow the pattern of returning True on success, False on failure,
    and handle authentication checks where appropriate.
    """

    # ==================== CLOSURE EVENTS ====================

    def _closure_event(self):
        """
        Handle end-of-day closure operation.

        When the CLOSURE button is pressed:
        1. Verifies the cashier is authorized (administrator) for closure.
        2. If not authorized, shows an error via MessageForm and stops.
        3. If authorized, reads the current ClosureNumber from transaction_sequence,
           aggregates all transactions with that closure_number from transaction_head
           and related tables (payments, taxes, discounts, departments, tips, etc.),
           creates a Closure record and all summary records (VAT, tip, discount,
           payment type, document type, department, currency, cashier).
        4. Increments transaction_sequence ClosureNumber by 1 and sets
           ReceiptNumber to 1.

        Returns:
            bool: True if closure completed successfully, False otherwise.
        """

        logger.debug("[CLOSURE] _closure_event method called!")

        try:
            if not self.login_succeed:
                self._show_closure_error("Not logged in", "Please log in to perform closure.")
                return False

            if not self.cashier_data:
                self._show_closure_error("No cashier", "No current cashier found.")
                return False

            # Only administrators are allowed to perform closure
            if not getattr(self.cashier_data, "is_administrator", False):
                self._show_closure_error(
                    "Not authorized",
                    "Only authorized cashiers (administrators) can perform closure.",
                )
                return False
            logger.debug("[CLOSURE] Login succeeded and cashier data is set.")
            # Get current closure number from transaction_sequence
            current_closure_number = self._get_sequence_value("ClosureNumber")
            if current_closure_number is None:
                self._show_closure_error("Configuration error", "ClosureNumber sequence not found.")
                return False

            # Load transactions for this closure number
            heads = TransactionHead.filter_by(
                closure_number=current_closure_number,
                is_deleted=False,
            )
            if not heads:
                logger.debug("[CLOSURE] No transactions found for closure number", current_closure_number)
                self._show_closure_error(
                    "Closure not allowed",
                    f"No transactions found for closure number {current_closure_number}. Closure cannot be performed.",
                )
                return False

            head_ids = [h.id for h in heads]

            # Resolve store, pos, base currency from first transaction or pos_data
            store_id, pos_id, base_currency_id = self._resolve_closure_context(heads)
            if not store_id or not pos_id or not base_currency_id:
                self._show_closure_error("Configuration error", "Store, POS or base currency not found.")
                return False

            # Compute period start/end from transactions or use now
            closure_start_time = datetime.now()
            closure_end_time = datetime.now()
            if heads:
                dates = [h.transaction_date_time for h in heads]
                closure_start_time = min(dates)
                closure_end_time = max(dates)

            # Aggregate totals from transaction heads and related tables
            totals = self._aggregate_closure_totals(head_ids, heads)

            # Create main Closure record
            closure = self._create_closure_record(
                closure_number=current_closure_number,
                store_id=store_id,
                pos_id=pos_id,
                base_currency_id=base_currency_id,
                closure_start_time=closure_start_time,
                closure_end_time=closure_end_time,
                totals=totals,
            )
            if not closure:
                self._show_closure_error("Error", "Failed to create closure record.")
                return False

            closure_id = closure.id

            # Create summary records
            self._create_closure_vat_summaries(closure_id, head_ids, totals)
            self._create_closure_tip_summaries(closure_id, head_ids, totals)
            self._create_closure_discount_summaries(closure_id, head_ids, totals)
            self._create_closure_payment_type_summaries(closure_id, head_ids, totals)
            self._create_closure_document_type_summaries(closure_id, heads, totals)
            self._create_closure_department_summaries(closure_id, head_ids, totals)
            self._create_closure_currency_summaries(closure_id, head_ids, totals, base_currency_id)
            self._create_closure_cashier_summary(closure_id, totals)

            # Update sequences: ClosureNumber += 1, ReceiptNumber = 1
            if not self._update_closure_sequences(current_closure_number):
                self._show_closure_error("Error", "Failed to update transaction sequences.")
                return False

            # Refresh pos_data cache so next document uses new sequences
            self.refresh_pos_data_model(TransactionSequence)

            # Update current_data: create new open closure and load it into self.closure
            self.create_empty_closure()

            logger.info("[CLOSURE] Closure completed successfully. Closure Number: %s", current_closure_number)
            return True

        except Exception as e:
            logger.exception("[CLOSURE] Error during closure: %s", e)
            self._show_closure_error("Closure error", str(e))
            return False

    def _show_closure_error(self, title: str, message: str):
        """Show error dialog using MessageForm and optional LabelValue text."""
        try:
            from PySide6.QtWidgets import QApplication
            from user_interface.form.message_form import MessageForm
            from data_layer.model import LabelValue

            parent = QApplication.instance().activeWindow() if QApplication.instance() else None
            line2 = message
            try:
                label_values = LabelValue.filter_by(key="ClosureNotAuthorized", culture_info="en-GB", is_deleted=False)
                if label_values:
                    line2 = label_values[0].value
            except Exception:
                pass
            MessageForm.show_error(parent, title, line2)
        except Exception as e:
            logger.warning("[CLOSURE] Could not show message form: %s", e)

    def _get_sequence_value(self, name: str) -> int | None:
        """Get value for a sequence by name from database."""
        try:
            seq = TransactionSequence.find_first(name=name)
            return seq.value if seq else None
        except Exception:
            return None

    def _resolve_closure_context(self, heads):
        """Resolve store_id, pos_id (UUID), base_currency_id from heads or pos_data."""
        store_id = None
        pos_id = None
        base_currency_id = None
        if heads:
            store_id = heads[0].fk_store_id
        if not store_id and self.pos_data:
            stores = self.pos_data.get("Store", [])
            if stores:
                store_id = stores[0].id
        if not self.pos_settings:
            return store_id, pos_id, base_currency_id
        pos_id = self.pos_settings.id
        base_currency_id = getattr(self.pos_settings, "fk_current_currency_id", None)
        if not base_currency_id and self.product_data:
            currencies = self.product_data.get("Currency", [])
            if currencies:
                base_currency_id = currencies[0].id
        return store_id, pos_id, base_currency_id

    def _aggregate_closure_totals(self, head_ids, heads):
        """Aggregate totals from transaction heads and related tables."""
        from decimal import Decimal

        totals = {
            "total_document_count": len(heads),
            "gross_sales_amount": Decimal("0"),
            "net_sales_amount": Decimal("0"),
            "total_tax_amount": Decimal("0"),
            "total_discount_amount": Decimal("0"),
            "total_tip_amount": Decimal("0"),
            "valid_transaction_count": 0,
            "canceled_transaction_count": 0,
            "return_transaction_count": 0,
            "opening_cash_amount": Decimal("0"),
            "closing_cash_amount": Decimal("0"),
            "expected_cash_amount": Decimal("0"),
            "cash_difference": Decimal("0"),
            "paid_in_count": 0,
            "paid_in_total": Decimal("0"),
            "paid_out_count": 0,
            "paid_out_total": Decimal("0"),
            "by_payment_type": defaultdict(lambda: {"count": 0, "amount": Decimal("0")}),
            "by_document_type": defaultdict(lambda: {"valid_count": 0, "valid_amount": Decimal("0"), "valid_tax": Decimal("0"), "canceled_count": 0, "canceled_amount": Decimal("0"), "canceled_tax": Decimal("0")}),
            "by_discount_type": defaultdict(lambda: {"count": 0, "amount": Decimal("0"), "affected_amount": Decimal("0")}),
            "by_department": defaultdict(lambda: {"transaction_count": 0, "gross_amount": Decimal("0"), "tax_amount": Decimal("0"), "net_amount": Decimal("0"), "discount_amount": Decimal("0")}),
            "by_tax": defaultdict(lambda: {"taxable_amount": Decimal("0"), "tax_amount": Decimal("0"), "transaction_count": 0, "exempt_amount": Decimal("0"), "exempt_count": 0}),
            "by_tip_payment_type": defaultdict(lambda: {"tip_count": 0, "total_tip_amount": Decimal("0")}),
            "by_currency": defaultdict(lambda: {"currency_amount": Decimal("0"), "base_currency_amount": Decimal("0"), "exchange_rate": Decimal("1")}),
        }

        for h in heads:
            totals["gross_sales_amount"] += (h.total_amount or Decimal("0"))
            totals["net_sales_amount"] += (h.total_amount or Decimal("0")) - (h.total_discount_amount or Decimal("0")) + (h.total_surcharge_amount or Decimal("0"))
            totals["total_tax_amount"] += (h.total_vat_amount or Decimal("0"))
            totals["total_discount_amount"] += (h.total_discount_amount or Decimal("0"))
            totals["total_tip_amount"] += (h.tip_amount or Decimal("0"))
            totals["expected_cash_amount"] += (h.total_payment_amount or Decimal("0")) - (h.total_change_amount or Decimal("0"))

            if getattr(h, "is_cancel", False):
                totals["canceled_transaction_count"] += 1
            elif getattr(h, "transaction_type", None) == TransactionType.RETURN.value:
                totals["return_transaction_count"] += 1
            else:
                totals["valid_transaction_count"] += 1

            doc_type = getattr(h, "document_type", None) or "FISCAL_RECEIPT"
            totals["by_document_type"][doc_type]["valid_count"] += 0 if getattr(h, "is_cancel", False) else 1
            totals["by_document_type"][doc_type]["valid_amount"] += Decimal("0") if getattr(h, "is_cancel", False) else (h.total_amount or Decimal("0"))
            totals["by_document_type"][doc_type]["valid_tax"] += Decimal("0") if getattr(h, "is_cancel", False) else (h.total_vat_amount or Decimal("0"))
            if getattr(h, "is_cancel", False):
                totals["by_document_type"][doc_type]["canceled_count"] += 1
                totals["by_document_type"][doc_type]["canceled_amount"] += (h.total_amount or Decimal("0"))
                totals["by_document_type"][doc_type]["canceled_tax"] += (h.total_vat_amount or Decimal("0"))

        if not head_ids:
            return totals

        # Payments by type and currency (all heads)
        with Engine().get_session() as session:
            payments = session.query(TransactionPayment).filter(
                TransactionPayment.fk_transaction_head_id.in_(head_ids),
                TransactionPayment.is_cancel == False,
            ).all()

        for p in payments:
            pt = getattr(p, "payment_type", None) or "CASH"
            totals["by_payment_type"][pt]["count"] += 1
            totals["by_payment_type"][pt]["amount"] += (p.payment_total or Decimal("0"))
            code = getattr(p, "currency_code", None) or "GBP"
            rate = p.currency_exchange_rate if hasattr(p, "currency_exchange_rate") and p.currency_exchange_rate else Decimal("1")
            totals["by_currency"][code]["currency_amount"] += (p.currency_total or Decimal("0"))
            totals["by_currency"][code]["base_currency_amount"] += (p.payment_total or Decimal("0"))
            totals["by_currency"][code]["exchange_rate"] = rate
            if getattr(p, "tip_amount", None):
                totals["by_tip_payment_type"][pt]["tip_count"] += 1
                totals["by_tip_payment_type"][pt]["total_tip_amount"] += (p.tip_amount or Decimal("0"))

        # Tax breakdown
        for hid in head_ids:
            taxes = TransactionTax.filter_by(fk_transaction_head_id=hid)
            for t in taxes:
                key = (t.tax_rate, t.tax_name or "", getattr(t, "jurisdiction_code", None) or "")
                totals["by_tax"][key]["taxable_amount"] += (t.taxable_amount or Decimal("0"))
                totals["by_tax"][key]["tax_amount"] += (t.tax_amount or Decimal("0"))
                totals["by_tax"][key]["transaction_count"] += 1
                if getattr(t, "is_exempt", False):
                    totals["by_tax"][key]["exempt_count"] += 1

        # Discount by type
        for hid in head_ids:
            disc = TransactionDiscount.filter_by(fk_transaction_head_id=hid, is_cancel=False)
            for d in disc:
                dt_id = str(d.fk_discount_type_id) if d.fk_discount_type_id else "default"
                totals["by_discount_type"][dt_id]["count"] += 1
                totals["by_discount_type"][dt_id]["amount"] += (d.discount_amount or Decimal("0"))

        # Department breakdown
        for hid in head_ids:
            depts = TransactionDepartment.filter_by(fk_transaction_head_id=hid)
            for d in depts:
                dept_id = d.fk_department_main_group_id
                totals["by_department"][dept_id]["transaction_count"] += 1
                totals["by_department"][dept_id]["gross_amount"] += (d.total_department or Decimal("0"))
                totals["by_department"][dept_id]["tax_amount"] += (d.total_department_vat or Decimal("0"))
                totals["by_department"][dept_id]["net_amount"] += (d.total_department or Decimal("0"))
                totals["by_department"][dept_id]["discount_amount"] += Decimal("0")

        return totals

    def _create_closure_record(self, closure_number, store_id, pos_id, base_currency_id,
                                closure_start_time, closure_end_time, totals):
        """Create and persist the main Closure record."""
        try:
            today = date.today()
            closure_unique_id = f"{today.strftime('%Y%m%d')}-{closure_number:04d}"
            cashier_id = self.cashier_data.id

            c = Closure()
            c.closure_unique_id = closure_unique_id
            c.closure_number = closure_number
            c.fk_store_id = store_id
            c.fk_pos_id = pos_id
            c.closure_date = today
            c.closure_start_time = closure_start_time
            c.closure_end_time = closure_end_time
            c.fk_base_currency_id = base_currency_id
            c.fk_cashier_opened_id = cashier_id
            c.fk_cashier_closed_id = cashier_id
            c.total_document_count = totals["total_document_count"]
            c.gross_sales_amount = totals["gross_sales_amount"]
            c.net_sales_amount = totals["net_sales_amount"]
            c.total_tax_amount = totals["total_tax_amount"]
            c.total_discount_amount = totals["total_discount_amount"]
            c.total_tip_amount = totals["total_tip_amount"]
            c.valid_transaction_count = totals["valid_transaction_count"]
            c.canceled_transaction_count = totals["canceled_transaction_count"]
            c.return_transaction_count = totals["return_transaction_count"]
            c.expected_cash_amount = totals["expected_cash_amount"]
            c.create()
            return c
        except Exception as e:
            logger.error("[CLOSURE] Create closure record error: %s", e)
            return None

    def _create_closure_vat_summaries(self, closure_id, head_ids, totals):
        """Create ClosureVATSummary records from tax aggregation."""
        for key, data in totals["by_tax"].items():
            if isinstance(key, (tuple, list)) and len(key) >= 3:
                rate, name, juris = key[0], key[1], key[2]
            else:
                rate, name, juris = 0, "", ""
            vat_id = None
            if self.product_data and "Vat" in self.product_data:
                for v in self.product_data["Vat"]:
                    if v.rate == rate:
                        vat_id = v.id
                        break
            s = ClosureVATSummary()
            s.fk_closure_id = closure_id
            s.fk_tax_rate_id = vat_id
            s.tax_rate_percentage = rate
            s.tax_jurisdiction = juris or name
            s.taxable_amount = data["taxable_amount"]
            s.tax_amount = data["tax_amount"]
            s.transaction_count = data["transaction_count"]
            s.exempt_amount = data.get("exempt_amount", Decimal("0"))
            s.exempt_count = data.get("exempt_count", 0)
            s.create()

    def _create_closure_tip_summaries(self, closure_id, head_ids, totals):
        """Create ClosureTipSummary for each payment type that has tips."""
        payment_types = self.pos_data.get("PaymentType", []) if self.pos_data else []
        type_by_name = {pt.type_name: pt.id for pt in payment_types}
        for pt_name, data in totals["by_tip_payment_type"].items():
            if data["tip_count"] == 0 and data["total_tip_amount"] == 0:
                continue
            pt_id = type_by_name.get(pt_name)
            if not pt_id and payment_types:
                pt_id = payment_types[0].id
            if not pt_id:
                continue
            s = ClosureTipSummary()
            s.fk_closure_id = closure_id
            s.fk_payment_type_id = pt_id
            s.tip_count = data["tip_count"]
            s.total_tip_amount = data["total_tip_amount"]
            s.average_tip_amount = (data["total_tip_amount"] / data["tip_count"]) if data["tip_count"] else Decimal("0")
            s.average_tip_percentage = Decimal("0")
            s.create()

    def _create_closure_discount_summaries(self, closure_id, head_ids, totals):
        """Create ClosureDiscountSummary by discount type."""
        for dt_id, data in totals["by_discount_type"].items():
            if data["count"] == 0 and data["amount"] == 0:
                continue
            try:
                from uuid import UUID
                uid = UUID(dt_id) if dt_id != "default" and len(str(dt_id)) == 36 else None
            except Exception:
                uid = None
            if not uid and self.pos_data:
                dtypes = self.pos_data.get("TransactionDiscountType", [])
                if dtypes:
                    uid = dtypes[0].id
            if uid is None:
                continue
            s = ClosureDiscountSummary()
            s.fk_closure_id = closure_id
            s.fk_discount_type_id = uid
            s.discount_count = data["count"]
            s.total_discount_amount = data["amount"]
            s.affected_amount = data.get("affected_amount", Decimal("0"))
            s.create()

    def _create_closure_payment_type_summaries(self, closure_id, head_ids, totals):
        """Create ClosurePaymentTypeSummary for each payment type."""
        payment_types = self.pos_data.get("PaymentType", []) if self.pos_data else []
        type_by_name = {pt.type_name: pt.id for pt in payment_types}
        for pt_name, data in totals["by_payment_type"].items():
            pt_id = type_by_name.get(pt_name)
            if not pt_id and payment_types:
                pt_id = payment_types[0].id
            if not pt_id:
                continue
            s = ClosurePaymentTypeSummary()
            s.fk_closure_id = closure_id
            s.fk_payment_type_id = pt_id
            s.total_count = data["count"]
            s.total_amount = data["amount"]
            s.create()

    def _create_closure_document_type_summaries(self, closure_id, heads, totals):
        """Create ClosureDocumentTypeSummary by document type."""
        doc_types = self.pos_data.get("TransactionDocumentType", []) if self.pos_data else []
        type_by_name = {getattr(dt, "name", ""): dt.id for dt in doc_types}
        for doc_name, data in totals["by_document_type"].items():
            dt_id = type_by_name.get(doc_name)
            if not dt_id and doc_types:
                dt_id = doc_types[0].id
            if not dt_id:
                continue
            s = ClosureDocumentTypeSummary()
            s.fk_closure_id = closure_id
            s.fk_document_type_id = dt_id
            s.valid_count = data["valid_count"]
            s.valid_amount = data["valid_amount"]
            s.valid_tax_amount = data["valid_tax"]
            s.canceled_count = data["canceled_count"]
            s.canceled_amount = data["canceled_amount"]
            s.canceled_tax_amount = data["canceled_tax"]
            s.create()

    def _create_closure_department_summaries(self, closure_id, head_ids, totals):
        """Create ClosureDepartmentSummary by department."""
        for dept_id, data in totals["by_department"].items():
            s = ClosureDepartmentSummary()
            s.fk_closure_id = closure_id
            s.fk_department_main_group_id = dept_id
            s.transaction_count = data["transaction_count"]
            s.gross_amount = data["gross_amount"]
            s.tax_amount = data["tax_amount"]
            s.net_amount = data["net_amount"]
            s.discount_amount = data.get("discount_amount", Decimal("0"))
            s.create()

    def _create_closure_currency_summaries(self, closure_id, head_ids, totals, base_currency_id):
        """Create ClosureCurrency for each currency used."""
        currencies = self.product_data.get("Currency", []) if self.product_data else []
        currency_by_code = {getattr(c, "currency_code", None) or getattr(c, "sign", ""): c for c in currencies}
        for code, data in totals["by_currency"].items():
            if data["currency_amount"] == 0 and data["base_currency_amount"] == 0:
                continue
            cur = currency_by_code.get(code)
            if not cur:
                continue
            s = ClosureCurrency()
            s.fk_closure_id = closure_id
            s.fk_currency_id = cur.id
            s.currency_amount = data["currency_amount"]
            s.exchange_rate = data.get("exchange_rate", Decimal("1"))
            s.base_currency_amount = data["base_currency_amount"]
            s.create()

    def _create_closure_cashier_summary(self, closure_id, totals):
        """Create one ClosureCashierSummary for the closing cashier with period totals."""
        cashier_id = self.cashier_data.id
        valid = totals["valid_transaction_count"]
        total_sales = totals["gross_sales_amount"]
        s = ClosureCashierSummary()
        s.fk_closure_id = closure_id
        s.fk_cashier_id = cashier_id
        s.transaction_count = totals["total_document_count"]
        s.total_sales_amount = total_sales
        s.average_transaction_amount = (total_sales / valid) if valid else Decimal("0")
        s.void_count = totals.get("void_count", 0)
        s.void_amount = totals.get("void_amount", Decimal("0"))
        s.correction_count = totals.get("correction_count", 0)
        s.create()

    def _update_closure_sequences(self, current_closure_number):
        """Increment ClosureNumber by 1 and set ReceiptNumber to 1 in transaction_sequence."""
        try:
            with Engine().get_session() as session:
                closure_seq = session.query(TransactionSequence).filter(
                    TransactionSequence.name == "ClosureNumber",
                ).first()
                receipt_seq = session.query(TransactionSequence).filter(
                    TransactionSequence.name == "ReceiptNumber",
                ).first()
                if closure_seq:
                    closure_seq.value = (closure_seq.value or 0) + 1
                    session.merge(closure_seq)
                if receipt_seq:
                    receipt_seq.value = 1
                    session.merge(receipt_seq)
                session.commit()
            return True
        except Exception as e:
            logger.error("[CLOSURE] Update sequences error: %s", e)
            return False

    def _closure_form_event(self):
        """
        Navigate to the closure form.

        Opens the closure management form where users can:
        - View daily totals
        - Initiate closure process
        - View closure history
        - Print reports

        Returns:
            bool: True if form opened successfully, False otherwise
        """
        logger.debug("[CLOSURE_FORM] Navigating to closure form...")

        try:
            from data_layer.enums import FormName

            if not self.login_succeed:
                logger.warning("[CLOSURE_FORM] User not logged in")
                return False

            result = self.show_form(FormName.CLOSURE.name)

            if result:
                logger.info("[CLOSURE_FORM] Closure form opened successfully")
            else:
                logger.warning("[CLOSURE_FORM] Failed to open closure form")

            return result

        except Exception as e:
            logger.exception("[CLOSURE_FORM] Error opening closure form: %s", e)
            return False
