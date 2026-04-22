from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol
import base64
import json
import re
import subprocess

from social_ops_kit.config import SocialOpsConfig
from social_ops_kit.platforms.douyin.browser import DouyinBrowserConfig


def _read_varint(buf: bytes, index: int) -> tuple[int, int]:
    shift = 0
    value = 0
    while True:
        current = buf[index]
        index += 1
        value |= (current & 0x7F) << shift
        if not (current & 0x80):
            return value, index
        shift += 7


def _parse_wire_fields(buf: bytes, *, limit_fields: int = 400) -> list[dict[str, Any]]:
    index = 0
    fields: list[dict[str, Any]] = []
    while index < len(buf) and len(fields) < limit_fields:
        try:
            key, index = _read_varint(buf, index)
        except Exception:
            break
        field_no = key >> 3
        wire_type = key & 7
        item: dict[str, Any] = {"field": field_no, "wire": wire_type}
        if wire_type == 0:
            value, index = _read_varint(buf, index)
            item["value"] = value
        elif wire_type == 1:
            item["value"] = int.from_bytes(buf[index : index + 8], "little")
            index += 8
        elif wire_type == 2:
            length, index = _read_varint(buf, index)
            raw = buf[index : index + length]
            index += length
            item["raw"] = raw
        elif wire_type == 5:
            item["value"] = int.from_bytes(buf[index : index + 4], "little")
            index += 4
        else:
            break
        fields.append(item)
    return fields


def _iter_length_delimited_strings(buf: bytes, *, depth: int = 0) -> list[str]:
    if depth > 4:
        return []
    strings: list[str] = []
    try:
        fields = _parse_wire_fields(buf)
    except Exception:
        return []
    for field in fields:
        raw = field.get("raw")
        if not isinstance(raw, (bytes, bytearray)):
            continue
        try:
            text = raw.decode("utf-8")
        except Exception:
            text = ""
        if text and sum(ch.isprintable() for ch in text) / max(1, len(text)) > 0.8:
            strings.append(text)
        if depth < 4 and raw and any(byte < 9 or 13 < byte < 32 for byte in raw[:64]):
            strings.extend(_iter_length_delimited_strings(bytes(raw), depth=depth + 1))
    return strings


def _extract_json_payload(stdout: str) -> dict[str, Any]:
    text = stdout.strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(text[start : end + 1])


_CONVERSATION_ID_RE = re.compile(r"\b\d{18,20}\b")
_SEC_UID_RE = re.compile(r"(?:L|7)MS4w\.LjABAAAA[\w\-]{20,}")
_SKIP_TEXT_RE = re.compile(
    r"^(?:OK|true|false|0|1|2|3|4|5|6|7|8|9|session_|browser_|screen_|timezone_|priority_|"
    r"app_name|deviceId|douyin_pc|douyin_web|web_sdk|webid|fp|is-retry|referer|user_agent|"
    r"group_|conversation_id|floating_bar|valid_templates|bar_id|schema_extra|https?://)"
)
_FALLBACK_PROFILE_DIR = Path("/tmp/douyin-profile-single-stable")


@dataclass(frozen=True)
class DouyinMessageThread:
    thread_id: str
    conversation_short_id: str | None
    user_sec_uid: str | None
    user_name: str
    last_message: str
    unread_count: int
    source: str = "douyin_imapi"

    def as_dict(self) -> dict[str, Any]:
        return {
            "thread_id": self.thread_id,
            "conversation_short_id": self.conversation_short_id,
            "user_sec_uid": self.user_sec_uid,
            "user_name": self.user_name,
            "last_message": self.last_message,
            "unread_count": self.unread_count,
            "source": self.source,
        }


class DouyinImArtifactParser:
    @staticmethod
    def extract_threads(conversation_payload: bytes, info_payload: bytes | None = None) -> list[DouyinMessageThread]:
        conversation_strings = _iter_length_delimited_strings(conversation_payload)
        info_strings = _iter_length_delimited_strings(info_payload or b"")

        conversation_ids = list(dict.fromkeys(_CONVERSATION_ID_RE.findall("\n".join(conversation_strings))))
        sec_uids = list(dict.fromkeys(_SEC_UID_RE.findall("\n".join(conversation_strings))))

        descriptive_texts: list[str] = []
        for text in info_strings:
            normalized = text.strip()
            if len(normalized) < 2:
                continue
            if _SKIP_TEXT_RE.match(normalized):
                continue
            if _CONVERSATION_ID_RE.search(normalized) or _SEC_UID_RE.search(normalized):
                continue
            if normalized.startswith("a:") or normalized.startswith("s:"):
                continue
            descriptive_texts.append(normalized)

        descriptive_texts = list(dict.fromkeys(descriptive_texts))
        threads: list[DouyinMessageThread] = []
        for index, conversation_id in enumerate(conversation_ids):
            threads.append(
                DouyinMessageThread(
                    thread_id=conversation_id,
                    conversation_short_id=conversation_id,
                    user_sec_uid=sec_uids[index] if index < len(sec_uids) else None,
                    user_name=descriptive_texts[index] if index < len(descriptive_texts) else "",
                    last_message=descriptive_texts[index + 1] if index + 1 < len(descriptive_texts) else "",
                    unread_count=0,
                )
            )
        return threads

    @staticmethod
    def extract_threads_from_payload_items(payloads: list[dict[str, Any]]) -> list[DouyinMessageThread]:
        conversation_raw = b""
        info_raw = b""
        for item in payloads:
            url = str(item.get("url") or "")
            body_base64 = str(item.get("bodyBase64") or "")
            if not body_base64:
                continue
            raw = base64.b64decode(body_base64)
            if "/v1/conversation/list" in url:
                conversation_raw = raw
            elif "/v2/conversation/get_info_list" in url:
                info_raw = raw
        if not conversation_raw:
            return []
        return DouyinImArtifactParser.extract_threads(conversation_raw, info_raw or None)


@dataclass(frozen=True)
class DouyinImArtifacts:
    request_path: Path
    response_path: Path

    @classmethod
    def from_workspace(cls, config: SocialOpsConfig) -> "DouyinImArtifacts":
        artifacts_dir = config.workspace / "artifacts"
        return cls(
            request_path=artifacts_dir / "douyin_im_requests.json",
            response_path=artifacts_dir / "douyin_im_base64.json",
        )


class JsonCommandRunner(Protocol):
    def run_json(self, command: list[str], cwd: Path | None = None) -> dict[str, Any]: ...


@dataclass(frozen=True)
class SubprocessJsonRunner:
    timeout_sec: int = 180

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
                "success": False,
                "error": "script_failed",
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }
        try:
            payload = _extract_json_payload(completed.stdout)
        except Exception as exc:
            return {
                "success": False,
                "error": "invalid_json_output",
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "exception": str(exc),
            }
        if "success" not in payload:
            payload["success"] = True
        return payload


class DouyinRealMessageRuntime:
    def __init__(
        self,
        artifacts: DouyinImArtifacts,
        *,
        browser: DouyinBrowserConfig,
        workspace: Path,
        runner: JsonCommandRunner | None = None,
    ) -> None:
        self._artifacts = artifacts
        self._browser = browser
        self._workspace = workspace
        self._runner = runner or SubprocessJsonRunner()

    @classmethod
    def from_config(cls, config: SocialOpsConfig) -> "DouyinRealMessageRuntime":
        return cls(
            DouyinImArtifacts.from_workspace(config),
            browser=DouyinBrowserConfig.from_config(config),
            workspace=config.workspace,
            runner=SubprocessJsonRunner(),
        )

    def _live_script_path(self) -> Path:
        return self._workspace / "scripts" / "douyin_live_messages.js"

    def _resolve_profile_dir(self) -> Path:
        if self._browser.profile_dir.exists():
            return self._browser.profile_dir
        if _FALLBACK_PROFILE_DIR.exists():
            return _FALLBACK_PROFILE_DIR
        return self._browser.profile_dir

    def _run_live_action(self, action: str, **kwargs: Any) -> dict[str, Any]:
        script_path = self._live_script_path()
        if not script_path.exists():
            return {
                "success": False,
                "error": "live_script_missing",
                "script_path": str(script_path),
            }
        command = [
            "node",
            str(script_path),
            "--action",
            action,
            "--profile-dir",
            str(self._resolve_profile_dir()),
            "--url",
            "https://www.douyin.com/user/self",
        ]
        if self._browser.proxy:
            command.extend(["--proxy", self._browser.proxy])
        for key, value in kwargs.items():
            if value is None:
                continue
            command.extend([f"--{key.replace('_', '-')}", str(value)])
        return self._runner.run_json(command, cwd=self._workspace)

    def list_threads_from_artifacts(self) -> list[DouyinMessageThread]:
        if not self._artifacts.response_path.exists():
            return []
        payloads = json.loads(self._artifacts.response_path.read_text(encoding="utf-8"))
        return DouyinImArtifactParser.extract_threads_from_payload_items(payloads)

    def _merge_live_items(self, live_items: list[dict[str, Any]], limit: int | None = None) -> list[DouyinMessageThread]:
        artifact_threads = self.list_threads_from_artifacts()
        merged: list[DouyinMessageThread] = []
        for index, item in enumerate(live_items):
            artifact = artifact_threads[index] if index < len(artifact_threads) else None
            fallback_id = str(item.get("thread_id") or item.get("conversation_short_id") or index)
            merged.append(
                DouyinMessageThread(
                    thread_id=str(artifact.thread_id if artifact else fallback_id),
                    conversation_short_id=(artifact.conversation_short_id if artifact else str(item.get("conversation_short_id") or fallback_id)),
                    user_sec_uid=(artifact.user_sec_uid if artifact else str(item.get("user_sec_uid") or "") or None),
                    user_name=str(item.get("user_name") or (artifact.user_name if artifact else "")),
                    last_message=str(item.get("last_message") or (artifact.last_message if artifact else "")),
                    unread_count=int(item.get("unread_count") or 0),
                    source="douyin_web_im",
                )
            )
        return merged[:limit] if limit is not None else merged

    def list_threads(self, limit: int | None = None) -> tuple[list[DouyinMessageThread], str]:
        live_payload = self._run_live_action("list_threads", limit=limit)
        live_items = list(live_payload.get("items") or []) if live_payload.get("success") else []
        if live_items:
            return self._merge_live_items(live_items, limit=limit), "douyin_web_im"

        live_hits = list(live_payload.get("hits") or []) if live_payload.get("success") else []
        if live_hits:
            parsed_live = DouyinImArtifactParser.extract_threads_from_payload_items(live_hits)
            if parsed_live:
                sliced_live = parsed_live[:limit] if limit is not None else parsed_live
                return sliced_live, "douyin_web_imapi_live"

        fallback_items = self.list_threads_from_artifacts()
        sliced = fallback_items[:limit] if limit is not None else fallback_items
        return sliced, "douyin_imapi_artifacts"

    def reply_message(self, thread_id: str, content: str) -> dict[str, Any]:
        normalized_thread_id = str(thread_id or "").strip()
        normalized_content = str(content or "").strip()
        if not normalized_thread_id:
            return {"success": False, "error": "missing_thread_id", "thread_id": "", "content": normalized_content}
        if not normalized_content:
            return {"success": False, "error": "empty_content", "thread_id": normalized_thread_id, "content": normalized_content}

        target_name = next((item.user_name for item in self.list_threads_from_artifacts() if item.thread_id == normalized_thread_id and item.user_name), "")
        result = self._run_live_action(
            "reply_message",
            thread_id=normalized_thread_id,
            target_name=target_name,
            content=normalized_content,
        )
        return {
            "thread_id": normalized_thread_id,
            "content": normalized_content,
            "target_name": target_name,
            "source": "douyin_web_im",
            **result,
        }
