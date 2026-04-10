"""
SaleFlex.PyPOS - Glue between POS event flows and integration layer.

Mirrors pos/peripherals/hooks.py: event handlers import these thin functions
instead of importing integration internals directly.  Keeping the glue
separate means event handler code stays unaware of whether GATE is enabled,
which connector is active, or how retries are handled.

Copyright (c) 2026 Ferhat Mousavi

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
