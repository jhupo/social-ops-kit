from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from social_ops_kit.config import SocialOpsConfig
from social_ops_kit.platforms.xhs.live import XhsLiveRuntime


class FakeRunner:
    def __init__(self, payload: dict):
        self.payload = payload
        self.calls: list[list[str]] = []

    def run_json(self, command: list[str], cwd: Path | None = None) -> dict:
        self.calls.append(command)
        return self.payload


def make_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.execute(
        'CREATE TABLE accounts (id TEXT PRIMARY KEY, name TEXT UNIQUE NOT NULL, proxy TEXT, state JSON, status TEXT, created_at TEXT, updated_at TEXT)'
    )
    state = json.dumps({"cookies": [], "origins": []}, ensure_ascii=False)
    conn.execute(
        'INSERT INTO accounts (id, name, proxy, state, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
        ('acc-1', 'Hermes', None, state, 'active', 'now', 'now'),
    )
    conn.commit()
    conn.close()


def test_xhs_live_runtime_reads_single_active_account_and_posts_comment(tmp_path) -> None:
    db_path = tmp_path / 'xhs.db'
    make_db(db_path)
    (tmp_path / 'scripts').mkdir(parents=True, exist_ok=True)
    (tmp_path / 'scripts' / 'xhs_live_actions.mjs').write_text('// test shim\n', encoding='utf-8')
    runner = FakeRunner({"success": True, "result": {"success": True}})
    runtime = XhsLiveRuntime(workspace=tmp_path, db_path=db_path, package_path=tmp_path, runner=runner)

    result = runtime.post_comment('note-1', 'token-1', '你好呀')

    assert result['success'] is True
    assert result['account'] == 'Hermes'
    joined = ' '.join(runner.calls[-1])
    assert '--note-id note-1' in joined
    assert '--content 你好呀' in joined


def test_xhs_live_runtime_reports_missing_account(tmp_path) -> None:
    db_path = tmp_path / 'xhs.db'
    make_db(db_path)
    (tmp_path / 'scripts').mkdir(parents=True, exist_ok=True)
    (tmp_path / 'scripts' / 'xhs_live_actions.mjs').write_text('// test shim\n', encoding='utf-8')
    runtime = XhsLiveRuntime(workspace=tmp_path, db_path=db_path, package_path=tmp_path, runner=FakeRunner({"success": True}))

    result = runtime.reply_comment('note-1', 'token-1', 'comment-1', '谢谢', account='missing')

    assert result['success'] is False
    assert 'not found' in result['error']
