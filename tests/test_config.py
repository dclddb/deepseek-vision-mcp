import pytest

from deepseek_vision_mcp.config import VisionConfig, _parse_bool


def test_defaults_are_empty():
    cfg = VisionConfig()
    assert cfg.api_key == ""
    assert cfg.api_base_url == ""
    assert cfg.ocr_endpoint == ""
    assert cfg.ocr_model == ""
    assert cfg.full_model == ""


def test_from_env(monkeypatch):
    monkeypatch.setenv("VISION_API_KEY", "test-key")
    monkeypatch.setenv("VISION_API_BASE_URL", "https://example.com/v1")
    monkeypatch.setenv("VISION_FULL_MODEL", "my-model")
    cfg = VisionConfig.from_env()
    assert cfg.api_key == "test-key"
    assert cfg.api_base_url == "https://example.com/v1"
    assert cfg.full_model == "my-model"


def test_parse_bool():
    assert _parse_bool("true") is True
    assert _parse_bool("false") is False
    assert _parse_bool("1") is True
    assert _parse_bool("0") is False
    assert _parse_bool("yes") is True


def test_invalid_int_raises(monkeypatch):
    monkeypatch.setenv("VISION_RETRY_MAX", "abc")
    with pytest.raises(ValueError):
        VisionConfig.from_env()


def test_invalid_float_raises(monkeypatch):
    monkeypatch.setenv("VISION_TIMEOUT", "xyz")
    with pytest.raises(ValueError):
        VisionConfig.from_env()
