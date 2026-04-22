from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from social_ops_kit.config import SocialOpsConfig


@dataclass(frozen=True)
class XhsPathSet:
    root: Path
    drafts_dir: Path
    profile_dir: Path
    cache_dir: Path

    @classmethod
    def from_config(cls, config: SocialOpsConfig) -> "XhsPathSet":
        root = config.xhs_state_dir
        return cls(
            root=root,
            drafts_dir=root / "drafts",
            profile_dir=root / "profile",
            cache_dir=root / "cache",
        )


@dataclass(frozen=True)
class XhsBrowserSessionConfig:
    headless: bool = True
    locale: str = "zh-CN"
    timezone_id: str = "Asia/Shanghai"
    viewport_width: int = 1920
    viewport_height: int = 1080
    proxy: str | None = None
    launch_args: tuple[str, ...] = field(
        default_factory=lambda: (
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-blink-features=AutomationControlled",
        )
    )

    @classmethod
    def from_config(cls, config: SocialOpsConfig) -> "XhsBrowserSessionConfig":
        return cls(proxy=config.proxy)
