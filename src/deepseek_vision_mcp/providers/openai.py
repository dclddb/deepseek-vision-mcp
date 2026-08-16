"""OpenAI 兼容多模态 Chat Completions 协议实现。"""

import base64

import httpx

from deepseek_vision_mcp.models import ProcessedImage
from deepseek_vision_mcp.providers.base import Provider, ProviderError


class OpenAIChatProvider(Provider):
    """OpenAI 兼容多模态 Chat Completions 协议（适用于 GLM / Qwen 等大多数视觉模型）。"""

    name = "openai_chat"

    def __init__(self, api_key: str, base_url: str, timeout: float = 60.0):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def analyze(self, model: str, image: ProcessedImage, prompt: str, max_tokens: int = 4096, mode: str = "") -> str:
        url = f"{self._base_url}/chat/completions"
        data_url = f"data:{image.mime_type};base64,{base64.b64encode(image.bytes).decode()}"

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": data_url}},
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            "max_tokens": max_tokens,
        }

        try:
            resp = httpx.post(
                url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                timeout=self._timeout,
            )
        except httpx.HTTPError as e:
            raise ProviderError(
                f"[Vision] model={model} endpoint={url} mode={mode} error=请求失败:{e}",
                retryable=True,
            ) from e

        if resp.status_code != 200:
            raise ProviderError(
                f"[Vision] model={model} endpoint={url} mode={mode} "
                f"http={resp.status_code} error={resp.text[:500]}",
                retryable=resp.status_code >= 500,
            )

        try:
            data = resp.json()
            message = data["choices"][0].get("message", {})
            # 取 content（答案），不要 reasoning_content（思考链）
            return message.get("content") or ""
        except (KeyError, IndexError, ValueError) as e:
            raise ProviderError(
                f"[Vision] model={model} endpoint={url} mode={mode} 响应解析失败:{e}",
                retryable=False,
            ) from e
