from __future__ import annotations

from dataclasses import dataclass
import os
import signal
import subprocess
import time
from pathlib import Path
from typing import Any, Protocol

from social_ops_kit.config import SocialOpsConfig
from social_ops_kit.platforms.douyin.browser import DouyinBrowserConfig
from social_ops_kit.platforms.douyin.state import (
    DouyinPathSet,
    ensure_douyin_dirs,
    read_json_file,
    write_json_file,
)


class ProcessLike(Protocol):
    pid: int


class ProcessStarter(Protocol):
    def start(self, command: list[str], cwd: Path, log_path: Path) -> ProcessLike: ...


@dataclass(frozen=True)
class SubprocessStarter:
    def start(self, command: list[str], cwd: Path, log_path: Path) -> ProcessLike:
        with log_path.open("ab") as log_file:
            return subprocess.Popen(
                command,
                cwd=str(cwd),
                stdout=log_file,
                stderr=log_file,
                start_new_session=True,
            )


@dataclass(frozen=True)
class DouyinLoginRuntime:
    paths: DouyinPathSet
    browser: DouyinBrowserConfig
    starter: ProcessStarter

    @classmethod
    def from_config(cls, config: SocialOpsConfig) -> "DouyinLoginRuntime":
        paths = DouyinPathSet.from_config(config)
        ensure_douyin_dirs(paths)
        return cls(paths=paths, browser=DouyinBrowserConfig.from_config(config), starter=SubprocessStarter())

    def get_login_state(self) -> dict[str, Any]:
        return read_json_file(self.paths.login_state_file, default={"status": "unknown"})

    def get_login_meta(self) -> dict[str, Any]:
        return read_json_file(self.paths.login_meta_file, default={})

    def set_login_state(self, payload: dict[str, Any]) -> None:
        write_json_file(self.paths.login_state_file, payload)

    def set_login_meta(self, payload: dict[str, Any]) -> None:
        write_json_file(self.paths.login_meta_file, payload)

    def is_pid_alive(self, pid: int | None) -> bool:
        if not isinstance(pid, int) or pid <= 0:
            return False
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

    def login_status(self) -> dict[str, Any]:
        meta = self.get_login_meta()
        state = self.get_login_state()
        pid = meta.get("pid")
        running = self.is_pid_alive(pid)
        payload: dict[str, Any] = {
            "meta": meta,
            "state": state,
            "running": running,
            "login_state_path": str(self.paths.login_state_file),
            "login_meta_path": str(self.paths.login_meta_file),
        }
        qr_path = state.get("qr_path") or state.get("qrPath")
        if qr_path and Path(qr_path).exists():
            payload["qr_path"] = qr_path
        screenshot_path = state.get("screenshot_path") or state.get("screenshotPath")
        if screenshot_path and Path(screenshot_path).exists():
            payload["screenshot_path"] = screenshot_path
        return payload

    def start_login(self, script_name: str = "douyin_single_session.js") -> dict[str, Any]:
        current = self.login_status()
        current_pid = current.get("meta", {}).get("pid")
        if self.is_pid_alive(current_pid):
            current["message"] = "login session already running"
            return current
        script_path = self.browser.script_dir / script_name
        if not script_path.exists():
            raise FileNotFoundError(f"Douyin login script not found: {script_path}")
        started_at = int(time.time())
        log_path = self.paths.login_log_dir / f"login_session_{started_at}.log"
        proc = self.starter.start(["node", str(script_path)], self.browser.script_dir, log_path)
        self.paths.login_pid_file.write_text(str(proc.pid), encoding="utf-8")
        self.set_login_meta(
            {
                "pid": proc.pid,
                "started_at": started_at,
                "log_path": str(log_path),
                "script": script_name,
            }
        )
        payload = self.login_status()
        payload["message"] = "login session started"
        return payload

    def stop_login(self) -> dict[str, Any]:
        meta = self.get_login_meta()
        pid = meta.get("pid")
        stopped = False
        if self.is_pid_alive(pid):
            os.killpg(pid, signal.SIGTERM)
            stopped = True
        payload = self.login_status()
        payload["stopped"] = stopped
        return payload
