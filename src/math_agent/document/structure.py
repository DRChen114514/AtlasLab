"""文档结构解析器 —— 提取标题、章节、段落层次。

对解析后的 Markdown/纯文本进行结构化分析，识别文档的层级结构
（一级标题、二级标题、段落、列表），输出 DocumentStructure。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Section:
    """文档章节。"""
    level: int
    title: str
    content: str = ""
    start_line: int = 0
    end_line: int = 0
    children: list["Section"] = field(default_factory=list)


@dataclass
class DocumentStructure:
    """文档结构化视图。"""
    title: str = ""
    sections: list[Section] = field(default_factory=list)
    total_lines: int = 0
    total_chars: int = 0
    language: str = ""  # "zh", "en", "mixed"


class StructureParser:
    """从 Markdown/文本中提取文档结构。"""

    _HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

    def parse(self, text: str, *, title: str = "") -> DocumentStructure:
        """解析文本结构，识别标题层级并构建章节树。"""
        lines = text.split("\n")
        total_chars = len(text)

        headings: list[tuple[int, int, str]] = []
        for idx, line in enumerate(lines):
            m = self._HEADING_RE.match(line)
            if m:
                level = len(m.group(1))
                heading_text = m.group(2).strip()
                headings.append((idx, level, heading_text))

        if not headings:
            return DocumentStructure(
                title=title,
                sections=[
                    Section(level=0, title="全文", content=text,
                            start_line=0, end_line=len(lines))
                ],
                total_lines=len(lines),
                total_chars=total_chars,
                language=self._detect_language(text),
            )

        if not title:
            for _, level, heading_text in headings:
                if level == 1:
                    title = heading_text
                    break

        sections = self._build_sections(lines, headings)
        return DocumentStructure(
            title=title,
            sections=sections,
            total_lines=len(lines),
            total_chars=total_chars,
            language=self._detect_language(text),
        )

    def _build_sections(
        self, lines: list[str], headings: list[tuple[int, int, str]]
    ) -> list[Section]:
        """构建章节树，基于标题层级嵌套。"""
        if not headings:
            return []
        sections: list[Section] = []
        stack: list[Section] = []
        for i, (line_idx, level, heading_text) in enumerate(headings):
            next_line = headings[i + 1][0] if i + 1 < len(headings) else len(lines)
            content = "\n".join(lines[line_idx + 1 : next_line]).strip()
            section = Section(
                level=level,
                title=heading_text,
                content=content,
                start_line=line_idx,
                end_line=next_line,
            )
            while stack and stack[-1].level >= level:
                stack.pop()
            if stack:
                stack[-1].children.append(section)
            else:
                sections.append(section)
            stack.append(section)
        return sections

    @staticmethod
    def _detect_language(text: str) -> str:
        """检测文本主要语言。"""
        if not text:
            return ""
        chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
        english_words = len(re.findall(r"[a-zA-Z]+", text))
        if chinese_chars > english_words * 2:
            return "zh"
        elif english_words > chinese_chars * 2:
            return "en"
        return "mixed"

    def to_outline(self, structure: DocumentStructure) -> str:
        """将文档结构渲染为 Markdown 大纲。"""
        lines = ["# " + structure.title if structure.title else "# 文档大纲"]
        def _render(secs: list[Section], indent: int = 0):
            for sec in secs:
                prefix = "  " * indent + "-"
                lines.append(f"{prefix} {'#' * sec.level} {sec.title}")
                if sec.children:
                    _render(sec.children, indent + 1)
        _render(structure.sections)
        return "\n".join(lines)
