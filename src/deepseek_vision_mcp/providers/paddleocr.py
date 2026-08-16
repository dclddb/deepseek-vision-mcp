"""PaddleOCR 专用 OCR API 实现。"""

import base64

import httpx

from deepseek_vision_mcp.models import ProcessedImage
from deepseek_vision_mcp.providers.base import Provider, ProviderError


class PaddleOCRProvider(Provider):
    """PaddleOCR-VL-1.5 专用 OCR 协议（/v1/p006/ocr/paddleocr）。"""

    name = "paddleocr"

    def __init__(self, api_key: str, endpoint: str, timeout: float = 60.0):
        self._api_key = api_key
        self._endpoint = endpoint
        self._timeout = timeout

    def analyze(self, model: str, image: ProcessedImage, prompt: str, max_tokens: int = 4096, mode: str = "ocr") -> str:
        # 实测：file 字段接受「裸 base64」（不带 data: 前缀），fileType=0
        b64 = base64.b64encode(image.bytes).decode()

        payload = {
            "model": model,
            "file": b64,
            "fileType": 0,
            "useChartRecognition": True,
            "useDocUnwarping": True,
            "useLayoutDetection": True,
            "layoutNms": True,
            "repetitionPenalty": 1.0,
            "temperature": 0,
            "topP": 1.0,
            "minPixels": 147384,
            "maxPixels": 2822400,
            "visualize": False,
        }

        try:
            resp = httpx.post(
                self._endpoint,
                json=payload,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                timeout=self._timeout,
            )
        except httpx.HTTPError as e:
            raise ProviderError(
                f"[Vision] model={model} endpoint={self._endpoint} mode={mode} error=请求失败:{e}",
                retryable=True,
            ) from e

        if resp.status_code != 200:
            raise ProviderError(
                f"[Vision] model={model} endpoint={self._endpoint} mode={mode} "
                f"http={resp.status_code} error={resp.text[:500]}",
                retryable=resp.status_code >= 500,
            )

        try:
            data = resp.json()
            if data.get("errorCode") != 0:
                raise ProviderError(
                    f"[Vision] model={model} endpoint={self._endpoint} mode={mode} "
                    f"errorCode={data.get('errorCode')} errorMsg={data.get('errorMsg')}",
                    retryable=False,
                )
            return self._extract_text(data)
        except (KeyError, IndexError, ValueError) as e:
            raise ProviderError(
                f"[Vision] model={model} endpoint={self._endpoint} mode={mode} 响应解析失败:{e}",
                retryable=False,
            ) from e

    @staticmethod
    def _extract_text(data: dict) -> str:
        """从 parsing_res_list 提取文字，按 block_order 排序拼接。"""
        blocks = []
        try:
            items = data["result"]["layoutParsingResults"][0]["prunedResult"]["parsing_res_list"]
        except (KeyError, IndexError, TypeError):
            return ""

        def sort_key(item):
            o = item.get("block_order")
            return (o is None, o if o is not None else 0)

        for item in sorted(items, key=sort_key):
            content = (item.get("block_content") or "").strip()
            if content:
                blocks.append(content)
        return "\n".join(blocks)
