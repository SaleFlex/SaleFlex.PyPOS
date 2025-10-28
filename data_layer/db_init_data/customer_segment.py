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

from sqlalchemy.orm import Session
from data_layer.model.definition import CustomerSegment


def _insert_customer_segments(session: Session):
    """
    Insert default customer segments
    """
    existing = session.query(CustomerSegment).first()
    if existing:
        print("Customer segments already exist, skipping...")
        return

    segments = [
        CustomerSegment(
            code="VIP",
            name="VIP Customers",
            description="High-value customers with significant purchase history",
            segment_type="VIP",
            criteria_json='{"min_annual_spending": 10000, "min_lifetime_spending": 50000}',
            is_active=True,
            customer_count=0,
            display_order=1,
            color_code="#FFD700",
            icon="workspace_premium"
        ),
        CustomerSegment(
            code="NEW_CUSTOMER",
            name="New Customers",
            description="Customers who registered within the last 30 days",
            segment_type="NEW_CUSTOMER",
            criteria_json='{"days_since_registration": 30, "max_purchases": 1}',
            is_active=True,
            customer_count=0,
            display_order=2,
            color_code="#4CAF50",
            icon="new_releases"
        ),
        CustomerSegment(
            code="FREQUENT_BUYER",
            name="Frequent Buyers",
            description="Customers who shop regularly (at least monthly)",
            segment_type="FREQUENT_BUYER",
            criteria_json='{"min_purchases_per_month": 4, "min_total_purchases": 12}',
            is_active=True,
            customer_count=0,
            display_order=3,
            color_code="#2196F3",
            icon="trending_up"
        ),
        CustomerSegment(
            code="HIGH_VALUE",
            name="High Value Customers",
            description="Customers with high average transaction value",
            segment_type="HIGH_VALUE",
            criteria_json='{"min_avg_transaction": 200, "min_annual_spending": 5000}',
            is_active=True,
            customer_count=0,
            display_order=4,
            color_code="#9C27B0",
            icon="attach_money"
        ),
        CustomerSegment(
            code="INACTIVE",
            name="Inactive Customers",
            description="Customers who haven't purchased in the last 90 days",
            segment_type="INACTIVE",
            criteria_json='{"days_since_last_purchase": 90}',
            is_active=True,
            customer_count=0,
            display_order=5,
            color_code="#FF5722",
            icon="schedule"
        ),
        CustomerSegment(
            code="BIRTHDAY",
            name="Birthday This Month",
            description="Customers with birthdays in the current month",
            segment_type="BIRTHDAY",
            criteria_json='{"birthday_month": "current"}',
            is_active=True,
            customer_count=0,
            display_order=6,
            color_code="#FF4081",
            icon="cake"
        ),
    ]

    for segment in segments:
        session.add(segment)

    session.commit()
    print(f"✓ Inserted {len(segments)} customer segments")

