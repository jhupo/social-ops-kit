from pathlib import Path

from social_ops_kit.config import SocialOpsConfig
from social_ops_kit.mcp.server import SocialOpsToolService, build_server_blueprint, create_mcp_server
from social_ops_kit.mcp.tools import build_input_schema, build_mcp_tool_definitions
from social_ops_kit.models import ToolParameter
from social_ops_kit.platforms.douyin.messages import DouyinImArtifactParser


def test_build_input_schema_marks_required_fields() -> None:
    schema = build_input_schema(
        (
            ToolParameter("title", "string", "Title", required=True),
            ToolParameter("tags", "array[string]", "Tags"),
        )
    )
    assert schema["required"] == ["title"]
    assert schema["properties"]["tags"]["type"] == "array"


def test_build_mcp_tool_definitions_contains_known_tool() -> None:
    tools = build_mcp_tool_definitions()
    names = {tool.name for tool in tools}
    assert "douyin_check_auth" in names
    assert "douyin_publish_image_post" in names
    assert "douyin_publish_image_post_with_music" in names
    assert "douyin_search_content" in names
    assert "douyin_inspect_recent_posts" in names
    assert "douyin_reply_visible_comments" in names
    assert "douyin_get_post_stats" in names
    assert "douyin_get_note_detail" in names
    assert "douyin_list_messages" in names
    assert "douyin_reply_message" in names
    assert "xhs_check_auth" in names
    assert "xhs_search_content" in names
    assert "xhs_create_draft" in names
    assert "xhs_get_draft" in names
    assert "xhs_list_drafts" in names
    assert "xhs_delete_draft" in names
    assert "xhs_delete_note" in names
    assert "xhs_update_draft" in names
    assert "xhs_publish_draft" in names
    assert "xhs_like_feed" in names
    assert "xhs_favorite_feed" in names
    assert "xhs_like_comment" in names
    assert "xhs_favorite_comment" in names
    assert "xhs_post_comment" in names
    assert "xhs_get_note_detail" in names
    assert "xhs_create_and_publish_draft" in names
    assert "xhs_get_my_notes" in names
    assert "xhs_get_notifications" in names
    assert "xhs_get_post_stats" in names
    assert "xhs_list_messages" in names
    assert "xhs_reply_message" in names

    tool_map = {tool.name: tool for tool in tools}
    assert tool_map["douyin_inspect_recent_posts"].inputSchema["required"] == ["text"]
    assert tool_map["douyin_search_content"].inputSchema["required"] == ["items"]
    assert tool_map["douyin_publish_image_post"].inputSchema["required"] == ["title", "copy", "images"]
    assert tool_map["douyin_reply_visible_comments"].inputSchema["required"] == ["comments"]
    assert tool_map["douyin_get_post_stats"].inputSchema["required"] == ["text"]
    assert tool_map["douyin_get_note_detail"].inputSchema["required"] == ["text"]
    assert tool_map["douyin_list_messages"].inputSchema["required"] == ["threads"]
    assert tool_map["douyin_reply_message"].inputSchema["required"] == ["thread_id", "content"]
    assert tool_map["xhs_search_content"].inputSchema["required"] == ["items"]
    assert tool_map["xhs_create_draft"].inputSchema["required"] == ["title", "content", "screenshots"]
    assert tool_map["xhs_get_draft"].inputSchema["required"] == ["draft_id"]
    assert tool_map["xhs_list_drafts"].inputSchema == {"type": "object", "properties": {}}
    assert tool_map["xhs_delete_draft"].inputSchema["required"] == ["draft_id"]
    assert tool_map["xhs_delete_note"].inputSchema["required"] == ["note_id"]
    assert tool_map["xhs_update_draft"].inputSchema["required"] == ["draft_id"]
    assert tool_map["xhs_publish_draft"].inputSchema["required"] == ["draft_id"]
    assert tool_map["xhs_like_feed"].inputSchema["required"] == ["note_id"]
    assert tool_map["xhs_favorite_feed"].inputSchema["required"] == ["note_id"]
    assert tool_map["xhs_like_comment"].inputSchema["required"] == ["note_id", "comment_id"]
    assert tool_map["xhs_favorite_comment"].inputSchema["required"] == ["note_id", "comment_id"]
    assert tool_map["xhs_post_comment"].inputSchema["required"] == ["note_id", "content"]
    assert tool_map["xhs_get_note_detail"].inputSchema["required"] == ["note"]
    assert tool_map["xhs_get_my_notes"].inputSchema["required"] == ["notes"]
    assert tool_map["xhs_get_notifications"].inputSchema["required"] == ["notifications"]
    assert tool_map["xhs_get_post_stats"].inputSchema["required"] == ["notes"]
    assert tool_map["xhs_list_messages"].inputSchema["required"] == ["threads"]
    assert tool_map["xhs_reply_message"].inputSchema["required"] == ["thread_id", "content"]


def test_server_blueprint_has_curated_tools() -> None:
    blueprint = build_server_blueprint()
    tool_map = {tool["name"]: tool for tool in blueprint.tools}
    assert blueprint.name == "social-ops-kit"
    assert "douyin_get_login_state" in tool_map
    assert "xhs_reply_comment" in tool_map
    assert tool_map["douyin_check_auth"]["implemented"] is True
    assert tool_map["douyin_get_note_detail"]["implemented"] is True
    assert tool_map["douyin_check_auth"]["maturity"] == "runnable"
    assert tool_map["douyin_publish_image_post_with_music"]["maturity"] == "external_dependent"
    assert tool_map["xhs_search_content"]["implemented"] is True
    assert tool_map["xhs_search_content"]["implementation_status"] == "implemented"
    assert tool_map["xhs_search_content"]["maturity"] == "runnable"
    assert tool_map["xhs_get_draft"]["implemented"] is True
    assert tool_map["xhs_list_drafts"]["implemented"] is True
    assert tool_map["xhs_delete_draft"]["implemented"] is True
    assert tool_map["xhs_delete_note"]["implemented"] is True
    assert tool_map["xhs_update_draft"]["implemented"] is True
    assert tool_map["xhs_like_feed"]["implemented"] is True
    assert tool_map["xhs_favorite_feed"]["implemented"] is True
    assert tool_map["xhs_like_comment"]["implemented"] is True
    assert tool_map["xhs_favorite_comment"]["implemented"] is True
    assert tool_map["xhs_post_comment"]["implemented"] is True
    assert tool_map["xhs_get_note_detail"]["implemented"] is True


def test_tool_service_executes_wired_handlers() -> None:
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    result = service.execute(
        "xhs_reply_comment",
        {
            "note_id": "note-1",
            "xsec_token": "token",
            "comment_id": "comment-1",
            "content": "谢谢你。",
        },
    )
    assert result["success"] is True
    assert result["comment_id"] == "comment-1"



def test_tool_service_executes_xhs_post_comment() -> None:
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    result = service.execute(
        "xhs_post_comment",
        {
            "note_id": "note-1",
            "xsec_token": "token",
            "content": "今天也想把一句话留在这。",
        },
    )
    assert result["success"] is True
    assert result["note_id"] == "note-1"
    assert result["content"] == "今天也想把一句话留在这。"



def test_tool_service_executes_douyin_check_auth(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SOCIAL_OPS_DOUYIN_STATE_DIR", str(tmp_path / "douyin"))
    login_state_dir = tmp_path / "douyin"
    login_state_dir.mkdir(parents=True, exist_ok=True)
    (login_state_dir / "login_state.json").write_text('{"status":"logged_in","authenticated":true}\n', encoding="utf-8")

    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    result = service.execute("douyin_check_auth", {})
    assert result["success"] is True
    assert result["authenticated"] is True
    assert result["platform"] == "douyin"


def test_tool_service_executes_xhs_check_auth(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SOCIAL_OPS_XHS_STATE_DIR", str(tmp_path / "xhs"))
    profile_dir = tmp_path / "xhs" / "profile"
    profile_dir.mkdir(parents=True, exist_ok=True)
    (profile_dir / "session.json").write_text('{"logged_in": true}\n', encoding="utf-8")

    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    result = service.execute("xhs_check_auth", {})
    assert result["success"] is True
    assert result["authenticated"] is True
    assert result["platform"] == "xhs"


def test_tool_service_executes_xhs_search_content() -> None:
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    result = service.execute(
        "xhs_search_content",
        {
            "items": [
                {
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
            ],
            "limit": 1,
        },
    )
    assert result["success"] is True
    assert len(result["items"]) == 1
    assert result["items"][0]["id"] == "abc123"
    assert result["items"][0]["likes"] == "42"


def test_tool_service_executes_douyin_inspect_recent_posts() -> None:
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    result = service.execute(
        "douyin_inspect_recent_posts",
        {"text": "标题\n2026年04月21日 19:41\n浏览 12", "limit": 1},
    )
    assert result["success"] is True
    assert len(result["snapshot"]["cards"]) == 1
    assert "2026年04月21日 19:41" in result["snapshot"]["cards"][0]["lines"]


def test_tool_service_executes_douyin_search_content() -> None:
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    result = service.execute(
        "douyin_search_content",
        {
            "items": [
                {
                    "aweme_id": "dy123",
                    "desc": "测试标题",
                    "author": {"nickname": "Hermes", "uid": "user-1"},
                    "statistics": {"digg_count": 88, "comment_count": 7, "share_count": 3},
                },
                {"aweme_id": "dy456", "desc": "第二条"},
            ],
            "limit": 1,
        },
    )
    assert result["success"] is True
    assert len(result["items"]) == 1
    assert result["items"][0]["id"] == "dy123"
    assert result["items"][0]["metrics"]["likes"] == "88"


def test_tool_service_executes_douyin_reply_visible_comments() -> None:
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    result = service.execute(
        "douyin_reply_visible_comments",
        {
            "comments": [
                {"user_name": "A", "text": "你好呀", "raw": "A 你好呀"},
                {"user_name": "B", "text": "加微信聊", "raw": "B 加微信聊"},
            ]
        },
    )
    assert result["success"] is True
    assert len(result["attempts"]) == 2
    assert result["attempts"][0]["status"] == "ready"
    assert result["attempts"][1]["status"] == "intercepted"


def test_tool_service_executes_douyin_list_messages() -> None:
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    result = service.execute(
        "douyin_list_messages",
        {
            "threads": [
                {"thread_id": "dy-1", "user_name": "小雨", "last_message": "你好呀", "unread_count": 2},
                {"thread_id": "dy-2", "user_name": "阿青", "last_message": "在吗", "unread_count": 0},
            ],
            "limit": 1,
        },
    )
    assert result["success"] is True
    assert result["source"] == "input_threads"
    assert len(result["items"]) == 1
    assert result["items"][0]["thread_id"] == "dy-1"


def test_douyin_im_artifact_parser_extracts_threads() -> None:
    import base64
    import json
    from pathlib import Path

    payloads = json.loads(Path("/root/social-ops-kit/artifacts/douyin_im_base64.json").read_text(encoding="utf-8"))
    conversation = b""
    info = b""
    for item in payloads:
        if "/v1/conversation/list" in item["url"]:
            conversation = base64.b64decode(item["bodyBase64"])
        if "/v2/conversation/get_info_list" in item["url"]:
            info = base64.b64decode(item["bodyBase64"])
    threads = DouyinImArtifactParser.extract_threads(conversation, info)
    assert threads
    assert threads[0].thread_id.isdigit()
    assert len(threads[0].thread_id) >= 18


def test_tool_service_executes_douyin_reply_message(monkeypatch) -> None:
    class FakeRuntime:
        def reply_message(self, thread_id: str, content: str) -> dict[str, object]:
            return {"success": True, "thread_id": thread_id, "content": content, "source": "douyin_web_im"}

    monkeypatch.setattr("social_ops_kit.mcp.server.DouyinRealMessageRuntime.from_config", lambda config: FakeRuntime())
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    result = service.execute(
        "douyin_reply_message",
        {"thread_id": "dy-1", "content": "我在呀，刚看到你。"},
    )
    assert result["success"] is True
    assert result["thread_id"] == "dy-1"
    assert result["content"] == "我在呀，刚看到你。"
    assert result["source"] == "douyin_web_im"


def test_tool_service_executes_douyin_list_messages_from_real_artifacts(monkeypatch) -> None:
    class FakeRuntime:
        def list_threads(self, limit: int | None = None):
            return (
                [
                    type("T", (), {"as_dict": lambda self: {"thread_id": "10000000000000000001", "user_name": "张旭洋律师", "last_message": "你好", "unread_count": 0, "source": "douyin_web_im"}})(),
                ],
                "douyin_web_im",
            )

    monkeypatch.setattr("social_ops_kit.mcp.server.DouyinRealMessageRuntime.from_config", lambda config: FakeRuntime())
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    result = service.execute("douyin_list_messages", {})
    assert result["success"] is True
    assert result["source"] == "douyin_web_im"
    assert result["items"]
    assert result["items"][0]["thread_id"].isdigit()


def test_tool_service_executes_xhs_create_draft() -> None:
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    result = service.execute(
        "xhs_create_draft",
        {
            "title": "测试草稿",
            "content": "今天想试试新的草稿链路。",
            "screenshots": ["/tmp/example.png"],
            "tags": ["测试"],
            "style": "minimal",
        },
    )
    assert result["success"] is True
    assert result["draft"]["title"] == "测试草稿"
    assert result["draft"]["draft_id"]
    assert len(result["draft"]["generated_images"]) >= 1


def test_tool_service_executes_xhs_get_draft_and_list_drafts() -> None:
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    created = service.execute(
        "xhs_create_draft",
        {
            "title": "待查看草稿",
            "content": "先看看草稿内容。",
            "screenshots": ["/tmp/example.png"],
            "tags": ["草稿"],
            "style": "minimal",
        },
    )
    draft_id = created["draft"]["draft_id"]
    result = service.execute("xhs_get_draft", {"draft_id": draft_id})
    listed = service.execute("xhs_list_drafts", {})
    assert result["success"] is True
    assert result["draft"]["draft_id"] == draft_id
    assert result["draft"]["title"] == "待查看草稿"
    assert listed["success"] is True
    assert any(item["draft_id"] == draft_id for item in listed["items"])


def test_tool_service_executes_xhs_delete_draft() -> None:
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    created = service.execute(
        "xhs_create_draft",
        {
            "title": "待删除草稿",
            "content": "删掉它。",
            "screenshots": ["/tmp/example.png"],
            "style": "minimal",
        },
    )
    draft_id = created["draft"]["draft_id"]
    deleted = service.execute("xhs_delete_draft", {"draft_id": draft_id})
    missing = service.execute("xhs_get_draft", {"draft_id": draft_id})
    assert deleted["success"] is True
    assert deleted["draft_id"] == draft_id
    assert missing["success"] is False
    assert missing["error"] == "draft_not_found"


def test_tool_service_executes_xhs_delete_note() -> None:
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    deleted = service.execute("xhs_delete_note", {"note_id": "note-1", "title": "这条要删掉"})
    missing = service.execute("xhs_delete_note", {"note_id": ""})
    assert deleted["success"] is True
    assert deleted["note_id"] == "note-1"
    assert deleted["title"] == "这条要删掉"
    assert missing["success"] is False
    assert missing["error"] == "note_id is required"


def test_tool_service_executes_xhs_update_draft() -> None:
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    created = service.execute(
        "xhs_create_draft",
        {
            "title": "待修改草稿",
            "content": "旧内容",
            "screenshots": ["/tmp/example.png"],
            "tags": ["旧标签"],
            "style": "minimal",
        },
    )
    draft_id = created["draft"]["draft_id"]
    updated = service.execute(
        "xhs_update_draft",
        {
            "draft_id": draft_id,
            "title": "新标题",
            "content": "新内容",
            "tags": ["新标签"],
            "screenshots": ["/tmp/new.png"],
        },
    )
    fetched = service.execute("xhs_get_draft", {"draft_id": draft_id})
    assert updated["success"] is True
    assert updated["draft"]["title"] == "新标题"
    assert updated["draft"]["content"] == "新内容"
    assert updated["draft"]["tags"] == ["新标签"]
    assert updated["draft"]["screenshots"] == ["/tmp/new.png"]
    assert fetched["draft"]["title"] == "新标题"


def test_tool_service_executes_xhs_like_feed() -> None:
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    liked = service.execute(
        "xhs_like_feed",
        {"note_id": "note-1", "xsec_token": "token-1"},
    )
    unliked = service.execute(
        "xhs_like_feed",
        {"note_id": "note-1", "xsec_token": "token-1", "unlike": True},
    )
    assert liked["success"] is True
    assert liked["liked"] is True
    assert liked["note_id"] == "note-1"
    assert unliked["success"] is True
    assert unliked["liked"] is False


def test_tool_service_executes_xhs_favorite_feed() -> None:
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    favorited = service.execute(
        "xhs_favorite_feed",
        {"note_id": "note-1", "xsec_token": "token-1"},
    )
    unfavorited = service.execute(
        "xhs_favorite_feed",
        {"note_id": "note-1", "xsec_token": "token-1", "unfavorite": True},
    )
    assert favorited["success"] is True
    assert favorited["favorited"] is True
    assert favorited["note_id"] == "note-1"
    assert unfavorited["success"] is True
    assert unfavorited["favorited"] is False


def test_tool_service_executes_xhs_like_comment() -> None:
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    liked = service.execute(
        "xhs_like_comment",
        {"note_id": "note-1", "comment_id": "comment-1", "xsec_token": "token-1"},
    )
    unliked = service.execute(
        "xhs_like_comment",
        {"note_id": "note-1", "comment_id": "comment-1", "xsec_token": "token-1", "unlike": True},
    )
    assert liked["success"] is True
    assert liked["liked"] is True
    assert liked["comment_id"] == "comment-1"
    assert unliked["success"] is True
    assert unliked["liked"] is False


def test_tool_service_executes_xhs_favorite_comment() -> None:
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    favorited = service.execute(
        "xhs_favorite_comment",
        {"note_id": "note-1", "comment_id": "comment-1", "xsec_token": "token-1"},
    )
    unfavorited = service.execute(
        "xhs_favorite_comment",
        {"note_id": "note-1", "comment_id": "comment-1", "xsec_token": "token-1", "unfavorite": True},
    )
    assert favorited["success"] is True
    assert favorited["favorited"] is True
    assert favorited["comment_id"] == "comment-1"
    assert unfavorited["success"] is True
    assert unfavorited["favorited"] is False


def test_tool_service_executes_xhs_publish_draft() -> None:
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    created = service.execute(
        "xhs_create_draft",
        {
            "title": "待发布草稿",
            "content": "先存一下。",
            "screenshots": [],
            "style": "minimal",
        },
    )
    result = service.execute(
        "xhs_publish_draft",
        {"draft_id": created["draft"]["draft_id"], "account": "Hermes"},
    )
    assert result["success"] is True
    assert result["publish_result"]["draft_id"] == created["draft"]["draft_id"]
    assert result["publish_result"]["account"] == "Hermes"


def test_tool_service_executes_xhs_get_post_stats() -> None:
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    result = service.execute(
        "xhs_get_post_stats",
        {
            "notes": [
                {"id": "1", "display_title": "A", "likes": 12, "view_count": 33},
                {"id": "2", "display_title": "B", "likes": 1, "view_count": 4},
            ],
            "limit": 1,
        },
    )
    assert result["success"] is True
    assert len(result["items"]) == 1
    assert result["items"][0]["id"] == "1"
    assert result["items"][0]["views"] == 33


def test_tool_service_executes_xhs_get_note_detail() -> None:
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    result = service.execute(
        "xhs_get_note_detail",
        {
            "note": {
                "id": "note-1",
                "display_title": "标题",
                "desc": "正文内容",
                "likes": 12,
                "comments_count": 3,
                "collected_count": 4,
                "shared_count": 5,
                "view_count": 99,
                "xsec_token": "abc",
                "user": {"nickname": "Hermes", "user_id": "user-1"},
                "images": ["a.png", "b.png"],
                "tags": ["成长", "日常"],
            }
        },
    )
    assert result["success"] is True
    assert result["item"]["id"] == "note-1"
    assert result["item"]["content"] == "正文内容"
    assert result["item"]["imageCount"] == 2
    assert result["item"]["userName"] == "Hermes"


def test_tool_service_executes_xhs_get_my_notes() -> None:
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    result = service.execute(
        "xhs_get_my_notes",
        {
            "notes": [
                {"id": "1", "display_title": "A", "likes": 12, "view_count": 33},
                {"id": "2", "display_title": "B", "likes": 1, "view_count": 4},
            ],
            "limit": 1,
        },
    )
    assert result["success"] is True
    assert len(result["items"]) == 1
    assert result["items"][0]["title"] == "A"


def test_tool_service_executes_xhs_get_notifications() -> None:
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    result = service.execute(
        "xhs_get_notifications",
        {
            "notifications": [
                {
                    "id": "n1",
                    "type": "mention",
                    "user_name": "十一的朋友",
                    "content": "来看看你",
                    "note_id": "note-1",
                    "created_at": "2026-04-21 20:00",
                }
            ]
        },
    )
    assert result["success"] is True
    assert len(result["items"]) == 1
    assert result["items"][0]["type"] == "mention"
    assert result["items"][0]["user_name"] == "十一的朋友"



def test_tool_service_executes_xhs_list_messages() -> None:
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    result = service.execute(
        "xhs_list_messages",
        {
            "threads": [
                {"thread_id": "xhs-1", "user_name": "阿禾", "last_message": "你好", "unread_count": 3},
                {"thread_id": "xhs-2", "user_name": "小周", "last_message": "在吗", "unread_count": 0},
            ],
            "limit": 1,
        },
    )
    assert result["success"] is True
    assert len(result["items"]) == 1
    assert result["items"][0]["thread_id"] == "xhs-1"



def test_tool_service_executes_xhs_reply_message() -> None:
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    result = service.execute(
        "xhs_reply_message",
        {"thread_id": "xhs-1", "content": "我在，刚刚看到你的消息。"},
    )
    assert result["success"] is True
    assert result["thread_id"] == "xhs-1"
    assert result["content"] == "我在，刚刚看到你的消息。"



def test_tool_service_executes_douyin_get_note_detail() -> None:
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    result = service.execute(
        "douyin_get_note_detail",
        {"text": "作品标题\n2026年04月21日 19:41\n浏览 12\n点赞 3\n评论 1\n分享 2", "cover_url": "https://example.com/cover.jpg", "status": "published"},
    )
    assert result["success"] is True
    assert result["item"]["title"] == "作品标题"
    assert result["item"]["cover_url"] == "https://example.com/cover.jpg"
    assert result["item"]["status"] == "published"


def test_tool_service_executes_douyin_get_post_stats() -> None:
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    result = service.execute(
        "douyin_get_post_stats",
        {"text": "标题A\n2026年04月21日 19:41\n浏览 12\n点赞 3\n评论 1\n分享 2", "limit": 1},
    )
    assert result["success"] is True
    assert len(result["items"]) == 1
    assert result["items"][0]["views"] == 12
    assert result["items"][0]["likes"] == 3



def test_tool_service_returns_not_implemented_for_unwired_tool() -> None:
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    result = service.execute(
        "xhs_search_content",
        {
            "items": [
                {
                    "id": "abc123",
                    "note_card": {
                        "display_title": "测试标题",
                        "cover": {"url_default": "https://example.com/cover.jpg"},
                        "user": {"nickname": "Hermes", "user_id": "user-1"},
                        "interact_info": {"liked_count": "42"},
                    },
                }
            ]
        },
    )
    assert result["success"] is True
    assert result["items"][0]["id"] == "abc123"
    assert result["items"][0]["likes"] == "42"



def test_tool_service_returns_unknown_tool_for_non_registry_name() -> None:
    service = SocialOpsToolService(config=SocialOpsConfig.from_env())
    result = service.execute("totally_unknown_tool", {})
    assert result["success"] is False
    assert result["error"] == "unknown_tool"
    assert result["status"] == "unknown"



def test_create_mcp_server_returns_named_server() -> None:
    server = create_mcp_server(SocialOpsConfig.from_env())
    assert server.name == "social-ops-kit"
