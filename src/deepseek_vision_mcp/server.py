"""deepseek-vision-mcp MCP server。"""

from fastmcp import FastMCP

from deepseek_vision_mcp.analysis.analyzer import run_analysis
from deepseek_vision_mcp.config import VisionConfig
from deepseek_vision_mcp.image.loader import LoadError
from deepseek_vision_mcp.image.validate import ValidationError
from deepseek_vision_mcp.providers.base import ProviderError

mcp = FastMCP("deepseek-vision-mcp")


@mcp.tool()
def analyze_image(path_or_url: str, mode: str = "full") -> str:
    """当用户提供图片、截图、图表、照片，或要求查看图像内容时，调用本工具获取图片的视觉内容描述。

    注意：本工具面向「自身无法直接查看图片」的主模型。若你自身具备原生视觉、能直接查看图片内容，应优先使用自己的原生视觉能力，无需调用本工具；仅在自身无法直接看图时才使用本工具。

    默认使用 mode=full 进行完整视觉理解。仅当用户明确要求精确提取图片文字/表格内容时，使用 mode=ocr。

    Args:
        path_or_url: 本地图片路径或 http(s) URL。
        mode: "full"（默认，全面理解）或 "ocr"（仅提取文字）。
    """
    try:
        config = VisionConfig.from_env()
        result = run_analysis(config, path_or_url, mode)
        return result.raw
    except LoadError as e:
        return f"视觉分析失败：图片加载错误 - {e}"
    except ValidationError as e:
        return f"视觉分析失败：图片校验错误 - {e}"
    except ProviderError as e:
        return f"视觉分析失败：{e}"
    except ValueError as e:
        return f"视觉分析失败：{e}"
    except Exception as e:
        return f"视觉分析失败：{type(e).__name__} - {e}"


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
