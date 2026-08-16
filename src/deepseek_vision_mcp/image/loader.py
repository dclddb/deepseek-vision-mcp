"""图片加载：本地路径 / http(s) URL → 原始 bytes。"""

from pathlib import Path

import httpx


class LoadError(Exception):
    """加载图片失败。"""


def load(path_or_url: str) -> bytes:
    """读取本地文件或 http(s) URL，返回原始 bytes。"""
    if path_or_url.startswith(("http://", "https://")):
        return _load_url(path_or_url)
    return _load_local(path_or_url)


def _load_local(path: str) -> bytes:
    p = Path(path)
    if not p.exists():
        raise LoadError(f"文件不存在: {path}")
    if not p.is_file():
        raise LoadError(f"不是文件: {path}")
    return p.read_bytes()


def _load_url(url: str) -> bytes:
    try:
        resp = httpx.get(url, follow_redirects=True, timeout=30.0)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        raise LoadError(f"URL 下载失败: {url} ({e})") from e
    return resp.content
