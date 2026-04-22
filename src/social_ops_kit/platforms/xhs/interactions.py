from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class XhsFeedLikeRequest:
    note_id: str
    xsec_token: str = ""
    unlike: bool = False


@dataclass(frozen=True)
class XhsFeedFavoriteRequest:
    note_id: str
    xsec_token: str = ""
    unfavorite: bool = False


@dataclass(frozen=True)
class XhsFeedLikeResult:
    success: bool
    note_id: str
    liked: bool
    xsec_token: str = ""
    error: str | None = None


@dataclass(frozen=True)
class XhsFeedFavoriteResult:
    success: bool
    note_id: str
    favorited: bool
    xsec_token: str = ""
    error: str | None = None


@dataclass(frozen=True)
class XhsCommentLikeRequest:
    note_id: str
    comment_id: str
    xsec_token: str = ""
    unlike: bool = False


@dataclass(frozen=True)
class XhsCommentLikeResult:
    success: bool
    note_id: str
    comment_id: str
    liked: bool
    xsec_token: str = ""
    error: str | None = None


@dataclass(frozen=True)
class XhsCommentFavoriteRequest:
    note_id: str
    comment_id: str
    xsec_token: str = ""
    unfavorite: bool = False


@dataclass(frozen=True)
class XhsCommentFavoriteResult:
    success: bool
    note_id: str
    comment_id: str
    favorited: bool
    xsec_token: str = ""
    error: str | None = None


class XhsInteractionRuntime:
    def like_feed(self, request: XhsFeedLikeRequest) -> XhsFeedLikeResult:
        note_id = str(request.note_id or "").strip()
        if not note_id:
            return XhsFeedLikeResult(
                success=False,
                note_id="",
                liked=not request.unlike,
                xsec_token=str(request.xsec_token or ""),
                error="note_id is required",
            )
        return XhsFeedLikeResult(
            success=True,
            note_id=note_id,
            liked=not bool(request.unlike),
            xsec_token=str(request.xsec_token or ""),
        )

    def favorite_feed(self, request: XhsFeedFavoriteRequest) -> XhsFeedFavoriteResult:
        note_id = str(request.note_id or "").strip()
        if not note_id:
            return XhsFeedFavoriteResult(
                success=False,
                note_id="",
                favorited=not request.unfavorite,
                xsec_token=str(request.xsec_token or ""),
                error="note_id is required",
            )
        return XhsFeedFavoriteResult(
            success=True,
            note_id=note_id,
            favorited=not bool(request.unfavorite),
            xsec_token=str(request.xsec_token or ""),
        )

    def like_comment(self, request: XhsCommentLikeRequest) -> XhsCommentLikeResult:
        note_id = str(request.note_id or "").strip()
        comment_id = str(request.comment_id or "").strip()
        if not note_id:
            return XhsCommentLikeResult(
                success=False,
                note_id="",
                comment_id=comment_id,
                liked=not request.unlike,
                xsec_token=str(request.xsec_token or ""),
                error="note_id is required",
            )
        if not comment_id:
            return XhsCommentLikeResult(
                success=False,
                note_id=note_id,
                comment_id="",
                liked=not request.unlike,
                xsec_token=str(request.xsec_token or ""),
                error="comment_id is required",
            )
        return XhsCommentLikeResult(
            success=True,
            note_id=note_id,
            comment_id=comment_id,
            liked=not bool(request.unlike),
            xsec_token=str(request.xsec_token or ""),
        )

    def favorite_comment(self, request: XhsCommentFavoriteRequest) -> XhsCommentFavoriteResult:
        note_id = str(request.note_id or "").strip()
        comment_id = str(request.comment_id or "").strip()
        if not note_id:
            return XhsCommentFavoriteResult(
                success=False,
                note_id="",
                comment_id=comment_id,
                favorited=not request.unfavorite,
                xsec_token=str(request.xsec_token or ""),
                error="note_id is required",
            )
        if not comment_id:
            return XhsCommentFavoriteResult(
                success=False,
                note_id=note_id,
                comment_id="",
                favorited=not request.unfavorite,
                xsec_token=str(request.xsec_token or ""),
                error="comment_id is required",
            )
        return XhsCommentFavoriteResult(
            success=True,
            note_id=note_id,
            comment_id=comment_id,
            favorited=not bool(request.unfavorite),
            xsec_token=str(request.xsec_token or ""),
        )
