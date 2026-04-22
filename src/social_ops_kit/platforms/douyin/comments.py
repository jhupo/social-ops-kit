from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1
from typing import Any


AD_PATTERN = (
    r"加微|加v|vx|v信|微[\s\-_:：]?信|私聊|私信我|联系我|引流|推广|代发|代做|兼职|赚钱|返利|"
    r"代理|课程|培训|\+v|q群|qq群|飞机|tg|telegram|whatsapp|线下|合作请私|商务合作"
)
HOSTILE_PATTERN = r"傻逼|煞笔|沙比|垃圾|废物|滚|去死|脑残|智障|狗东西|有病|恶心|骗[子人]?|死妈|妈的|他妈|你妈|装什么|神经病"


@dataclass(frozen=True)
class DouyinVisibleComment:
    user_name: str
    text: str
    raw: str = ""
    has_author_badge: bool = False


@dataclass(frozen=True)
class DouyinReplyAttempt:
    user_name: str
    comment: str
    kind: str
    reply: str | None
    status: str


FRIENDLY_REPLIES = (
    "这条我看到了，后面继续聊。",
    "收到，欢迎继续留言。",
    "看见啦，有想聊的可以继续说。",
    "这条先接住，后面可以展开聊。",
)
HOSTILE_REPLIES = (
    "说话注意分寸。这里欢迎讨论，不欢迎冒犯。",
    "想交流可以好好说，带情绪挑衅这边不接。",
    "别在这里逞口舌之快，内容区不是给你发泄情绪的。",
    "有观点就正常表达，阴阳怪气和冒犯言论不会被惯着。",
)


def comment_key(comment: DouyinVisibleComment) -> str:
    basis = f"{comment.user_name}|{comment.text}|{comment.raw}"
    return sha1(basis.encode("utf-8")).hexdigest()


def classify_comment(text: str) -> str:
    import re

    normalized = str(text or "").strip()
    if re.search(AD_PATTERN, normalized, re.IGNORECASE):
        return "ad"
    if re.search(HOSTILE_PATTERN, normalized, re.IGNORECASE):
        return "hostile"
    return "normal"


def _pick_by_text(text: str, options: tuple[str, ...]) -> str:
    total = sum(ord(ch) for ch in str(text or ""))
    return options[total % len(options)]


def make_reply(text: str) -> str | None:
    kind = classify_comment(text)
    normalized = str(text or "").strip()
    if kind == "ad":
        return None
    if kind == "hostile":
        return _pick_by_text(normalized, HOSTILE_REPLIES)
    return _pick_by_text(normalized, FRIENDLY_REPLIES)


class DouyinCommentRuntime:
    def build_attempt(self, comment: DouyinVisibleComment) -> DouyinReplyAttempt:
        kind = classify_comment(comment.text)
        reply = make_reply(comment.text)
        status = "intercepted" if kind == "ad" else "ready"
        return DouyinReplyAttempt(
            user_name=comment.user_name,
            comment=comment.text,
            kind=kind,
            reply=reply,
            status=status,
        )
