"""Provider 抽象接口。"""

from abc import ABC, abstractmethod

from deepseek_vision_mcp.models import ProcessedImage


class ProviderError(Exception):
    """视觉 API 调用失败。retryable=True 表示临时错误（可重试）。"""

    def __init__(self, message: str, retryable: bool = False):
        super().__init__(message)
        self.retryable = retryable


class Provider(ABC):
    """视觉 Provider 抽象接口。未来新增 Provider 只需继承并实现 analyze。"""

    name: str = ""

    @abstractmethod
    def analyze(self, model: str, image: ProcessedImage, prompt: str, max_tokens: int = 4096, mode: str = "") -> str:
        """调用视觉模型，返回文字内容（不含思考链）。"""
        raise NotImplementedError
