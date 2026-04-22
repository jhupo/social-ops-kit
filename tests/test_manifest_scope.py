from social_ops_kit.registry import build_default_registry


EXPECTED = {
    "douyin_get_post_stats",
    "douyin_get_note_detail",
    "xhs_get_post_stats",
    "xhs_get_note_detail",
    "xhs_delete_note",
    "douyin_list_messages",
    "douyin_reply_message",
    "xhs_list_messages",
    "xhs_reply_message",
}


def test_registry_contains_stats_and_message_tools() -> None:
    names = {tool.name for tool in build_default_registry()}
    missing = EXPECTED - names
    assert not missing, f"Missing expected tools: {sorted(missing)}"
