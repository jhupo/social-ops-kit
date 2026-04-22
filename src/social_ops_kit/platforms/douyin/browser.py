from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from textwrap import dedent

from social_ops_kit.config import SocialOpsConfig


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
DEFAULT_INIT_SCRIPT = dedent(
    """
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    window.chrome = window.chrome || { runtime: {} };
    """
).strip()


@dataclass(frozen=True)
class DouyinBrowserConfig:
    profile_dir: Path
    script_dir: Path
    headless: bool = False
    proxy: str | None = None
    locale: str = "zh-CN"
    timezone_id: str = "Asia/Shanghai"
    user_agent: str = DEFAULT_USER_AGENT
    init_script: str = DEFAULT_INIT_SCRIPT
    launch_args: tuple[str, ...] = field(
        default_factory=lambda: (
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-blink-features=AutomationControlled",
        )
    )

    @classmethod
    def from_config(cls, config: SocialOpsConfig) -> "DouyinBrowserConfig":
        return cls(
            profile_dir=config.douyin_state_dir / "profile",
            script_dir=config.douyin_script_dir,
            proxy=config.proxy,
        )
