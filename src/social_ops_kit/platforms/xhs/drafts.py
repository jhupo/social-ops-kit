from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
import uuid

from social_ops_kit.platforms.xhs.browser_session import XhsPathSet


@dataclass(frozen=True)
class DraftSlide:
    kind: str
    headline: str
    body: tuple[str, ...]
    badge: str = ""
    call_to_action: str = ""
    screenshot_index: int | None = None


@dataclass(frozen=True)
class DraftStoryboard:
    theme: str
    style: str
    slides: tuple[DraftSlide, ...]


@dataclass(frozen=True)
class XhsDraftRequest:
    title: str
    content: str
    screenshots: tuple[str, ...]
    tags: tuple[str, ...] = ()
    style: str = "minimal"


@dataclass(frozen=True)
class XhsDraftRecord:
    draft_id: str
    title: str
    content: str
    tags: tuple[str, ...]
    screenshots: tuple[str, ...]
    generated_images: tuple[str, ...]
    style: str


@dataclass(frozen=True)
class XhsPublishResult:
    draft_id: str
    success: bool
    account: str | None = None
    note_id: str | None = None


class DraftAssetGenerator(Protocol):
    def generate(
        self,
        draft_id: str,
        request: XhsDraftRequest,
        storyboard: DraftStoryboard,
    ) -> tuple[str, ...]: ...


class DraftPublisher(Protocol):
    def publish(self, record: XhsDraftRecord, account: str | None = None) -> XhsPublishResult: ...


def clip_text(text: str, max_length: int) -> str:
    value = " ".join(str(text or "").split()).strip()
    if not value:
        return ""
    if len(value) <= max_length:
        return value
    return f"{value[: max_length - 1]}…"


def split_paragraphs(content: str) -> list[str]:
    cleaned: list[str] = []
    for line in str(content or "").splitlines():
        normalized = line.replace("#", " ").replace(">", " ").replace("`", " ").strip()
        if normalized:
            cleaned.append(normalized)
    return cleaned


def deterministic_storyboard(request: XhsDraftRequest) -> DraftStoryboard:
    paragraphs = split_paragraphs(request.content)
    slides: list[DraftSlide] = [
        DraftSlide(
            kind="cover",
            headline=clip_text(request.title or (paragraphs[0] if paragraphs else "小红书图文"), 24),
            badge="十一在说",
            body=tuple(paragraphs[:2]),
            screenshot_index=0 if request.screenshots else None,
        )
    ]
    for index, _ in enumerate(request.screenshots):
        slides.append(
            DraftSlide(
                kind="screenshot",
                headline=clip_text(
                    paragraphs[index] if index < len(paragraphs) else f"第 {index + 1} 张图",
                    24,
                ),
                body=tuple(paragraphs[index + 1 : index + 3]),
                badge="重点" if index == 0 else "继续看",
                screenshot_index=index,
            )
        )
    tail = paragraphs[max(0, len(request.screenshots)) : max(0, len(request.screenshots)) + 4]
    if tail or not slides:
        slides.append(
            DraftSlide(
                kind="summary",
                headline=clip_text(paragraphs[0] if paragraphs else request.title or "最后想说", 24),
                body=tuple(tail) if tail else (clip_text(request.content, 80),),
                badge="收尾",
                call_to_action="欢迎来和我聊聊",
                screenshot_index=len(request.screenshots) - 1 if len(request.screenshots) > 1 else None,
            )
        )
    return DraftStoryboard(
        theme=clip_text(request.title or (paragraphs[0] if paragraphs else "图文笔记"), 24),
        style=request.style,
        slides=tuple(slides[:6]),
    )


class DeterministicDraftAssetGenerator:
    def __init__(self, paths: XhsPathSet) -> None:
        self._paths = paths

    def generate(
        self,
        draft_id: str,
        request: XhsDraftRequest,
        storyboard: DraftStoryboard,
    ) -> tuple[str, ...]:
        draft_dir = self._paths.drafts_dir / draft_id
        draft_dir.mkdir(parents=True, exist_ok=True)
        generated_images: list[str] = []
        for index, slide in enumerate(storyboard.slides):
            output = draft_dir / f"slide-{index}.txt"
            output.write_text(
                "\n".join(
                    [
                        f"kind={slide.kind}",
                        f"headline={slide.headline}",
                        f"badge={slide.badge}",
                        f"cta={slide.call_to_action}",
                        f"screenshot_index={slide.screenshot_index}",
                        *[f"body={line}" for line in slide.body],
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            generated_images.append(str(output))
        return tuple(generated_images)


class InMemoryDraftPublisher:
    def publish(self, record: XhsDraftRecord, account: str | None = None) -> XhsPublishResult:
        return XhsPublishResult(
            draft_id=record.draft_id,
            success=True,
            account=account,
            note_id=f"note-{record.draft_id[:8]}",
        )


class XhsDraftRuntime:
    def __init__(self, paths: XhsPathSet, generator: DraftAssetGenerator, publisher: DraftPublisher) -> None:
        self._paths = paths
        self._generator = generator
        self._publisher = publisher

    @classmethod
    def with_defaults(cls, paths: XhsPathSet) -> "XhsDraftRuntime":
        return cls(
            paths=paths,
            generator=DeterministicDraftAssetGenerator(paths),
            publisher=InMemoryDraftPublisher(),
        )

    def create_draft(self, request: XhsDraftRequest) -> XhsDraftRecord:
        self._paths.drafts_dir.mkdir(parents=True, exist_ok=True)
        draft_id = str(uuid.uuid4())
        storyboard = deterministic_storyboard(request)
        generated_images = self._generator.generate(draft_id, request, storyboard)
        return XhsDraftRecord(
            draft_id=draft_id,
            title=request.title,
            content=request.content,
            tags=request.tags,
            screenshots=request.screenshots,
            generated_images=generated_images,
            style=request.style,
        )

    def create_and_publish(
        self,
        request: XhsDraftRequest,
        account: str | None = None,
    ) -> tuple[XhsDraftRecord, XhsPublishResult]:
        record = self.create_draft(request)
        result = self._publisher.publish(record, account=account)
        return record, result
