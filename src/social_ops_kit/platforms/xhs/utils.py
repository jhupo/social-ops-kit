from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse


def is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
