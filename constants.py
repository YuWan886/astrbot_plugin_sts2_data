"""Constants for Slay the Spire 2 data plugin."""

from typing import TypedDict

from typing_extensions import NotRequired


class EndpointConfig(TypedDict):
    """Configuration for an API endpoint."""

    path: str
    id_path: str
    search_param: NotRequired[str | None]


API_BASE = "https://spire-codex.com"

ENDPOINTS: dict[str, EndpointConfig] = {
    "cards": {
        "path": "/api/cards",
        "search_param": "search",
        "id_path": "/api/cards/{id}",
    },
    "characters": {
        "path": "/api/characters",
        "search_param": "search",
        "id_path": "/api/characters/{id}",
    },
    "relics": {
        "path": "/api/relics",
        "search_param": "search",
        "id_path": "/api/relics/{id}",
    },
    "monsters": {
        "path": "/api/monsters",
        "search_param": "search",
        "id_path": "/api/monsters/{id}",
    },
    "potions": {
        "path": "/api/potions",
        "search_param": "search",
        "id_path": "/api/potions/{id}",
    },
    "powers": {
        "path": "/api/powers",
        "search_param": "search",
        "id_path": "/api/powers/{id}",
    },
    "enchantments": {
        "path": "/api/enchantments",
        "search_param": "search",
        "id_path": "/api/enchantments/{id}",
    },
    "encounters": {
        "path": "/api/encounters",
        "search_param": "search",
        "id_path": "/api/encounters/{id}",
    },
    "events": {
        "path": "/api/events",
        "search_param": "search",
        "id_path": "/api/events/{id}",
    },
    "epochs": {
        "path": "/api/epochs",
        "search_param": "search",
        "id_path": "/api/epochs/{id}",
    },
    "keywords": {
        "path": "/api/keywords",
        "search_param": None,
        "id_path": "/api/keywords/{id}",
    },
    "orbs": {"path": "/api/orbs", "search_param": None, "id_path": "/api/orbs/{id}"},
    "afflictions": {
        "path": "/api/afflictions",
        "search_param": None,
        "id_path": "/api/afflictions/{id}",
    },
    "modifiers": {
        "path": "/api/modifiers",
        "search_param": None,
        "id_path": "/api/modifiers/{id}",
    },
    "achievements": {
        "path": "/api/achievements",
        "search_param": None,
        "id_path": "/api/achievements/{id}",
    },
    "acts": {"path": "/api/acts", "search_param": None, "id_path": "/api/acts/{id}"},
    "ascensions": {
        "path": "/api/ascensions",
        "search_param": None,
        "id_path": "/api/ascensions/{id}",
    },
    "stories": {
        "path": "/api/stories",
        "search_param": None,
        "id_path": "/api/stories/{id}",
    },
    "intents": {
        "path": "/api/intents",
        "search_param": None,
        "id_path": "/api/intents/{id}",
    },
}

SINGULAR_ALIASES = {
    "card": "cards",
    "character": "characters",
    "relic": "relics",
    "monster": "monsters",
    "potion": "potions",
    "power": "powers",
    "enchantment": "enchantments",
    "encounter": "encounters",
    "event": "events",
    "epoch": "epochs",
    "keyword": "keywords",
    "orb": "orbs",
    "affliction": "afflictions",
    "modifier": "modifiers",
    "achievement": "achievements",
    "act": "acts",
    "ascension": "ascensions",
    "story": "stories",
    "intent": "intents",
}

# Supported endpoints that return detailed information with images
DETAILED_ENDPOINTS = {
    "cards",
    "relics",
    "monsters",
    "potions",
    "enchantments",
    "events",
    "powers",
}

# Default language for API requests
DEFAULT_LANG = "zhs"

# Request timeout in seconds
REQUEST_TIMEOUT = 10

# Maximum number of items to show in list results
MAX_LIST_ITEMS = 5
