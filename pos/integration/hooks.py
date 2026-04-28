"""
SaleFlex.PyPOS - Glue between POS event flows and integration layer.

Mirrors pos/peripherals/hooks.py: event handlers import these thin functions
instead of importing integration internals directly.  Keeping the glue
separate means event handler code stays unaware of whether GATE is enabled,
which connector is active, or how retries are handled.
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

from __future__ import annotations

from typing import Any

from core.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _gate_sync():
    """Lazy import to avoid circular references at module load time."""
    from pos.integration.gate.gate_sync_service import get_default_gate_sync
    return get_default_gate_sync()


def _gate_pull():
    from pos.integration.gate.gate_pull_service import get_default_gate_pull
    return get_default_gate_pull()


# ---------------------------------------------------------------------------
# Transaction hooks  (called from PaymentEvent)
# ---------------------------------------------------------------------------

def push_transaction_to_gate(app: Any, transaction_head_id: str) -> None:
    """
    Queue a completed transaction for upload to SaleFlex.GATE.

    Called by PaymentEvent after a sale document is fully paid and closed.
    Silently skips when GATE integration is disabled.

    Args:
        app:                 Application singleton (not used directly; kept for
                             consistency with the peripherals/hooks signature).
        transaction_head_id: UUID of the completed TransactionHead record.
    """
    sync = _gate_sync()
    if not sync.is_enabled():
        return
    try:
        sync.queue_transaction(transaction_head_id)
    except Exception as e:
        logger.warning("push_transaction_to_gate failed (non-fatal): %s", e)


# ---------------------------------------------------------------------------
# Closure hooks  (called from ClosureEvent)
# ---------------------------------------------------------------------------

def push_closure_to_gate(app: Any, closure_id: str) -> None:
    """
    Queue a completed end-of-day closure for upload to SaleFlex.GATE.

    Called by ClosureEvent after a closure has been successfully persisted
    to the local database.  Silently skips when GATE is disabled.

    Args:
        app:        Application singleton.
        closure_id: UUID of the completed Closure record.
    """
    sync = _gate_sync()
    if not sync.is_enabled():
        return
    try:
        sync.queue_closure(closure_id)
    except Exception as e:
        logger.warning("push_closure_to_gate failed (non-fatal): %s", e)


# ---------------------------------------------------------------------------
# Warehouse hooks  (called from WarehouseEvent)
# ---------------------------------------------------------------------------

def push_warehouse_movement_to_gate(app: Any, movement_id: str) -> None:
    """
    Queue a stock movement event for upload to SaleFlex.GATE.

    Args:
        app:         Application singleton.
        movement_id: UUID of the WarehouseStockMovement record.
    """
    sync = _gate_sync()
    if not sync.is_enabled():
        return
    try:
        sync.queue_warehouse_movement(movement_id)
    except Exception as e:
        logger.warning("push_warehouse_movement_to_gate failed (non-fatal): %s", e)


# ---------------------------------------------------------------------------
# Pull / update hooks  (called from GeneralEvent on startup or manual refresh)
# ---------------------------------------------------------------------------

def pull_updates_from_gate(app: Any) -> None:
    """
    Pull product, pricing, campaign, and notification updates from GATE.

    Called by GeneralEvent during application startup and by SyncWorker
    on its periodic schedule.  Silently skips when GATE is disabled.

    Args:
        app: Application singleton (used to trigger cache refresh signals).
    """
    pull = _gate_pull()
    if not pull.is_enabled():
        return
    try:
        pull.pull_product_updates()
        pull.pull_campaign_updates()
        pull.pull_notifications()
    except Exception as e:
        logger.warning("pull_updates_from_gate failed (non-fatal): %s", e)
    finally:
        from pos.service.campaign.active_campaign_cache import ActiveCampaignCache

        ActiveCampaignCache.reload_safely()


# ---------------------------------------------------------------------------
# Campaign / ERP / Payment hooks  (routing via IntegrationMixin)
# ---------------------------------------------------------------------------

def apply_campaign_discounts(app: Any, cart_data: dict) -> dict:
    """
    Request campaign discount calculation from GATE or a direct third-party module.

    Returns the original cart_data unchanged when no integration is active,
    so the sale flow is never interrupted.

    Args:
        app:       Application singleton.
        cart_data: Prefer canonical snapshot dict (``schema_version`` 1.0 from
            ``pos.service.campaign``) or ``document_data`` with ``head`` and
            ``products``; see ``normalize_cart_data_for_campaign_request``.

    Returns:
        Updated cart_data with applied discounts, or original dict if integration
        is not available.
    """
    try:
        applier = getattr(app, "_integration_mixin", None)
        if applier is None and hasattr(app, "apply_campaign"):
            applier = app
        if applier is not None and hasattr(applier, "apply_campaign"):
            return applier.apply_campaign(cart_data)
    except Exception as e:
        logger.warning("apply_campaign_discounts failed (non-fatal): %s", e)
    return cart_data
