from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MessageThread:
    thread_id: str
    user_name: str
    last_message: str
    unread_count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "thread_id": self.thread_id,
            "user_name": self.user_name,
            "last_message": self.last_message,
            "unread_count": self.unread_count,
        }


@dataclass(frozen=True)
class MessageReply:
    thread_id: str
    content: str
    success: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "thread_id": self.thread_id,
            "content": self.content,
            "success": self.success,
        }


class MessageRuntime:
    def list_threads(self, threads: list[dict[str, Any]], limit: int | None = None) -> list[MessageThread]:
        parsed = [
            MessageThread(
                thread_id=str(item.get("thread_id") or item.get("id") or ""),
                user_name=str(item.get("user_name") or item.get("user") or ""),
                last_message=str(item.get("last_message") or item.get("content") or ""),
                unread_count=int(item.get("unread_count") or 0),
            )
            for item in threads
        ]
        return parsed[:limit] if limit is not None else parsed

    def reply_message(self, thread_id: str, content: str) -> MessageReply:
        return MessageReply(thread_id=str(thread_id or ""), content=str(content or ""), success=bool(str(content or "").strip()))
