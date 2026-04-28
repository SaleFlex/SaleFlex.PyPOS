"""
SaleFlex.PyPOS - Database Initial Data
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
