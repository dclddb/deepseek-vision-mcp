"""串联「加载 → 校验 → 预处理 → hash → 缓存 → 路由 → 重试 → 归一化」。"""

import hashlib
import time

from deepseek_vision_mcp.analysis.normalizer import normalize
from deepseek_vision_mcp.analysis.prompts import prompt_for
from deepseek_vision_mcp.cache import VisionCache
from deepseek_vision_mcp.config import VisionConfig
from deepseek_vision_mcp.image.loader import load
from deepseek_vision_mcp.image.preprocess import preprocess
from deepseek_vision_mcp.image.validate import validate
from deepseek_vision_mcp.models import AnalysisResult, ImageInfo, ProcessedImage
from deepseek_vision_mcp.providers.base import Provider, ProviderError
from deepseek_vision_mcp.providers.router import get_provider, resolve_model

# 版本号：Cache Key 组成部分。prompt / preprocess / output schema / cache schema 变更时递增。
PROMPT_VERSION = "1"
PREPROCESS_VERSION = "1"
OUTPUT_SCHEMA_VERSION = "1"
CACHE_SCHEMA_VERSION = "1"


def run_analysis(config: VisionConfig, path_or_url: str, mode: str = "full") -> AnalysisResult:
    # 1. 加载原始 bytes
    source_bytes = load(path_or_url)
    source_sha256 = hashlib.sha256(source_bytes).hexdigest()

    # 2. 校验
    mime_type, width, height = validate(source_bytes)

    # 3. 预处理 → ProcessedImage（Hash 与 Provider 输入的唯一来源）
    processed = preprocess(source_bytes, mime_type, width, height)
    image_sha256 = hashlib.sha256(processed.bytes).hexdigest()

    image_info = ImageInfo(
        path_or_url=path_or_url,
        mime_type=processed.mime_type,
        width=processed.width,
        height=processed.height,
        size_bytes=len(processed.bytes),
        image_sha256=image_sha256,
        source_sha256=source_sha256,
    )

    # 4. 路由（mode → model → provider）
    model = resolve_model(config, mode)
    provider = get_provider(config, model)
    prompt = prompt_for(mode)
    max_tokens = 4096 if mode == "full" else 2048

    # 5. 缓存 lookup（image_sha256 内容寻址）
    cache = VisionCache(config)
    cache_key = _build_cache_key(image_sha256, mode, provider.name, model)
    if cache.enabled:
        cached = cache.get(cache_key)
        if cached is not None:
            return AnalysisResult.from_dict(cached)

    # 6. 调视觉 API（临时错误有限重试）
    content = _call_with_retry(provider, model, processed, prompt, max_tokens, mode, config.retry_max)

    # 7. 归一化
    result = normalize(content, image_info)

    # 8. 缓存保存（只缓存成功结果）
    if cache.enabled:
        cache.set(cache_key, result.to_dict())

    return result


def _build_cache_key(image_sha256: str, mode: str, provider: str, model: str) -> str:
    return "|".join([
        image_sha256, mode, provider, model,
        PROMPT_VERSION, PREPROCESS_VERSION, OUTPUT_SCHEMA_VERSION, CACHE_SCHEMA_VERSION,
    ])


def _call_with_retry(
    provider: Provider,
    model: str,
    image: ProcessedImage,
    prompt: str,
    max_tokens: int,
    mode: str,
    retry_max: int,
) -> str:
    last_err: ProviderError | None = None
    for attempt in range(retry_max + 1):
        try:
            return provider.analyze(model=model, image=image, prompt=prompt, max_tokens=max_tokens, mode=mode)
        except ProviderError as e:
            last_err = e
            if attempt >= retry_max or not e.retryable:
                raise
            time.sleep(2 ** attempt)  # 指数退避 1s, 2s
    raise last_err  # pragma: no cover
