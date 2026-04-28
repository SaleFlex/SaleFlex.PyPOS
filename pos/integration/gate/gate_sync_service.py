"""
SaleFlex.PyPOS - SaleFlex.GATE outbound synchronisation service.

Responsible for pushing local POS data (transactions, closures, warehouse
movements) to SaleFlex.GATE.  Uses the offline outbox pattern: every event
is first written to the local SyncQueueItem table and then sent by the
SyncWorker background thread, ensuring no data is lost during connectivity
gaps.
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

from typing import List

from core.logger import get_logger
from core.exceptions import GATESyncError
from pos.integration.gate.gate_client import get_default_gate_client
from pos.integration.gate.serializers.transaction_serializer import TransactionSerializer
from pos.integration.gate.serializers.closure_serializer import ClosureSerializer
from pos.integration.gate.serializers.warehouse_serializer import WarehouseSerializer

logger = get_logger(__name__)

_default_gate_sync: "GateSyncService | None" = None


class GateSyncService:
    """
    Outbound push service for SaleFlex.GATE.

    Call queue_*() methods from event hooks immediately after a local record
    is persisted.  The actual HTTP transmission is handled by SyncWorker in
    a background QThread so the UI is never blocked.

    Offline outbox flow:
        1. queue_transaction(head_id)  ← called by PaymentEvent hook
        2. SyncQueueItem row is written with status="pending"
        3. SyncWorker calls flush_pending_queue() on its schedule
        4. Each pending item is serialised and pushed via GateClient
        5. Successful items are marked status="sent"; failures increment
           retry_count and are retried on the next cycle.
    """

    def __init__(self) -> None:
        self._client = get_default_gate_client()

    # ------------------------------------------------------------------
    # Public: enable check
    # ------------------------------------------------------------------

    def is_enabled(self) -> bool:
        """Return True when GATE push is configured and active."""
        return self._client.is_enabled()

    # ------------------------------------------------------------------
    # Public: queue methods  (called from hooks.py)
    # ------------------------------------------------------------------

    def queue_transaction(self, transaction_head_id: str) -> None:
        """
        Add a completed transaction to the outbox for upload to GATE.

        Args:
            transaction_head_id: UUID of the TransactionHead record.
        """
        self._enqueue("gate", "transaction", {"head_id": transaction_head_id})

    def queue_closure(self, closure_id: str) -> None:
        """
        Add a completed end-of-day closure to the outbox.

        Args:
            closure_id: UUID of the Closure record.
        """
        self._enqueue("gate", "closure", {"closure_id": closure_id})

    def queue_warehouse_movement(self, movement_id: str) -> None:
        """
        Add a stock movement event to the outbox.

        Args:
            movement_id: UUID of the WarehouseStockMovement record.
        """
        self._enqueue("gate", "warehouse_movement", {"movement_id": movement_id})

    def queue_erp_payload(self, payload: dict) -> None:
        """
        Forward an ERP synchronisation payload through GATE.

        Used when gate.manages_erp = true in settings.toml.

        Args:
            payload: Arbitrary dict that GATE will relay to its ERP backend.
        """
        self._enqueue("gate_erp", "erp_sync", payload)

    def queue_payment_payload(self, payload: dict) -> None:
        """
        Forward a payment request through GATE's built-in payment layer.

        Used when gate.manages_payment = true in settings.toml.

        Args:
            payload: Payment request dict.
        """
        self._enqueue("gate_payment", "payment", payload)

    # ------------------------------------------------------------------
    # Public: flush  (called by SyncWorker)
    # ------------------------------------------------------------------

    def flush_pending_queue(self) -> None:
        """
        Process all SyncQueueItem rows with status='pending'.

        Iterates the local outbox, serialises each record, pushes it to GATE,
        and updates the item status to 'sent' or 'failed'.

        TODO: Implement the DB query and push loop once SyncQueueItem model
              is registered in data_layer/model/__init__.py.
        """
        logger.info("[GateSyncService] flush_pending_queue (stub)")
        # Stub outline:
        # items = SyncQueueItem.get_pending()
        # for item in items:
        #     try:
        #         payload = self._build_payload(item)
        #         self._client.push(payload)
        #         item.mark_sent()
        #     except GATESyncError as e:
        #         item.increment_retry(str(e))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _enqueue(self, connector_type: str, event_type: str, data: dict) -> None:
        """
        Write a new SyncQueueItem row to the local database outbox.

        Args:
            connector_type: "gate" | "gate_erp" | "gate_payment"
            event_type:     "transaction" | "closure" | "warehouse_movement" | …
            data:           Dict that will be stored as JSON payload.
        """
        logger.info("[GateSyncService] enqueue connector=%s event=%s data_keys=%s",
                    connector_type, event_type, list(data.keys()))
        # TODO: Create and save a SyncQueueItem record here.
        # from data_layer.model.definition.sync_queue_item import SyncQueueItem
        # SyncQueueItem.create(connector_type, event_type, data)

    def _build_payload(self, queue_item) -> dict:
        """
        Serialise a SyncQueueItem into the GATE API payload format.

        Selects the appropriate serializer based on the item's event_type.
        """
        event_type = queue_item.event_type
        data = queue_item.payload

        if event_type == "transaction":
            return TransactionSerializer.serialize(data["head_id"])
        if event_type == "closure":
            return ClosureSerializer.serialize(data["closure_id"])
        if event_type == "warehouse_movement":
            return WarehouseSerializer.serialize(data["movement_id"])

        # Fallback: pass the raw payload dict with the endpoint tag.
        payload = dict(data)
        payload["_endpoint"] = f"api/{event_type}/"
        return payload


# ---------------------------------------------------------------------------
# Module-level factory
# ---------------------------------------------------------------------------

def get_default_gate_sync() -> GateSyncService:
    """Return the module-level GateSyncService singleton."""
    global _default_gate_sync
    if _default_gate_sync is None:
        _default_gate_sync = GateSyncService()
    return _default_gate_sync
