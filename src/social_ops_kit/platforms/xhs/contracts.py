from __future__ import annotations

from dataclasses import dataclass

from social_ops_kit.platforms.base import Capability


@dataclass(frozen=True)
class XhsCapabilityCatalog:
    @staticmethod
    def stable() -> list[Capability]:
        return [
            Capability("check_auth", "Check whether the current Xiaohongshu account is logged in."),
            Capability("search_content", "Search Xiaohongshu notes or videos for research and topic analysis."),
            Capability("create_draft", "Create a Xiaohongshu image-note draft from text and screenshots."),
            Capability("get_draft", "Fetch a previously created Xiaohongshu draft by id."),
            Capability("list_drafts", "List currently available Xiaohongshu drafts in the local runtime cache."),
            Capability("delete_draft", "Delete a previously created Xiaohongshu draft from the local runtime cache."),
            Capability("delete_note", "Delete a published Xiaohongshu note by id from the normalized management surface."),
            Capability("update_draft", "Update fields on a previously created Xiaohongshu draft in the local runtime cache."),
            Capability("publish_draft", "Publish a previously created Xiaohongshu draft."),
            Capability("like_feed", "Like or unlike a Xiaohongshu note feed item."),
            Capability("favorite_feed", "Favorite or unfavorite a Xiaohongshu note feed item."),
            Capability("like_comment", "Like or unlike a Xiaohongshu comment."),
            Capability("favorite_comment", "Favorite or unfavorite a Xiaohongshu comment."),
            Capability("post_comment", "Post a new top-level comment on a Xiaohongshu note."),
            Capability("create_and_publish_draft", "Run the one-click draft + publish flow."),
            Capability("get_my_notes", "Fetch published notes from creator center."),
            Capability("get_note_detail", "Normalize one Xiaohongshu note detail payload into a stable detail object."),
            Capability("get_post_stats", "Fetch recent Xiaohongshu note performance metrics for review loops and monitoring."),
            Capability("get_notifications", "Fetch comment / mention notifications."),
            Capability("list_messages", "List creator-side Xiaohongshu private message threads or recent inbound messages."),
            Capability("reply_message", "Reply to a Xiaohongshu private message thread with generated or operator-approved text."),
            Capability("reply_comment", "Reply to a specific creator-side comment."),
        ]
