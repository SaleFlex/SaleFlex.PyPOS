"""
SaleFlex.PyPOS - Database Initial Data

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

from data_layer.model import TransactionDocumentType



from core.logger import get_logger

logger = get_logger(__name__)

def _insert_transaction_document_types(session):
    """Insert default transaction document types if not exists"""
    doc_type_exists = session.query(TransactionDocumentType).first()
    if not doc_type_exists:
        document_types = [
            {"no": 1, "name": "FISCAL_RECEIPT", "display_name": "Receipt", "description": "Fiscal Receipt"},
            {"no": 2, "name": "NONE_FISCAL_RECEIPT", "display_name": "Receipt", "description": "Non Fiscal Receipt"},
            {"no": 3, "name": "NONE_FISCAL_INVOICE", "display_name": "Invoice", "description": "Printed Invoice"},
            {"no": 4, "name": "NONE_FISCAL_E_INVOICE", "display_name": "E Invoice",
             "description": "Electronic Invoice"},
            {"no": 5, "name": "NONE_FISCAL_E_ARCHIVE_INVOICE", "display_name": "E Archive Invoice",
             "description": "Electronic Archive Invoice"},
            {"no": 6, "name": "NONE_FISCAL_DIPLOMATIC_RECEIPT", "display_name": "Diplomatic Invoice",
             "description": "Diplomatic Invoice"},
            {"no": 7, "name": "NONE_FISCAL_WAYBILL", "display_name": "Waybill", "description": "Waybill"},
            {"no": 8, "name": "NONE_FISCAL_DELIVERY_NOTE", "display_name": "Delivery Note",
             "description": "Delivery Note"},
            {"no": 9, "name": "NONE_FISCAL_CASH_OUT_FLOW", "display_name": "Cash Out flow",
             "description": "Cash Out flow"},
            {"no": 10, "name": "NONE_FISCAL_CASH_IN_FLOW", "display_name": "Cash In flow",
             "description": "Cash In flow"},
            {"no": 11, "name": "NONE_FISCAL_RETURN", "display_name": "Return", "description": "Return"},
            {"no": 12, "name": "NONE_FISCAL_SELF_BILLING_INVOICE", "display_name": "Self Billing Invoice",
             "description": "Self Billing Invoice"}
        ]

        for doc_type_data in document_types:
            doc_type = TransactionDocumentType(
                no=doc_type_data["no"],
                name=doc_type_data["name"],
                display_name=doc_type_data["display_name"],
                description=doc_type_data["description"]
            )
            session.add(doc_type)
        logger.info("✓ Default transaction document types added")
