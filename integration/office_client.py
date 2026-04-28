"""
SaleFlex.PyPOS - SaleFlex.OFFICE REST Client
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

    def push_transactions(
        self,
        pos_id: int,
        transactions: list[dict],
        sequences: list[dict] | None = None,
    ) -> dict:
        """
        Push a batch of completed transaction records to OFFICE.

        Parameters
        ----------
        pos_id:
            Integer POS terminal number (pos_no_in_store) of this terminal.
        transactions:
            List of serialised transaction dicts, each containing:
            {"head": {...}, "products": [...], "payments": [...], ...}
        sequences:
            Optional list of sequence counter updates:
            [{"name": "ReceiptNumber", "value": 42}, ...]

        Returns
        -------
        dict with keys: status, accepted, rejected

        Raises
        ------
        OfficeConnectionError
            When the OFFICE server cannot be reached.
        RuntimeError
            When OFFICE returns an unexpected HTTP status code.
        """
        url = f"{self._base_url}{self._api_prefix}/pos/transactions"
        payload = {
            "office_code":   self._office_code,
            "store_code":    self._store_code,
            "terminal_code": self._terminal_code,
            "pos_id":        pos_id,
            "transactions":  transactions,
            "sequences":     sequences or [],
        }

        logger.info(
            "[OfficeClient] Pushing %d transaction(s) to OFFICE (pos_id=%d)",
            len(transactions), pos_id,
        )

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self._timeout,
            )
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

        if response.status_code not in (200, 201):
            raise RuntimeError(
                f"Unexpected OFFICE response HTTP {response.status_code}: "
                f"{response.text[:200]}"
            )

        result = response.json()
        logger.info(
            "[OfficeClient] Push result: accepted=%s rejected=%s",
            result.get("accepted"),
            result.get("rejected"),
        )
        return result

    def push_sequences(self, pos_id: int, sequences: list[dict]) -> dict:
        """
        Push sequence counter updates to OFFICE for this terminal.

        Parameters
        ----------
        pos_id:
            Integer POS terminal number.
        sequences:
            List of dicts: [{"name": "ReceiptNumber", "value": 42}, ...]

        Returns
        -------
        dict with keys: status, updated

        Raises
        ------
        OfficeConnectionError, RuntimeError – same as push_transactions.
        """
        url = f"{self._base_url}{self._api_prefix}/pos/sequences"
        payload = {
            "office_code":   self._office_code,
            "store_code":    self._store_code,
            "terminal_code": self._terminal_code,
            "pos_id":        pos_id,
            "sequences":     sequences,
        }

        try:
            response = requests.post(url, json=payload, timeout=self._timeout)
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

        if response.status_code not in (200, 201):
            raise RuntimeError(
                f"Unexpected OFFICE response HTTP {response.status_code}: "
                f"{response.text[:200]}"
            )

        return response.json()

    def push_closures(
        self,
        pos_id: int,
        closures: list[dict],
        sequences: list[dict] | None = None,
    ) -> dict:
        """
        Push completed end-of-day closure records to OFFICE.

        The caller may pass one closure per request to keep queue status updates
        precise.  Current sequence counters are sent with every request.
        """
        url = f"{self._base_url}{self._api_prefix}/pos/closures"
        payload = {
            "office_code":   self._office_code,
            "store_code":    self._store_code,
            "terminal_code": self._terminal_code,
            "pos_id":        pos_id,
            "closures":      closures,
            "sequences":     sequences or [],
        }

        logger.info(
            "[OfficeClient] Pushing %d closure(s) to OFFICE (pos_id=%d)",
            len(closures), pos_id,
        )

        try:
            response = requests.post(url, json=payload, timeout=self._timeout)
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

        if response.status_code not in (200, 201):
            raise RuntimeError(
                f"Unexpected OFFICE response HTTP {response.status_code}: "
                f"{response.text[:200]}"
            )

        result = response.json()
        logger.info(
            "[OfficeClient] Closure push result: accepted=%s rejected=%s",
            result.get("accepted"),
            result.get("rejected"),
        )
        return result
