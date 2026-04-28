"""
SaleFlex.PyPOS - SaleFlex.GATE HTTP client.

Low-level transport layer that wraps the `requests` library.  All methods
are log-only stubs until a real GATE instance is configured via settings.toml.
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
from core.exceptions import GATEConnectionError, GATEAuthError
from pos.integration.external_device import ExternalDevice
from pos.integration.gate.gate_auth import GateAuth

logger = get_logger(__name__)

# Module-level default instance (same pattern as get_default_pos_printer).
_default_gate_client: "GateClient | None" = None


class GateClient(ExternalDevice):
    """
    HTTP client for the SaleFlex.GATE REST API.

    Responsibilities:
    - Build authenticated request headers using GateAuth.
    - Execute GET / POST requests with configurable timeout and retry logic.
    - Raise GATEConnectionError / GATEAuthError on unrecoverable failures.
    - Return empty dicts when GATE is disabled, so callers never crash.

    All network calls are stubs.  Replace the TODO sections with real
    `requests` calls once GATE credentials are available in settings.toml.
    """

    def __init__(
        self,
        base_url: str = "",
        api_key: str = "",
        terminal_id: str = "",
        timeout_seconds: int = 10,
        retry_attempts: int = 3,
    ) -> None:
        super().__init__(logical_name="GateClient")
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds
        self._retry_attempts = retry_attempts
        self._auth = GateAuth(base_url, api_key, terminal_id)
        self._enabled = bool(base_url and api_key)

    # ------------------------------------------------------------------
    # ExternalDevice overrides
    # ------------------------------------------------------------------

    def connect(self) -> bool:
        """Authenticate and verify connectivity with GATE."""
        if not self._enabled:
            logger.info("[GateClient] connect skipped — GATE not configured")
            return False
        token = self._auth.get_token()
        if token:
            self._connected = True
            logger.info("[GateClient] connected to %s", self._base_url)
        else:
            logger.warning("[GateClient] connect failed — could not acquire token")
        return self._connected

    def is_connected(self) -> bool:
        return self._connected and self._enabled

    def is_enabled(self) -> bool:
        """Return True when GATE is configured and enabled in settings."""
        return self._enabled

    def push(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        HTTP POST *payload* to the endpoint specified in payload["_endpoint"].

        The special key ``_endpoint`` is removed before serialisation.

        TODO: Replace stub with:
              import requests
              url = f"{self._base_url}/{endpoint}"
              headers = self._build_headers()
              resp = requests.post(url, json=payload, headers=headers,
                                   timeout=self._timeout)
              resp.raise_for_status()
              return resp.json()

        Returns:
            Response dict from GATE, or empty dict on stub/error.
        """
        endpoint = payload.pop("_endpoint", "unknown")
        logger.info("[GateClient] POST (stub) %s/%s payload_keys=%s",
                    self._base_url, endpoint, list(payload.keys()))
        return {}

    def pull(self, resource: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        HTTP GET *resource* from GATE.

        TODO: Replace stub with:
              import requests
              url = f"{self._base_url}/{resource}"
              headers = self._build_headers()
              resp = requests.get(url, params=params, headers=headers,
                                  timeout=self._timeout)
              resp.raise_for_status()
              return resp.json()

        Returns:
            Response dict from GATE, or empty dict on stub/error.
        """
        logger.info("[GateClient] GET (stub) %s/%s params=%s",
                    self._base_url, resource, params)
        return {}

    def health_check(self) -> bool:
        """
        Lightweight liveness probe — GET /api/health/.

        TODO: Replace stub with a real GET request.
        """
        logger.info("[GateClient] health_check (stub) %s", self._base_url)
        return False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_headers(self) -> Dict[str, str]:
        """Build the Authorization header for every request."""
        token = self._auth.get_token()
        if not token:
            raise GATEAuthError("GateClient: no valid token available")
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }


# ---------------------------------------------------------------------------
# Module-level factory  (same pattern as pos/peripherals)
# ---------------------------------------------------------------------------

def get_default_gate_client() -> GateClient:
    """Return the module-level GateClient singleton, creating it on first call."""
    global _default_gate_client
    if _default_gate_client is None:
        try:
            from settings.settings import Settings
            s = Settings()
            gate_cfg = s.gate
            _default_gate_client = GateClient(
                base_url=gate_cfg.get("base_url", ""),
                api_key=gate_cfg.get("api_key", ""),
                terminal_id=gate_cfg.get("terminal_id", ""),
                timeout_seconds=int(gate_cfg.get("timeout_seconds", 10)),
                retry_attempts=int(gate_cfg.get("retry_attempts", 3)),
            )
        except Exception as e:
            logger.warning("[GateClient] could not read settings, using stub: %s", e)
            _default_gate_client = GateClient()
    return _default_gate_client
