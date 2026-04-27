"""Catalog loader for BTRFS tool metadata."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Tool:
    name: str
    kind: str
    category: str
    repo: str
    docs: str
    interface_hints: list[str]


@dataclass(frozen=True)
class FunctionalArea:
    name: str
    commands: list[str]


@dataclass(frozen=True)
class Catalog:
    tagline: str
    ux_principles: list[str]
    tools: list[Tool]
    functional_areas: list[FunctionalArea]
    navigation: list[dict[str, str]]


DATA_PATH = Path(__file__).parent / "data" / "tools.json"


def _load_raw(path: Path = DATA_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_catalog(path: Path = DATA_PATH) -> Catalog:
    raw = _load_raw(path)
    tools = [Tool(**tool) for tool in raw["tools"]]
    areas = [FunctionalArea(**area) for area in raw["btrfs_progs"]["functional_areas"]]
    return Catalog(
        tagline=raw["vision"]["tagline"],
        ux_principles=raw["vision"]["ux_principles"],
        tools=tools,
        functional_areas=areas,
        navigation=raw["navigation"],
    )


def tools_by_category(catalog: Catalog) -> dict[str, list[Tool]]:
    grouped: dict[str, list[Tool]] = {}
    for tool in catalog.tools:
        grouped.setdefault(tool.category, []).append(tool)
    return dict(sorted(grouped.items(), key=lambda item: item[0].lower()))
