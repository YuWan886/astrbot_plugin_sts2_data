"""API client for Slay the Spire 2 Codex database."""

from __future__ import annotations

import asyncio
from typing import Any

import aiohttp

from astrbot.api import logger

from .constants import API_BASE, DEFAULT_LANG, ENDPOINTS, REQUEST_TIMEOUT


class STS2APIClient:
    """Client for interacting with the Slay the Spire 2 Codex API."""

    def __init__(self, timeout: int = REQUEST_TIMEOUT):
        """Initialize the API client.

        Args:
            timeout: Request timeout in seconds.
        """
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: aiohttp.ClientSession | None = None

    async def start(self) -> None:
        """Start the underlying HTTP session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)

    async def close(self) -> None:
        """Close the underlying HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            raise RuntimeError("API client session is not initialized")
        return self._session

    async def fetch_endpoint(
        self, endpoint: str, keyword: str | None = None
    ) -> list[dict[str, Any]]:
        """Fetch data from a specific endpoint.

        Args:
            endpoint: The endpoint name (e.g., "cards", "relics").
            keyword: Optional search keyword.

        Returns:
            List of items matching the search criteria.

        Raises:
            ValueError: If the endpoint is not supported.
            aiohttp.ClientError: If the HTTP request fails.
        """
        if endpoint not in ENDPOINTS:
            raise ValueError(f"Unsupported endpoint: {endpoint}")

        endpoint_meta = ENDPOINTS[endpoint]
        url = f"{API_BASE}{endpoint_meta['path']}"

        params: dict[str, str] = {"lang": DEFAULT_LANG}
        search_param = endpoint_meta.get("search_param")

        if search_param and keyword:
            params[search_param] = keyword

        logger.debug("Fetching %s from %s with params: %s", endpoint, url, params)

        try:
            session = self._get_session()
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                payload = await response.json()

            items = self._extract_items(payload, endpoint)

            # If there's no search param but we have a keyword, filter locally
            if keyword and not search_param:
                items = self._filter_items(items, keyword)

            logger.debug("Retrieved %s items from %s", len(items), endpoint)
            return items

        except aiohttp.ContentTypeError as exc:
            logger.error(
                "Unexpected response content for %s with params %s: %s",
                endpoint,
                params,
                exc,
            )
            raise
        except aiohttp.ClientResponseError as exc:
            logger.error(
                "HTTP error %s for %s with params %s: %s",
                exc.status,
                endpoint,
                params,
                exc.message,
            )
            raise
        except aiohttp.ClientError as exc:
            logger.error(
                "HTTP request failed for %s with params %s: %s", endpoint, params, exc
            )
            raise
        except asyncio.TimeoutError:
            logger.error(
                "Request timeout for %s after %ss with params %s",
                endpoint,
                self.timeout.total,
                params,
            )
            raise

    def _extract_items(self, payload: Any, endpoint: str) -> list[dict[str, Any]]:
        if isinstance(payload, list):
            return payload

        if isinstance(payload, dict):
            data = payload.get("data")
            if isinstance(data, list):
                return data
            items = payload.get("items")
            if isinstance(items, list):
                return items

        logger.warning(
            "Unexpected payload structure for %s: %s", endpoint, type(payload)
        )
        return []

    @staticmethod
    def _filter_items(
        items: list[dict[str, Any]], keyword: str
    ) -> list[dict[str, Any]]:
        """Filter items locally based on keyword.

        Args:
            items: List of items to filter.
            keyword: Search keyword.

        Returns:
            Filtered list of items.
        """
        if not keyword:
            return items

        needle = keyword.lower()
        results: list[dict[str, Any]] = []

        for item in items:
            name = str(item.get("name", "")).lower()
            item_id = str(item.get("id", "")).lower()

            if needle in name or needle in item_id:
                results.append(item)

        return results

    def normalize_image_url(self, url: str | None) -> str | None:
        """Normalize image URL by prepending API base if needed.

        Args:
            url: The image URL (may be relative or absolute).

        Returns:
            Normalized absolute URL, or None if input is invalid.
        """
        if not url or not isinstance(url, str):
            return None

        if url.startswith("/"):
            return f"{API_BASE}{url}"

        return url
