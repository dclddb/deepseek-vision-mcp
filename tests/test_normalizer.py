from deepseek_vision_mcp.analysis.normalizer import normalize
from deepseek_vision_mcp.models import ImageInfo


def _image_info():
    return ImageInfo(
        path_or_url="x.png", mime_type="image/png", width=1, height=1,
        size_bytes=1, image_sha256="abc",
    )


MARKDOWN = """## 提取文字
HELLO

## 版面与元素
- 一个红色矩形

## 摘要
一句话摘要。

## 不确定项
- 某处无法确认 → 原因：分辨率不足
"""


def test_normalize_parses_sections():
    r = normalize(MARKDOWN, _image_info())
    assert "HELLO" in r.raw
    assert r.summary.strip() == "一句话摘要。"
    assert len(r.uncertainties) == 1
    assert r.uncertainties[0].what == "某处无法确认"
    assert r.uncertainties[0].why == "原因：分辨率不足"
    assert len(r.text_blocks) == 1


def test_normalize_plain_text():
    r = normalize("纯文字无标题", _image_info())
    assert r.raw == "纯文字无标题"
    assert r.summary == ""
    assert r.text_blocks == []
    assert r.uncertainties == []
