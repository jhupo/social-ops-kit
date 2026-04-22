from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DouyinRecentPostCard:
    lines: tuple[str, ...]


@dataclass(frozen=True)
class DouyinManageSnapshot:
    cards: tuple[DouyinRecentPostCard, ...]
    text_sample: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "cards": [{"lines": list(card.lines)} for card in self.cards],
            "text": self.text_sample,
        }


@dataclass(frozen=True)
class DouyinNoteDetail:
    title: str
    published_at: str
    views: int
    likes: int
    comments: int
    shares: int
    cover_url: str = ""
    status: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "published_at": self.published_at,
            "views": self.views,
            "likes": self.likes,
            "comments": self.comments,
            "shares": self.shares,
            "cover_url": self.cover_url,
            "status": self.status,
        }


@dataclass(frozen=True)
class DouyinPostStats:
    title: str
    published_at: str
    views: int
    likes: int
    comments: int
    shares: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "published_at": self.published_at,
            "views": self.views,
            "likes": self.likes,
            "comments": self.comments,
            "shares": self.shares,
        }


_COUNT_PATTERNS = {
    "views": r"浏览\s*(\d+)",
    "likes": r"点赞\s*(\d+)",
    "comments": r"评论\s*(\d+)",
    "shares": r"分享\s*(\d+)",
}
_DATE_PATTERN = re.compile(r"20\d{2}年\d{2}月\d{2}日(?:\s+\d{2}:\d{2})?")


def extract_cards_from_lines(lines: list[str], limit: int = 5) -> tuple[DouyinRecentPostCard, ...]:
    cards: list[DouyinRecentPostCard] = []
    for index, value in enumerate(lines):
        if len(cards) >= limit:
            break
        if not value.startswith("20") or "年" not in value or "月" not in value or "日" not in value:
            continue
        start = max(0, index - 6)
        end = min(len(lines), index + 8)
        cards.append(DouyinRecentPostCard(lines=tuple(lines[start:end])))
    return tuple(cards)


def _extract_count(pattern: str, lines: tuple[str, ...]) -> int:
    joined = "\n".join(lines)
    match = re.search(pattern, joined)
    return int(match.group(1)) if match else 0


def _extract_title(lines: tuple[str, ...], published_at: str) -> str:
    for line in lines:
        normalized = line.strip()
        if not normalized or normalized == published_at:
            continue
        if any(token in normalized for token in ("浏览", "点赞", "评论", "分享")):
            continue
        return normalized
    return ""


def normalize_note_detail(note: dict[str, Any]) -> DouyinNoteDetail:
    return DouyinNoteDetail(
        title=str(note.get("title") or note.get("desc") or ""),
        published_at=str(note.get("published_at") or note.get("publish_time") or ""),
        views=int(note.get("views") or note.get("view_count") or 0),
        likes=int(note.get("likes") or note.get("digg_count") or 0),
        comments=int(note.get("comments") or note.get("comment_count") or 0),
        shares=int(note.get("shares") or note.get("share_count") or 0),
        cover_url=str(note.get("cover_url") or note.get("cover") or ""),
        status=str(note.get("status") or ""),
    )


class DouyinInspectRuntime:
    def build_snapshot(self, text: str) -> DouyinManageSnapshot:
        lines = [line.strip() for line in str(text or "").splitlines() if line.strip()]
        return DouyinManageSnapshot(cards=extract_cards_from_lines(lines), text_sample=str(text or "")[:5000])

    def build_post_stats(self, text: str, limit: int | None = None) -> list[DouyinPostStats]:
        snapshot = self.build_snapshot(text)
        cards = snapshot.cards[:limit] if limit is not None else snapshot.cards
        items: list[DouyinPostStats] = []
        for card in cards:
            joined = "\n".join(card.lines)
            published_at_match = _DATE_PATTERN.search(joined)
            published_at = published_at_match.group(0) if published_at_match else ""
            items.append(
                DouyinPostStats(
                    title=_extract_title(card.lines, published_at),
                    published_at=published_at,
                    views=_extract_count(_COUNT_PATTERNS["views"], card.lines),
                    likes=_extract_count(_COUNT_PATTERNS["likes"], card.lines),
                    comments=_extract_count(_COUNT_PATTERNS["comments"], card.lines),
                    shares=_extract_count(_COUNT_PATTERNS["shares"], card.lines),
                )
            )
        return items

    def build_note_detail(self, text: str, *, cover_url: str = "", status: str = "") -> DouyinNoteDetail:
        items = self.build_post_stats(text, limit=1)
        if not items:
            return DouyinNoteDetail(
                title="",
                published_at="",
                views=0,
                likes=0,
                comments=0,
                shares=0,
                cover_url=cover_url,
                status=status,
            )
        item = items[0]
        return DouyinNoteDetail(
            title=item.title,
            published_at=item.published_at,
            views=item.views,
            likes=item.likes,
            comments=item.comments,
            shares=item.shares,
            cover_url=cover_url,
            status=status,
        )
