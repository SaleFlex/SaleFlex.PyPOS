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
