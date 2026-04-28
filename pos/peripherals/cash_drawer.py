"""
SaleFlex.PyPOS - Cash drawer peripheral (OPOS-style, log-only stub).
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

from core.logger import get_logger
from pos.peripherals.opos_device import OposDevice

logger = get_logger(__name__)

_default_drawer: "CashDrawer | None" = None


class CashDrawer(OposDevice):
    """Kick-out drawer command; currently logs only."""

    def open_drawer(self, reason: str = "") -> None:
        msg = reason.strip() or "unspecified"
        logger.info("[CashDrawer] open_drawer (%s) logical_name=%s", msg, self.logical_name)


def get_default_cash_drawer() -> CashDrawer:
    global _default_drawer
    if _default_drawer is None:
        _default_drawer = CashDrawer("default")
    return _default_drawer
