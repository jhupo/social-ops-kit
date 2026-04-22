from __future__ import annotations

from dataclasses import dataclass

from social_ops_kit.platforms.base import Capability


@dataclass(frozen=True)
class DouyinCapabilityCatalog:
    @staticmethod
    def stable() -> list[Capability]:
        return [
            Capability("check_auth", "Check whether Douyin web login cookies/session markers are present."),
            Capability("start_login", "Start a persistent QR login worker for Douyin web."),
            Capability("get_login_state", "Read QR/login completion state from the Douyin login worker."),
            Capability("stop_login", "Stop the persistent Douyin login worker."),
            Capability("search_content", "Search Douyin posts, creators, or videos for research and planning."),
            Capability("publish_image_post", "Publish a curated Douyin image-note workflow."),
            Capability("publish_image_post_with_music", "Publish a Douyin image-note workflow with background music selection or injection."),
            Capability("inspect_recent_posts", "Inspect creator-side recent post status for verification."),
            Capability("get_post_stats", "Fetch recent Douyin post performance metrics for review loops and monitoring."),
            Capability("get_note_detail", "Normalize one Douyin creator-side note detail payload into a stable detail object."),
            Capability("list_messages", "List creator-side Douyin private message threads or recent inbound messages."),
            Capability("reply_message", "Reply to a Douyin private message thread with generated or operator-approved text."),
            Capability("reply_visible_comments", "Reply to visible unreplied creator comments."),
        ]
