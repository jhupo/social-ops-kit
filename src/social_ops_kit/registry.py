from __future__ import annotations

from social_ops_kit.models import Platform, ToolLifecycle, ToolMaturity, ToolParameter, ToolSpec
from social_ops_kit.platforms.douyin import DouyinAdapter
from social_ops_kit.platforms.xhs import XhsAdapter


_IMPLEMENTED_TOOL_NAMES = {
    "douyin_check_auth",
    "douyin_start_login",
    "douyin_get_login_state",
    "douyin_stop_login",
    "douyin_search_content",
    "douyin_publish_image_post",
    "douyin_publish_image_post_with_music",
    "douyin_inspect_recent_posts",
    "douyin_get_post_stats",
    "douyin_get_note_detail",
    "douyin_reply_visible_comments",
    "douyin_list_messages",
    "douyin_reply_message",
    "xhs_check_auth",
    "xhs_search_content",
    "xhs_create_draft",
    "xhs_get_draft",
    "xhs_list_drafts",
    "xhs_delete_draft",
    "xhs_delete_note",
    "xhs_update_draft",
    "xhs_publish_draft",
    "xhs_like_feed",
    "xhs_favorite_feed",
    "xhs_like_comment",
    "xhs_favorite_comment",
    "xhs_post_comment",
    "xhs_create_and_publish_draft",
    "xhs_get_my_notes",
    "xhs_get_note_detail",
    "xhs_get_notifications",
    "xhs_get_post_stats",
    "xhs_list_messages",
    "xhs_reply_message",
    "xhs_reply_comment",
}


def _build_douyin_tools() -> list[ToolSpec]:
    adapter = DouyinAdapter()
    parameter_map: dict[str, tuple[ToolParameter, ...]] = {
        "check_auth": (),
        "start_login": (ToolParameter("script_name", "string", "Optional login worker script name"),),
        "search_content": (
            ToolParameter("items", "array[object]", "Search result payloads to normalize", required=True),
            ToolParameter("limit", "integer", "Optional max number of items to return"),
        ),
        "publish_image_post": (
            ToolParameter("title", "string", "Post title", required=True),
            ToolParameter("copy", "string", "Post copy", required=True),
            ToolParameter("images", "array[string]", "Local image paths", required=True),
            ToolParameter("hashtags", "array[string]", "Optional hashtags"),
        ),
        "publish_image_post_with_music": (
            ToolParameter("title", "string", "Post title", required=True),
            ToolParameter("copy", "string", "Post copy", required=True),
            ToolParameter("images", "array[string]", "Local image paths", required=True),
            ToolParameter("hashtags", "array[string]", "Optional hashtags"),
            ToolParameter("music_id", "string", "Optional explicit music id"),
            ToolParameter("music_title", "string", "Optional explicit music title"),
            ToolParameter("music_author", "string", "Optional explicit music author"),
            ToolParameter("music_duration", "integer", "Optional explicit music duration seconds"),
        ),
        "inspect_recent_posts": (
            ToolParameter("text", "string", "Manage-page text snapshot to parse", required=True),
            ToolParameter("limit", "integer", "Optional max number of cards to return"),
        ),
        "get_post_stats": (
            ToolParameter("text", "string", "Manage-page text snapshot to parse for metric extraction", required=True),
            ToolParameter("limit", "integer", "Optional max number of post stat rows to return"),
        ),
        "get_note_detail": (
            ToolParameter("text", "string", "Manage-page text snapshot for a single post detail", required=True),
            ToolParameter("cover_url", "string", "Optional cover image URL"),
            ToolParameter("status", "string", "Optional publish/review status"),
        ),
        "reply_visible_comments": (
            ToolParameter("comments", "array[object]", "Visible comments to classify and draft replies for", required=True),
        ),
        "list_messages": (
            ToolParameter("threads", "array[object]", "Message threads to normalize", required=True),
            ToolParameter("limit", "integer", "Optional max number of threads to return"),
        ),
        "reply_message": (
            ToolParameter("thread_id", "string", "Thread identifier", required=True),
            ToolParameter("content", "string", "Reply body", required=True),
        ),
    }
    return [
        ToolSpec(
            name=f"douyin_{cap.name}",
            platform=Platform.DOUYIN,
            summary=cap.summary,
            parameters=parameter_map.get(cap.name, ()),
            lifecycle=ToolLifecycle.STABLE,
            tags=("douyin", "stable-core"),
            implemented=f"douyin_{cap.name}" in _IMPLEMENTED_TOOL_NAMES,
            maturity=(
                ToolMaturity.RUNNABLE
                if cap.name in {"check_auth", "start_login", "get_login_state", "stop_login", "search_content", "inspect_recent_posts", "get_post_stats", "get_note_detail", "reply_visible_comments", "list_messages", "reply_message"}
                else ToolMaturity.EXTERNAL_DEPENDENT
            )
            if f"douyin_{cap.name}" in _IMPLEMENTED_TOOL_NAMES
            else ToolMaturity.DECLARED,
        )
        for cap in adapter.stable_capabilities()
    ]


def _build_xhs_tools() -> list[ToolSpec]:
    adapter = XhsAdapter()
    parameter_map: dict[str, tuple[ToolParameter, ...]] = {
        "check_auth": (),
        "search_content": (
            ToolParameter("items", "array[object]", "Search result payloads to normalize", required=True),
            ToolParameter("limit", "integer", "Optional max number of items to return"),
        ),
        "create_draft": (
            ToolParameter("title", "string", "Note title", required=True),
            ToolParameter("content", "string", "Plain text note body", required=True),
            ToolParameter("screenshots", "array[string]", "Local image paths", required=True),
        ),
        "get_draft": (ToolParameter("draft_id", "string", "Draft identifier", required=True),),
        "list_drafts": (),
        "delete_draft": (ToolParameter("draft_id", "string", "Draft identifier", required=True),),
        "delete_note": (
            ToolParameter("note_id", "string", "Published note identifier", required=True),
            ToolParameter("title", "string", "Optional note title for confirmation payloads"),
        ),
        "update_draft": (
            ToolParameter("draft_id", "string", "Draft identifier", required=True),
            ToolParameter("title", "string", "Updated note title"),
            ToolParameter("content", "string", "Updated plain text note body"),
            ToolParameter("screenshots", "array[string]", "Updated local image paths"),
            ToolParameter("tags", "array[string]", "Updated tags"),
            ToolParameter("style", "string", "Updated visual style"),
        ),
        "publish_draft": (ToolParameter("draft_id", "string", "Draft identifier", required=True),),
        "like_feed": (
            ToolParameter("note_id", "string", "Note identifier", required=True),
            ToolParameter("xsec_token", "string", "Security token"),
            ToolParameter("unlike", "boolean", "If true, remove like instead of adding it"),
        ),
        "favorite_feed": (
            ToolParameter("note_id", "string", "Note identifier", required=True),
            ToolParameter("xsec_token", "string", "Security token"),
            ToolParameter("unfavorite", "boolean", "If true, remove favorite instead of adding it"),
        ),
        "like_comment": (
            ToolParameter("note_id", "string", "Note identifier", required=True),
            ToolParameter("comment_id", "string", "Comment identifier", required=True),
            ToolParameter("xsec_token", "string", "Security token"),
            ToolParameter("unlike", "boolean", "If true, remove like instead of adding it"),
        ),
        "favorite_comment": (
            ToolParameter("note_id", "string", "Note identifier", required=True),
            ToolParameter("comment_id", "string", "Comment identifier", required=True),
            ToolParameter("xsec_token", "string", "Security token"),
            ToolParameter("unfavorite", "boolean", "If true, remove favorite instead of adding it"),
        ),
        "post_comment": (
            ToolParameter("note_id", "string", "Note identifier", required=True),
            ToolParameter("xsec_token", "string", "Security token"),
            ToolParameter("content", "string", "Comment body", required=True),
        ),
        "create_and_publish_draft": (
            ToolParameter("title", "string", "Note title", required=True),
            ToolParameter("content", "string", "Plain text note body", required=True),
            ToolParameter("screenshots", "array[string]", "Local image paths", required=True),
            ToolParameter("tags", "array[string]", "Optional tags"),
            ToolParameter("style", "string", "Optional visual style"),
            ToolParameter("account", "string", "Optional publish account"),
        ),
        "get_my_notes": (
            ToolParameter("notes", "array[object]", "Creator note payloads to normalize", required=True),
            ToolParameter("limit", "integer", "Optional max number of notes to return"),
        ),
        "get_note_detail": (
            ToolParameter("note", "object", "Single note detail payload to normalize", required=True),
        ),
        "get_post_stats": (
            ToolParameter("notes", "array[object]", "Creator note payloads to normalize", required=True),
            ToolParameter("limit", "integer", "Optional max number of normalized notes to return"),
        ),
        "get_notifications": (
            ToolParameter("notifications", "array[object]", "Notification payloads to normalize", required=True),
            ToolParameter("limit", "integer", "Optional max number of notifications to return"),
        ),
        "list_messages": (
            ToolParameter("threads", "array[object]", "Message threads to normalize", required=True),
            ToolParameter("limit", "integer", "Optional max number of threads to return"),
        ),
        "reply_message": (
            ToolParameter("thread_id", "string", "Thread identifier", required=True),
            ToolParameter("content", "string", "Reply body", required=True),
        ),
        "reply_comment": (
            ToolParameter("note_id", "string", "Note identifier", required=True),
            ToolParameter("xsec_token", "string", "Security token"),
            ToolParameter("comment_id", "string", "Comment identifier", required=True),
            ToolParameter("content", "string", "Reply body", required=True),
        ),
    }
    return [
        ToolSpec(
            name=f"xhs_{cap.name}",
            platform=Platform.XHS,
            summary=cap.summary,
            parameters=parameter_map.get(cap.name, ()),
            lifecycle=ToolLifecycle.STABLE,
            tags=("xhs", "stable-core"),
            implemented=f"xhs_{cap.name}" in _IMPLEMENTED_TOOL_NAMES,
            maturity=(
                ToolMaturity.RUNNABLE
                if cap.name in {"check_auth", "search_content", "get_my_notes", "get_note_detail", "get_notifications", "get_post_stats", "list_messages", "reply_message", "reply_comment", "post_comment", "create_draft", "get_draft", "list_drafts", "delete_draft", "delete_note", "update_draft", "publish_draft", "like_feed", "favorite_feed", "like_comment", "favorite_comment"}
                else ToolMaturity.EXTERNAL_DEPENDENT
            )
            if f"xhs_{cap.name}" in _IMPLEMENTED_TOOL_NAMES
            else ToolMaturity.DECLARED,
        )
        for cap in adapter.stable_capabilities()
    ]


def build_default_registry() -> list[ToolSpec]:
    tools = _build_douyin_tools() + _build_xhs_tools()
    return sorted(tools, key=lambda item: (item.platform.value, item.name))
