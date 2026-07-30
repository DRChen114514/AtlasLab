"""元数据提取器 —— 从文档中提取结构化元信息。

包括：标题、作者、日期、摘要、关键词、语言、页数、引用信息等。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class DocumentMetadata:
    """文档元数据。"""
    title: str = ""
    authors: list[str] = field(default_factory=list)
    date: str = ""
    abstract: str = ""
    keywords: list[str] = field(default_factory=list)
    language: str = ""
    page_count: int = 0
    word_count: int = 0
    char_count: int = 0
    file_format: str = ""
    file_size_bytes: int = 0
    source_path: str = ""
    references: list[str] = field(default_factory=list)
    institutions: list[str] = field(default_factory=list)
    doi: str = ""
    extra: dict = field(default_factory=dict)


class MetadataExtractor:
    """从文档文本中提取元数据。

    用法:
        extractor = MetadataExtractor()
        meta = extractor.extract(document_text, file_format="pdf")
    """

    # 中文 "摘要：" / "Abstract:" 模式
    _ABSTRACT_RE = re.compile(
        r"(?:摘要|Abstract|概要)[：:]\s*(.+?)(?:\n\n|\n(?:\S))", re.DOTALL
    )
    _KEYWORDS_RE = re.compile(
        r"(?:关键词|Keywords|关键字)[：:]\s*(.+)",
    )

    def extract(self, text: str, *, file_format: str = "",
                source_path: str = "",
                file_size_bytes: int = 0) -> DocumentMetadata:
        """从文本中提取元数据。

        Args:
            text: 文档全文。
            file_format: 文件格式 (pdf, docx, md 等)。
            source_path: 源文件路径。
            file_size_bytes: 文件大小 (字节)。

        Returns:
            DocumentMetadata。
        """
        meta = DocumentMetadata(
            file_format=file_format,
            source_path=source_path,
            file_size_bytes=file_size_bytes,
            char_count=len(text),
            word_count=len(text.split()),
        )

        # 提取摘要
        m = self._ABSTRACT_RE.search(text)
        if m:
            abstract_text = m.group(1).strip()
            # 取第一个换行前的内容作为摘要
            meta.abstract = abstract_text.split("\n", 1)[0].strip()[:2000]

        # 提取关键词
        m = self._KEYWORDS_RE.search(text)
        if m:
            kw_text = m.group(1).strip()
            # 按中英文逗号、分号分割
            meta.keywords = [
                kw.strip()
                for kw in re.split(r"[，,;；]", kw_text)
                if kw.strip()
            ]

        # 检测语言
        chinese = len(re.findall(r"[\u4e00-\u9fff]", text))
        english = len(re.findall(r"[a-zA-Z]+", text))
        if chinese > english:
            meta.language = "zh"
        elif english > chinese:
            meta.language = "en"
        else:
            meta.language = "mixed"

        # 提取 DOI
        doi_match = re.search(r"10\.\d{4,}/[^\s]+", text)
        if doi_match:
            meta.doi = doi_match.group(0)

        return meta

    @staticmethod
    def from_markdown_frontmatter(text: str) -> DocumentMetadata:
        """从 Markdown frontmatter (YAML) 中提取元数据。"""
        frontmatter_match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
        if not frontmatter_match:
            return DocumentMetadata()

        fm = frontmatter_match.group(1)
        meta = DocumentMetadata()

        title_match = re.search(r"^title:\s*(.+)$", fm, re.MULTILINE)
        if title_match:
            meta.title = title_match.group(1).strip().strip('"').strip("'")

        date_match = re.search(r"^date:\s*(.+)$", fm, re.MULTILINE)
        if date_match:
            meta.date = date_match.group(1).strip()

        abstract_match = re.search(r"^abstract:\s*(.+)$", fm, re.MULTILINE)
        if abstract_match:
            meta.abstract = abstract_match.group(1).strip()

        return meta
