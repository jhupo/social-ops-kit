from __future__ import annotations

from dataclasses import dataclass

from social_ops_kit.config import SocialOpsConfig
from social_ops_kit.platforms.xhs.browser_session import XhsBrowserSessionConfig, XhsPathSet
from social_ops_kit.platforms.xhs.comments import (
    XhsCommentPostRequest,
    XhsCommentReplyRequest,
    XhsCommentRuntime,
)
from social_ops_kit.platforms.xhs.drafts import XhsDraftRuntime, XhsDraftRequest
from social_ops_kit.platforms.xhs.interactions import XhsInteractionRuntime
from social_ops_kit.platforms.xhs.notifications import XhsNotificationRuntime
from social_ops_kit.platforms.xhs.posts import XhsPostStatsRuntime
from social_ops_kit.platforms.xhs.search import SearchFilters, SearchSessionProtocol, XhsSearchRuntime


@dataclass(frozen=True)
class XhsRuntime:
    paths: XhsPathSet
    browser: XhsBrowserSessionConfig

    @classmethod
    def from_config(cls, config: SocialOpsConfig) -> "XhsRuntime":
        return cls(
            paths=XhsPathSet.from_config(config),
            browser=XhsBrowserSessionConfig.from_config(config),
        )

    def search_runtime(self, session: SearchSessionProtocol) -> XhsSearchRuntime:
        return XhsSearchRuntime(session)

    def draft_runtime(self) -> XhsDraftRuntime:
        return XhsDraftRuntime.with_defaults(self.paths)

    def post_stats_runtime(self) -> XhsPostStatsRuntime:
        return XhsPostStatsRuntime()

    def notification_runtime(self) -> XhsNotificationRuntime:
        return XhsNotificationRuntime()

    def comment_runtime(self) -> XhsCommentRuntime:
        return XhsCommentRuntime()

    def interaction_runtime(self) -> XhsInteractionRuntime:
        return XhsInteractionRuntime()


__all__ = [
    "SearchFilters",
    "SearchSessionProtocol",
    "XhsCommentPostRequest",
    "XhsCommentReplyRequest",
    "XhsCommentRuntime",
    "XhsDraftRequest",
    "XhsDraftRuntime",
    "XhsNotificationRuntime",
    "XhsPostStatsRuntime",
    "XhsRuntime",
    "XhsSearchRuntime",
]
