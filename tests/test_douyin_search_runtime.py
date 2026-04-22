from social_ops_kit.platforms.douyin.search import DouyinSearchItem, normalize_search_item


SAMPLE_ITEM = {
    "aweme_id": "dy123",
    "desc": "测试标题",
    "author": {
        "nickname": "Hermes",
        "uid": "user-1",
    },
    "statistics": {
        "digg_count": 88,
        "comment_count": 7,
        "share_count": 3,
    },
    "video": {
        "cover": {"url_list": ["https://example.com/cover.jpg"]},
    },
    "create_time": "2026-04-21 20:00",
    "share_url": "https://www.douyin.com/video/dy123",
}


def test_normalize_search_item() -> None:
    item = normalize_search_item(SAMPLE_ITEM)
    assert isinstance(item, DouyinSearchItem)
    assert item.item_id == "dy123"
    assert item.title == "测试标题"
    assert item.user_name == "Hermes"
    assert item.likes == "88"
    assert item.comments == "7"
    assert item.shares == "3"
    assert item.publish_time == "2026-04-21 20:00"
    assert item.share_url == "https://www.douyin.com/video/dy123"


def test_as_dict_preserves_shape() -> None:
    item = normalize_search_item(SAMPLE_ITEM)
    payload = item.as_dict()
    assert payload["id"] == "dy123"
    assert payload["user"]["nickname"] == "Hermes"
    assert payload["metrics"]["likes"] == "88"
