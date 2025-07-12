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

from data_layer.model import TransactionDocumentType


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
        print("✓ Default transaction document types added")
