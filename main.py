"""Slay the Spire 2 data plugin for AstrBot."""

from __future__ import annotations

import asyncio
from typing import Any

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register

from .api_client import STS2APIClient
from .constants import ENDPOINTS, SINGULAR_ALIASES
from .formatters import STS2Formatter


@register("sts2_data", "YuWan886", "查询杀戮尖塔2数据库信息", "1.2.2")
class Sts2DataPlugin(Star):
    """Plugin for querying Slay the Spire 2 Codex database."""

    def __init__(self, context: Context):
        """Initialize the plugin.

        Args:
            context: Plugin context provided by AstrBot.
        """
        super().__init__(context)
        self.api_client = STS2APIClient()
        self.formatter = STS2Formatter(self.api_client)

    async def initialize(self) -> None:
        """Optional async initialization."""
        await self.api_client.start()
        logger.info("STS2 Data plugin initialized")

    @filter.command("sts2_help")
    async def sts2_help(self, event: AstrMessageEvent) -> Any:
        """Show help for sts2 commands.

        Args:
            event: The message event.
        """
        help_text = self.formatter.format_help()
        yield event.plain_result(help_text)

    @filter.command("sts2")
    async def sts2_query(self, event: AstrMessageEvent) -> Any:
        """Query Slay the Spire 2 Codex database.

        Args:
            event: The message event containing the query.
        """
        query = event.message_str.strip()

        # Parse query to extract endpoint and keyword
        endpoint, keyword = self._parse_query(query)
        if endpoint is None:
            yield event.plain_result(
                "Usage: /sts2 <endpoint> <keyword>. Example: /sts2 cards strike"
            )
            return

        # Validate endpoint
        if endpoint not in ENDPOINTS:
            yield event.plain_result(
                "Unsupported endpoint. Use: " + ", ".join(sorted(ENDPOINTS.keys()))
            )
            return

        if keyword is None:
            yield event.plain_result(
                "请补充关键词，例如：/sts2 cards strike 或 /sts2 relics lantern"
            )
            return

        try:
            await self.api_client.start()

            # Fetch data from API
            data = await self.api_client.fetch_endpoint(endpoint, keyword)

            # Format and yield results
            for result in self.formatter.format_response(endpoint, data, event):
                yield result

        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("STS2 data fetch failed")
            yield event.plain_result("请求失败，请稍后重试。")

    def _parse_query(self, query: str) -> tuple[str | None, str | None]:
        """Parse user query to extract endpoint and keyword.

        Args:
            query: The raw query string.

        Returns:
            Tuple of (endpoint, keyword) or (None, None) if parsing fails.
        """
        if not query:
            return None, None

        parts = query.split()
        first = parts[0].lower()

        # Remove command prefixes
        command_prefixes = {"sts2", "/sts2", "yw-sts2", "/yw-sts2"}
        if first in command_prefixes:
            parts = parts[1:]
        elif first.startswith("yw-"):
            parts[0] = first.removeprefix("yw-")

        if not parts:
            return None, None

        # Try to identify endpoint
        endpoint = parts[0].lower()
        endpoint = SINGULAR_ALIASES.get(endpoint, endpoint)

        # If first word is not a valid endpoint, check second word
        if endpoint not in ENDPOINTS and len(parts) > 1:
            candidate = SINGULAR_ALIASES.get(parts[1].lower(), parts[1].lower())
            if candidate in ENDPOINTS:
                parts = parts[1:]
                endpoint = candidate

        # Extract keyword
        keyword = " ".join(parts[1:]).strip() if len(parts) > 1 else ""

        # Final endpoint normalization
        endpoint = SINGULAR_ALIASES.get(endpoint, endpoint)

        return endpoint, keyword if keyword else None

    async def terminate(self) -> None:
        """Optional async termination."""
        await self.api_client.close()
        logger.info("STS2 Data plugin terminated")
