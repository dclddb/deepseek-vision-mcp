import json

from deepseek_vision_mcp.cache import VisionCache
from deepseek_vision_mcp.config import VisionConfig


def _cache(tmp_path):
    cfg = VisionConfig(
        cache_enabled=True, cache_dir=str(tmp_path),
        cache_ttl_days=30, cache_max_size_mb=128,
    )
    return VisionCache(cfg)


def test_set_and_get(tmp_path):
    c = _cache(tmp_path)
    c.set("key1", {"raw": "hello"})
    assert c.get("key1") == {"raw": "hello"}


def test_miss_returns_none(tmp_path):
    assert _cache(tmp_path).get("nonexistent") is None


def test_hash_sharding(tmp_path):
    c = _cache(tmp_path)
    c.set("some-key", {"raw": "x"})
    subdirs = [p.name for p in tmp_path.iterdir() if p.is_dir()]
    assert len(subdirs) == 1
    assert len(subdirs[0]) == 2


def test_ttl_expiry(tmp_path):
    c = _cache(tmp_path)
    c.set("key1", {"raw": "hello"})
    f = next(tmp_path.rglob("*.json"))
    data = json.loads(f.read_text(encoding="utf-8"))
    data["created_at"] = 0
    f.write_text(json.dumps(data), encoding="utf-8")
    assert c.get("key1") is None


def test_disabled_cache(tmp_path):
    cfg = VisionConfig(cache_enabled=False, cache_dir=str(tmp_path))
    c = VisionCache(cfg)
    c.set("key1", {"raw": "hello"})
    assert c.get("key1") is None
