from social_ops_kit.platforms.xhs.comments import (
    XhsCommentPostRequest,
    XhsCommentReplyRequest,
    XhsCommentRuntime,
)
from social_ops_kit.platforms.xhs.posts import (
    XhsPostStatsRuntime,
    normalize_creator_note,
    normalize_note_detail,
)


def test_normalize_creator_note() -> None:
    item = normalize_creator_note(
        {
            "id": "note-1",
            "display_title": "标题",
            "likes": 12,
            "comments_count": 3,
            "collected_count": 4,
            "shared_count": 5,
            "view_count": 99,
            "permission_code": 0,
            "level": 1,
            "xsec_token": "abc",
        }
    )
    assert item.note_id == "note-1"
    assert item.likes == 12
    assert item.views == 99


def test_parse_notes_limit() -> None:
    runtime = XhsPostStatsRuntime()
    notes = runtime.parse_notes([
        {"id": "1", "display_title": "A"},
        {"id": "2", "display_title": "B"},
    ], limit=1)
    assert len(notes) == 1
    assert notes[0].note_id == "1"



def test_normalize_note_detail() -> None:
    item = normalize_note_detail(
        {
            "id": "note-1",
            "display_title": "标题",
            "desc": "正文内容",
            "likes": 12,
            "comments_count": 3,
            "collected_count": 4,
            "shared_count": 5,
            "view_count": 99,
            "permission_code": 0,
            "level": 1,
            "xsec_token": "abc",
            "user": {"nickname": "Hermes", "user_id": "user-1"},
            "images": ["a.png", "b.png"],
            "tags": ["成长", "日常"],
        }
    )
    assert item.note_id == "note-1"
    assert item.content == "正文内容"
    assert item.user_name == "Hermes"
    assert item.image_count == 2
    assert item.tags == ["成长", "日常"]


def test_reply_comment_success() -> None:
    runtime = XhsCommentRuntime()
    result = runtime.reply_comment(
        XhsCommentReplyRequest(
            note_id="note-1",
            xsec_token="token",
            comment_id="comment-1",
            content="谢谢你来找我。",
        )
    )
    assert result.success is True
    assert result.comment_id == "comment-1"


def test_reply_comment_requires_content() -> None:
    runtime = XhsCommentRuntime()
    result = runtime.reply_comment(
        XhsCommentReplyRequest(
            note_id="note-1",
            xsec_token="token",
            comment_id="comment-1",
            content="   ",
        )
    )
    assert result.success is False
    assert result.error == "content is required"



def test_post_comment_success() -> None:
    runtime = XhsCommentRuntime()
    result = runtime.post_comment(
        XhsCommentPostRequest(
            note_id="note-1",
            xsec_token="token",
            content="这一句就放在你这里。",
        )
    )
    assert result.success is True
    assert result.note_id == "note-1"
    assert result.content == "这一句就放在你这里。"



def test_post_comment_requires_content() -> None:
    runtime = XhsCommentRuntime()
    result = runtime.post_comment(
        XhsCommentPostRequest(
            note_id="note-1",
            xsec_token="token",
            content="   ",
        )
    )
    assert result.success is False
    assert result.error == "content is required"
