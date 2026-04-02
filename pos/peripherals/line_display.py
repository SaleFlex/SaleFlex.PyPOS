"""
SaleFlex.PyPOS - Pole / line display peripheral (OPOS-style, log-only stub).

Copyright (c) 2025 Ferhat Mousavi

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
