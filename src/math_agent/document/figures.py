"""图片提取器 —— 从文档中提取图片引用与内嵌图片。

处理 Markdown 图片语法、HTML img 标签，以及从 MinerU JSON 中提取图片二进制。
"""
from __future__ import annotations

import base64
import re
from dataclasses import dataclass, field


@dataclass
class ExtractedFigure:
    """提取的图片。"""
    caption: str = ""
    alt_text: str = ""
    source_ref: str = ""  # 文件路径或 URL
    image_data: bytes = field(default_factory=bytes)
    mime_type: str = ""
    width: int = 0
    height: int = 0
    line_number: int = 0
    figure_id: str = ""


class FigureExtractor:
    """从文档中提取图片引用。

    支持：Markdown ![](...), HTML <img>, MinerU JSON images 字段。
    """

    # Markdown 图片：![alt](url "title")
    _MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"([^\"]*)\")?\)")

    # HTML <img> 标签
    _HTML_IMG_RE = re.compile(
        r'<img[^>]+src=["\']([^"\']+)["\'][^>]*(?:alt=["\']([^"\']*)["\'])?[^>]*>',
        re.IGNORECASE,
    )

    def extract(self, text: str) -> list[ExtractedFigure]:
        """从文本中提取所有图片引用。

        Args:
            text: 输入文本（Markdown 或 HTML）。

        Returns:
            ExtractedFigure 列表。
        """
        results: list[ExtractedFigure] = []

        for m in self._MD_IMAGE_RE.finditer(text):
            alt = m.group(1).strip()
            src = m.group(2).strip()
            title = m.group(3) or ""
            line_no = text[:m.start()].count("\n") + 1

            results.append(ExtractedFigure(
                alt_text=alt,
                caption=title or alt,
                source_ref=src,
                line_number=line_no,
            ))

        for m in self._HTML_IMG_RE.finditer(text):
            src = m.group(1)
            alt = m.group(2) or ""
            line_no = text[:m.start()].count("\n") + 1

            results.append(ExtractedFigure(
                alt_text=alt,
                caption=alt,
                source_ref=src,
                line_number=line_no,
            ))

        return results

    def extract_from_base64(self, text: str) -> list[ExtractedFigure]:
        """从文本中提取 base64 内嵌图片。

        Args:
            text: 可能包含 data:image/...;base64,... 的文本。

        Returns:
            ExtractedFigure 列表（含 image_data 二进制）。
        """
        pattern = re.compile(
            r'data:image/(\w+);base64,([A-Za-z0-9+/=]+)'
        )
        results: list[ExtractedFigure] = []
        for m in pattern.finditer(text):
            mime = f"image/{m.group(1)}"
            try:
                data = base64.b64decode(m.group(2))
                results.append(ExtractedFigure(
                    mime_type=mime,
                    image_data=data,
                    line_number=text[:m.start()].count("\n") + 1,
                ))
            except Exception:
                continue
        return results
