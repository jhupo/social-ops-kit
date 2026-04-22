from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Capability:
    name: str
    summary: str


class PlatformAdapter(Protocol):
    platform_name: str

    def stable_capabilities(self) -> list[Capability]:
        """Return only the capabilities intended for the stable OSS core."""
