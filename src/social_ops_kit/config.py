from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


def _env(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value not in (None, "") else default


@dataclass(frozen=True)
class SocialOpsConfig:
    workspace: Path
    proxy: str | None
    douyin_state_dir: Path
    xhs_state_dir: Path
    artifacts_dir: Path
    douyin_script_dir: Path

    @classmethod
    def from_env(cls) -> "SocialOpsConfig":
        workspace = Path(_env("SOCIAL_OPS_WORKSPACE", "/root/social-ops-kit")).expanduser()
        proxy = os.getenv("SOCIAL_OPS_PROXY") or None
        douyin_state_dir = Path(
            _env("SOCIAL_OPS_DOUYIN_STATE_DIR", str(workspace / "state" / "douyin"))
        ).expanduser()
        xhs_state_dir = Path(_env("SOCIAL_OPS_XHS_STATE_DIR", str(workspace / "state" / "xhs"))).expanduser()
        artifacts_dir = Path(
            _env("SOCIAL_OPS_ARTIFACTS_DIR", str(workspace / "artifacts"))
        ).expanduser()
        douyin_script_dir = Path(
            _env("SOCIAL_OPS_DOUYIN_SCRIPT_DIR", "/root/.hermes/scripts/douyin")
        ).expanduser()
        return cls(
            workspace=workspace,
            proxy=proxy,
            douyin_state_dir=douyin_state_dir,
            xhs_state_dir=xhs_state_dir,
            artifacts_dir=artifacts_dir,
            douyin_script_dir=douyin_script_dir,
        )

    def doctor(self) -> dict[str, str | bool]:
        return {
            "workspace_exists": self.workspace.exists(),
            "douyin_state_dir": str(self.douyin_state_dir),
            "xhs_state_dir": str(self.xhs_state_dir),
            "artifacts_dir": str(self.artifacts_dir),
            "douyin_script_dir": str(self.douyin_script_dir),
            "proxy": self.proxy or "",
        }
