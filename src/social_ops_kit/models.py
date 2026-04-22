from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Platform(str, Enum):
    DOUYIN = "douyin"
    XHS = "xhs"


class ToolLifecycle(str, Enum):
    STABLE = "stable"
    EXPERIMENTAL = "experimental"
    INTERNAL = "internal"


class ToolMaturity(str, Enum):
    DECLARED = "declared"
    FOUNDATION = "foundation"
    RUNNABLE = "runnable"
    EXTERNAL_DEPENDENT = "external_dependent"


@dataclass(frozen=True)
class ToolParameter:
    name: str
    type_name: str
    description: str
    required: bool = False


@dataclass(frozen=True)
class ToolSpec:
    name: str
    platform: Platform
    summary: str
    parameters: tuple[ToolParameter, ...] = ()
    lifecycle: ToolLifecycle = ToolLifecycle.STABLE
    tags: tuple[str, ...] = ()
    implemented: bool = False
    maturity: ToolMaturity = ToolMaturity.DECLARED

    def as_dict(self) -> dict[str, Any]:
        implementation_status = "implemented" if self.implemented else "declared_not_implemented"
        return {
            "name": self.name,
            "platform": self.platform.value,
            "summary": self.summary,
            "lifecycle": self.lifecycle.value,
            "tags": list(self.tags),
            "implemented": self.implemented,
            "maturity": self.maturity.value,
            "implementation_status": implementation_status,
            "parameters": [
                {
                    "name": param.name,
                    "type": param.type_name,
                    "description": param.description,
                    "required": param.required,
                }
                for param in self.parameters
            ],
        }


@dataclass(frozen=True)
class SkillSpec:
    name: str
    platform: Platform | None
    summary: str
    path: str
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class LegacyDecision:
    path: str
    decision: str
    reason: str
    replacement: str | None = None


@dataclass
class ProjectSnapshot:
    tools: list[ToolSpec] = field(default_factory=list)
    skills: list[SkillSpec] = field(default_factory=list)
    legacy: list[LegacyDecision] = field(default_factory=list)
