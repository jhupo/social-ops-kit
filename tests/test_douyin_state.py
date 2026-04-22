from social_ops_kit.config import SocialOpsConfig
from social_ops_kit.platforms.douyin.browser import DouyinBrowserConfig
from social_ops_kit.platforms.douyin.login import DouyinLoginRuntime
from social_ops_kit.platforms.douyin.state import DouyinPathSet, read_json_file


class FakeProcess:
    def __init__(self, pid: int) -> None:
        self.pid = pid


class FakeStarter:
    def __init__(self, pid: int = 4321) -> None:
        self.pid = pid
        self.calls = []

    def start(self, command, cwd, log_path):
        self.calls.append({"command": command, "cwd": cwd, "log_path": log_path})
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text("started\n", encoding="utf-8")
        return FakeProcess(self.pid)


class FakeLoginRuntime(DouyinLoginRuntime):
    alive_pids: set[int] = set()

    def is_pid_alive(self, pid):
        return isinstance(pid, int) and pid in self.alive_pids


def test_douyin_path_set_defaults() -> None:
    config = SocialOpsConfig.from_env()
    paths = DouyinPathSet.from_config(config)
    assert str(paths.login_state_file).endswith("state/douyin/login_state.json")
    assert str(paths.login_pid_file).endswith("state/douyin/login_session.pid")
    assert str(paths.music_selected_file).endswith("state/douyin/music_selected.json")


def test_douyin_login_runtime_roundtrip() -> None:
    runtime = DouyinLoginRuntime.from_config(SocialOpsConfig.from_env())
    runtime.set_login_state({"status": "ready"})
    assert runtime.get_login_state()["status"] == "ready"
    assert read_json_file(runtime.paths.login_state_file)["status"] == "ready"


def test_douyin_browser_config_uses_script_dir() -> None:
    browser = DouyinBrowserConfig.from_config(SocialOpsConfig.from_env())
    assert str(browser.script_dir).endswith("scripts/douyin")
    assert browser.proxy in {None, ""} or isinstance(browser.proxy, str)


def test_start_login_writes_meta_and_pid() -> None:
    config = SocialOpsConfig.from_env()
    paths = DouyinPathSet.from_config(config)
    runtime = FakeLoginRuntime(paths=paths, browser=DouyinBrowserConfig.from_config(config), starter=FakeStarter())
    runtime.browser.script_dir.mkdir(parents=True, exist_ok=True)
    (runtime.browser.script_dir / "douyin_single_session.js").write_text("// mock\n", encoding="utf-8")
    result = runtime.start_login()
    assert result["message"] == "login session started"
    assert runtime.get_login_meta()["pid"] == 4321
    assert runtime.paths.login_pid_file.exists()


def test_login_status_reports_running_when_pid_alive() -> None:
    config = SocialOpsConfig.from_env()
    paths = DouyinPathSet.from_config(config)
    runtime = FakeLoginRuntime(paths=paths, browser=DouyinBrowserConfig.from_config(config), starter=FakeStarter())
    runtime.alive_pids = {9999}
    runtime.set_login_meta({"pid": 9999})
    status = runtime.login_status()
    assert status["running"] is True
