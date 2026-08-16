"""本地缓存：用户级全局视觉结果缓存（只存结果，不存图片）。"""

import hashlib
import json
import os
import time
from pathlib import Path

from deepseek_vision_mcp.config import VisionConfig


class VisionCache:
    """视觉结果缓存。按 image_sha256 内容寻址，hash 分片，TTL + 容量上限。"""

    def __init__(self, config: VisionConfig):
        self.enabled = config.cache_enabled and config.cache_scope != "none"
        self.ttl_days = config.cache_ttl_days
        self.max_size_mb = config.cache_max_size_mb
        self._dir = self._resolve_dir(config)

    @staticmethod
    def _resolve_dir(config: VisionConfig) -> Path:
        if config.cache_dir:
            return Path(config.cache_dir)
        if config.cache_scope == "project":
            return Path(".cache/deepseek-vision-mcp")
        if os.name == "nt":  # Windows
            base = os.environ.get("LOCALAPPDATA") or str(Path.home())
            return Path(base) / "deepseek-vision-mcp" / "cache"
        return Path.home() / ".cache" / "deepseek-vision-mcp"

    def get(self, cache_key: str) -> dict | None:
        """命中返回 result dict，未命中/过期返回 None。"""
        if not self.enabled:
            return None
        path = self._path_for(cache_key)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

        created = data.get("created_at", 0)
        if time.time() - created > self.ttl_days * 86400:
            try:
                path.unlink()
            except OSError:
                pass
            return None

        data["last_accessed_at"] = time.time()
        try:
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        except OSError:
            pass
        return data.get("result")

    def set(self, cache_key: str, result: dict) -> None:
        """只缓存成功结果（调用方保证）。"""
        if not self.enabled:
            return
        path = self._path_for(cache_key)
        data = {
            "cache_schema_version": 1,
            "created_at": time.time(),
            "last_accessed_at": time.time(),
            "result": result,
        }
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        except OSError:
            return
        self._enforce_size_limit()

    def _path_for(self, cache_key: str) -> Path:
        h = hashlib.sha256(cache_key.encode("utf-8")).hexdigest()
        return self._dir / h[:2] / f"{h}.json"

    def _enforce_size_limit(self) -> None:
        """超容量时按最近访问时间（mtime）淘汰最旧。"""
        limit = self.max_size_mb * 1024 * 1024
        try:
            files = list(self._dir.rglob("*.json"))
            total = sum(f.stat().st_size for f in files)
            if total <= limit:
                return
            files.sort(key=lambda f: f.stat().st_mtime)
            for f in files:
                if total <= limit:
                    break
                try:
                    total -= f.stat().st_size
                    f.unlink()
                except OSError:
                    pass
        except OSError:
            pass
