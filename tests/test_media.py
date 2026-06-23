import base64
from pathlib import Path

import pytest

from src.media import encode_image, load_media, MediaType


def test_load_local_image(tmp_path):
    img = tmp_path / "test.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\nfake")
    media = load_media(str(img))
    assert media.media_type == MediaType.IMAGE
    assert media.mime == "image/png"


def test_load_local_video(tmp_path):
    video = tmp_path / "test.mp4"
    video.write_bytes(b"fake video")
    media = load_media(str(video))
    assert media.media_type == MediaType.VIDEO
    assert media.mime == "video/mp4"


def test_load_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_media(str(tmp_path / "missing.png"))


def test_load_unsupported_type(tmp_path):
    txt = tmp_path / "test.txt"
    txt.write_bytes(b"hello")
    with pytest.raises(ValueError, match="Unsupported media type"):
        load_media(str(txt))


def test_load_too_large(tmp_path):
    img = tmp_path / "test.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\n" + b"x" * (1024 * 1024))
    with pytest.raises(ValueError, match="File too large"):
        load_media(str(img), max_size_mb=1)


def test_encode_image(tmp_path):
    img = tmp_path / "test.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\nfake data")
    b64, mime = encode_image(str(img))
    assert mime == "image/png"
    assert base64.b64decode(b64) == b"\x89PNG\r\n\x1a\nfake data"


def test_encode_image_rejects_video(tmp_path):
    video = tmp_path / "test.mp4"
    video.write_bytes(b"fake video")
    with pytest.raises(ValueError, match="Expected image"):
        encode_image(str(video))
