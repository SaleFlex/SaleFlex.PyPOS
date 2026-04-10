"""
Campaign usage totals from ``CampaignUsage`` for global and per-customer caps.

Copyright (c) 2025-2026 Ferhat Mousavi
"""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from data_layer.model.definition.campaign import Campaign
from data_layer.model.definition.campaign_usage import CampaignUsage


class CampaignUsageLimits:
    """Read ``CampaignUsage`` rows to enforce ``total_usage_limit`` / ``usage_limit_per_customer``."""

    @staticmethod
    def count_total(session: Session, fk_campaign_id: Any) -> int:
        return (
            session.query(func.count(CampaignUsage.id))
            .filter(
                CampaignUsage.fk_campaign_id == fk_campaign_id,
                CampaignUsage.is_deleted.is_(False),
            )
            .scalar()
            or 0
        )

    @staticmethod
    def count_for_customer(session: Session, fk_campaign_id: Any, fk_customer_id: Any) -> int:
        if fk_customer_id is None:
            return 0
        return (
            session.query(func.count(CampaignUsage.id))
            .filter(
                CampaignUsage.fk_campaign_id == fk_campaign_id,
                CampaignUsage.fk_customer_id == fk_customer_id,
                CampaignUsage.is_deleted.is_(False),
            )
            .scalar()
            or 0
        )

    @staticmethod
    def allows_new_application(
        session: Session,
        campaign: Campaign,
        fk_customer_id: Optional[Any],
    ) -> bool:
        tlim = campaign.total_usage_limit
        if tlim is not None and int(tlim) > 0:
            if CampaignUsageLimits.count_total(session, campaign.id) >= int(tlim):
                return False
        pc = campaign.usage_limit_per_customer
        if pc is not None and int(pc) > 0 and fk_customer_id is not None:
            if CampaignUsageLimits.count_for_customer(session, campaign.id, fk_customer_id) >= int(
                pc
            ):
                return False
        return True


__all__ = ["CampaignUsageLimits"]
