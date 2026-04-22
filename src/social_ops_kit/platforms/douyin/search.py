from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DouyinSearchItem:
    item_id: str
    title: str
    cover: str
    note_type: str
    user_name: str
    user_id: str
    likes: str
    comments: str
    shares: str
    publish_time: str
    share_url: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.item_id,
            "title": self.title,
            "cover": self.cover,
            "type": self.note_type,
            "user": {
                "nickname": self.user_name,
                "userid": self.user_id,
            },
            "metrics": {
                "likes": self.likes,
                "comments": self.comments,
                "shares": self.shares,
            },
            "publishTime": self.publish_time,
            "shareUrl": self.share_url,
        }


def _first_text(*values: Any) -> str:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def _cover_from(item: dict[str, Any]) -> str:
    video = item.get("video") or {}
    cover = item.get("cover") or item.get("image") or {}
    if isinstance(video, dict):
        for key in ("cover", "origin_cover", "dynamic_cover"):
            nested = video.get(key)
            if isinstance(nested, dict):
                urls = nested.get("url_list") or nested.get("urlList") or []
                if urls:
                    return str(urls[0])
    if isinstance(cover, dict):
        urls = cover.get("url_list") or cover.get("urlList") or []
        if urls:
            return str(urls[0])
        for key in ("url", "url_default", "urlDefault"):
            if cover.get(key):
                return str(cover[key])
    return ""


def normalize_search_item(item: dict[str, Any]) -> DouyinSearchItem:
    author = item.get("author") or item.get("user") or {}
    statistics = item.get("statistics") or item.get("stat") or {}
    return DouyinSearchItem(
        item_id=_first_text(item.get("aweme_id"), item.get("id"), item.get("item_id")),
        title=_first_text(item.get("desc"), item.get("title"), item.get("name")),
        cover=_cover_from(item),
        note_type=_first_text(item.get("aweme_type"), item.get("type"), "video" if item.get("video") else "image"),
        user_name=_first_text(author.get("nickname"), author.get("name"), author.get("unique_id"), item.get("user_name")),
        user_id=_first_text(author.get("uid"), author.get("user_id"), item.get("user_id")),
        likes=_first_text(statistics.get("digg_count"), statistics.get("like_count"), item.get("likes"), "0"),
        comments=_first_text(statistics.get("comment_count"), item.get("comments"), "0"),
        shares=_first_text(statistics.get("share_count"), item.get("shares"), "0"),
        publish_time=_first_text(item.get("create_time"), item.get("publish_time"), item.get("published_at")),
        share_url=_first_text(item.get("share_url"), item.get("shareUrl"), item.get("url")),
    )
