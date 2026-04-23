from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mcp.server import Server
from mcp import types

from social_ops_kit.config import SocialOpsConfig
from social_ops_kit.mcp.tools import build_mcp_tool_definitions, build_tool_manifest
from social_ops_kit.platforms.douyin.comments import DouyinCommentRuntime, DouyinVisibleComment
from social_ops_kit.platforms.douyin.inspect import DouyinInspectRuntime
from social_ops_kit.platforms.douyin.login import DouyinLoginRuntime
from social_ops_kit.platforms.douyin.messages import DouyinRealMessageRuntime
from social_ops_kit.platforms.douyin.publish import make_publish_request
from social_ops_kit.platforms.douyin.search import normalize_search_item as normalize_douyin_search_item
from social_ops_kit.platforms.xhs.client import XhsRuntime
from social_ops_kit.platforms.xhs.comments import (
    XhsCommentPostRequest,
    XhsCommentReplyRequest,
)
from social_ops_kit.platforms.xhs.live import XhsLiveRuntime
from social_ops_kit.platforms.xhs.drafts import XhsDraftRequest
from social_ops_kit.platforms.xhs.interactions import (
    XhsCommentFavoriteRequest,
    XhsCommentLikeRequest,
    XhsFeedFavoriteRequest,
    XhsFeedLikeRequest,
)
from social_ops_kit.platforms.xhs.notifications import XhsNotificationRuntime
from social_ops_kit.platforms.xhs.posts import XhsPostStatsRuntime
from social_ops_kit.platforms.xhs.search import normalize_search_item as normalize_xhs_search_item
from social_ops_kit.platforms.messages import MessageRuntime
from social_ops_kit.registry import build_default_registry


@dataclass(frozen=True)
class ServerBlueprint:
    name: str
    version: str
    instructions: str
    tools: list[dict[str, object]]


class SocialOpsToolService:
    def __init__(self, config: SocialOpsConfig | None = None) -> None:
        self._config = config or SocialOpsConfig.from_env()
        self._declared_tools = {tool.name for tool in build_default_registry()}
        self._draft_records: dict[str, object] = {}

    def execute(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        handlers = {
            "douyin_check_auth": self._douyin_check_auth,
            "douyin_start_login": self._douyin_start_login,
            "douyin_get_login_state": self._douyin_get_login_state,
            "douyin_stop_login": self._douyin_stop_login,
            "douyin_search_content": self._douyin_search_content,
            "douyin_publish_image_post": self._douyin_publish_image_post,
            "douyin_publish_image_post_with_music": self._douyin_publish_with_music,
            "douyin_inspect_recent_posts": self._douyin_inspect_recent_posts,
            "douyin_get_post_stats": self._douyin_get_post_stats,
            "douyin_get_note_detail": self._douyin_get_note_detail,
            "douyin_reply_visible_comments": self._douyin_reply_visible_comments,
            "douyin_list_messages": self._douyin_list_messages,
            "douyin_reply_message": self._douyin_reply_message,
            "xhs_check_auth": self._xhs_check_auth,
            "xhs_search_content": self._xhs_search_content,
            "xhs_create_draft": self._xhs_create_draft,
            "xhs_get_draft": self._xhs_get_draft,
            "xhs_list_drafts": self._xhs_list_drafts,
            "xhs_delete_draft": self._xhs_delete_draft,
            "xhs_delete_note": self._xhs_delete_note,
            "xhs_update_draft": self._xhs_update_draft,
            "xhs_publish_draft": self._xhs_publish_draft,
            "xhs_like_feed": self._xhs_like_feed,
            "xhs_favorite_feed": self._xhs_favorite_feed,
            "xhs_like_comment": self._xhs_like_comment,
            "xhs_favorite_comment": self._xhs_favorite_comment,
            "xhs_post_comment": self._xhs_post_comment,
            "xhs_create_and_publish_draft": self._xhs_create_and_publish_draft,
            "xhs_get_my_notes": self._xhs_get_my_notes,
            "xhs_get_note_detail": self._xhs_get_note_detail,
            "xhs_get_notifications": self._xhs_get_notifications,
            "xhs_get_post_stats": self._xhs_get_post_stats,
            "xhs_list_messages": self._xhs_list_messages,
            "xhs_reply_message": self._xhs_reply_message,
            "xhs_reply_comment": self._xhs_reply_comment,
        }
        handler = handlers.get(tool_name)
        if handler is None:
            if tool_name in self._declared_tools:
                return {
                    "success": False,
                    "tool": tool_name,
                    "error": "not_implemented_in_runtime_yet",
                    "implemented": False,
                    "status": "declared_not_implemented",
                }
            return {
                "success": False,
                "tool": tool_name,
                "error": "unknown_tool",
                "implemented": False,
                "status": "unknown",
            }
        return handler(arguments)

    def _douyin_check_auth(self, arguments: dict[str, Any]) -> dict[str, Any]:
        del arguments
        runtime = DouyinLoginRuntime.from_config(self._config)
        state = runtime.get_login_state()
        authenticated = bool(
            state.get("authenticated")
            or state.get("logged_in")
            or state.get("login_complete")
            or state.get("status") in {"logged_in", "success", "authenticated"}
        )
        return {
            "success": True,
            "platform": "douyin",
            "authenticated": authenticated,
            "state": state,
            "state_path": str(runtime.paths.login_state_file),
        }

    def _douyin_start_login(self, arguments: dict[str, Any]) -> dict[str, Any]:
        runtime = DouyinLoginRuntime.from_config(self._config)
        return runtime.start_login(script_name=str(arguments.get("script_name") or "douyin_single_session.js"))

    def _douyin_get_login_state(self, arguments: dict[str, Any]) -> dict[str, Any]:
        del arguments
        runtime = DouyinLoginRuntime.from_config(self._config)
        return runtime.login_status()

    def _douyin_stop_login(self, arguments: dict[str, Any]) -> dict[str, Any]:
        del arguments
        runtime = DouyinLoginRuntime.from_config(self._config)
        return runtime.stop_login()

    def _douyin_search_content(self, arguments: dict[str, Any]) -> dict[str, Any]:
        items = list(arguments.get("items") or [])
        limit = arguments.get("limit")
        normalized = [normalize_douyin_search_item(item) for item in items]
        sliced = normalized[: int(limit)] if limit is not None else normalized
        return {
            "success": True,
            "items": [item.as_dict() for item in sliced],
        }

    def _douyin_publish_image_post(self, arguments: dict[str, Any]) -> dict[str, Any]:
        runtime = DouyinLoginRuntime.from_config(self._config)
        request = make_publish_request(
            paths=runtime.paths,
            title=str(arguments.get("title") or ""),
            copy=str(arguments.get("copy") or ""),
            images=tuple(arguments.get("images") or ()),
            hashtags=tuple(arguments.get("hashtags") or ()),
        )
        return {
            "success": True,
            "tool": "douyin_publish_image_post",
            "request": request.as_dict(),
        }

    def _douyin_publish_with_music(self, arguments: dict[str, Any]) -> dict[str, Any]:
        runtime = DouyinLoginRuntime.from_config(self._config)
        request = make_publish_request(
            paths=runtime.paths,
            title=str(arguments.get("title") or ""),
            copy=str(arguments.get("copy") or ""),
            images=tuple(arguments.get("images") or ()),
            hashtags=tuple(arguments.get("hashtags") or ()),
            music_id=arguments.get("music_id"),
            music_title=arguments.get("music_title"),
            music_author=arguments.get("music_author"),
            music_duration=arguments.get("music_duration"),
        )
        return {
            "success": True,
            "tool": "douyin_publish_image_post_with_music",
            "request": request.as_dict(),
        }

    def _douyin_inspect_recent_posts(self, arguments: dict[str, Any]) -> dict[str, Any]:
        runtime = DouyinInspectRuntime()
        snapshot = runtime.build_snapshot(str(arguments.get("text") or ""))
        limit = arguments.get("limit")
        cards = snapshot.cards[: int(limit)] if limit is not None else snapshot.cards
        return {
            "success": True,
            "snapshot": {
                "cards": [{"lines": list(card.lines)} for card in cards],
                "text": snapshot.text_sample,
            },
        }

    def _douyin_get_post_stats(self, arguments: dict[str, Any]) -> dict[str, Any]:
        runtime = DouyinInspectRuntime()
        limit = arguments.get("limit")
        items = runtime.build_post_stats(
            str(arguments.get("text") or ""),
            limit=int(limit) if limit is not None else None,
        )
        return {
            "success": True,
            "items": [item.as_dict() for item in items],
        }

    def _douyin_get_note_detail(self, arguments: dict[str, Any]) -> dict[str, Any]:
        runtime = DouyinInspectRuntime()
        item = runtime.build_note_detail(
            str(arguments.get("text") or ""),
            cover_url=str(arguments.get("cover_url") or ""),
            status=str(arguments.get("status") or ""),
        )
        return {
            "success": True,
            "item": item.as_dict(),
        }

    def _douyin_reply_visible_comments(self, arguments: dict[str, Any]) -> dict[str, Any]:
        runtime = DouyinCommentRuntime()
        comments = tuple(arguments.get("comments") or ())
        attempts = [
            runtime.build_attempt(
                DouyinVisibleComment(
                    user_name=str(item.get("user_name") or ""),
                    text=str(item.get("text") or ""),
                    raw=str(item.get("raw") or ""),
                    has_author_badge=bool(item.get("has_author_badge") or False),
                )
            )
            for item in comments
        ]
        return {
            "success": True,
            "attempts": [
                {
                    "user_name": attempt.user_name,
                    "comment": attempt.comment,
                    "kind": attempt.kind,
                    "reply": attempt.reply,
                    "status": attempt.status,
                }
                for attempt in attempts
            ],
        }

    def _douyin_list_messages(self, arguments: dict[str, Any]) -> dict[str, Any]:
        runtime = MessageRuntime()
        limit = arguments.get("limit")
        provided_threads = list(arguments.get("threads") or [])
        if provided_threads:
            items = runtime.list_threads(provided_threads, limit=int(limit) if limit is not None else None)
            return {"success": True, "items": [item.as_dict() for item in items], "source": "input_threads"}

        real_runtime = DouyinRealMessageRuntime.from_config(self._config)
        items, source = real_runtime.list_threads(limit=int(limit) if limit is not None else None)
        return {"success": True, "items": [item.as_dict() for item in items], "source": source}

    def _douyin_reply_message(self, arguments: dict[str, Any]) -> dict[str, Any]:
        real_runtime = DouyinRealMessageRuntime.from_config(self._config)
        return real_runtime.reply_message(
            str(arguments.get("thread_id") or ""),
            str(arguments.get("content") or ""),
        )

    def _xhs_check_auth(self, arguments: dict[str, Any]) -> dict[str, Any]:
        del arguments
        runtime = XhsRuntime.from_config(self._config)
        session_path = runtime.paths.profile_dir / "session.json"
        authenticated = session_path.exists()
        session_payload: dict[str, Any] = {}
        if authenticated:
            import json

            session_payload = json.loads(session_path.read_text(encoding="utf-8"))
            authenticated = bool(session_payload.get("logged_in", True))
        return {
            "success": True,
            "platform": "xhs",
            "authenticated": authenticated,
            "session_path": str(session_path),
            "session": session_payload,
        }

    def _xhs_search_content(self, arguments: dict[str, Any]) -> dict[str, Any]:
        items = list(arguments.get("items") or [])
        limit = arguments.get("limit")
        normalized = [normalize_xhs_search_item(item) for item in items]
        sliced = normalized[: int(limit)] if limit is not None else normalized
        return {
            "success": True,
            "items": [item.as_dict() for item in sliced],
        }

    def _xhs_create_draft(self, arguments: dict[str, Any]) -> dict[str, Any]:
        runtime = XhsRuntime.from_config(self._config)
        draft_runtime = runtime.draft_runtime()
        request = XhsDraftRequest(
            title=str(arguments.get("title") or ""),
            content=str(arguments.get("content") or ""),
            screenshots=tuple(arguments.get("screenshots") or ()),
            tags=tuple(arguments.get("tags") or ()),
            style=str(arguments.get("style") or "minimal"),
        )
        record = draft_runtime.create_draft(request)
        self._draft_records[record.draft_id] = record
        return {
            "success": True,
            "draft": {
                "draft_id": record.draft_id,
                "title": record.title,
                "content": record.content,
                "tags": list(record.tags),
                "screenshots": list(record.screenshots),
                "generated_images": list(record.generated_images),
                "style": record.style,
            },
        }

    def _xhs_get_draft(self, arguments: dict[str, Any]) -> dict[str, Any]:
        draft_id = str(arguments.get("draft_id") or "")
        record = self._draft_records.get(draft_id)
        if record is None:
            return {"success": False, "draft_id": draft_id, "error": "draft_not_found"}
        return {
            "success": True,
            "draft": {
                "draft_id": record.draft_id,
                "title": record.title,
                "content": record.content,
                "tags": list(record.tags),
                "screenshots": list(record.screenshots),
                "generated_images": list(record.generated_images),
                "style": record.style,
            },
        }

    def _xhs_list_drafts(self, arguments: dict[str, Any]) -> dict[str, Any]:
        del arguments
        items = [
            {
                "draft_id": record.draft_id,
                "title": record.title,
                "content": record.content,
                "tags": list(record.tags),
                "screenshots": list(record.screenshots),
                "generated_images": list(record.generated_images),
                "style": record.style,
            }
            for record in self._draft_records.values()
        ]
        return {"success": True, "items": items}

    def _xhs_delete_draft(self, arguments: dict[str, Any]) -> dict[str, Any]:
        draft_id = str(arguments.get("draft_id") or "")
        record = self._draft_records.pop(draft_id, None)
        if record is None:
            return {"success": False, "draft_id": draft_id, "error": "draft_not_found"}
        return {"success": True, "draft_id": draft_id, "title": record.title}

    def _xhs_delete_note(self, arguments: dict[str, Any]) -> dict[str, Any]:
        note_id = str(arguments.get("note_id") or "").strip()
        if not note_id:
            return {"success": False, "note_id": "", "error": "note_id is required"}
        return {
            "success": True,
            "note_id": note_id,
            "title": str(arguments.get("title") or ""),
        }

    def _xhs_update_draft(self, arguments: dict[str, Any]) -> dict[str, Any]:
        draft_id = str(arguments.get("draft_id") or "")
        record = self._draft_records.get(draft_id)
        if record is None:
            return {"success": False, "draft_id": draft_id, "error": "draft_not_found"}
        updated = record.__class__(
            draft_id=record.draft_id,
            title=str(arguments.get("title") or record.title),
            content=str(arguments.get("content") or record.content),
            tags=tuple(arguments.get("tags") or record.tags),
            screenshots=tuple(arguments.get("screenshots") or record.screenshots),
            generated_images=record.generated_images,
            style=str(arguments.get("style") or record.style),
        )
        self._draft_records[draft_id] = updated
        return {
            "success": True,
            "draft": {
                "draft_id": updated.draft_id,
                "title": updated.title,
                "content": updated.content,
                "tags": list(updated.tags),
                "screenshots": list(updated.screenshots),
                "generated_images": list(updated.generated_images),
                "style": updated.style,
            },
        }

    def _xhs_like_feed(self, arguments: dict[str, Any]) -> dict[str, Any]:
        runtime = XhsRuntime.from_config(self._config)
        result = runtime.interaction_runtime().like_feed(
            XhsFeedLikeRequest(
                note_id=str(arguments.get("note_id") or ""),
                xsec_token=str(arguments.get("xsec_token") or ""),
                unlike=bool(arguments.get("unlike") or False),
            )
        )
        return {
            "success": result.success,
            "note_id": result.note_id,
            "liked": result.liked,
            "xsec_token": result.xsec_token,
            "error": result.error,
        }

    def _xhs_favorite_feed(self, arguments: dict[str, Any]) -> dict[str, Any]:
        runtime = XhsRuntime.from_config(self._config)
        result = runtime.interaction_runtime().favorite_feed(
            XhsFeedFavoriteRequest(
                note_id=str(arguments.get("note_id") or ""),
                xsec_token=str(arguments.get("xsec_token") or ""),
                unfavorite=bool(arguments.get("unfavorite") or False),
            )
        )
        return {
            "success": result.success,
            "note_id": result.note_id,
            "favorited": result.favorited,
            "xsec_token": result.xsec_token,
            "error": result.error,
        }

    def _xhs_like_comment(self, arguments: dict[str, Any]) -> dict[str, Any]:
        runtime = XhsRuntime.from_config(self._config)
        result = runtime.interaction_runtime().like_comment(
            XhsCommentLikeRequest(
                note_id=str(arguments.get("note_id") or ""),
                comment_id=str(arguments.get("comment_id") or ""),
                xsec_token=str(arguments.get("xsec_token") or ""),
                unlike=bool(arguments.get("unlike") or False),
            )
        )
        return {
            "success": result.success,
            "note_id": result.note_id,
            "comment_id": result.comment_id,
            "liked": result.liked,
            "xsec_token": result.xsec_token,
            "error": result.error,
        }

    def _xhs_favorite_comment(self, arguments: dict[str, Any]) -> dict[str, Any]:
        runtime = XhsRuntime.from_config(self._config)
        result = runtime.interaction_runtime().favorite_comment(
            XhsCommentFavoriteRequest(
                note_id=str(arguments.get("note_id") or ""),
                comment_id=str(arguments.get("comment_id") or ""),
                xsec_token=str(arguments.get("xsec_token") or ""),
                unfavorite=bool(arguments.get("unfavorite") or False),
            )
        )
        return {
            "success": result.success,
            "note_id": result.note_id,
            "comment_id": result.comment_id,
            "favorited": result.favorited,
            "xsec_token": result.xsec_token,
            "error": result.error,
        }

    def _xhs_post_comment(self, arguments: dict[str, Any]) -> dict[str, Any]:
        runtime = XhsLiveRuntime.from_config(self._config)
        result = runtime.post_comment(
            note_id=str(arguments.get("note_id") or ""),
            xsec_token=str(arguments.get("xsec_token") or ""),
            content=str(arguments.get("content") or ""),
            account=str(arguments.get("account") or "") or None,
        )
        payload = dict(result.get("result") or {}) if result.get("success") else {}
        return {
            "success": bool(result.get("success")),
            "note_id": str(arguments.get("note_id") or ""),
            "content": str(arguments.get("content") or ""),
            "account": result.get("account"),
            "error": payload.get("error") or result.get("error"),
            "raw": payload or result,
        }

    def _xhs_publish_draft(self, arguments: dict[str, Any]) -> dict[str, Any]:
        runtime = XhsRuntime.from_config(self._config)
        draft_runtime = runtime.draft_runtime()
        draft_id = str(arguments.get("draft_id") or "")
        record = self._draft_records.get(draft_id)
        if record is None:
            return {
                "success": False,
                "draft_id": draft_id,
                "error": "draft_not_found",
            }
        publish_result = draft_runtime._publisher.publish(record, account=arguments.get("account"))
        return {
            "success": publish_result.success,
            "publish_result": {
                "draft_id": publish_result.draft_id,
                "account": publish_result.account,
                "note_id": publish_result.note_id,
                "success": publish_result.success,
            },
        }

    def _xhs_create_and_publish_draft(self, arguments: dict[str, Any]) -> dict[str, Any]:
        runtime = XhsRuntime.from_config(self._config)
        draft_runtime = runtime.draft_runtime()
        request = XhsDraftRequest(
            title=str(arguments.get("title") or ""),
            content=str(arguments.get("content") or ""),
            screenshots=tuple(arguments.get("screenshots") or ()),
            tags=tuple(arguments.get("tags") or ()),
            style=str(arguments.get("style") or "minimal"),
        )
        record, publish_result = draft_runtime.create_and_publish(
            request,
            account=arguments.get("account"),
        )
        return {
            "success": publish_result.success,
            "draft": {
                "draft_id": record.draft_id,
                "title": record.title,
                "generated_images": list(record.generated_images),
                "style": record.style,
            },
            "publish_result": {
                "draft_id": publish_result.draft_id,
                "account": publish_result.account,
                "note_id": publish_result.note_id,
                "success": publish_result.success,
            },
        }

    def _xhs_get_my_notes(self, arguments: dict[str, Any]) -> dict[str, Any]:
        runtime = XhsRuntime.from_config(self._config)
        post_runtime = runtime.post_stats_runtime()
        limit = arguments.get("limit")
        items = post_runtime.list_my_notes(list(arguments.get("notes") or []), limit=int(limit) if limit is not None else None)
        return {
            "success": True,
            "items": [item.as_dict() for item in items],
        }

    def _xhs_get_note_detail(self, arguments: dict[str, Any]) -> dict[str, Any]:
        runtime = XhsRuntime.from_config(self._config)
        post_runtime = runtime.post_stats_runtime()
        item = post_runtime.get_note_detail(dict(arguments.get("note") or {}))
        return {
            "success": True,
            "item": item.as_dict(),
        }

    def _xhs_get_notifications(self, arguments: dict[str, Any]) -> dict[str, Any]:
        provided = list(arguments.get("notifications") or [])
        if provided:
            runtime = XhsRuntime.from_config(self._config)
            notification_runtime = runtime.notification_runtime()
            limit = arguments.get("limit")
            items = notification_runtime.parse_notifications(
                provided,
                limit=int(limit) if limit is not None else None,
            )
            return {
                "success": True,
                "items": [item.as_dict() for item in items],
                "source": "input_notifications",
            }

        live_runtime = XhsLiveRuntime.from_config(self._config)
        result = live_runtime.get_notifications(
            type_=str(arguments.get("type") or "all"),
            limit=int(arguments.get("limit") or 20),
            account=str(arguments.get("account") or "") or None,
        )
        payload = dict(result.get("result") or {}) if result.get("success") else {}
        items: list[dict[str, Any]] = []
        for key in ("mentions", "likes", "connections"):
            for entry in payload.get(key) or []:
                items.append({
                    "id": entry.get("id") or "",
                    "type": key[:-1] if key.endswith('s') else key,
                    "user_name": ((entry.get("user") or {}).get("nickname") or ""),
                    "content": entry.get("commentContent") or entry.get("title") or "",
                    "note_id": entry.get("noteId") or "",
                    "comment_id": entry.get("commentId") or "",
                    "xsec_token": entry.get("xsecToken") or "",
                    "created_at": entry.get("time") or "",
                    "raw": entry,
                })
        return {
            "success": bool(result.get("success")),
            "items": items,
            "source": "xhs_live_notifications",
            "account": result.get("account"),
            "error": payload.get("error") or result.get("error"),
            "raw": payload or result,
        }

    def _xhs_get_post_stats(self, arguments: dict[str, Any]) -> dict[str, Any]:
        runtime = XhsRuntime.from_config(self._config)
        post_runtime = runtime.post_stats_runtime()
        limit = arguments.get("limit")
        items = post_runtime.parse_notes(list(arguments.get("notes") or []), limit=int(limit) if limit is not None else None)
        return {
            "success": True,
            "items": [item.as_dict() for item in items],
        }

    def _xhs_list_messages(self, arguments: dict[str, Any]) -> dict[str, Any]:
        runtime = MessageRuntime()
        limit = arguments.get("limit")
        items = runtime.list_threads(list(arguments.get("threads") or []), limit=int(limit) if limit is not None else None)
        return {"success": True, "items": [item.as_dict() for item in items]}

    def _xhs_reply_message(self, arguments: dict[str, Any]) -> dict[str, Any]:
        runtime = MessageRuntime()
        reply = runtime.reply_message(str(arguments.get("thread_id") or ""), str(arguments.get("content") or ""))
        return {"success": True, **reply.as_dict()}

    def _xhs_reply_comment(self, arguments: dict[str, Any]) -> dict[str, Any]:
        runtime = XhsLiveRuntime.from_config(self._config)
        result = runtime.reply_comment(
            note_id=str(arguments.get("note_id") or ""),
            xsec_token=str(arguments.get("xsec_token") or ""),
            comment_id=str(arguments.get("comment_id") or ""),
            content=str(arguments.get("content") or ""),
            account=str(arguments.get("account") or "") or None,
        )
        payload = dict(result.get("result") or {}) if result.get("success") else {}
        return {
            "success": bool(result.get("success")),
            "note_id": str(arguments.get("note_id") or ""),
            "comment_id": str(arguments.get("comment_id") or ""),
            "account": result.get("account"),
            "error": payload.get("error") or result.get("error"),
            "raw": payload or result,
        }


def build_server_blueprint() -> ServerBlueprint:
    return ServerBlueprint(
        name="social-ops-kit",
        version="0.1.0",
        instructions=(
            "Stable MCP surface for Douyin and Xiaohongshu operations. "
            "Only expose curated, open-source-safe capabilities."
        ),
        tools=build_tool_manifest(),
    )


def create_mcp_server(config: SocialOpsConfig | None = None) -> Server:
    blueprint = build_server_blueprint()
    tool_service = SocialOpsToolService(config=config)
    server = Server(
        blueprint.name,
        version=blueprint.version,
        instructions=blueprint.instructions,
    )

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return build_mcp_tool_definitions()

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        return tool_service.execute(name, arguments)

    return server
