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

