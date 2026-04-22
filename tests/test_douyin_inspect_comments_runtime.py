from social_ops_kit.platforms.douyin.comments import (
    DouyinCommentRuntime,
    DouyinVisibleComment,
    classify_comment,
    comment_key,
    make_reply,
)
from social_ops_kit.platforms.douyin.inspect import (
    DouyinInspectRuntime,
    extract_cards_from_lines,
    normalize_note_detail,
)


def test_extract_cards_from_lines() -> None:
    lines = [
        "作品标题",
        "更多内容",
        "2026年04月21日 19:41",
        "浏览 12",
    ]
    cards = extract_cards_from_lines(lines)
    assert len(cards) == 1
    assert "2026年04月21日 19:41" in cards[0].lines


def test_build_snapshot_trims_text() -> None:
    runtime = DouyinInspectRuntime()
    snapshot = runtime.build_snapshot("标题\n2026年04月21日 19:41\n浏览 12")
    assert len(snapshot.cards) == 1
    assert snapshot.text_sample.startswith("标题")


def test_classify_comment() -> None:
    assert classify_comment("加微信聊") == "ad"
    assert classify_comment("你是不是有病") == "hostile"
    assert classify_comment("你好呀") == "normal"


def test_comment_key_is_stable() -> None:
    comment = DouyinVisibleComment(user_name="A", text="你好", raw="A 你好")
    assert comment_key(comment) == comment_key(comment)


def test_make_reply_handles_ad_and_normal() -> None:
    assert make_reply("加微信") is None
    assert make_reply("你好") is not None


def test_build_attempt_marks_intercepted_for_ads() -> None:
    runtime = DouyinCommentRuntime()
    attempt = runtime.build_attempt(DouyinVisibleComment(user_name="A", text="加微信", raw="加微信"))
    assert attempt.kind == "ad"
    assert attempt.status == "intercepted"


def test_normalize_douyin_note_detail() -> None:
    item = normalize_note_detail(
        {
            "title": "作品标题",
            "published_at": "2026年04月21日 19:41",
            "views": 12,
            "likes": 3,
            "comments": 1,
            "shares": 2,
            "cover_url": "https://example.com/cover.jpg",
            "status": "published",
        }
    )
    assert item.title == "作品标题"
    assert item.cover_url == "https://example.com/cover.jpg"
    assert item.status == "published"
    assert item.views == 12


def test_build_note_detail_from_text() -> None:
    runtime = DouyinInspectRuntime()
    item = runtime.build_note_detail("作品标题\n2026年04月21日 19:41\n浏览 12\n点赞 3\n评论 1\n分享 2")
    assert item.title == "作品标题"
    assert item.published_at == "2026年04月21日 19:41"
    assert item.likes == 3
    assert item.comments == 1
