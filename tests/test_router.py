import pytest

from deepseek_vision_mcp.config import VisionConfig
from deepseek_vision_mcp.providers.openai import OpenAIChatProvider
from deepseek_vision_mcp.providers.paddleocr import PaddleOCRProvider
from deepseek_vision_mcp.providers.router import get_provider, resolve_model


def _cfg():
    return VisionConfig(
        api_key="k",
        api_base_url="https://example.com/v1",
        ocr_endpoint="https://ocr.example.com/v1/paddleocr",
        ocr_model="PaddleOCR-VL-1.5",
        full_model="my-vision-model",
    )


def test_paddleocr_model_routes_to_paddleocr_provider():
    p = get_provider(_cfg(), "PaddleOCR-VL-1.5")
    assert isinstance(p, PaddleOCRProvider)


def test_other_model_routes_to_openai_provider():
    p = get_provider(_cfg(), "GLM-4.5V")
    assert isinstance(p, OpenAIChatProvider)


def test_resolve_model():
    cfg = _cfg()
    assert resolve_model(cfg, "full") == "my-vision-model"
    assert resolve_model(cfg, "ocr") == "PaddleOCR-VL-1.5"


def test_resolve_model_unknown_mode():
    with pytest.raises(ValueError):
        resolve_model(_cfg(), "unknown")
