"""
SaleFlex.PyPOS - SaleFlex.OFFICE REST Client

Copyright (c) 2025-2026 Ferhat Mousavi

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

from typing import Any

import requests

from core.logger import get_logger
from settings.settings import Settings

logger = get_logger(__name__)


class OfficeConnectionError(Exception):
    """Raised when the OFFICE server cannot be reached."""


class OfficeAuthError(Exception):
    """Raised when the OFFICE server rejects the terminal credentials."""


class OfficeClient:
    """
    Thin HTTP client that communicates with SaleFlex.OFFICE REST API.

    The client reads all connection parameters (base_url, api_prefix,
    office_code, store_code, terminal_code, timeout) from settings.toml
    so no runtime arguments are required for construction.
    """

    def __init__(self) -> None:
        settings = Settings()
        base_url = settings.office_base_url.rstrip("/")

        # Ensure the URL has a scheme so requests doesn't reject it.
        if base_url and not base_url.startswith(("http://", "https://")):
            base_url = f"http://{base_url}"

        self._base_url     = base_url
        self._api_prefix   = settings.office_api_prefix.rstrip("/")
        self._office_code  = settings.office_code
        self._store_code   = settings.store_code
        self._terminal_code = settings.terminal_code
        self._timeout      = settings.office_timeout_seconds

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check_health(self) -> bool:
        """
        Ping the OFFICE health endpoint.

        Returns True when OFFICE is reachable and healthy, False otherwise.
        """
        url = f"{self._base_url}{self._api_prefix}/health"
        try:
            response = requests.get(url, timeout=self._timeout)
            return response.status_code == 200
        except requests.RequestException as exc:
            logger.warning("OFFICE health check failed: %s", exc)
            return False

    def fetch_init_data(self) -> dict[str, Any]:
        """
        Pull all initialization data from OFFICE for this terminal.

        Returns the ``data`` dict from the OFFICE response on success.

        Raises
        ------
        OfficeConnectionError
            When the OFFICE server cannot be reached within the configured
            timeout, or when an unexpected network error occurs.
        OfficeAuthError
            When OFFICE rejects the (office_code, store_code, terminal_code)
            combination (HTTP 404 or 403).
        RuntimeError
            When OFFICE returns an unexpected HTTP status code.
        """
        url = f"{self._base_url}{self._api_prefix}/pos/init"
        params = {
            "office_code":   self._office_code,
            "store_code":    self._store_code,
            "terminal_code": self._terminal_code,
        }

        logger.info(
            "Connecting to OFFICE at %s (office=%s store=%s terminal=%s)",
            self._base_url,
            self._office_code,
            self._store_code,
            self._terminal_code,
        )

        try:
            response = requests.get(url, params=params, timeout=self._timeout)
        except requests.ConnectionError as exc:
            raise OfficeConnectionError(
                f"Cannot connect to SaleFlex.OFFICE at {self._base_url}: {exc}"
            ) from exc
        except requests.Timeout as exc:
            raise OfficeConnectionError(
                f"Connection to SaleFlex.OFFICE timed out after {self._timeout}s"
            ) from exc
        except requests.RequestException as exc:
            raise OfficeConnectionError(
                f"Network error while contacting SaleFlex.OFFICE: {exc}"
            ) from exc

        if response.status_code in (403, 404):
            body = response.json() if response.content else {}
            message = body.get("message", f"HTTP {response.status_code}")
            raise OfficeAuthError(
                f"OFFICE rejected terminal credentials – {message}"
            )

        if response.status_code != 200:
            raise RuntimeError(
                f"Unexpected OFFICE response HTTP {response.status_code}: "
                f"{response.text[:200]}"
            )

        payload = response.json()
        if payload.get("status") != "ok":
            raise RuntimeError(
                f"OFFICE returned error status: {payload.get('message', 'unknown')}"
            )

        data = payload.get("data", {})
        logger.info(
            "✓ Init data received from OFFICE (%d resource types)",
            len(data),
        )
        return data
