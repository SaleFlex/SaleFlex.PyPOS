"""
SaleFlex.PyPOS - External Device base class for the integration layer.

Mirrors the OposDevice pattern used in pos/peripherals/: all methods are
log-only stubs until a real connector is wired in. Concrete connectors
(GateClient, third-party adapters) inherit this class and override the
relevant methods.

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
