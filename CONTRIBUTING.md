# 贡献指南

感谢你有兴趣为 `deepseek-vision-mcp` 贡献！这是一个「给无视觉能力的文本 LLM 当眼睛」的云端视觉适配层，欢迎任何形式的贡献。

## 报告 Bug

如果你发现了问题，请在 GitHub 上提 Issue，并尽量包含：

1. 你的环境（操作系统、Python 版本、主模型）。
2. 复现步骤。
3. 期望行为 vs 实际行为。
4. 相关日志（本工具的错误信息会带 `[Vision] model=... endpoint=... mode=... http=... error=...` 上下文，直接贴上来）。

## 提功能建议

提 Issue 并说明：

- 你想解决什么问题（场景）。
- 你期望的接口/行为。

## 提交代码

标准 fork + PR 流程：

1. Fork 本仓库。
2. 从 `main` 拉一个新分支（分支名描述用途，如 `feat/add-xxx-provider`）。
3. 修改代码。
4. 跑测试（见下）。
5. 提交并推送，开 Pull Request。

## 本地开发环境

需要 Python 3.11+ 和 [uv](https://docs.astral.sh/uv/)。

```bash
uv sync          # 安装依赖 + dev 依赖（pytest）
uv run pytest    # 跑测试
```

## 测试

所有改动应通过现有测试；新增功能请补对应测试。测试放在 `tests/` 目录。

```bash
uv run pytest
```

## 代码规范

- 保持分层清晰：`image/`（图片处理）、`providers/`（视觉 API 适配）、`analysis/`（prompt / 归一化）、`cache.py`（缓存）、`server.py`（MCP 接口）。
- 错误处理遵循「失败透明」：视觉服务失败时明确报错，绝不伪造结果。
- 不要在代码里硬编码任何 API key。

## 添加新 Provider（最常见贡献场景）

本项目的核心可扩展点是 Provider。添加一个新的视觉 API 只需 3 步：

1. 在 `src/deepseek_vision_mcp/providers/` 新建文件，继承 `base.Provider` 并实现 `analyze`：

   ```python
   from deepseek_vision_mcp.models import ProcessedImage
   from deepseek_vision_mcp.providers.base import Provider, ProviderError

   class MyProvider(Provider):
       name = "my_provider"

       def analyze(self, model, image, prompt, max_tokens=4096, mode=""):
           # 调用你的视觉 API，返回文字结果
           ...
   ```

2. 在 `providers/router.py` 的 `get_provider` 中按模型名（或其他判断）返回你的 Provider。

3. 在 `tests/` 补一个测试，用 `httpx.MockTransport` 或 monkeypatch 验证请求格式和响应解析。

完成这 3 步后，上层 `analyze_image` 工具无需任何改动即可使用新 Provider。

## 行为准则

请保持友善、尊重他人。这是一个协作项目，我们希望每个人都能愉快地参与。



# Contributing

Thanks for your interest in contributing to `deepseek-vision-mcp`! This is a cloud vision adapter layer that acts as the "eyes" for text-only LLMs. All forms of contribution are welcome.

## Reporting Bugs

If you find a bug, please open an Issue with:

1. Your environment (OS, Python version, main model).
2. Steps to reproduce.
3. Expected vs actual behavior.
4. Relevant logs (error messages carry `[Vision] model=... endpoint=... mode=... http=... error=...` context — paste them directly).

## Feature Requests

Open an Issue and describe:

- The problem you want to solve (scenario).
- The interface/behavior you expect.

## Submitting Code

Standard fork + PR workflow:

1. Fork this repository.
2. Create a branch from `main` (name it after the change, e.g. `feat/add-xxx-provider`).
3. Make your changes.
4. Run the tests (see below).
5. Commit, push, and open a Pull Request.

## Local Development

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync          # install deps + dev deps (pytest)
uv run pytest    # run tests
```

## Tests

All changes should pass existing tests; add tests for new features under `tests/`.

```bash
uv run pytest
```

## Code Style

- Keep the layering clear: `image/` (image processing), `providers/` (vision API adapters), `analysis/` (prompts / normalization), `cache.py` (cache), `server.py` (MCP interface).
- Follow "failure transparency": report errors clearly, never fabricate results.
- Never hardcode any API key.

## Adding a New Provider (the most common contribution)

The core extension point of this project is Provider. Adding a new vision API takes 3 steps:

1. Create a new file under `src/deepseek_vision_mcp/providers/`, subclass `base.Provider` and implement `analyze`:

   ```python
   from deepseek_vision_mcp.models import ProcessedImage
   from deepseek_vision_mcp.providers.base import Provider, ProviderError

   class MyProvider(Provider):
       name = "my_provider"

       def analyze(self, model, image, prompt, max_tokens=4096, mode=""):
           # call your vision API, return text result
           ...
   ```

2. Return your provider from `get_provider` in `providers/router.py` (keyed by model name or other criteria).

3. Add a test under `tests/` using `httpx.MockTransport` or monkeypatch to verify the request format and response parsing.

After these 3 steps, the upper-level `analyze_image` tool works with the new provider without any changes.

## Code of Conduct

Be kind and respectful. This is a collaborative project, and we want everyone to enjoy participating.
