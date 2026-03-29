"""Data models for Slay the Spire 2 API responses."""

from typing import Any, TypedDict


class BaseItem(TypedDict, total=False):
    """Base item structure for all API responses."""

    id: str
    name: str
    description: str | None
    image_url: str | None


class Card(BaseItem, total=False):
    """Card data structure."""

    cost: str | None
    type: str | None
    rarity: str | None
    beta_image_url: str | None
    upgrade: dict[str, Any] | None


class Relic(BaseItem, total=False):
    """Relic data structure."""

    rarity: str | None
    pool: str | None
    flavor: str | None


class Monster(BaseItem, total=False):
    """Monster data structure."""

    type: str | None
    min_hp: int | None
    max_hp: int | None
    min_hp_ascension: int | None
    max_hp_ascension: int | None
    beta_image_url: str | None
    moves: list[dict[str, Any]] | None


class Potion(BaseItem, total=False):
    """Potion data structure."""

    rarity: str | None
    pool: str | None


class Enchantment(BaseItem, total=False):
    """Enchantment data structure."""

    extra_card_text: str | None


class Event(BaseItem, total=False):
    """Event data structure."""

    type: str | None
    act: str | None
    options: list[dict[str, Any]] | None


class Power(BaseItem, total=False):
    """Power data structure."""

    type: str | None
    stack_type: str | None


# Type aliases for convenience
ItemData = dict[str, Any]
ItemList = list[ItemData]

# Mapping from endpoint names to model types
ENDPOINT_MODELS = {
    "cards": Card,
    "relics": Relic,
    "monsters": Monster,
    "potions": Potion,
    "enchantments": Enchantment,
    "events": Event,
    "powers": Power,
}
