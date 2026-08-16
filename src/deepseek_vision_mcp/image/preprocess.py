"""图片预处理：EXIF orientation / 等比例缩放 / 格式归一化 → ProcessedImage。"""

import io

from PIL import Image, ImageOps

from deepseek_vision_mcp.models import ProcessedImage

MAX_DIMENSION = 2048  # 长边最大 2048px


def preprocess(data: bytes, mime_type: str, width: int, height: int) -> ProcessedImage:
    """预处理图片，返回最终提交给 Provider 的 ProcessedImage。

    规则：
    - EXIF orientation 修正。
    - 等比例缩放长边到 MAX_DIMENSION。
    - 默认 PNG 保持 PNG、JPEG 保持 JPEG；其它格式统一转 PNG。
    - 文字密集型优先保清晰，不做过度 JPEG 压缩。
    """
    img = Image.open(io.BytesIO(data))
    src_format = (img.format or "").upper()

    img = ImageOps.exif_transpose(img)  # EXIF orientation 修正
    img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.Resampling.LANCZOS)

    out_format = src_format if src_format in ("PNG", "JPEG") else "PNG"

    buf = io.BytesIO()
    if out_format == "JPEG":
        img = img.convert("RGB")  # JPEG 无 alpha
        img.save(buf, format="JPEG", quality=95, optimize=True)
        out_mime = "image/jpeg"
    else:
        img.save(buf, format="PNG", optimize=True)
        out_mime = "image/png"

    return ProcessedImage(
        bytes=buf.getvalue(),
        mime_type=out_mime,
        width=img.width,
        height=img.height,
    )
