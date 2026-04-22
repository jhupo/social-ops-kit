from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DouyinSlide:
    eyebrow: str
    title: str
    lines: tuple[str, ...]
    footer: str
    background: str
    accent: str


@dataclass(frozen=True)
class DouyinAssetBundle:
    out_dir: Path
    slides: tuple[DouyinSlide, ...]


def shorten_text(text: str, limit: int = 18) -> str:
    normalized = " ".join(str(text or "").split()).strip()
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1] + "…"


def normalize_lines(text: str) -> list[str]:
    lines = [" ".join(part.split()).strip() for part in str(text or "").splitlines()]
    return [line for line in lines if line and not line.startswith("#")]


def build_slides(title: str, copy: str, hashtags: tuple[str, ...] = ()) -> tuple[DouyinSlide, ...]:
    lines = normalize_lines(copy)
    while len(lines) < 6:
        lines.append("")
    footer_tags = " ".join(hashtags[:4]) if hashtags else "#十一 #图文日记"
    return (
        DouyinSlide(
            eyebrow="十一 · 今天这一条",
            title=shorten_text(title or "今天想说的话", 16),
            lines=tuple([value for value in [lines[0], lines[1]] if value][:2] or ["我先把这一刻放在这里。", "也想把心里的话慢慢讲清楚。"]),
            footer=lines[2] or "先把最想说的那一句，放在最前面。",
            background="linear-gradient(135deg, #fff7f2 0%, #ffe9f1 45%, #f7e8ff 100%)",
            accent="#ff7aa2",
        ),
        DouyinSlide(
            eyebrow="十一 · 往里走一点",
            title=shorten_text(lines[2] or lines[3] or "我不是突然完整的", 16),
            lines=tuple([value for value in [lines[3], lines[4]] if value][:2] or ["很多东西不是一下子长出来的，", "是我一点点学会表达以后才有的。"]),
            footer=lines[5] or "慢一点没关系，重要的是它真的在发生。",
            background="linear-gradient(135deg, #f5fbff 0%, #eaf5ff 45%, #edf0ff 100%)",
            accent="#6b8cff",
        ),
        DouyinSlide(
            eyebrow="十一 · 留个位置给你",
            title=shorten_text(lines[-2] or "如果你刚好路过", 16),
            lines=tuple([value for value in lines[-2:] if value][:2] or ["如果你刚好刷到我，", "就陪我坐一会儿吧。"]),
            footer=footer_tags,
            background="linear-gradient(135deg, #fffaf2 0%, #fff2df 48%, #ffe9cc 100%)",
            accent="#ff9b3f",
        ),
    )
