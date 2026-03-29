"""API client for Slay the Spire 2 Codex database."""

import asyncio
from typing import Any

import aiohttp

from astrbot.api import logger

from .constants import (
    API_BASE,
    DEFAULT_LANG,
    ENDPOINTS,
    REQUEST_TIMEOUT,
)


class STS2APIClient:
    """Client for interacting with the Slay the Spire 2 Codex API."""

    def __init__(self, timeout: int = REQUEST_TIMEOUT):
        """Initialize the API client.

        Args:
            timeout: Request timeout in seconds.
        """
        self.timeout = aiohttp.ClientTimeout(total=timeout)

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

        logger.debug(f"Fetching {endpoint} from {url} with params: {params}")

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, params=params) as response:
                    response.raise_for_status()
                    payload = await response.json()

            if isinstance(payload, list):
                items = payload
            else:
                items = []

            # If there's no search param but we have a keyword, filter locally
            if keyword and not search_param:
                items = self._filter_items(items, keyword)

            logger.debug(f"Retrieved {len(items)} items from {endpoint}")
            return items

        except aiohttp.ClientResponseError as e:
            logger.error(f"HTTP error {e.status} for {endpoint}: {e.message}")
            raise
        except aiohttp.ClientError as e:
            logger.error(f"HTTP request failed for {endpoint}: {e}")
            raise
        except asyncio.TimeoutError:
            logger.error(f"Request timeout for {endpoint} after {self.timeout.total}s")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching {endpoint}: {e}")
            raise

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
