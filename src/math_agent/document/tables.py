"""表格提取器 —— 从文档中提取表格数据。

支持 Markdown 表格、CSV/TSV 文本，以及从 MinerU JSON 中提取结构化表格。
"""
from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass, field


@dataclass
class ExtractedTable:
    """提取的表格。"""
    caption: str = ""
    headers: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
    raw_markdown: str = ""
    line_number: int = 0
    table_id: str = ""


class TableExtractor:
    """从文本中提取表格数据。

    支持格式：Markdown、CSV、HTML <table>、MinerU JSON。
    """

    # Markdown 表格：| header1 | header2 | ... |---|---|---|
    _MD_TABLE_RE = re.compile(
        r"(?:^|\n)(\|[^\n]+\|\s*\n\|[-:| ]+\|\s*\n(?:\|[^\n]+\|\s*\n)*)",
        re.MULTILINE,
    )

    def extract_markdown(self, text: str) -> list[ExtractedTable]:
        """从 Markdown 文本中提取表格。

        Args:
            text: Markdown 文本。

        Returns:
            ExtractedTable 列表。
        """
        results: list[ExtractedTable] = []
        for m in self._MD_TABLE_RE.finditer(text):
            block = m.group(1).strip()
            line_no = text[:m.start()].count("\n") + 1

            lines = block.strip().split("\n")
            if len(lines) < 2:
                continue

            # 解析表头
            headers = [cell.strip() for cell in lines[0].split("|") if cell.strip()]

            # 跳过分隔行 |---|---|
            data_lines = [ln for ln in lines[1:] if not re.match(r"^[\| \-:]+$", ln)]
            rows: list[list[str]] = []
            for line in data_lines:
                cells = [cell.strip() for cell in line.split("|") if cell.strip()]
                if cells:
                    rows.append(cells)

            if headers or rows:
                results.append(ExtractedTable(
                    headers=headers,
                    rows=rows,
                    raw_markdown=block,
                    line_number=line_no,
                ))

        return results

    def extract_csv(self, text: str, *, delimiter: str = ",") -> list[ExtractedTable]:
        """从 CSV 文本中提取表格。

        Args:
            text: CSV 文本。
            delimiter: 分隔符。

        Returns:
            ExtractedTable 列表。
        """
        results: list[ExtractedTable] = []
        reader = csv.reader(io.StringIO(text), delimiter=delimiter)
        all_rows = list(reader)

        if not all_rows:
            return results

        headers = all_rows[0]
        data_rows = all_rows[1:] if len(all_rows) > 1 else []

        results.append(ExtractedTable(
            headers=headers,
            rows=data_rows,
            raw_markdown=text,
        ))
        return results

    def extract_all(self, text: str) -> list[ExtractedTable]:
        """尝试多种策略提取表格。"""
        md_tables = self.extract_markdown(text)
        if md_tables:
            return md_tables
        # 尝试 CSV 检测
        if "," in text and "\n" in text:
            try:
                return self.extract_csv(text)
            except Exception:
                pass
        return []
