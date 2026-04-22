from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import time

from social_ops_kit.platforms.douyin.assets import build_slides
from social_ops_kit.platforms.douyin.state import DouyinPathSet, read_json_file


@dataclass(frozen=True)
class DouyinMusicSelection:
    music_id: str
    title: str
    author: str
    duration: int
    play_url: tuple[str, ...]
    cover_url: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.music_id,
            "title": self.title,
            "author": self.author,
            "duration": self.duration,
            "play_url": list(self.play_url),
            "cover_url": self.cover_url,
        }


@dataclass(frozen=True)
class DouyinPublishRequest:
    title: str
    copy: str
    hashtags: tuple[str, ...]
    images: tuple[str, ...]
    out_dir: Path
    music: DouyinMusicSelection
    slides: tuple[dict[str, Any], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "copy": self.copy,
            "hashtags": list(self.hashtags),
            "images": list(self.images),
            "out_dir": str(self.out_dir),
            "music": self.music.as_dict(),
            "slides": list(self.slides),
        }


DEFAULT_MUSIC = DouyinMusicSelection(
    music_id="6705082944836339713",
    title="Time",
    author="Hans Zimmer",
    duration=60,
    play_url=("https://example.com/placeholder.mp3",),
    cover_url="https://example.com/time.jpg",
)


def pick_music(
    paths: DouyinPathSet,
    music_id: str | None = None,
    music_title: str | None = None,
    music_author: str | None = None,
    music_duration: int | None = None,
) -> DouyinMusicSelection:
    if music_id or music_title or music_author or music_duration:
        return DouyinMusicSelection(
            music_id=music_id or DEFAULT_MUSIC.music_id,
            title=music_title or DEFAULT_MUSIC.title,
            author=music_author or DEFAULT_MUSIC.author,
            duration=music_duration or DEFAULT_MUSIC.duration,
            play_url=DEFAULT_MUSIC.play_url,
            cover_url=DEFAULT_MUSIC.cover_url,
        )
    selected = read_json_file(paths.music_selected_file)
    if selected:
        return DouyinMusicSelection(
            music_id=str(selected.get("id") or DEFAULT_MUSIC.music_id),
            title=str(selected.get("title") or DEFAULT_MUSIC.title),
            author=str(selected.get("author") or DEFAULT_MUSIC.author),
            duration=int(selected.get("duration") or DEFAULT_MUSIC.duration),
            play_url=tuple(selected.get("play_url") or DEFAULT_MUSIC.play_url),
            cover_url=str(selected.get("cover_url") or DEFAULT_MUSIC.cover_url),
        )
    return DEFAULT_MUSIC


def make_publish_request(
    paths: DouyinPathSet,
    title: str,
    copy: str,
    images: tuple[str, ...],
    hashtags: tuple[str, ...] = (),
    music_id: str | None = None,
    music_title: str | None = None,
    music_author: str | None = None,
    music_duration: int | None = None,
) -> DouyinPublishRequest:
    out_dir = paths.runs_dir / f"dynamic_post_{int(time.time())}"
    out_dir.mkdir(parents=True, exist_ok=True)
    body = copy.strip()
    missing_tags = [tag for tag in hashtags if tag not in body]
    if missing_tags:
        body = body + "\n\n" + " ".join(missing_tags)
    slides = tuple(
        {
            "eyebrow": slide.eyebrow,
            "title": slide.title,
            "lines": list(slide.lines),
            "footer": slide.footer,
            "bg": slide.background,
            "accent": slide.accent,
        }
        for slide in build_slides(title, body, hashtags)
    )
    return DouyinPublishRequest(
        title=title,
        copy=body,
        hashtags=hashtags,
        images=images,
        out_dir=out_dir,
        music=pick_music(paths, music_id, music_title, music_author, music_duration),
        slides=slides,
    )
