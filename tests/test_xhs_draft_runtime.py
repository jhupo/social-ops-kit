from social_ops_kit.config import SocialOpsConfig
from social_ops_kit.platforms.xhs.browser_session import XhsPathSet
from social_ops_kit.platforms.xhs.drafts import (
    XhsDraftRequest,
    XhsDraftRuntime,
    clip_text,
    deterministic_storyboard,
    split_paragraphs,
)


def test_split_paragraphs() -> None:
    assert split_paragraphs("# 你好\n\n第二段\n") == ["你好", "第二段"]


def test_clip_text_truncates() -> None:
    assert clip_text("abcdef", 4) == "abc…"


def test_deterministic_storyboard_contains_cover() -> None:
    request = XhsDraftRequest(
        title="测试标题",
        content="第一段\n第二段\n第三段",
        screenshots=("/tmp/a.png",),
    )
    storyboard = deterministic_storyboard(request)
    assert storyboard.slides[0].kind == "cover"
    assert storyboard.slides[0].headline == "测试标题"


def test_draft_runtime_creates_files() -> None:
    runtime = XhsDraftRuntime.with_defaults(XhsPathSet.from_config(SocialOpsConfig.from_env()))
    request = XhsDraftRequest(
        title="测试草稿",
        content="今天想试试新的草稿链路。\n再多写一句。",
        screenshots=("/tmp/example.png",),
        tags=("测试",),
    )
    record = runtime.create_draft(request)
    assert record.title == "测试草稿"
    assert len(record.generated_images) >= 1


def test_create_and_publish_returns_note_id() -> None:
    runtime = XhsDraftRuntime.with_defaults(XhsPathSet.from_config(SocialOpsConfig.from_env()))
    request = XhsDraftRequest(
        title="发布测试",
        content="试试一键发布。",
        screenshots=(),
    )
    record, result = runtime.create_and_publish(request, account="Hermes")
    assert result.success is True
    assert result.account == "Hermes"
    assert result.note_id is not None
    assert result.draft_id == record.draft_id
