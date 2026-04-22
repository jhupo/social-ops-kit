from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class XhsPostStats:
    note_id: str
    title: str
    likes: int
    comments: int
    collects: int
    shares: int
    views: int
    permission_code: int
    level: int
    xsec_token: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.note_id,
            "title": self.title,
            "likes": self.likes,
            "comments": self.comments,
            "collects": self.collects,
            "shares": self.shares,
            "views": self.views,
            "permissionCode": self.permission_code,
            "level": self.level,
            "xsecToken": self.xsec_token,
        }


@dataclass(frozen=True)
class XhsNoteDetail:
    note_id: str
    title: str
    content: str
    likes: int
    comments: int
    collects: int
    shares: int
    views: int
    permission_code: int
    level: int
    xsec_token: str
    user_name: str
    user_id: str
    image_count: int
    tags: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.note_id,
            "title": self.title,
            "content": self.content,
            "likes": self.likes,
            "comments": self.comments,
            "collects": self.collects,
            "shares": self.shares,
            "views": self.views,
            "permissionCode": self.permission_code,
            "level": self.level,
            "xsecToken": self.xsec_token,
            "userName": self.user_name,
            "userId": self.user_id,
            "imageCount": self.image_count,
            "tags": list(self.tags),
        }


def normalize_creator_note(note: dict[str, Any]) -> XhsPostStats:
    return XhsPostStats(
        note_id=str(note.get("id") or ""),
        title=str(note.get("display_title") or note.get("title") or ""),
        likes=int(note.get("likes") or 0),
        comments=int(note.get("comments_count") or note.get("comments") or 0),
        collects=int(note.get("collected_count") or note.get("collects") or 0),
        shares=int(note.get("shared_count") or note.get("shares") or 0),
        views=int(note.get("view_count") or note.get("views") or 0),
        permission_code=int(note.get("permission_code") or 0),
        level=int(note.get("level") or 0),
        xsec_token=str(note.get("xsec_token") or note.get("xsecToken") or ""),
    )


def normalize_note_detail(note: dict[str, Any]) -> XhsNoteDetail:
    user = note.get("user") or {}
    images = note.get("images") or note.get("image_list") or ()
    tags = note.get("tags") or note.get("topics") or ()
    return XhsNoteDetail(
        note_id=str(note.get("id") or note.get("note_id") or ""),
        title=str(note.get("display_title") or note.get("title") or ""),
        content=str(note.get("desc") or note.get("content") or ""),
        likes=int(note.get("likes") or 0),
        comments=int(note.get("comments_count") or note.get("comments") or 0),
        collects=int(note.get("collected_count") or note.get("collects") or 0),
        shares=int(note.get("shared_count") or note.get("shares") or 0),
        views=int(note.get("view_count") or note.get("views") or 0),
        permission_code=int(note.get("permission_code") or 0),
        level=int(note.get("level") or 0),
        xsec_token=str(note.get("xsec_token") or note.get("xsecToken") or ""),
        user_name=str(user.get("nickname") or user.get("name") or ""),
        user_id=str(user.get("user_id") or user.get("id") or ""),
        image_count=len(images),
        tags=[str(tag) for tag in tags],
    )


class XhsPostStatsRuntime:
    def parse_notes(self, notes: list[dict[str, Any]], limit: int | None = None) -> list[XhsPostStats]:
        parsed = [normalize_creator_note(note) for note in notes]
        return parsed[:limit] if limit is not None else parsed

    def list_my_notes(self, notes: list[dict[str, Any]], limit: int | None = None) -> list[XhsPostStats]:
        return self.parse_notes(notes, limit=limit)

    def get_note_detail(self, note: dict[str, Any]) -> XhsNoteDetail:
        return normalize_note_detail(note)
