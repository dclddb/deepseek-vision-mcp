"""内部数据结构。"""

from dataclasses import dataclass, field, asdict


@dataclass
class ProcessedImage:
    """预处理后的最终图片，是 Hash 与 Provider 输入的唯一来源。"""

    bytes: bytes
    mime_type: str
    width: int
    height: int


@dataclass
class ImageInfo:
    path_or_url: str
    mime_type: str
    width: int
    height: int
    size_bytes: int
    image_sha256: str  # = SHA-256(final processed image bytes)
    source_sha256: str | None = None  # 可选，仅诊断用；非 Cache Key 依据


@dataclass
class TextBlock:
    text: str


@dataclass
class VisualElement:
    kind: str
    position: str
    size: str
    color: str
    shape: str


@dataclass
class Uncertainty:
    what: str  # 什么无法确认
    why: str  # 为什么无法确认
    # 注意：无 leaning 字段，禁止输出"我倾向于/最可能是"


@dataclass
class AnalysisResult:
    image_info: ImageInfo
    text_blocks: list[TextBlock] = field(default_factory=list)
    elements: list[VisualElement] = field(default_factory=list)
    summary: str = ""
    uncertainties: list[Uncertainty] = field(default_factory=list)
    raw: str = ""  # 原始视觉模型返回，用于调试和追查

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "AnalysisResult":
        ii = d.get("image_info") or {}
        image_info = ImageInfo(
            path_or_url=ii.get("path_or_url", ""),
            mime_type=ii.get("mime_type", ""),
            width=ii.get("width", 0),
            height=ii.get("height", 0),
            size_bytes=ii.get("size_bytes", 0),
            image_sha256=ii.get("image_sha256", ""),
            source_sha256=ii.get("source_sha256"),
        )
        return cls(
            image_info=image_info,
            text_blocks=[TextBlock(text=b.get("text", "")) for b in d.get("text_blocks", [])],
            elements=[VisualElement(
                kind=e.get("kind", ""), position=e.get("position", ""),
                size=e.get("size", ""), color=e.get("color", ""), shape=e.get("shape", ""),
            ) for e in d.get("elements", [])],
            summary=d.get("summary", ""),
            uncertainties=[Uncertainty(what=u.get("what", ""), why=u.get("why", "")) for u in d.get("uncertainties", [])],
            raw=d.get("raw", ""),
        )
