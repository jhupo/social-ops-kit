from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class XhsNotification:
    notification_id: str
    type: str
    user_name: str
    content: str
    note_id: str
    created_at: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.notification_id,
            "type": self.type,
            "user_name": self.user_name,
            "content": self.content,
            "note_id": self.note_id,
            "created_at": self.created_at,
        }


class XhsNotificationRuntime:
    def parse_notifications(
        self, notifications: list[dict[str, Any]], limit: int | None = None
    ) -> list[XhsNotification]:
        parsed = [
            XhsNotification(
                notification_id=str(item.get("id") or ""),
                type=str(item.get("type") or "unknown"),
                user_name=str(item.get("user_name") or item.get("user") or ""),
                content=str(item.get("content") or ""),
                note_id=str(item.get("note_id") or ""),
                created_at=str(item.get("created_at") or ""),
            )
            for item in notifications
        ]
        return parsed[:limit] if limit is not None else parsed
