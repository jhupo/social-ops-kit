from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from social_ops_kit.platforms.xhs.selectors import (
    SEARCH_DEFAULT_COUNT,
    SEARCH_DEFAULT_TIMEOUT_MS,
    SEARCH_FILTER_MAP,
    SEARCH_MAX_COUNT,
    SEARCH_MAX_NO_DATA_RETRIES,
)


@dataclass(frozen=True)
class SearchFilters:
    sort_by: str = "general"
    note_type: str = "all"
    publish_time: str = "all"
    search_scope: str = "all"

    def active_filter_labels(self) -> dict[str, str]:
        labels: dict[str, str] = {}
        if self.sort_by != "general":
            labels["sort_by"] = SEARCH_FILTER_MAP["sort_by"][self.sort_by]
        if self.note_type != "all":
            labels["note_type"] = SEARCH_FILTER_MAP["note_type"][self.note_type]
        if self.publish_time != "all":
            labels["publish_time"] = SEARCH_FILTER_MAP["publish_time"][self.publish_time]
        if self.search_scope != "all":
            labels["search_scope"] = SEARCH_FILTER_MAP["search_scope"][self.search_scope]
        return labels


@dataclass(frozen=True)
class XhsSearchItem:
    note_id: str
    xsec_token: str
    title: str
    cover: str
    note_type: str
    user_nickname: str
    user_avatar: str
    user_id: str
    likes: str

    def as_dict(self) -> dict[str, str]:
        return {
            "id": self.note_id,
            "xsecToken": self.xsec_token,
            "title": self.title,
            "cover": self.cover,
            "type": self.note_type,
            "user": {
                "nickname": self.user_nickname,
                "avatar": self.user_avatar,
                "userid": self.user_id,
            },
            "likes": self.likes,
        }


class SearchPageProtocol(Protocol):
    async def goto(self, url: str, wait_until: str = ...) -> None: ...

    async def wait_for_load_state(self, state: str) -> None: ...

    async def wait_for_function(self, expression: str, timeout: int) -> None: ...

    async def evaluate(self, expression: str, *args: Any) -> Any: ...

    async def close(self) -> None: ...


class SearchSessionProtocol(Protocol):
    async def ensure_context(self) -> None: ...

    async def new_page(self) -> SearchPageProtocol: ...

    async def human_scroll(self) -> None: ...

    async def sleep(self, milliseconds: int) -> None: ...


class XhsSearchRuntime:
    def __init__(self, session: SearchSessionProtocol) -> None:
        self._session = session

    async def search_content(
        self,
        keyword: str,
        count: int = SEARCH_DEFAULT_COUNT,
        timeout_ms: int = SEARCH_DEFAULT_TIMEOUT_MS,
        filters: SearchFilters | None = None,
    ) -> list[XhsSearchItem]:
        await self._session.ensure_context()
        page = await self._session.new_page()
        try:
            await page.goto(self.build_search_url(keyword), wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle")
            await page.wait_for_function("window.__INITIAL_STATE__ !== undefined", timeout=timeout_ms)
            await self._session.sleep(1_000)
            active_filters = (filters or SearchFilters()).active_filter_labels()
            if active_filters:
                await self.apply_search_filters(page, active_filters)
                await self._session.sleep(1_000)
            unique_items: dict[str, dict[str, Any]] = {}
            no_new_data_count = 0
            target_count = min(count, SEARCH_MAX_COUNT)
            while len(unique_items) < target_count:
                for item in await self.get_current_feeds(page):
                    item_id = str(item.get("id") or "")
                    if item_id and item_id not in unique_items:
                        unique_items[item_id] = item
                if len(unique_items) >= target_count:
                    break
                previous_count = len(unique_items)
                await self._session.human_scroll()
                for item in await self.get_current_feeds(page):
                    item_id = str(item.get("id") or "")
                    if item_id and item_id not in unique_items:
                        unique_items[item_id] = item
                if len(unique_items) == previous_count:
                    no_new_data_count += 1
                    if no_new_data_count >= SEARCH_MAX_NO_DATA_RETRIES:
                        break
                    await self._session.sleep(800)
                else:
                    no_new_data_count = 0
            return [normalize_search_item(item) for item in list(unique_items.values())[:target_count]]
        finally:
            await page.close()

    @staticmethod
    def build_search_url(keyword: str) -> str:
        from urllib.parse import quote

        return (
            "https://www.xiaohongshu.com/search_result?keyword="
            f"{quote(keyword)}&source=web_explore_feed"
        )

    async def apply_search_filters(self, page: SearchPageProtocol, active_filters: dict[str, str]) -> None:
        for label in active_filters.values():
            await page.evaluate(
                """
                (label) => {
                  const candidates = Array.from(document.querySelectorAll('button, div, span'));
                  const target = candidates.find((node) => node.textContent?.trim() === label);
                  if (target) {
                    target.click();
                    return true;
                  }
                  return false;
                }
                """,
                label,
            )
            await self._session.sleep(300)

    async def get_current_feeds(self, page: SearchPageProtocol) -> list[dict[str, Any]]:
        raw = await page.evaluate(
            """
            () => {
              const state = window.__INITIAL_STATE__;
              if (!state?.search?.feeds) {
                return '[]';
              }
              const feeds = state.search.feeds;
              const value = feeds.value !== undefined ? feeds.value : feeds._value;
              return JSON.stringify(value || []);
            }
            """
        )
        import json

        return json.loads(raw or "[]")


def normalize_search_item(item: dict[str, Any]) -> XhsSearchItem:
    note_card = item.get("noteCard") or item.get("note_card") or {}
    user = note_card.get("user") or {}
    interact_info = note_card.get("interactInfo") or note_card.get("interact_info") or {}
    cover = note_card.get("cover") or {}
    return XhsSearchItem(
        note_id=str(item.get("id") or ""),
        xsec_token=str(item.get("xsec_token") or item.get("xsecToken") or ""),
        title=str(note_card.get("displayTitle") or note_card.get("display_title") or note_card.get("title") or ""),
        cover=str(cover.get("urlDefault") or cover.get("url_default") or ""),
        note_type=str(note_card.get("type") or "normal"),
        user_nickname=str(user.get("nickname") or ""),
        user_avatar=str(user.get("avatar") or ""),
        user_id=str(user.get("userId") or user.get("user_id") or ""),
        likes=str(interact_info.get("likedCount") or interact_info.get("liked_count") or "0"),
    )
