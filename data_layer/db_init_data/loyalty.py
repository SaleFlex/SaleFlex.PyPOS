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

from datetime import datetime
from sqlalchemy.orm import Session
from data_layer.model.definition import LoyaltyProgram, LoyaltyTier



from core.logger import get_logger

logger = get_logger(__name__)

def _insert_loyalty_program(session: Session, admin_cashier_id):
    """
    Insert default loyalty program
    """
    existing = session.query(LoyaltyProgram).first()
    if existing:
        logger.warning("Loyalty program already exists, skipping...")
        return existing

    loyalty_program = LoyaltyProgram(
        name="SaleFlex Rewards",
        description="Earn points on every purchase and redeem for discounts",
        points_per_currency=0.1,  # 1 point per 10 TL
        currency_per_point=0.5,  # 1 point = 0.5 TL discount
        min_purchase_for_points=10.0,  # Minimum 10 TL to earn points
        point_expiry_days=365,  # Points expire after 1 year
        is_active=True,
        start_date=datetime.now(),
        welcome_points=100,  # 100 points for new members
        birthday_points=50,  # 50 points on birthday
        terms_conditions="Earn 1 point for every 10 TL spent. Points can be redeemed for discounts. Points expire after 1 year.",
        fk_created_by=admin_cashier_id
    )

    session.add(loyalty_program)
    session.commit()
    logger.info("✓ Inserted default loyalty program")
    return loyalty_program


def _insert_loyalty_tiers(session: Session, loyalty_program_id):
    """
    Insert default loyalty tiers (Bronze, Silver, Gold, Platinum)
    """
    existing = session.query(LoyaltyTier).first()
    if existing:
        logger.warning("Loyalty tiers already exist, skipping...")
        return

    tiers = [
        LoyaltyTier(
            fk_loyalty_program_id=loyalty_program_id,
            name="Bronze",
            code="BRONZE",
            description="Entry level membership",
            min_points_required=0,
            min_annual_spending=0,
            tier_level=1,
            points_multiplier=1.0,
            discount_percentage=0,
            special_benefits="Welcome bonus points",
            color_code="#CD7F32",
            icon="star_border",
            is_active=True,
            display_order=1
        ),
        LoyaltyTier(
            fk_loyalty_program_id=loyalty_program_id,
            name="Silver",
            code="SILVER",
            description="Earn 10% more points on purchases",
            min_points_required=500,
            min_annual_spending=1000.0,
            tier_level=2,
            points_multiplier=1.1,
            discount_percentage=0,
            special_benefits="10% bonus points on all purchases",
            color_code="#C0C0C0",
            icon="star_half",
            is_active=True,
            display_order=2
        ),
        LoyaltyTier(
            fk_loyalty_program_id=loyalty_program_id,
            name="Gold",
            code="GOLD",
            description="Earn 25% more points plus 5% discount",
            min_points_required=1500,
            min_annual_spending=5000.0,
            tier_level=3,
            points_multiplier=1.25,
            discount_percentage=5.0,
            special_benefits="25% bonus points + 5% discount on all purchases",
            color_code="#FFD700",
            icon="star",
            is_active=True,
            display_order=3
        ),
        LoyaltyTier(
            fk_loyalty_program_id=loyalty_program_id,
            name="Platinum",
            code="PLATINUM",
            description="VIP status with 50% more points and 10% discount",
            min_points_required=5000,
            min_annual_spending=15000.0,
            tier_level=4,
            points_multiplier=1.5,
            discount_percentage=10.0,
            special_benefits="50% bonus points + 10% discount + Priority support + Exclusive offers",
            color_code="#E5E4E2",
            icon="stars",
            is_active=True,
            display_order=4
        ),
    ]

    for tier in tiers:
        session.add(tier)

    session.commit()
    logger.info("✓ Inserted %s loyalty tiers", len(tiers))


def _insert_loyalty(session: Session, admin_cashier_id):
    """
    Main function to insert all loyalty-related data
    """
    loyalty_program = _insert_loyalty_program(session, admin_cashier_id)
    if loyalty_program:
        _insert_loyalty_tiers(session, loyalty_program.id)

