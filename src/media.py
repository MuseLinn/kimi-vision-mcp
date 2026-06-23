"""Media loading, validation, and encoding utilities."""

import base64
import mimetypes
import tempfile
import urllib.parse
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import httpx


class MediaType(Enum):
    IMAGE = "image"
    VIDEO = "video"
    UNKNOWN = "unknown"


@dataclass
class Media:
    path: Path
    media_type: MediaType
    mime: str
    size_bytes: int


_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff", ".tif"}
_VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm", ".flv", ".wmv"}


def _guess_media_type(path: Path) -> tuple[MediaType, str]:
    mime, _ = mimetypes.guess_type(str(path))
    mime = mime or "application/octet-stream"
    suffix = path.suffix.lower()
    if suffix in _IMAGE_EXTS or mime.startswith("image/"):
        return MediaType.IMAGE, mime
    if suffix in _VIDEO_EXTS or mime.startswith("video/"):
        return MediaType.VIDEO, mime
    return MediaType.UNKNOWN, mime


def download_url(url: str, timeout: float = 60.0) -> Path:
    """Download a URL to a temporary file and return its path."""
    parsed = urllib.parse.urlparse(url)
    suffix = Path(parsed.path).suffix or ".bin"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            with client.stream("GET", url) as response:
                response.raise_for_status()
                for chunk in response.iter_bytes(chunk_size=8192):
                    f.write(chunk)
        return Path(f.name)


def load_media(source: str, max_size_mb: int = 100) -> Media:
    """Load a local path or URL into a Media object."""
    if source.startswith(("http://", "https://")):
        path = download_url(source)
    else:
        path = Path(source).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"Media not found: {path}")

    size_bytes = path.stat().st_size
    max_bytes = max_size_mb * 1024 * 1024
    if size_bytes > max_bytes:
        raise ValueError(
            f"File too large: {size_bytes / 1024 / 1024:.1f} MB "
            f"(max {max_size_mb} MB). Consider compressing before analysis."
        )

    media_type, mime = _guess_media_type(path)
    if media_type == MediaType.UNKNOWN:
        raise ValueError(f"Unsupported media type: {path.suffix or mime}")

    return Media(path=path, media_type=media_type, mime=mime, size_bytes=size_bytes)


def encode_image(source: str, max_size_mb: int = 20) -> tuple[str, str]:
    """Load and base64 encode an image. Returns (base64_string, mime_type)."""
    media = load_media(source, max_size_mb=max_size_mb)
    if media.media_type != MediaType.IMAGE:
        raise ValueError(f"Expected image, got {media.media_type.value}")
    b64 = base64.b64encode(media.path.read_bytes()).decode("utf-8")
    return b64, media.mime
