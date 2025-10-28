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

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from data_layer.model.definition import CampaignType, Campaign, CampaignRule, CampaignProduct


def _insert_campaign_types(session: Session):
    """
    Insert default campaign types
    """
    existing = session.query(CampaignType).first()
    if existing:
        print("Campaign types already exist, skipping...")
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
    print(f"✓ Inserted {len(campaign_types)} campaign types")


def _insert_sample_campaigns(session: Session, admin_cashier_id):
    """
    Insert sample campaigns for demonstration
    """
    existing = session.query(Campaign).first()
    if existing:
        print("Campaigns already exist, skipping...")
        return

    # Get campaign types
    product_discount_type = session.query(CampaignType).filter_by(code="PRODUCT_DISCOUNT").first()
    basket_discount_type = session.query(CampaignType).filter_by(code="BASKET_DISCOUNT").first()
    time_based_type = session.query(CampaignType).filter_by(code="TIME_BASED").first()
    buy_x_get_y_type = session.query(CampaignType).filter_by(code="BUY_X_GET_Y").first()

    now = datetime.now()
    next_month = now + timedelta(days=30)

    campaigns = [
        Campaign(
            code="WELCOME10",
            name="Welcome Discount 10%",
            description="10% discount for new customers on first purchase",
            fk_campaign_type_id=product_discount_type.id if product_discount_type else None,
            discount_type="PERCENTAGE",
            discount_percentage=10.0,
            start_date=now,
            end_date=next_month,
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
            end_date=next_month,
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
            end_date=next_month,
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
            end_date=next_month,
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
    print(f"✓ Inserted {len(campaigns)} sample campaigns")


def _insert_campaigns(session: Session, admin_cashier_id):
    """
    Main function to insert all campaign-related data
    """
    _insert_campaign_types(session)
    _insert_sample_campaigns(session, admin_cashier_id)

