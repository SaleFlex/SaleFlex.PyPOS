"""
SaleFlex.PyPOS - OPOS-style peripheral base (stub lifecycle).
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


class OposDevice:
    """
    Minimal OPOS-like device lifecycle. Real drivers will override these hooks.
    No connection checks are performed in the current implementation.
    """

    def __init__(self, logical_name: str = "") -> None:
        self.logical_name = logical_name or self.__class__.__name__

    def open(self) -> bool:
        return True

    def claim(self, timeout_ms: int = 0) -> bool:
        return True

    def release(self) -> bool:
        return True

    def close(self) -> bool:
        return True
