"""
SaleFlex.PyPOS - External Device base class for the integration layer.

Mirrors the OposDevice pattern used in pos/peripherals/: all methods are
log-only stubs until a real connector is wired in. Concrete connectors
(GateClient, third-party adapters) inherit this class and override the
relevant methods.
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

from typing import Any, Dict, Optional

from core.logger import get_logger

logger = get_logger(__name__)


class ExternalDevice:
    """
    Minimal external-system lifecycle stub.

    All methods return safe default values and write to the application log.
    Real connectors override connect / push / pull / health_check without
    changing any call sites in event handlers or hooks.

    Design contract (same philosophy as OposDevice):
    - connect()      → open a session / authenticate
    - is_connected() → return current connection state
    - disconnect()   → close session gracefully
    - push()         → send data to the remote system
    - pull()         → fetch data from the remote system
    - health_check() → lightweight liveness probe
    """

    def __init__(self, logical_name: str = "") -> None:
        self.logical_name = logical_name or self.__class__.__name__
        self._connected: bool = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def connect(self) -> bool:
        """Open a connection / authenticate with the remote system."""
        logger.info("[%s] connect (stub)", self.logical_name)
        return False

    def is_connected(self) -> bool:
        """Return True when an active session exists."""
        return self._connected

    def disconnect(self) -> bool:
        """Close the active session gracefully."""
        logger.info("[%s] disconnect (stub)", self.logical_name)
        self._connected = False
        return True

    # ------------------------------------------------------------------
    # Data exchange
    # ------------------------------------------------------------------

    def push(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send *payload* to the remote system.

        Args:
            payload: Serialised data to transmit.

        Returns:
            Response dict from the remote system, or empty dict on stub/failure.
        """
        logger.info("[%s] push (stub): %s", self.logical_name, payload)
        return {}

    def pull(self, resource: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Fetch *resource* from the remote system.

        Args:
            resource: Endpoint name or resource identifier.
            params:   Optional query parameters.

        Returns:
            Response dict from the remote system, or empty dict on stub/failure.
        """
        logger.info("[%s] pull (stub) resource=%s params=%s", self.logical_name, resource, params)
        return {}

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def health_check(self) -> bool:
        """Lightweight probe that returns True when the remote system is reachable."""
        logger.info("[%s] health_check (stub)", self.logical_name)
        return False
