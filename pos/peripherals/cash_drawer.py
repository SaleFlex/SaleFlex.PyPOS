"""
SaleFlex.PyPOS - Cash drawer peripheral (OPOS-style, log-only stub).

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
