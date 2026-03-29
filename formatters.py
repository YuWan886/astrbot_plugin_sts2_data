"""Formatters for converting API data to user-friendly messages."""

from collections.abc import Generator
import re
from typing import Any

from astrbot.api.event import AstrMessageEvent

from .api_client import STS2APIClient
from .constants import DETAILED_ENDPOINTS, MAX_LIST_ITEMS


class STS2Formatter:
    """Formatter for Slay the Spire 2 data responses."""

    def __init__(self, api_client: STS2APIClient):
        """Initialize the formatter.

        Args:
            api_client: API client instance for URL normalization.
        """
        self.api_client = api_client

    def format_response(
        self, endpoint: str, data: list[dict[str, Any]], event: AstrMessageEvent
    ) -> Generator[Any, None, None]:
        """Format API response and yield results.

        Args:
            endpoint: The endpoint name.
            data: List of items from the API.
            event: The message event for generating results.
        """
        if not data:
            yield event.plain_result("No matching records found.")
            return

        if endpoint in DETAILED_ENDPOINTS:
            if len(data) > 1:
                yield from self._format_list(data, event)
                yield event.plain_result(
                    f"共 {len(data)} 条结果，请补充更精确的关键词查看详情。"
                )
                return
            yield from self._format_detailed(endpoint, data[0], event)
        else:
            yield from self._format_list(data, event)

    def _format_detailed(
        self, endpoint: str, item: dict[str, Any], event: AstrMessageEvent
    ) -> Generator[Any, None, None]:
        """Format a detailed item view.

        Args:
            endpoint: The endpoint name.
            item: The item data.
            event: The message event for generating results.
        """
        # Dispatch to specific formatter based on endpoint
        formatter_map = {
            "cards": self._format_card,
            "relics": self._format_relic,
            "monsters": self._format_monster,
            "potions": self._format_potion,
            "enchantments": self._format_enchantment,
            "events": self._format_event,
            "powers": self._format_power,
        }

        formatter = formatter_map.get(endpoint)
        if formatter:
            yield from formatter(item, event)
        else:
            # Fallback to generic detailed format
            yield from self._format_generic_detailed(item, event)

    def _format_card(
        self, card: dict[str, Any], event: AstrMessageEvent
    ) -> Generator[Any, None, None]:
        """Format a card item."""
        image_url = card.get("image_url") or card.get("beta_image_url")
        normalized_url = self.api_client.normalize_image_url(image_url)

        if normalized_url:
            yield event.image_result(normalized_url)

        header = (
            f"{self._safe_text(card.get('name'), 'Unknown')} | "
            f"{self._safe_text(card.get('id'), 'N/A')}"
        )
        detail = (
            f"费用: {self._safe_text(card.get('cost'), 'N/A')} | "
            f"类型: {self._safe_text(card.get('type'), 'N/A')} | "
            f"稀有度: {self._safe_text(card.get('rarity'), 'N/A')}"
        )

        description = self._safe_text(card.get("description"))
        lines = [header, detail, f"描述: {description}"]

        upgrade = card.get("upgrade")
        if isinstance(upgrade, dict) and upgrade:
            upgrade_desc = ", ".join(
                f"{self._safe_text(key)}: {self._safe_text(value)}"
                for key, value in upgrade.items()
                if value is not None
            )
            if upgrade_desc:
                lines.append(f"升级: {upgrade_desc}")

        yield event.plain_result("\n".join(lines))

    def _format_relic(
        self, relic: dict[str, Any], event: AstrMessageEvent
    ) -> Generator[Any, None, None]:
        """Format a relic item."""
        image_url = self.api_client.normalize_image_url(relic.get("image_url"))
        if image_url:
            yield event.image_result(image_url)

        header = (
            f"{self._safe_text(relic.get('name'), 'Unknown')} | "
            f"{self._safe_text(relic.get('id'), 'N/A')}"
        )
        detail = (
            f"稀有度: {self._safe_text(relic.get('rarity'), 'N/A')} | "
            f"池: {self._safe_text(relic.get('pool'), 'N/A')}"
        )

        description = self._safe_text(relic.get("description"))
        lines = [header, detail, f"描述: {description}"]

        flavor = self._safe_text(relic.get("flavor"))
        if flavor:
            lines.append(f"背景: {flavor}")

        yield event.plain_result("\n".join(lines))

    def _format_monster(
        self, monster: dict[str, Any], event: AstrMessageEvent
    ) -> Generator[Any, None, None]:
        """Format a monster item."""
        image_url = monster.get("image_url") or monster.get("beta_image_url")
        normalized_url = self.api_client.normalize_image_url(image_url)

        if normalized_url:
            yield event.image_result(normalized_url)

        header = (
            f"{self._safe_text(monster.get('name'), 'Unknown')} | "
            f"{self._safe_text(monster.get('id'), 'N/A')}"
        )

        hp_normal = (
            f"{self._safe_text(monster.get('min_hp'), 'N/A')}-"
            f"{self._safe_text(monster.get('max_hp'), 'N/A')}"
        )
        hp_asc = (
            f"{self._safe_text(monster.get('min_hp_ascension'), 'N/A')}-"
            f"{self._safe_text(monster.get('max_hp_ascension'), 'N/A')}"
        )

        detail = (
            f"类型: {self._safe_text(monster.get('type'), 'N/A')} | "
            f"生命: {hp_normal} | 进阶: {hp_asc}"
        )

        lines = [header, detail]

        moves = monster.get("moves") or []
        move_names = ", ".join(
            self._safe_text(move.get("name"))
            for move in moves
            if isinstance(move, dict) and move.get("name")
        )

        if move_names:
            lines.append(f"招式: {move_names}")

        yield event.plain_result("\n".join(lines))

    def _format_potion(
        self, potion: dict[str, Any], event: AstrMessageEvent
    ) -> Generator[Any, None, None]:
        """Format a potion item."""
        image_url = self.api_client.normalize_image_url(potion.get("image_url"))
        if image_url:
            yield event.image_result(image_url)

        header = (
            f"{self._safe_text(potion.get('name'), 'Unknown')} | "
            f"{self._safe_text(potion.get('id'), 'N/A')}"
        )
        detail = (
            f"稀有度: {self._safe_text(potion.get('rarity'), 'N/A')} | "
            f"池: {self._safe_text(potion.get('pool'), 'N/A')}"
        )

        description = self._safe_text(potion.get("description"))
        lines = [header, detail, f"描述: {description}"]

        yield event.plain_result("\n".join(lines))

    def _format_enchantment(
        self, enchantment: dict[str, Any], event: AstrMessageEvent
    ) -> Generator[Any, None, None]:
        """Format an enchantment item."""
        image_url = self.api_client.normalize_image_url(enchantment.get("image_url"))
        if image_url:
            yield event.image_result(image_url)

        header = (
            f"{self._safe_text(enchantment.get('name'), 'Unknown')} | "
            f"{self._safe_text(enchantment.get('id'), 'N/A')}"
        )
        description = self._safe_text(enchantment.get("description"))

        lines = [header, f"描述: {description}"]

        extra_text = self._safe_text(enchantment.get("extra_card_text"))
        if extra_text:
            lines.append(f"附加: {extra_text}")

        yield event.plain_result("\n".join(lines))

    def _format_event(
        self, event_item: dict[str, Any], event: AstrMessageEvent
    ) -> Generator[Any, None, None]:
        """Format an event item."""
        header = (
            f"{self._safe_text(event_item.get('name'), 'Unknown')} | "
            f"{self._safe_text(event_item.get('id'), 'N/A')}"
        )
        detail = (
            f"类型: {self._safe_text(event_item.get('type'), 'N/A')} | "
            f"章节: {self._safe_text(event_item.get('act'), 'N/A')}"
        )

        description = self._safe_text(event_item.get("description"))
        lines = [header, detail, f"描述: {description}"]

        options = event_item.get("options") or []
        option_lines = []

        for opt in options:
            if isinstance(opt, dict):
                title = self._safe_text(opt.get("title") or opt.get("id"))
                desc = self._safe_text(opt.get("description"))
                if title:
                    option_lines.append(f"- {title}: {desc}" if desc else f"- {title}")

        if option_lines:
            lines.append("选项:\n" + "\n".join(option_lines))

        yield event.plain_result("\n".join(lines))

    def _format_power(
        self, power: dict[str, Any], event: AstrMessageEvent
    ) -> Generator[Any, None, None]:
        """Format a power item."""
        image_url = self.api_client.normalize_image_url(power.get("image_url"))
        if image_url:
            yield event.image_result(image_url)

        header = (
            f"{self._safe_text(power.get('name'), 'Unknown')} | "
            f"{self._safe_text(power.get('id'), 'N/A')}"
        )
        detail = (
            f"类型: {self._safe_text(power.get('type'), 'N/A')} | "
            f"叠加: {self._safe_text(power.get('stack_type'), 'N/A')}"
        )

        description = self._safe_text(power.get("description"))
        lines = [header, detail, f"描述: {description}"]

        yield event.plain_result("\n".join(lines))

    def _format_generic_detailed(
        self, item: dict[str, Any], event: AstrMessageEvent
    ) -> Generator[Any, None, None]:
        """Format a generic detailed item."""
        header = (
            f"{self._safe_text(item.get('name'), 'Unknown')} | "
            f"{self._safe_text(item.get('id'), 'N/A')}"
        )
        description = self._safe_text(item.get("description"))

        lines = [header]
        if description:
            lines.append(f"描述: {description}")

        yield event.plain_result("\n".join(lines))

    def _format_list(
        self, items: list[dict[str, Any]], event: AstrMessageEvent
    ) -> Generator[Any, None, None]:
        """Format a list of items."""
        lines = [
            f"{self._safe_text(item.get('name'), 'Unknown')} | "
            f"{self._safe_text(item.get('id'), 'N/A')}"
            for item in items[:MAX_LIST_ITEMS]
        ]

        if len(items) > MAX_LIST_ITEMS:
            lines.append(f"...and {len(items) - MAX_LIST_ITEMS} more")

        yield event.plain_result("\n".join(lines))

    @staticmethod
    def _sanitize_text(text: str) -> str:
        return re.sub(r"[\x00-\x1f\x7f]", "", text)

    def _safe_text(self, value: Any, default: str = "") -> str:
        if value is None:
            return default
        return self._sanitize_text(str(value))

    @staticmethod
    def format_help() -> str:
        """Format help message."""
        from .constants import ENDPOINTS

        endpoints = sorted(ENDPOINTS.keys())
        endpoints_text = "\n".join(f"- {name}" for name in endpoints)

        return (
            "用法:\n"
            "- /sts2 <endpoint> <关键词>\n"
            "可查询内容:\n" + endpoints_text
        )
