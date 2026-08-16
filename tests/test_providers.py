import base64
import json

import httpx

from deepseek_vision_mcp.models import ProcessedImage
from deepseek_vision_mcp.providers.openai import OpenAIChatProvider
from deepseek_vision_mcp.providers.paddleocr import PaddleOCRProvider


def _image():
    return ProcessedImage(bytes=b"fake-bytes", mime_type="image/png", width=10, height=10)


def _fake_post(status_code, response_json):
    captured = {}

    def handler(url, json=None, headers=None, timeout=None):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers

        class R:
            text = ""

            @staticmethod
            def json():
                return response_json

        R.status_code = status_code
        return R()

    return handler, captured


def test_openai_provider_sends_multimodal_payload(monkeypatch):
    handler, captured = _fake_post(200, {"choices": [{"message": {"content": "ok"}}]})
    monkeypatch.setattr(httpx, "post", handler)

    p = OpenAIChatProvider(api_key="k", base_url="https://example.com/v1")
    result = p.analyze(model="GLM-4.5V", image=_image(), prompt="描述", mode="full")

    assert result == "ok"
    assert captured["url"] == "https://example.com/v1/chat/completions"
    content = captured["json"]["messages"][0]["content"]
    assert content[0]["type"] == "image_url"
    assert content[0]["image_url"]["url"].startswith("data:image/png;base64,")
    assert content[1] == {"type": "text", "text": "描述"}


def test_paddleocr_provider_sends_raw_base64(monkeypatch):
    resp = {
        "errorCode": 0, "errorMsg": "Success",
        "result": {"layoutParsingResults": [{"prunedResult": {"parsing_res_list": [
            {"block_label": "text", "block_content": "HELLO", "block_order": 1}
        ]}}]},
    }
    handler, captured = _fake_post(200, resp)
    monkeypatch.setattr(httpx, "post", handler)

    p = PaddleOCRProvider(api_key="k", endpoint="https://ocr.example.com/v1/paddleocr")
    result = p.analyze(model="PaddleOCR-VL-1.5", image=_image(), prompt="", mode="ocr")

    assert result == "HELLO"
    assert captured["url"] == "https://ocr.example.com/v1/paddleocr"
    file_val = captured["json"]["file"]
    # file 必须是裸 base64，不带 data: 前缀
    assert not file_val.startswith("data:")
    assert base64.b64decode(file_val) == b"fake-bytes"


def test_provider_5xx_is_retryable(monkeypatch):
    handler, _ = _fake_post(500, {"error": "boom"})
    monkeypatch.setattr(httpx, "post", handler)

    from deepseek_vision_mcp.providers.base import ProviderError

    p = OpenAIChatProvider(api_key="k", base_url="https://example.com/v1")
    try:
        p.analyze(model="GLM-4.5V", image=_image(), prompt="x", mode="full")
    except ProviderError as e:
        assert e.retryable is True
    else:
        raise AssertionError("应抛出 ProviderError")
