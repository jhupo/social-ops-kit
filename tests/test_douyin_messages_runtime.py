from __future__ import annotations

import json
from pathlib import Path

from social_ops_kit.config import SocialOpsConfig
from social_ops_kit.platforms.douyin.messages import DouyinImArtifacts, DouyinRealMessageRuntime
from social_ops_kit.platforms.douyin.browser import DouyinBrowserConfig


class FakeRunner:
    def __init__(self, payload: dict):
        self.payload = payload
        self.calls: list[list[str]] = []

    def run_json(self, command: list[str], cwd: Path | None = None) -> dict:
        self.calls.append(command)
        return self.payload


def _artifact_payloads() -> list[dict]:
    return json.loads(Path('/root/social-ops-kit/artifacts/douyin_im_base64.json').read_text(encoding='utf-8'))


def test_douyin_runtime_marks_live_hit_threads_with_live_source(tmp_path) -> None:
    config = SocialOpsConfig.from_env()
    artifacts = DouyinImArtifacts.from_workspace(config)
    artifacts = DouyinImArtifacts(request_path=tmp_path / 'artifacts' / 'douyin_im_requests.json', response_path=tmp_path / 'artifacts' / 'douyin_im_base64.json')
    (tmp_path / 'scripts').mkdir(parents=True, exist_ok=True)
    (tmp_path / 'scripts' / 'douyin_live_messages.js').write_text('// test shim\n', encoding='utf-8')
    runner = FakeRunner({"success": True, "items": [], "hits": _artifact_payloads()})
    runtime = DouyinRealMessageRuntime(
        artifacts,
        browser=runtime_browser(config),
        workspace=tmp_path,
        runner=runner,
    )

    items, source = runtime.list_threads()

    assert source == 'douyin_web_imapi_live'
    assert items
    assert all(item.source == 'douyin_web_imapi_live' for item in items)
    assert runner.calls
    saved = json.loads(artifacts.response_path.read_text(encoding='utf-8'))
    assert saved


def test_douyin_runtime_marks_artifact_threads_with_artifact_source(tmp_path) -> None:
    config = SocialOpsConfig.from_env()
    workspace = tmp_path / 'workspace'
    artifacts_dir = workspace / 'artifacts'
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    (artifacts_dir / 'douyin_im_base64.json').write_text(Path('/root/social-ops-kit/artifacts/douyin_im_base64.json').read_text(encoding='utf-8'), encoding='utf-8')
    runtime = DouyinRealMessageRuntime(
        DouyinImArtifacts.from_workspace(SocialOpsConfig(workspace=workspace, proxy=config.proxy, douyin_state_dir=config.douyin_state_dir, xhs_state_dir=config.xhs_state_dir, artifacts_dir=artifacts_dir, douyin_script_dir=config.douyin_script_dir)),
        browser=runtime_browser(config),
        workspace=tmp_path,
        runner=FakeRunner({"success": False}),
    )

    items, source = runtime.list_threads()

    assert source == 'douyin_imapi_artifacts'
    assert items
    assert all(item.source == 'douyin_imapi_artifacts' for item in items)


def test_douyin_reply_message_uses_artifact_target_name(tmp_path) -> None:
    config = SocialOpsConfig.from_env()
    (tmp_path / 'scripts').mkdir(parents=True, exist_ok=True)
    (tmp_path / 'scripts' / 'douyin_live_messages.js').write_text('// test shim\n', encoding='utf-8')
    runner = FakeRunner({"success": True, "sent": True})
    runtime = DouyinRealMessageRuntime(
        DouyinImArtifacts.from_workspace(config),
        browser=runtime_browser(config),
        workspace=tmp_path,
        runner=runner,
    )

    result = runtime.reply_message('7394389153657422373', '测试回复')

    assert result['success'] is True
    assert result['target_name'] == '福利领取专项1群'
    joined = ' '.join(runner.calls[-1])
    assert '--target-name 福利领取专项1群' in joined


def runtime_browser(config: SocialOpsConfig):
    return DouyinBrowserConfig.from_config(config)
