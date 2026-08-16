"""图片校验：magic bytes / 格式 / 尺寸 / 像素上限。"""

import io

from PIL import Image

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20MB
MAX_PIXELS = 40_000_000  # 4000 万像素

SUPPORTED_FORMATS = {"PNG", "JPEG", "WEBP", "GIF", "BMP"}


class ValidationError(Exception):
    """图片校验失败。"""


def validate(data: bytes) -> tuple[str, int, int]:
    """校验图片，返回 (mime_type, width, height)。

    不依赖扩展名，以 magic bytes（PIL 检测）为准。
    """
    if not data:
        raise ValidationError("图片为空")
    if len(data) > MAX_FILE_SIZE_BYTES:
        raise ValidationError(f"图片过大: {len(data)} bytes (上限 {MAX_FILE_SIZE_BYTES})")

    try:
        with Image.open(io.BytesIO(data)) as img:
            fmt = (img.format or "").upper()
            width, height = img.size
    except Exception as e:
        raise ValidationError(f"不是有效图片: {e}") from e

    if fmt not in SUPPORTED_FORMATS:
        raise ValidationError(f"不支持的图片格式: {fmt or '未知'}")

    if width * height > MAX_PIXELS:
        raise ValidationError(f"像素过多: {width}x{height} (上限 {MAX_PIXELS})")

    return _fmt_to_mime(fmt), width, height


def _fmt_to_mime(fmt: str) -> str:
    return {
        "PNG": "image/png",
        "JPEG": "image/jpeg",
        "WEBP": "image/webp",
        "GIF": "image/gif",
        "BMP": "image/bmp",
    }.get(fmt, "application/octet-stream")
