"""
SaleFlex.PyPOS - Point of Sale Application

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

"""
Transaction Models Initialization

Note: Transaction models do NOT require seed/initialization data as they are
created during the operation of the POS system. These models include:

Permanent Transaction Models:
- TransactionHead: Main transaction header
- TransactionProduct: Product line items
- TransactionPayment: Payment records
- TransactionDelivery: Delivery information
- TransactionDiscount: Discount records
- TransactionTotal: Department totals
- TransactionFiscal: Fiscal compliance data
- TransactionLoyalty: Loyalty program transactions
- TransactionNote: Transaction notes
- TransactionRefund: Refund records
- TransactionSurcharge: Surcharge records
- TransactionTax: Tax breakdown
- TransactionTip: Tip records
- TransactionLog: Audit trail (no seed data by design)
- TransactionVoid: Void records (no seed data by design)

Temporary Transaction Models (for in-progress transactions):
- TransactionHeadTemp
- TransactionProductTemp
- TransactionPaymentTemp
- TransactionDeliveryTemp
- TransactionDiscountTemp
- TransactionTotalTemp
- TransactionFiscalTemp
- TransactionLoyaltyTemp
- TransactionNoteTemp
- TransactionRefundTemp
- TransactionSurchargeTemp
- TransactionTaxTemp
- TransactionTipTemp

All these models are initialized empty and populated during POS operations.
"""


def _insert_transaction_placeholder(session):
    """
    Placeholder function for transaction models.
    
    Transaction models do not require seed data as they are created
    during the operation of the POS system.
    
    Args:
        session: SQLAlchemy session
        
    Returns:
        None
    """
    # No initialization data needed for transaction models
    # They will be populated during POS operations
    pass

