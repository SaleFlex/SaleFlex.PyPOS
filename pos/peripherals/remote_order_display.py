"""
SaleFlex.PyPOS - Kitchen / remote order display peripheral (OPOS-style stub for future use).
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

from typing import Any, Dict, List

from pos.peripherals.opos_device import OposDevice


class RemoteOrderDisplay(OposDevice):
    """Bump bar / KDS style output; not wired yet."""

    def post_order_lines(self, lines: List[Dict[str, Any]]) -> None:
        pass
