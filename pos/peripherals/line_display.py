"""
SaleFlex.PyPOS - Pole / line display peripheral (OPOS-style, log-only stub).
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

_default_line_display: "LineDisplay | None" = None


class LineDisplay(OposDevice):
    """Customer-facing multi-line display; currently logs three text lines."""

    def send_three_lines(self, line1: str, line2: str, line3: str) -> None:
        logger.info(
            "[LineDisplay] line1=%r line2=%r line3=%r (logical_name=%s)",
            line1,
            line2,
            line3,
            self.logical_name,
        )


def get_default_line_display() -> LineDisplay:
    global _default_line_display
    if _default_line_display is None:
        _default_line_display = LineDisplay("default")
    return _default_line_display
