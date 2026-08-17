"""配置读取。默认值在 `configs/default.yaml`，用点号路径覆盖单项。"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_PATH = Path(__file__).resolve().parents[2] / "configs" / "default.yaml"


@dataclass
class Config:
    values: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, path: str | Path | None = None) -> "Config":
        return cls(yaml.safe_load(Path(path or DEFAULT_PATH).read_text(encoding="utf-8")))

    def get(self, dotted: str, default: Any = None) -> Any:
        node: Any = self.values
        for part in dotted.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    def set(self, dotted: str, value: Any) -> "Config":
        parts = dotted.split(".")
        node = self.values
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = value
        return self

    def override(self, assignments: list[str]) -> "Config":
        """`--set figure.k_max=8` 这样的赋值串。"""
        for item in assignments:
            key, _, raw = item.partition("=")
            self.set(key.strip(), yaml.safe_load(raw))
        return self
