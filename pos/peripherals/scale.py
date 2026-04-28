"""
SaleFlex.PyPOS - Weighing scale peripheral (OPOS-style stub for future use).
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

from decimal import Decimal
from typing import Optional, Tuple

from pos.peripherals.opos_device import OposDevice


class Scale(OposDevice):
    """Retail scale; not wired into the UI yet."""

    def read_weight(self) -> Tuple[Optional[Decimal], Optional[str]]:
        return None, None
