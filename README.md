# deepseek-vision-mcp（Chinese README）

给无视觉能力的文本 LLM（如 DeepSeek）当「眼睛」的 MCP 服务器 —— 一个稳定、可替换后端的**云端视觉适配层**。

## 设计理念（四层分工）

- **主模型 = 大脑**：解释、推理、判断、建议、任务决策
- **Vision MCP = 眼睛**：忠实描述「我看到了什么」
- **Skill = 工作规范**：特定领域的规则（不在此项目）
- **Claude Code = 调度与执行**：调工具、改文件、执行任务

本 MCP 只回答「我看到了什么」，**不**回答「这意味着什么」，不替主模型思考。

## 功能特性

- 双协议分流：OpenAI 兼容 Chat Completions（通用视觉模型）+ PaddleOCR 专用 OCR 协议
- 图片三段式处理：加载 → 校验 → 预处理（EXIF 校正、等比缩放）
- 内容寻址缓存（`image_sha256`）：重复分析同一张图秒回，省额度
- 临时错误自动重试（≤2 次指数退避）
- 失败透明：视觉服务失败时明确报错，绝不伪造结果

## 安装

需要 Python 3.11+ 和 [uv](https://docs.astral.sh/uv/)。

```bash
uv sync
```

## 配置

所有配置通过环境变量注入（`.mcp.json` 的 `env` 或 `.env`）。

| 变量 | 说明 | 默认值 |
|---|---|---|
| `VISION_API_KEY` | 视觉 API 的 key | 无，必填 |
| `VISION_API_BASE_URL` | OpenAI 兼容 Chat 接口 base URL | 无，必填 |
| `VISION_OCR_ENDPOINT` | PaddleOCR 专用 OCR 接口完整地址 | 无（用 PaddleOCR 时填） |
| `VISION_OCR_MODEL` | `mode=ocr` 使用的模型 | 无，必填 |
| `VISION_FULL_MODEL` | `mode=full` 使用的模型 | 无，必填 |
| `VISION_CACHE_ENABLED` | 缓存总开关 | `true` |
| `VISION_CACHE_SCOPE` | `global` / `project` / `none` | `global` |
| `VISION_CACHE_DIR` | 缓存目录覆盖（空=平台默认） | 空 |
| `VISION_CACHE_TTL_DAYS` | 缓存有效期（天） | `30` |
| `VISION_CACHE_MAX_SIZE_MB` | 缓存最大容量（MB） | `128` |
| `VISION_FALLBACK_ENABLED` | fallback 开关 | `false` |
| `VISION_RETRY_MAX` | 临时错误重试上限 | `2` |
| `VISION_TIMEOUT` | 单次 API 超时（秒） | `60` |

参考 `.env.example`。

### 注册到 Claude Code

项目级（`.mcp.json`）或用户级（`~/.claude.json` 的 `mcpServers`）：

```json
{
  "mcpServers": {
    "deepseek-vision-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/deepseek-vision-mcp", "deepseek-vision-mcp"],
      "env": {
        "VISION_API_KEY": "sk-...",
        "VISION_API_BASE_URL": "https://your-vision-api.example.com/v1",
        "VISION_OCR_ENDPOINT": "https://your-ocr-api.example.com/v1/paddleocr",
        "VISION_OCR_MODEL": "PaddleOCR-VL-1.5",
        "VISION_FULL_MODEL": "your-vision-model"
      }
    }
  }
}
```

> 若 `uv` 不在 PATH，`command` 用 uv 的完整路径。

**Windows 示例**（`uv` 通常不在 PATH，`command` 用完整路径，目录用正斜杠）：

```json
{
  "mcpServers": {
    "deepseek-vision-mcp": {
      "command": "C:/Users/你的用户名/.local/bin/uv.exe",
      "args": ["run", "--directory", "D:/path/to/deepseek-vision-mcp", "deepseek-vision-mcp"],
      "env": {
        "VISION_API_KEY": "sk-...",
        "VISION_API_BASE_URL": "https://your-vision-api.example.com/v1",
        "VISION_FULL_MODEL": "your-vision-model"
      }
    }
  }
}
```

若 `uv` 通过其它方式安装（pipx / scoop / choco），把 `command` 指向对应的 `uv.exe` 路径即可。

## 使用

在对话里对主模型说：

- 「看下这张图 `D:\xxx\chart.png`」→ `analyze_image(path, mode="full")`
- 「把这张图的文字提取出来 `D:\xxx\table.png`」→ `analyze_image(path, mode="ocr")`

## 工具

### `analyze_image`

- `path_or_url`：本地图片路径或 http(s) URL（PNG / JPEG / WEBP / GIF / BMP）
- `mode`：`"full"`（默认，全面理解）或 `"ocr"`（仅提取文字）

## 如何添加新 Provider

1. 在 `src/deepseek_vision_mcp/providers/` 新建文件，继承 `base.Provider` 并实现 `analyze`。
2. 在 `router.py` 的 `get_provider` 中按模型名（或其他判断）返回你的 Provider。
3. 完成，`analyze_image` 上层接口无需改动。

## 说明

本工具**不提供视觉模型**，只做「适配层」。你需要自带视觉 API 的 key。

## License

MIT



# deepseek-vision-mcp（English README）

An MCP server that acts as the "eyes" for text-only LLMs (such as DeepSeek) — a stable, provider-swappable **cloud vision adapter layer**.

## Design Philosophy (Four Layers)

- **Main model = Brain**: interpret, reason, judge, advise, decide tasks
- **Vision MCP = Eyes**: faithfully describe "what I see"
- **Skill = Work spec**: domain-specific rules (not in this project)
- **Claude Code = Orchestrator**: call tools, edit files, execute tasks

This MCP only answers "what I see", **not** "what it means", and never thinks on behalf of the main model.

## Features

- Dual-protocol routing: OpenAI-compatible Chat Completions (general vision models) + PaddleOCR dedicated OCR protocol
- Three-stage image pipeline: load → validate → preprocess (EXIF correction, aspect-ratio-preserving resize)
- Content-addressed cache (`image_sha256`): repeated analysis of the same image returns instantly
- Automatic retry on transient errors (≤2 attempts, exponential backoff)
- Failure transparency: reports errors clearly, never fabricates results

## Installation

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Configuration

All configuration is injected via environment variables (`.mcp.json` `env` or `.env`).

| Variable | Description | Default |
|---|---|---|
| `VISION_API_KEY` | Vision API key | none, required |
| `VISION_API_BASE_URL` | OpenAI-compatible Chat API base URL | none, required |
| `VISION_OCR_ENDPOINT` | PaddleOCR dedicated OCR endpoint (full URL) | none (set when using PaddleOCR) |
| `VISION_OCR_MODEL` | Model for `mode=ocr` | none, required |
| `VISION_FULL_MODEL` | Model for `mode=full` | none, required |
| `VISION_CACHE_ENABLED` | Cache switch | `true` |
| `VISION_CACHE_SCOPE` | `global` / `project` / `none` | `global` |
| `VISION_CACHE_DIR` | Cache dir override (empty = platform default) | empty |
| `VISION_CACHE_TTL_DAYS` | Cache TTL (days) | `30` |
| `VISION_CACHE_MAX_SIZE_MB` | Max cache size (MB) | `128` |
| `VISION_FALLBACK_ENABLED` | Fallback switch | `false` |
| `VISION_RETRY_MAX` | Max retries on transient errors | `2` |
| `VISION_TIMEOUT` | Per-request timeout (seconds) | `60` |

See `.env.example`.

### Registering with Claude Code

Project-level (`.mcp.json`) or user-level (`mcpServers` in `~/.claude.json`):

```json
{
  "mcpServers": {
    "deepseek-vision-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/deepseek-vision-mcp", "deepseek-vision-mcp"],
      "env": {
        "VISION_API_KEY": "sk-...",
        "VISION_API_BASE_URL": "https://your-vision-api.example.com/v1",
        "VISION_OCR_ENDPOINT": "https://your-ocr-api.example.com/v1/paddleocr",
        "VISION_OCR_MODEL": "PaddleOCR-VL-1.5",
        "VISION_FULL_MODEL": "your-vision-model"
      }
    }
  }
}
```

> If `uv` is not on PATH, use the full path to `uv` for `command`.

**Windows example** (`uv` is usually not on PATH; use the full path for `command` and forward slashes for the directory):

```json
{
  "mcpServers": {
    "deepseek-vision-mcp": {
      "command": "C:/Users/yourname/.local/bin/uv.exe",
      "args": ["run", "--directory", "D:/path/to/deepseek-vision-mcp", "deepseek-vision-mcp"],
      "env": {
        "VISION_API_KEY": "sk-...",
        "VISION_API_BASE_URL": "https://your-vision-api.example.com/v1",
        "VISION_FULL_MODEL": "your-vision-model"
      }
    }
  }
}
```

If `uv` is installed another way (pipx / scoop / choco), point `command` at the corresponding `uv.exe`.

## Usage

Tell the main model:

- "Look at this image `D:\xxx\chart.png`" → `analyze_image(path, mode="full")`
- "Extract the text from this image `D:\xxx\table.png`" → `analyze_image(path, mode="ocr")`

## Tool

### `analyze_image`

- `path_or_url`: local image path or http(s) URL (PNG / JPEG / WEBP / GIF / BMP)
- `mode`: `"full"` (default, full understanding) or `"ocr"` (text extraction only)

## Adding a New Provider

1. Create a new file under `src/deepseek_vision_mcp/providers/`, subclass `base.Provider` and implement `analyze`.
2. Return your provider from `get_provider` in `router.py` (keyed by model name or other criteria).
3. Done — the upper-level `analyze_image` tool needs no changes.

## Note

This tool **does not provide vision models**; it is only an adapter layer. You need to bring your own vision API key.

## License

MIT
