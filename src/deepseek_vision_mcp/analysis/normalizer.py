"""原始响应 → 结构化 AnalysisResult。"""

import re

from deepseek_vision_mcp.models import (
    AnalysisResult,
    ImageInfo,
    TextBlock,
    Uncertainty,
    VisualElement,
)

_SECTION_RE = re.compile(r"^##\s+(.+)$", re.MULTILINE)


def normalize(content: str, image_info: ImageInfo) -> AnalysisResult:
    """把视觉模型的 markdown 输出解析为结构化结果。"""
    result = AnalysisResult(image_info=image_info, raw=content)

    for title, body in _split_sections(content):
        t = title.strip()
        if t.startswith("提取文字"):
            result.text_blocks = _parse_text_blocks(body)
        elif t.startswith("版面") or t.startswith("元素"):
            result.elements = _parse_elements(body)
        elif t.startswith("摘要"):
            result.summary = body.strip()
        elif t.startswith("不确定"):
            result.uncertainties = _parse_uncertainties(body)

    return result


def _split_sections(content: str) -> list[tuple[str, str]]:
    """按 `## 标题` 切分为 (标题, 正文) 列表。"""
    matches = list(_SECTION_RE.finditer(content))
    if not matches:
        return [("", content)]
    sections = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        sections.append((m.group(1), content[start:end].strip()))
    return sections


def _parse_text_blocks(body: str) -> list[TextBlock]:
    return [TextBlock(text=line.strip()) for line in body.splitlines() if line.strip()]


def _parse_elements(body: str) -> list[VisualElement]:
    # 版面与元素是自由文本，v1 做轻量解析：每个非空行作为一个元素（kind 存整行）
    elements = []
    for line in body.splitlines():
        line = line.strip().lstrip("-•*").strip()
        if line:
            elements.append(VisualElement(kind=line, position="", size="", color="", shape=""))
    return elements


def _parse_uncertainties(body: str) -> list[Uncertainty]:
    uncertainties = []
    for line in body.splitlines():
        line = line.strip().lstrip("-•*").strip()
        if not line:
            continue
        what, why = _split_what_why(line)
        uncertainties.append(Uncertainty(what=what, why=why))
    return uncertainties


def _split_what_why(line: str) -> tuple[str, str]:
    for sep in ("→", "->", "：", ":"):
        if sep in line:
            what, _, why = line.partition(sep)
            return what.strip(), why.strip()
    return line, ""
