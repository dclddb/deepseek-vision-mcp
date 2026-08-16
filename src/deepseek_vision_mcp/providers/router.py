"""Provider 路由：按模型名分流到不同协议的 Provider。"""

from deepseek_vision_mcp.config import VisionConfig
from deepseek_vision_mcp.providers.base import Provider
from deepseek_vision_mcp.providers.openai import OpenAIChatProvider
from deepseek_vision_mcp.providers.paddleocr import PaddleOCRProvider


def get_provider(config: VisionConfig, model: str) -> Provider:
    """根据模型名选择 Provider。

    - PaddleOCR-* → PaddleOCR 专用 OCR 协议。
    - 其他（GLM / Qwen 等）→ OpenAI 兼容 Chat Completions。
    """
    if model.startswith("PaddleOCR"):
        return PaddleOCRProvider(config.api_key, config.ocr_endpoint, config.timeout)
    return OpenAIChatProvider(config.api_key, config.api_base_url, config.timeout)


def resolve_model(config: VisionConfig, mode: str) -> str:
    """根据 mode 返回模型名。"""
    if mode == "ocr":
        return config.ocr_model
    if mode == "full":
        return config.full_model
    raise ValueError(f"未知 mode: {mode!r} (应为 'full' 或 'ocr')")
