"""
In-memory snapshot of campaign definitions for local evaluation (``CampaignService``).

Reload after GATE campaign pulls, ``campaign_update`` notifications, or any admin path
that mutates ``Campaign`` / related rows. Usage limits still query ``CampaignUsage``
from the database on each evaluation.

Copyright (c) 2025-2026 Ferhat Mousavi
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from core.logger import get_logger
from data_layer.model.definition.campaign import Campaign
from data_layer.model.definition.campaign_product import CampaignProduct
from data_layer.model.definition.campaign_rule import CampaignRule
from data_layer.model.definition.campaign_type import CampaignType

logger = get_logger(__name__)


@dataclass(frozen=True)
class ActiveCampaignEvalBundle:
    """Detached ORM rows safe to read outside the loading session."""

    types: Dict[Any, CampaignType]
    campaigns: List[Campaign]
    rules_by: Dict[Any, List[CampaignRule]]
    cp_by: Dict[Any, List[CampaignProduct]]
    loaded_at: datetime


class ActiveCampaignCache:
    """
    Thread-safe cache of active ``Campaign`` / ``CampaignType`` / rules / ``CampaignProduct``.

    Call :meth:`reload` after reference data changes. :meth:`get` returns ``None`` until
    the first successful reload.
    """

    _lock = threading.RLock()
    _bundle: Optional[ActiveCampaignEvalBundle] = None

    @classmethod
    def get(cls) -> Optional[ActiveCampaignEvalBundle]:
        with cls._lock:
            return cls._bundle

    @classmethod
    def reload(cls) -> None:
        """Load from the database and replace the snapshot (expunged, session-independent)."""
        from data_layer.engine import Engine

        try:
            with Engine().get_session() as session:
                bundle = cls._load_bundle(session)
            with cls._lock:
                cls._bundle = bundle
            logger.info(
                "[ActiveCampaignCache] reloaded %d campaigns (rules=%d keys, products=%d keys)",
                len(bundle.campaigns),
                len(bundle.rules_by),
                len(bundle.cp_by),
            )
        except Exception as exc:
            logger.error("[ActiveCampaignCache] reload failed: %s", exc)
            raise

    @classmethod
    def reload_safely(cls) -> None:
        """Like :meth:`reload` but log and ignore errors (GATE pull / startup paths)."""
        try:
            cls.reload()
        except Exception as exc:
            logger.warning("[ActiveCampaignCache] reload_safely skipped: %s", exc)

    @staticmethod
    def _load_bundle(session: Session) -> ActiveCampaignEvalBundle:
        type_rows = (
            session.query(CampaignType)
            .filter(CampaignType.is_deleted.is_(False), CampaignType.is_active.is_(True))
            .all()
        )
        types: Dict[Any, CampaignType] = {}
        for row in type_rows:
            types[row.id] = row
            session.expunge(row)

        campaigns = (
            session.query(Campaign)
            .filter(Campaign.is_deleted.is_(False), Campaign.is_active.is_(True))
            .all()
        )
        for c in campaigns:
            session.expunge(c)

        rules_by: Dict[Any, List[CampaignRule]] = {}
        for r in session.query(CampaignRule).filter(CampaignRule.is_deleted.is_(False)).all():
            session.expunge(r)
            rules_by.setdefault(r.fk_campaign_id, []).append(r)

        cp_by: Dict[Any, List[CampaignProduct]] = {}
        for cp in (
            session.query(CampaignProduct)
            .filter(CampaignProduct.is_deleted.is_(False), CampaignProduct.is_active.is_(True))
            .all()
        ):
            session.expunge(cp)
            cp_by.setdefault(cp.fk_campaign_id, []).append(cp)

        loaded_at = datetime.now(timezone.utc).replace(tzinfo=None)
        return ActiveCampaignEvalBundle(
            types=types,
            campaigns=campaigns,
            rules_by=rules_by,
            cp_by=cp_by,
            loaded_at=loaded_at,
        )


__all__ = [
    "ActiveCampaignCache",
    "ActiveCampaignEvalBundle",
]
