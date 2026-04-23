from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol
import json
import sqlite3
import subprocess
import tempfile

from social_ops_kit.config import SocialOpsConfig


_XHS_DB_CANDIDATES = (
    Path('/root/.hermes/state/xhs-mcp/data.db'),
    Path('/root/.xhs-mcp/data.db'),
)
_XHS_MCP_PACKAGE = Path('/root/.npm/_npx/e3e9a1d1813bae49/node_modules/@sillyl12324/xhs-mcp')


@dataclass(frozen=True)
class XhsLiveAccount:
    account_id: str
    name: str
    proxy: str | None
    state: dict[str, Any]


class JsonCommandRunner(Protocol):
    def run_json(self, command: list[str], cwd: Path | None = None) -> dict[str, Any]: ...


@dataclass(frozen=True)
class SubprocessJsonRunner:
    timeout_sec: int = 240

    def run_json(self, command: list[str], cwd: Path | None = None) -> dict[str, Any]:
        completed = subprocess.run(
            command,
            cwd=str(cwd) if cwd is not None else None,
            capture_output=True,
            text=True,
            timeout=self.timeout_sec,
            check=False,
        )
        if completed.returncode != 0:
            return {
                'success': False,
                'error': 'script_failed',
                'returncode': completed.returncode,
                'stdout': completed.stdout,
                'stderr': completed.stderr,
            }
        text = completed.stdout.strip()
        if not text:
            return {'success': False, 'error': 'empty_output'}
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find('{')
            end = text.rfind('}')
            if start == -1 or end == -1 or end <= start:
                return {'success': False, 'error': 'invalid_json_output', 'stdout': completed.stdout, 'stderr': completed.stderr}
            return json.loads(text[start:end + 1])


@dataclass(frozen=True)
class XhsLiveRuntime:
    workspace: Path
    db_path: Path
    package_path: Path
    runner: JsonCommandRunner

    @classmethod
    def from_config(cls, config: SocialOpsConfig) -> 'XhsLiveRuntime':
        db_path = next((path for path in _XHS_DB_CANDIDATES if path.exists()), _XHS_DB_CANDIDATES[0])
        return cls(
            workspace=config.workspace,
            db_path=db_path,
            package_path=_XHS_MCP_PACKAGE,
            runner=SubprocessJsonRunner(),
        )

    def _script_path(self) -> Path:
        return self.workspace / 'scripts' / 'xhs_live_actions.mjs'

    def _resolve_account(self, account: str | None = None) -> XhsLiveAccount:
        if not self.db_path.exists():
            raise FileNotFoundError(f'XHS MCP database not found: {self.db_path}')
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            if account:
                row = conn.execute(
                    'SELECT id, name, proxy, state FROM accounts WHERE status = ? AND (id = ? OR name = ?)',
                    ('active', account, account),
                ).fetchone()
                if row is None:
                    raise ValueError(f'XHS account not found: {account}')
            else:
                rows = conn.execute('SELECT id, name, proxy, state FROM accounts WHERE status = ? ORDER BY created_at DESC', ('active',)).fetchall()
                if not rows:
                    raise ValueError('No active XHS account found')
                if len(rows) > 1:
                    names = ', '.join(str(row['name']) for row in rows)
                    raise ValueError(f'Multiple active XHS accounts found; specify one: {names}')
                row = rows[0]
            state = json.loads(row['state']) if row['state'] else {}
            return XhsLiveAccount(
                account_id=str(row['id']),
                name=str(row['name']),
                proxy=str(row['proxy']) if row['proxy'] else None,
                state=state,
            )
        finally:
            conn.close()

    def _run_live_action(self, action: str, *, account: str | None = None, **kwargs: Any) -> dict[str, Any]:
        script_path = self._script_path()
        if not script_path.exists():
            return {'success': False, 'error': 'live_script_missing', 'script_path': str(script_path)}
        if not self.package_path.exists():
            return {'success': False, 'error': 'xhs_mcp_package_missing', 'package_path': str(self.package_path)}
        try:
            resolved = self._resolve_account(account)
        except Exception as exc:
            return {'success': False, 'error': str(exc)}

        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8') as handle:
            json.dump(resolved.state, handle, ensure_ascii=False)
            state_path = Path(handle.name)

        command = [
            'node',
            str(script_path),
            '--action', action,
            '--state-path', str(state_path),
            '--account-id', resolved.account_id,
            '--account-name', resolved.name,
            '--package-path', str(self.package_path),
        ]
        if resolved.proxy:
            command.extend(['--proxy', resolved.proxy])
        for key, value in kwargs.items():
            if value is None:
                continue
            command.extend([f'--{key.replace("_", "-")}', str(value)])
        result = self.runner.run_json(command, cwd=self.workspace)
        result.setdefault('account', resolved.name)
        return result

    def post_comment(self, note_id: str, xsec_token: str, content: str, account: str | None = None) -> dict[str, Any]:
        return self._run_live_action(
            'post_comment',
            account=account,
            note_id=str(note_id or '').strip(),
            xsec_token=str(xsec_token or '').strip(),
            content=str(content or '').strip(),
        )

    def reply_comment(self, note_id: str, xsec_token: str, comment_id: str, content: str, account: str | None = None) -> dict[str, Any]:
        return self._run_live_action(
            'reply_comment',
            account=account,
            note_id=str(note_id or '').strip(),
            xsec_token=str(xsec_token or '').strip(),
            comment_id=str(comment_id or '').strip(),
            content=str(content or '').strip(),
        )

    def get_notifications(self, type_: str = 'all', limit: int | None = None, account: str | None = None) -> dict[str, Any]:
        return self._run_live_action(
            'get_notifications',
            account=account,
            type=type_ or 'all',
            limit=limit if limit is not None else 20,
        )
