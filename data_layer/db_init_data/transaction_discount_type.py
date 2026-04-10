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

from data_layer.model import TransactionDiscountType



from core.logger import get_logger

logger = get_logger(__name__)

def _insert_transaction_discount_types(session):
    """Insert default transaction discount types if not exists"""
    discount_type_exists = session.query(TransactionDiscountType).first()
    if not discount_type_exists:
        discount_types = [
            {
                "code": "NONE",
                "name": "None",
                "display_name": "None",
                "description": "No discount applied"
            },
            {
                "code": "PERSONAL",
                "name": "Personal Discount",
                "display_name": "Personal",
                "description": "Personal discount for customer"
            },
            {
                "code": "MANAGER",
                "name": "Manager Discount",
                "display_name": "Manager",
                "description": "Manager approved discount"
            },
            {
                "code": "CUSTOMER_SATISFACTION",
                "name": "Customer Satisfaction Discount",
                "display_name": "Customer Satisfaction",
                "description": "Discount for customer satisfaction"
            },
            {
                "code": "PRODUCT",
                "name": "Product Discount",
                "display_name": "Product",
                "description": "Product-specific discount"
            }
        ]

        for discount_type_data in discount_types:
            discount_type = TransactionDiscountType(
                code=discount_type_data["code"],
                name=discount_type_data["name"],
                display_name=discount_type_data["display_name"],
                description=discount_type_data["description"]
            )
            session.add(discount_type)
        logger.info("✓ Default transaction discount types added")

    existing_loyalty = session.query(TransactionDiscountType).filter(TransactionDiscountType.code == "LOYALTY").first()
    if not existing_loyalty:
        session.add(
            TransactionDiscountType(
                code="LOYALTY",
                name="Loyalty Points Redemption",
                display_name="Loyalty Points",
                description="Basket discount from redeemed loyalty points (BONUS / PAY_TYPE_BONUS)",
            )
        )
        logger.info("✓ Loyalty transaction discount type added")

    existing_campaign = session.query(TransactionDiscountType).filter(TransactionDiscountType.code == "CAMPAIGN").first()
    if not existing_campaign:
        session.add(
            TransactionDiscountType(
                code="CAMPAIGN",
                name="Campaign / Promotion Discount",
                display_name="Campaign",
                description="Document discount from promotional campaign or coupon (discount_type on temp row; campaign or coupon code in discount_code)",
            )
        )
        logger.info("✓ Campaign transaction discount type added")


def ensure_transaction_discount_type_campaign(session) -> None:
    """
    Idempotent reference-data patch: ensure ``CAMPAIGN`` exists in ``transaction_discount_type``
    for databases seeded before this type was added.
    """
    existing = session.query(TransactionDiscountType).filter(TransactionDiscountType.code == "CAMPAIGN").first()
    if existing:
        return
    session.add(
        TransactionDiscountType(
            code="CAMPAIGN",
            name="Campaign / Promotion Discount",
            display_name="Campaign",
            description="Document discount from promotional campaign or coupon (discount_type on temp row; campaign or coupon code in discount_code)",
        )
    )
    logger.info("Schema patch: added CAMPAIGN transaction discount type")
