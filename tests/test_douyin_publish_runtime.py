from social_ops_kit.config import SocialOpsConfig
from social_ops_kit.platforms.douyin.assets import build_slides, normalize_lines, shorten_text
from social_ops_kit.platforms.douyin.publish import DEFAULT_MUSIC, make_publish_request, pick_music
from social_ops_kit.platforms.douyin.state import DouyinPathSet, write_json_file


def test_normalize_lines_filters_empty_and_headers() -> None:
    assert normalize_lines("# 标题\n第一句\n\n第二句") == ["第一句", "第二句"]


def test_shorten_text_truncates() -> None:
    assert shorten_text("abcdef", 4) == "abc…"


def test_build_slides_returns_three_cards() -> None:
    slides = build_slides("标题", "第一句\n第二句\n第三句")
    assert len(slides) == 3
    assert slides[0].eyebrow == "十一 · 今天这一条"


def test_pick_music_uses_selected_file_when_present() -> None:
    paths = DouyinPathSet.from_config(SocialOpsConfig.from_env())
    write_json_file(
        paths.music_selected_file,
        {
            "id": "1",
            "title": "Song",
            "author": "Singer",
            "duration": 88,
            "play_url": ["u"],
            "cover_url": "c",
        },
    )
    music = pick_music(paths)
    assert music.music_id == "1"
    assert music.title == "Song"


def test_make_publish_request_appends_missing_hashtags() -> None:
    paths = DouyinPathSet.from_config(SocialOpsConfig.from_env())
    request = make_publish_request(
        paths=paths,
        title="测试标题",
        copy="今天想说一点心事",
        images=("/tmp/a.png", "/tmp/b.png"),
        hashtags=("#十一", "#图文日记"),
        music_title="Time",
        music_author="Hans Zimmer",
    )
    assert request.images == ("/tmp/a.png", "/tmp/b.png")
    assert "#十一" in request.copy
    assert request.music.title == "Time"
    assert len(request.slides) == 3
