"""
SaleFlex.PyPOS - Database Initial Data

Copyright (c) 2025 Ferhat Mousavi (ferhat.mousavi@gmail.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from data_layer.model import LabelValue


def _insert_label_values(session):
    """Insert default label values if not exists"""
    label_value_exists = session.query(LabelValue).first()
    if not label_value_exists:
        label_values = [
            {"key": "ReceiptNo", "value": "Receipt No", "culture_info": "en-GB"},
            {"key": "CurrencySymbol", "value": "£", "culture_info": "en-GB"},
            {"key": "Quantity", "value": "Quantity", "culture_info": "en-GB"},
            {"key": "FunctionNotDefined", "value": "Function not defined!", "culture_info": "en-GB"},
            {"key": "LicenseOwner", "value": "Licensee", "culture_info": "en-GB"},
            {"key": "AreYouSure", "value": "Are you sure?", "culture_info": "en-GB"},
            {"key": "Cashier", "value": "Cashier", "culture_info": "en-GB"},
            {"key": "DepartmentNotFound", "value": "Department not found.", "culture_info": "en-GB"},
            {"key": "CanNotInsertTransactıon", "value": "Can not insert transactıon.", "culture_info": "en-GB"},
            {"key": "CanNotStartReceipt", "value": "Can not start receipt.", "culture_info": "en-GB"},
            {"key": "NeedCashierLogin", "value": "You need cashier login.", "culture_info": "en-GB"},
            {"key": "CashierLoginFailed", "value": "The login criteria may be incorrect, the operation failed.", "culture_info": "en-GB"},
            {"key": "PluNotFound", "value": "Product not found.", "culture_info": "en-GB"},
            {"key": "InsufficientStock", "value": "Insufficient Stock.", "culture_info": "en-GB"},
            {"key": "CanNotCloseReceipt", "value": "Can not Close Receipt.", "culture_info": "en-GB"},
            {"key": "PaymentTypeError", "value": "Payment Type Error.", "culture_info": "en-GB"},
            {"key": "PaymentNotPossible", "value": "Payment Is Not Possible.", "culture_info": "en-GB"},
            {"key": "CanNotCancelTransaction", "value": "Can not Cancel Transaction.", "culture_info": "en-GB"},
            {"key": "CanNotCancelDocument", "value": "Can not Cancel Document.", "culture_info": "en-GB"},
            {"key": "SubtotalNotPossible", "value": "Subtotal Is Not Possible.", "culture_info": "en-GB"},
            {"key": "SuspendQueueFull", "value": "Suspend Queue Is Full.", "culture_info": "en-GB"},
            {"key": "SuspendNotFull", "value": "Suspend Is Not Full.", "culture_info": "en-GB"},
            {"key": "NeedSuspend", "value": "Need Suspend.", "culture_info": "en-GB"},
            {"key": "ClosureNotPossible", "value": "Closure is not possible", "culture_info": "en-GB"},
            {"key": "Price", "value": "Price", "culture_info": "en-GB"},
            {"key": "GroupNo", "value": "Group No", "culture_info": "en-GB"},
            {"key": "ProductSale", "value": "Sale", "culture_info": "en-GB"},
            {"key": "ProductReturn", "value": "Return", "culture_info": "en-GB"},
            {"key": "Waybill", "value": "Waybill", "culture_info": "en-GB"},
            {"key": "DeliveryNote", "value": "Delivery Note", "culture_info": "en-GB"},
            {"key": "Invoice", "value": "Invoice", "culture_info": "en-GB"},
            {"key": "Return", "value": "Return", "culture_info": "en-GB"},
            {"key": "FiscalReceipt", "value": "Receipt", "culture_info": "en-GB"},
            {"key": "NoneFiscalReceipt", "value": "Receipt", "culture_info": "en-GB"},
            {"key": "EInvoice", "value": "Electronic Invoice", "culture_info": "en-GB"},
            {"key": "EArchiveInvoice", "value": "Electronic Receipt", "culture_info": "en-GB"},
            {"key": "DiplomaticInvoice", "value": "Diplomatic Invoice", "culture_info": "en-GB"},
            {"key": "CashOutflow", "value": "Cash Outflow", "culture_info": "en-GB"},
            {"key": "CashInflow", "value": "Cash Inflow", "culture_info": "en-GB"},
            {"key": "SelfBillingInvoice", "value": "Self-Billing Invoice", "culture_info": "en-GB"},
            {"key": "PasswordCode", "value": "Password Code", "culture_info": "en-GB"},
            {"key": "DefinitionIsNotProper", "value": "The definition is not appropriate.", "culture_info": "en-GB"},
            {"key": "LoginFailed", "value": "Login Failed", "culture_info": "en-GB"},
            {"key": "ProcessFinished", "value": "Process Finished", "culture_info": "en-GB"},
            {"key": "WrongPrice", "value": "Wrong Price", "culture_info": "en-GB"},
            {"key": "NotPossible", "value": "Is not possible.", "culture_info": "en-GB"},
            {"key": "CreditCardPaymentError", "value": "An error occurred with the credit card payment.", "culture_info": "en-GB"},
            {"key": "CancelInvoicePrint", "value": "Document printing was canceled.", "culture_info": "en-GB"},
            {"key": "CancelWaybillPrint", "value": "Waybill printing was canceled.", "culture_info": "en-GB"},
            {"key": "CancelDeliveryNotePrint", "value": "Delivery note printing was canceled.", "culture_info": "en-GB"},
            {"key": "CancelReturnPrint", "value": "Return invoice printing was canceled.", "culture_info": "en-GB"},
            {"key": "DefineDiscountSurchargeValue", "value": "Define Discount and Surcharge Value.", "culture_info": "en-GB"},
            {"key": "WrongQuantity", "value": "Wrong Quantity", "culture_info": "en-GB"},
            {"key": "Vat", "value": "Vat", "culture_info": "en-GB"},
            {"key": "PeriodicZReportWarning", "value": "Periodic Z Report Warning", "culture_info": "en-GB"},
            {"key": "DateAndTime", "value": "Date and Time", "culture_info": "en-GB"},
            {"key": "CashRegisterActivated", "value": "Cash Register Activated", "culture_info": "en-GB"},
            {"key": "OutOfService", "value": "Out of Service", "culture_info": "en-GB"},
            {"key": "ReceiptIsOpen", "value": "The receipt is open", "culture_info": "en-GB"},
            {"key": "ReceiptIsNotOpen", "value": "The receipt is not open", "culture_info": "en-GB"},
            {"key": "PaymentIsStarted", "value": "Payment is started", "culture_info": "en-GB"},
            {"key": "PaymentIsNotPossible", "value": "Payment is not possible", "culture_info": "en-GB"},
            {"key": "InsertPaper", "value": "Insert Paper", "culture_info": "en-GB"},
            {"key": "WaybillPrinted", "value": "Waybill Printed", "culture_info": "en-GB"},
            {"key": "DeliveryNotePrinted", "value": "Delivery Note Printed", "culture_info": "en-GB"},
            {"key": "InvoicePrinted", "value": "Invoice Printed", "culture_info": "en-GB"},
            {"key": "ReturnPrinted", "value": "Return Invoice Printed", "culture_info": "en-GB"},
            {"key": "PrintControl", "value": "Print Control", "culture_info": "en-GB"},
            {"key": "DiscountRate", "value": "Discount Rate", "culture_info": "en-GB"},
            {"key": "SurchargeRate", "value": "Surcharge Rate", "culture_info": "en-GB"},
            {"key": "DepartmentMaxWarning", "value": "Department Max Warning", "culture_info": "en-GB"},
            {"key": "DepartmentExistWarning", "value": "Department Exist Warning", "culture_info": "en-GB"},
            {"key": "PluMaxWarning", "value": "Plu Max Warning", "culture_info": "en-GB"},
            {"key": "PluExistWarning", "value": "Plu Exist Warning", "culture_info": "en-GB"},
            {"key": "PluGroupMaxWarning", "value": "Plu Group Max Warning", "culture_info": "en-GB"},
            {"key": "PluGroupExistWarning", "value": "Plu Group Exist Warning", "culture_info": "en-GB"},
            {"key": "VatSetError1", "value": "VAT must be between 1-99", "culture_info": "en-GB"},
            {"key": "VatSetError2", "value": "VAT Error", "culture_info": "en-GB"},
            {"key": "DocumentCancelled", "value": "Document Cancelled.", "culture_info": "en-GB"},
            {"key": "NetSale", "value": "NET SALE", "culture_info": "en-GB"},
            {"key": "Change", "value": "CHANGE", "culture_info": "en-GB"},
        ]

        for label_data in label_values:
            label_value = LabelValue(
                key=label_data["key"],
                value=label_data["value"],
                culture_info=label_data["culture_info"]
            )
            session.add(label_value)

        print("✓ Default label values added (79 labels)") 