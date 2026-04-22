from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from social_ops_kit.config import SocialOpsConfig


@dataclass(frozen=True)
class DouyinPathSet:
    root: Path
    login_state_file: Path
    login_meta_file: Path
    login_pid_file: Path
    login_log_dir: Path
    comment_state_file: Path
    music_selected_file: Path
    music_candidates_file: Path
    runs_dir: Path

    @classmethod
    def from_config(cls, config: SocialOpsConfig) -> "DouyinPathSet":
        root = config.douyin_state_dir
        return cls(
            root=root,
            login_state_file=root / "login_state.json",
            login_meta_file=root / "login_meta.json",
            login_pid_file=root / "login_session.pid",
            login_log_dir=root / "logs",
            comment_state_file=root / "comment_reply_state.json",
            music_selected_file=root / "music_selected.json",
            music_candidates_file=root / "music_candidates.json",
            runs_dir=root / "runs",
        )


def ensure_douyin_dirs(paths: DouyinPathSet) -> None:
    paths.root.mkdir(parents=True, exist_ok=True)
    paths.login_log_dir.mkdir(parents=True, exist_ok=True)
    paths.runs_dir.mkdir(parents=True, exist_ok=True)


def read_json_file(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return dict(default or {})
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_file(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
