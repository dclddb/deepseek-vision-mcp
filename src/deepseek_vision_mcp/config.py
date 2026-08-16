"""配置读取：从环境变量读取 VisionConfig。"""

import os
from dataclasses import dataclass


def _parse_bool(v: str) -> bool:
    return v.strip().lower() in ("1", "true", "yes", "on")


def _parse_int(name: str, raw: str) -> int:
    try:
        return int(raw)
    except (ValueError, TypeError):
        raise ValueError(f"环境变量 {name} 无效：{raw!r}（应为整数）") from None


def _parse_float(name: str, raw: str) -> float:
    try:
        return float(raw)
    except (ValueError, TypeError):
        raise ValueError(f"环境变量 {name} 无效：{raw!r}（应为数字）") from None


@dataclass
class VisionConfig:
    api_key: str = ""
    api_base_url: str = ""
    ocr_endpoint: str = ""
    ocr_model: str = ""
    full_model: str = ""
    cache_enabled: bool = True
    cache_scope: str = "global"
    cache_dir: str = ""
    cache_ttl_days: int = 30
    cache_max_size_mb: int = 128
    fallback_enabled: bool = False
    retry_max: int = 2
    timeout: float = 60.0

    @classmethod
    def from_env(cls) -> "VisionConfig":
        return cls(
            api_key=os.environ.get("VISION_API_KEY", ""),
            api_base_url=os.environ.get("VISION_API_BASE_URL", ""),
            ocr_endpoint=os.environ.get("VISION_OCR_ENDPOINT", ""),
            ocr_model=os.environ.get("VISION_OCR_MODEL", ""),
            full_model=os.environ.get("VISION_FULL_MODEL", ""),
            cache_enabled=_parse_bool(os.environ.get("VISION_CACHE_ENABLED", "true")),
            cache_scope=os.environ.get("VISION_CACHE_SCOPE", "global"),
            cache_dir=os.environ.get("VISION_CACHE_DIR", ""),
            cache_ttl_days=_parse_int("VISION_CACHE_TTL_DAYS", os.environ.get("VISION_CACHE_TTL_DAYS", "30")),
            cache_max_size_mb=_parse_int("VISION_CACHE_MAX_SIZE_MB", os.environ.get("VISION_CACHE_MAX_SIZE_MB", "128")),
            fallback_enabled=_parse_bool(os.environ.get("VISION_FALLBACK_ENABLED", "false")),
            retry_max=_parse_int("VISION_RETRY_MAX", os.environ.get("VISION_RETRY_MAX", "2")),
            timeout=_parse_float("VISION_TIMEOUT", os.environ.get("VISION_TIMEOUT", "60")),
        )
