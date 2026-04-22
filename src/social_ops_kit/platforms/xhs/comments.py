from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class XhsCommentPostRequest:
    note_id: str
    xsec_token: str
    content: str


@dataclass(frozen=True)
class XhsCommentPostResult:
    success: bool
    note_id: str
    content: str
    error: str | None = None


@dataclass(frozen=True)
class XhsCommentReplyRequest:
    note_id: str
    xsec_token: str
    comment_id: str
    content: str


@dataclass(frozen=True)
class XhsCommentReplyResult:
    success: bool
    note_id: str
    comment_id: str
    error: str | None = None


class CommentReplyBackend(Protocol):
    def submit_reply(self, request: XhsCommentReplyRequest) -> XhsCommentReplyResult: ...

    def submit_comment(self, request: XhsCommentPostRequest) -> XhsCommentPostResult: ...


class InMemoryCommentReplyBackend:
    def submit_reply(self, request: XhsCommentReplyRequest) -> XhsCommentReplyResult:
        if not request.comment_id:
            return XhsCommentReplyResult(
                success=False,
                note_id=request.note_id,
                comment_id=request.comment_id,
                error="comment_id is required",
            )
        if not request.content.strip():
            return XhsCommentReplyResult(
                success=False,
                note_id=request.note_id,
                comment_id=request.comment_id,
                error="content is required",
            )
        return XhsCommentReplyResult(success=True, note_id=request.note_id, comment_id=request.comment_id)

    def submit_comment(self, request: XhsCommentPostRequest) -> XhsCommentPostResult:
        if not request.note_id.strip():
            return XhsCommentPostResult(
                success=False,
                note_id="",
                content=request.content,
                error="note_id is required",
            )
        if not request.content.strip():
            return XhsCommentPostResult(
                success=False,
                note_id=request.note_id,
                content=request.content,
                error="content is required",
            )
        return XhsCommentPostResult(success=True, note_id=request.note_id, content=request.content)


class XhsCommentRuntime:
    def __init__(self, backend: CommentReplyBackend | None = None) -> None:
        self._backend = backend or InMemoryCommentReplyBackend()

    def post_comment(self, request: XhsCommentPostRequest) -> XhsCommentPostResult:
        return self._backend.submit_comment(request)

    def reply_comment(self, request: XhsCommentReplyRequest) -> XhsCommentReplyResult:
        return self._backend.submit_reply(request)
