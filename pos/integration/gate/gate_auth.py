"""
SaleFlex.PyPOS - SaleFlex.GATE authentication manager.

Handles API token acquisition, storage, and renewal.  The current
implementation is a stub: token logic is logged and safe defaults are
returned until real GATE credentials are configured.
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

from datetime import datetime, timedelta
from typing import Optional

from core.logger import get_logger

logger = get_logger(__name__)


class GateAuth:
    """
    Manages the authentication token used by GateClient.

    Responsibilities:
    - Obtain a token from GATE's auth endpoint using the configured API key.
    - Cache the token in memory together with its expiry timestamp.
    - Provide a valid (non-expired) token on every request via get_token().
    - Silently renew the token when it is about to expire.

    All network calls are stubs until a real GATE instance is configured.
    """

    # Renew the token this many seconds before it officially expires.
    _RENEWAL_BUFFER_SECONDS: int = 60

    def __init__(self, base_url: str, api_key: str, terminal_id: str) -> None:
        self._base_url = base_url
        self._api_key = api_key
        self._terminal_id = terminal_id

        self._token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_token(self) -> Optional[str]:
        """
        Return a valid bearer token, renewing it automatically when needed.

        Returns:
            Bearer token string, or None when authentication is not possible.
        """
        if self._token_is_valid():
            return self._token
        return self._acquire_token()

    def invalidate(self) -> None:
        """Force the next get_token() call to re-authenticate."""
        self._token = None
        self._token_expiry = None
        logger.info("[GateAuth] token invalidated")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _token_is_valid(self) -> bool:
        if not self._token or not self._token_expiry:
            return False
        remaining = (self._token_expiry - datetime.utcnow()).total_seconds()
        return remaining > self._RENEWAL_BUFFER_SECONDS

    def _acquire_token(self) -> Optional[str]:
        """
        Authenticate against GATE and store the returned token.

        TODO: Replace stub with real HTTP POST to GATE's auth endpoint:
              POST {base_url}/api/auth/token/
              Body: {"api_key": self._api_key, "terminal_id": self._terminal_id}

        Returns:
            Token string on success, None on failure.
        """
        logger.info("[GateAuth] _acquire_token (stub) — no real request made")
        # Stub: real implementation uses the requests library here.
        # self._token = response_json["access"]
        # self._token_expiry = datetime.utcnow() + timedelta(seconds=response_json["expires_in"])
        return None
