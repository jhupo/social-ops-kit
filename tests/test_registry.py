from social_ops_kit.registry import build_default_registry


LEGACY_PREFIXES = (
    'douyin_probe_',
    'douyin_debug_',
    'douyin_music_probe_',
    'xhs_explore_',
)


def test_registry_contains_only_curated_stable_tools():
    tools = build_default_registry()
    names = [tool.name for tool in tools]
    assert "douyin_publish_image_post" in names
    assert "douyin_get_note_detail" in names
    assert "xhs_create_and_publish_draft" in names
    assert "xhs_get_draft" in names
    assert "xhs_list_drafts" in names
    assert "xhs_delete_draft" in names
    assert "xhs_delete_note" in names
    assert "xhs_update_draft" in names
    assert "xhs_like_feed" in names
    assert "xhs_favorite_feed" in names
    assert "xhs_like_comment" in names
    assert "xhs_favorite_comment" in names
    assert "xhs_post_comment" in names
    assert "xhs_get_note_detail" in names
    for name in names:
        assert not name.startswith(LEGACY_PREFIXES)


def test_registry_exposes_expected_maturity_levels():
    tool_map = {tool.name: tool for tool in build_default_registry()}
    assert tool_map['douyin_check_auth'].maturity.value == 'runnable'
    assert tool_map['douyin_publish_image_post_with_music'].maturity.value == 'external_dependent'
    assert tool_map['xhs_search_content'].maturity.value == 'runnable'


def test_registry_names_are_unique():
    tools = build_default_registry()
    names = [tool.name for tool in tools]
    assert len(names) == len(set(names))
