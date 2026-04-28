"""
SaleFlex.PyPOS - GATE notification serializer.

Converts inbound GATE notification payloads to local GateNotification records
and prepares them for dispatch to the UI via NotificationWorker signals.

Notification types supported by GATE:
    - "product_update"    → trigger product_data cache refresh
    - "campaign_update"   → trigger campaign cache refresh
    - "price_change"      → trigger price cache refresh
    - "terminal_message"  → display a message on the POS screen
    - "system_alert"      → display a system-level alert
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

from typing import Dict, Any, List

from core.logger import get_logger

logger = get_logger(__name__)

# Known notification types that trigger a local cache refresh.
CACHE_REFRESH_TYPES = {"product_update", "campaign_update", "price_change"}


class NotificationSerializer:
    """
    Processes inbound notification payloads from SaleFlex.GATE.
    """

    @staticmethod
    def save_and_dispatch(notifications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Persist notifications to the local GateNotification table and return
        a list of processed records for the NotificationWorker to dispatch.

        Args:
            notifications: Raw notification dicts from GATE's notifications endpoint.

        Returns:
            List of processed notification dicts with at minimum:
            {"type": str, "title": str, "body": str}

        TODO: Create GateNotification DB records for each item.
              Mark items as "read" on GATE after processing.
        """
        logger.info("[NotificationSerializer] save_and_dispatch (stub) count=%d",
                    len(notifications))
        processed = []
        for notif in notifications:
            processed.append({
                "type": notif.get("type", "unknown"),
                "title": notif.get("title", ""),
                "body": notif.get("body", ""),
                "source_terminal_id": notif.get("source_terminal_id"),
            })
        return processed

    @staticmethod
    def requires_cache_refresh(notification_type: str) -> bool:
        """Return True when a notification type triggers a local cache refresh."""
        return notification_type in CACHE_REFRESH_TYPES
