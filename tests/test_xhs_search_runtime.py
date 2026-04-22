import json

from social_ops_kit.platforms.xhs.search import SearchFilters, XhsSearchRuntime, normalize_search_item


class FakePage:
    def __init__(self, feeds):
        self._feeds = list(feeds)
        self.closed = False
        self.clicked = []
        self.visits = []

    async def goto(self, url: str, wait_until: str = "domcontentloaded") -> None:
        self.visits.append((url, wait_until))

    async def wait_for_load_state(self, state: str) -> None:
        return None

    async def wait_for_function(self, expression: str, timeout: int) -> None:
        return None

    async def evaluate(self, expression: str, *args):
        if "JSON.stringify(value || [])" in expression:
            return json.dumps(self._feeds)
        if args:
            self.clicked.append(args[0])
            return True
        return None

    async def close(self) -> None:
        self.closed = True


class FakeSession:
    def __init__(self, page: FakePage):
        self.page = page
        self.sleep_calls = []
        self.scroll_calls = 0

    async def ensure_context(self) -> None:
        return None

    async def new_page(self) -> FakePage:
        return self.page

    async def human_scroll(self) -> None:
        self.scroll_calls += 1

    async def sleep(self, milliseconds: int) -> None:
        self.sleep_calls.append(milliseconds)


SAMPLE_ITEM = {
    "id": "abc123",
    "xsec_token": "token-1",
    "note_card": {
        "display_title": "测试标题",
        "cover": {"url_default": "https://example.com/cover.jpg"},
        "type": "video",
        "user": {
            "nickname": "Hermes",
            "avatar": "https://example.com/avatar.jpg",
            "user_id": "user-1",
        },
        "interact_info": {"liked_count": "42"},
    },
}


def test_normalize_search_item() -> None:
    item = normalize_search_item(SAMPLE_ITEM)
    assert item.note_id == "abc123"
    assert item.xsec_token == "token-1"
    assert item.title == "测试标题"
    assert item.note_type == "video"
    assert item.likes == "42"


def test_search_filter_labels() -> None:
    filters = SearchFilters(sort_by="latest", note_type="image", search_scope="following")
    assert filters.active_filter_labels() == {
        "sort_by": "最新",
        "note_type": "图文",
        "search_scope": "已关注",
    }


def test_search_runtime_collects_results() -> None:
    page = FakePage([SAMPLE_ITEM])
    runtime = XhsSearchRuntime(FakeSession(page))
    import asyncio

    results = asyncio.run(runtime.search_content("测试", count=1))
    assert len(results) == 1
    assert results[0].note_id == "abc123"
    assert page.closed is True


def test_build_search_url_encodes_keyword() -> None:
    url = XhsSearchRuntime.build_search_url("AI 助手")
    assert "keyword=AI%20%E5%8A%A9%E6%89%8B" in url
