"""Formatters for converting API data to user-friendly messages."""

from collections.abc import Generator
import re
from typing import Any

from astrbot.api.event import AstrMessageEvent

from .api_client import STS2APIClient
from .constants import DETAILED_ENDPOINTS, ENDPOINTS


class STS2Formatter:
    """Formatter for Slay the Spire 2 data responses."""

    def __init__(self, api_client: STS2APIClient):
        """Initialize the formatter.

        Args:
            api_client: API client instance for URL normalization.
        """
        self.api_client = api_client

    def _plain_result(self, event: AstrMessageEvent, text: str) -> Any:
        """Create a plain text result without text-to-image conversion."""
        return event.plain_result(text).use_t2i(False)

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
            yield self._plain_result(event, "No matching records found.")
            return

        if endpoint in DETAILED_ENDPOINTS:
            if len(data) > 1:
                yield from self._format_list(data, event)
                yield self._plain_result(event, 
                    f"共 {len(data)} 条结果，请补充更精确的关键词查看详情。"
                )
                return
            if not isinstance(data[0], dict):
                yield self._plain_result(event, "数据格式异常，请稍后重试。")
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

        header = self._build_header(card)
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

        yield self._plain_result(event, "\n".join(lines))

    def _format_relic(
        self, relic: dict[str, Any], event: AstrMessageEvent
    ) -> Generator[Any, None, None]:
        """Format a relic item."""
        image_url = self.api_client.normalize_image_url(relic.get("image_url"))
        if image_url:
            yield event.image_result(image_url)

        header = self._build_header(relic)
        detail = (
            f"稀有度: {self._safe_text(relic.get('rarity'), 'N/A')} | "
            f"池: {self._safe_text(relic.get('pool'), 'N/A')}"
        )

        description = self._safe_text(relic.get("description"))
        lines = [header, detail, f"描述: {description}"]

        flavor = self._safe_text(relic.get("flavor"))
        if flavor:
            lines.append(f"背景: {flavor}")

        yield self._plain_result(event, "\n".join(lines))

    def _format_monster(
        self, monster: dict[str, Any], event: AstrMessageEvent
    ) -> Generator[Any, None, None]:
        """Format a monster item."""
        image_url = monster.get("image_url") or monster.get("beta_image_url")
        normalized_url = self.api_client.normalize_image_url(image_url)

        if normalized_url:
            yield event.image_result(normalized_url)

        header = self._build_header(monster)

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

        yield self._plain_result(event, "\n".join(lines))

    def _format_potion(
        self, potion: dict[str, Any], event: AstrMessageEvent
    ) -> Generator[Any, None, None]:
        """Format a potion item."""
        image_url = self.api_client.normalize_image_url(potion.get("image_url"))
        if image_url:
            yield event.image_result(image_url)

        header = self._build_header(potion)
        detail = (
            f"稀有度: {self._safe_text(potion.get('rarity'), 'N/A')} | "
            f"池: {self._safe_text(potion.get('pool'), 'N/A')}"
        )

        description = self._safe_text(potion.get("description"))
        lines = [header, detail, f"描述: {description}"]

        yield self._plain_result(event, "\n".join(lines))

    def _format_enchantment(
        self, enchantment: dict[str, Any], event: AstrMessageEvent
    ) -> Generator[Any, None, None]:
        """Format an enchantment item."""
        image_url = self.api_client.normalize_image_url(enchantment.get("image_url"))
        if image_url:
            yield event.image_result(image_url)

        header = self._build_header(enchantment)
        description = self._safe_text(enchantment.get("description"))

        lines = [header, f"描述: {description}"]

        extra_text = self._safe_text(enchantment.get("extra_card_text"))
        if extra_text:
            lines.append(f"附加: {extra_text}")

        yield self._plain_result(event, "\n".join(lines))

    def _format_event(
        self, event_item: dict[str, Any], event: AstrMessageEvent
    ) -> Generator[Any, None, None]:
        """Format an event item."""
        image_url = self.api_client.normalize_image_url(event_item.get("image_url"))
        if image_url:
            yield event.image_result(image_url)

        header = self._build_header(event_item)
        detail = (
            f"类型: {self._safe_text(event_item.get('type'), 'N/A')} | "
            f"章节: {self._safe_text(event_item.get('act'), 'N/A')}"
        )

        description = self._safe_text(event_item.get("description"))
        lines = [header, detail, f"描述: {description}"]

        epithet = self._safe_text(event_item.get("epithet"))
        if epithet:
            lines.append(f"称号: {epithet}")

        relics = event_item.get("relics") or []
        if isinstance(relics, list):
            relic_text = ", ".join(
                self._safe_text(relic) for relic in relics if relic is not None
            )
            if relic_text:
                lines.append(f"遗物: {relic_text}")

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

        pages = event_item.get("pages") or []
        page_lines = []
        for page in pages:
            if not isinstance(page, dict):
                continue
            page_title = self._safe_text(page.get("id"))
            page_desc = self._safe_text(page.get("description"))
            page_header = page_title or "页面"
            page_lines.append(f"{page_header}: {page_desc}" if page_desc else page_header)
            page_options = page.get("options") or []
            page_option_lines = []
            for opt in page_options:
                if isinstance(opt, dict):
                    title = self._safe_text(opt.get("title") or opt.get("id"))
                    desc = self._safe_text(opt.get("description"))
                    if title:
                        page_option_lines.append(
                            f"  - {title}: {desc}" if desc else f"  - {title}"
                        )
            if page_option_lines:
                page_lines.extend(page_option_lines)

        if page_lines:
            lines.append("流程:\n" + "\n".join(page_lines))

        dialogue = event_item.get("dialogue") or {}
        dialogue_lines = []
        if isinstance(dialogue, dict):
            for key, entries in dialogue.items():
                if not isinstance(entries, list):
                    continue
                for entry in entries:
                    if not isinstance(entry, dict):
                        continue
                    order = self._safe_text(entry.get("order"))
                    speaker = self._safe_text(entry.get("speaker"))
                    text = self._safe_text(entry.get("text"))
                    if not (order or speaker or text):
                        continue
                    parts = [part for part in [order, speaker] if part]
                    prefix = " ".join(parts).strip()
                    if prefix:
                        dialogue_lines.append(f"- {prefix}: {text}" if text else f"- {prefix}")
                    else:
                        dialogue_lines.append(f"- {text}")

        if dialogue_lines:
            lines.append("对话:\n" + "\n".join(dialogue_lines))

        yield self._plain_result(event, "\n".join(lines))

    def _format_power(
        self, power: dict[str, Any], event: AstrMessageEvent
    ) -> Generator[Any, None, None]:
        """Format a power item."""
        image_url = self.api_client.normalize_image_url(power.get("image_url"))
        if image_url:
            yield event.image_result(image_url)

        header = self._build_header(power)
        detail = (
            f"类型: {self._safe_text(power.get('type'), 'N/A')} | "
            f"叠加: {self._safe_text(power.get('stack_type'), 'N/A')}"
        )

        description = self._safe_text(power.get("description"))
        lines = [header, detail, f"描述: {description}"]

        yield self._plain_result(event, "\n".join(lines))

    def _format_generic_detailed(
        self, item: dict[str, Any], event: AstrMessageEvent
    ) -> Generator[Any, None, None]:
        """Format a generic detailed item."""
        header = self._build_header(item)
        description = self._safe_text(item.get("description"))

        lines = [header]
        if description:
            lines.append(f"描述: {description}")

        yield self._plain_result(event, "\n".join(lines))

    def _format_list(
        self, items: list[dict[str, Any]], event: AstrMessageEvent
    ) -> Generator[Any, None, None]:
        """Format a list of items."""
        lines: list[str] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            lines.append(self._build_header(item))

        if not lines:
            yield self._plain_result(event, "数据格式异常，请稍后重试。")
            return

        yield self._plain_result(event, "\n".join(lines))

    def _build_header(self, item: dict[str, Any]) -> str:
        """Build a basic header with name and id."""
        return (
            f"{self._safe_text(item.get('name'), 'Unknown')} | "
            f"{self._safe_text(item.get('id'), 'N/A')}"
        )

    @staticmethod
    def _sanitize_text(text: str) -> str:
        """Remove control characters from text."""
        return re.sub(r"[\x00-\x1f\x7f]", "", text)

    def _safe_text(self, value: Any, default: str = "") -> str:
        """Convert value to sanitized string with a default fallback."""
        if value is None:
            return default
        return self._sanitize_text(str(value))

    @staticmethod
    def format_help() -> str:
        """Format help message."""
        endpoints = sorted(ENDPOINTS.keys())
        endpoints_text = "\n".join(f"- {name}" for name in endpoints)

        return (
            "用法:\n"
            "- /sts2 <endpoint> <关键词>\n"
            "可查询内容:\n" + endpoints_text
        )
