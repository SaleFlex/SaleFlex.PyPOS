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

from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from data_layer.model.definition import CampaignType, Campaign, CampaignRule, CampaignProduct
from data_layer.model.definition.coupon import Coupon
from data_layer.model.definition.product import Product



from core.logger import get_logger

logger = get_logger(__name__)

def _insert_campaign_types(session: Session):
    """
    Insert default campaign types
    """
    existing = session.query(CampaignType).first()
    if existing:
        logger.warning("Campaign types already exist, skipping...")
        return

    campaign_types = [
        CampaignType(
            code="PRODUCT_DISCOUNT",
            name="Product Discount",
            description="Discount on specific products",
            icon="tag",
            is_active=True,
            display_order=1,
            settings_json='{"requires_product_selection": true, "supports_percentage": true, "supports_fixed_amount": true}'
        ),
        CampaignType(
            code="BASKET_DISCOUNT",
            name="Basket Discount",
            description="Discount based on basket total amount",
            icon="shopping_cart",
            is_active=True,
            display_order=2,
            settings_json='{"min_amount_required": true, "supports_percentage": true, "supports_fixed_amount": true}'
        ),
        CampaignType(
            code="TIME_BASED",
            name="Time-Based Discount",
            description="Discounts active during specific time periods",
            icon="schedule",
            is_active=True,
            display_order=3,
            settings_json='{"requires_time_range": true, "supports_day_of_week": true}'
        ),
        CampaignType(
            code="BUY_X_GET_Y",
            name="Buy X Get Y",
            description="Buy X items, get Y items free or discounted",
            icon="redeem",
            is_active=True,
            display_order=4,
            settings_json='{"requires_quantity": true, "supports_free_product": true}'
        ),
        CampaignType(
            code="WELCOME_BONUS",
            name="Welcome Bonus",
            description="Special offer for new customers",
            icon="favorite",
            is_active=True,
            display_order=5,
            settings_json='{"one_time_use": true, "requires_new_customer": true}'
        ),
        CampaignType(
            code="PAYMENT_DISCOUNT",
            name="Payment Type Discount",
            description="Discount based on payment method",
            icon="payment",
            is_active=True,
            display_order=6,
            settings_json='{"requires_payment_type": true}'
        ),
    ]

    for campaign_type in campaign_types:
        session.add(campaign_type)

    session.commit()
    logger.info("✓ Inserted %s campaign types", len(campaign_types))


def _insert_sample_campaigns(session: Session, admin_cashier_id):
    """
    Insert sample campaigns for demonstration
    """
    existing = session.query(Campaign).first()
    if existing:
        logger.warning("Campaigns already exist, skipping...")
        return

    # Get campaign types
    product_discount_type = session.query(CampaignType).filter_by(code="PRODUCT_DISCOUNT").first()
    basket_discount_type = session.query(CampaignType).filter_by(code="BASKET_DISCOUNT").first()
    time_based_type = session.query(CampaignType).filter_by(code="TIME_BASED").first()
    buy_x_get_y_type = session.query(CampaignType).filter_by(code="BUY_X_GET_Y").first()

    now = datetime.now()
    # Long horizon so sample campaigns stay valid on dev databases (adjust in production).
    campaign_end = now + timedelta(days=365)

    campaigns = [
        Campaign(
            code="WELCOME10",
            name="Welcome Discount 10%",
            description="10% discount for new customers on first purchase",
            fk_campaign_type_id=product_discount_type.id if product_discount_type else None,
            discount_type="PERCENTAGE",
            discount_percentage=10.0,
            start_date=now,
            end_date=campaign_end,
            priority=5,
            is_combinable=False,
            usage_limit_per_customer=1,
            is_active=True,
            is_auto_apply=False,
            requires_coupon=True,
            notification_message="Welcome! Enjoy 10% off your first purchase!",
            fk_created_by=admin_cashier_id
        ),
        Campaign(
            code="BASKET100",
            name="Spend 100 Get 10 Off",
            description="Get 10 TL discount when you spend 100 TL or more",
            fk_campaign_type_id=basket_discount_type.id if basket_discount_type else None,
            discount_type="FIXED_AMOUNT",
            discount_value=10.0,
            min_purchase_amount=100.0,
            start_date=now,
            end_date=campaign_end,
            priority=3,
            is_combinable=True,
            is_active=True,
            is_auto_apply=True,
            requires_coupon=False,
            notification_message="Spend 100 TL, save 10 TL!",
            fk_created_by=admin_cashier_id
        ),
        Campaign(
            code="HAPPYHOUR",
            name="Happy Hour 20% Off",
            description="20% discount between 15:00-18:00",
            fk_campaign_type_id=time_based_type.id if time_based_type else None,
            discount_type="PERCENTAGE",
            discount_percentage=20.0,
            start_date=now,
            end_date=campaign_end,
            start_time=datetime.strptime("15:00", "%H:%M").time(),
            end_time=datetime.strptime("18:00", "%H:%M").time(),
            days_of_week="1,2,3,4,5",  # Monday to Friday
            priority=4,
            is_combinable=False,
            is_active=True,
            is_auto_apply=True,
            requires_coupon=False,
            notification_message="Happy Hour! Get 20% off between 3-6 PM!",
            fk_created_by=admin_cashier_id
        ),
        Campaign(
            code="BUY2GET1",
            name="Buy 2 Get 1 Free",
            description="Buy 2 products, get 1 free",
            fk_campaign_type_id=buy_x_get_y_type.id if buy_x_get_y_type else None,
            discount_type="BUY_X_GET_Y",
            buy_quantity=2,
            get_quantity=1,
            start_date=now,
            end_date=campaign_end,
            priority=6,
            is_combinable=False,
            is_active=True,
            is_auto_apply=True,
            requires_coupon=False,
            notification_message="Buy 2 Get 1 Free!",
            fk_created_by=admin_cashier_id
        ),
    ]

    for campaign in campaigns:
        session.add(campaign)

    session.commit()
    logger.info("✓ Inserted %s sample campaigns", len(campaigns))


def _insert_sample_coupons(session: Session) -> None:
    """Seed a public coupon linked to the WELCOME10 ``requires_coupon`` campaign."""
    if (
        session.query(Coupon)
        .filter(Coupon.is_deleted.is_(False), func.upper(Coupon.code) == "WELCOME10-DEMO")
        .first()
    ):
        return
    welcome = (
        session.query(Campaign)
        .filter(Campaign.code == "WELCOME10", Campaign.is_deleted.is_(False))
        .first()
    )
    if not welcome:
        return
    session.add(
        Coupon(
            code="WELCOME10-DEMO",
            name="Welcome 10% demo coupon",
            description="Sample coupon for campaign WELCOME10 (scan barcode or type code).",
            fk_campaign_id=welcome.id,
            coupon_type="PUBLIC",
            fk_customer_id=None,
            start_date=welcome.start_date,
            end_date=welcome.end_date,
            usage_limit=None,
            usage_count=0,
            is_active=True,
            barcode="2800100000001",
            qr_code=None,
            is_sent=False,
            sent_date=None,
            sent_method=None,
            fk_created_by=None,
        )
    )
    session.commit()
    logger.info("✓ Inserted sample coupon WELCOME10-DEMO for campaign WELCOME10")


def _insert_welcome10_campaign_product(session: Session) -> None:
    """Link first seeded product to WELCOME10 so PRODUCT_DISCOUNT proposals can fire."""
    welcome = (
        session.query(Campaign)
        .filter(Campaign.code == "WELCOME10", Campaign.is_deleted.is_(False))
        .first()
    )
    if not welcome:
        return
    if (
        session.query(CampaignProduct)
        .filter(
            CampaignProduct.fk_campaign_id == welcome.id,
            CampaignProduct.is_deleted.is_(False),
        )
        .first()
    ):
        return
    prod = session.query(Product).filter(Product.is_deleted.is_(False)).first()
    if not prod:
        return
    session.add(
        CampaignProduct(
            fk_campaign_id=welcome.id,
            fk_product_id=prod.id,
            is_gift_product=False,
            min_quantity=None,
            max_quantity=None,
            discount_value=None,
            discount_percentage=None,
            is_active=True,
            display_order=0,
        )
    )
    session.commit()


def ensure_welcome10_demo_campaign_product(session: Session) -> None:
    """Idempotent: ensure WELCOME10 has at least one ``CampaignProduct`` (existing DBs)."""
    _insert_welcome10_campaign_product(session)


def ensure_sample_coupon_welcome_demo(session: Session) -> None:
    """Idempotent: add WELCOME10-DEMO coupon when campaign exists (existing databases)."""
    if (
        session.query(Coupon)
        .filter(Coupon.is_deleted.is_(False), func.upper(Coupon.code) == "WELCOME10-DEMO")
        .first()
    ):
        return
    welcome = (
        session.query(Campaign)
        .filter(Campaign.code == "WELCOME10", Campaign.is_deleted.is_(False))
        .first()
    )
    if not welcome:
        return
    session.add(
        Coupon(
            code="WELCOME10-DEMO",
            name="Welcome 10% demo coupon",
            description="Sample coupon for campaign WELCOME10 (scan barcode or type code).",
            fk_campaign_id=welcome.id,
            coupon_type="PUBLIC",
            fk_customer_id=None,
            start_date=welcome.start_date,
            end_date=welcome.end_date,
            usage_limit=None,
            usage_count=0,
            is_active=True,
            barcode="2800100000001",
            qr_code=None,
            is_sent=False,
            sent_date=None,
            sent_method=None,
            fk_created_by=None,
        )
    )
    session.commit()


def _insert_campaigns(session: Session, admin_cashier_id):
    """
    Main function to insert all campaign-related data
    """
    _insert_campaign_types(session)
    _insert_sample_campaigns(session, admin_cashier_id)
    _insert_welcome10_campaign_product(session)
    _insert_sample_coupons(session)

