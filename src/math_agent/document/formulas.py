r"""公式提取器 —— 识别并提取数学公式（LaTeX / Unicode）。

从文档中检测行内公式 ($...$) 和块级公式 ($$...$$，begin...end)，
输出统一格式的 ExtractedFormula 列表。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ExtractedFormula:
    """提取的数学公式。"""
    latex: str
    display: bool = False  # True = 块级，False = 行内
    context_before: str = ""
    context_after: str = ""
    line_number: int = 0
    formula_id: str = ""


class FormulaExtractor:
    """从文本中提取 LaTeX 数学公式。

    支持: $inline$, $$display$$, \\[...\\], \\(...\\), \begin{equation}...\end{equation}
    """

    # 行内公式：$...$ 或 \(...\)
    _INLINE_RE = re.compile(r"(?<!\\)\$(.+?)(?<!\\)\$")
    _INLINE_PAREN_RE = re.compile(r"\\\((.*?)\\\)")

    # 块级公式：$$...$$，\[...\]，\begin{...}...\end{...}
    _DISPLAY_RE = re.compile(r"\$\$(.+?)\$\$", re.DOTALL)
    _DISPLAY_BRACKET_RE = re.compile(r"\\\[(.*?)\\\]", re.DOTALL)
    _ENV_RE = re.compile(
        r"\\begin\{(equation|align|eqnarray|gather|multline)\*?\}"
        r"(.*?)"
        r"\\end\{\1\*?\}",
        re.DOTALL,
    )

    def extract(self, text: str, *, context_chars: int = 80) -> list[ExtractedFormula]:
        """提取文档中的所有数学公式。

        Args:
            text: 输入文本。
            context_chars: 前/后文提取字符数。

        Returns:
            ExtractedFormula 列表。
        """
        results: list[ExtractedFormula] = []
        lines = text.split("\n")

        # 提取块级公式
        for m in re.finditer(self._ENV_RE, text):
            latex = m.group(2).strip()
            start = m.start()
            line_no = text[:start].count("\n") + 1
            ctx_before = text[max(0, start - context_chars):start].strip()
            ctx_after = text[m.end():m.end() + context_chars].strip()
            results.append(ExtractedFormula(
                latex=latex,
                display=True,
                context_before=ctx_before,
                context_after=ctx_after,
                line_number=line_no,
            ))

        for m in re.finditer(self._DISPLAY_RE, text):
            latex = m.group(1).strip()
            start = m.start()
            line_no = text[:start].count("\n") + 1
            ctx_before = text[max(0, start - context_chars):start].strip()
            ctx_after = text[m.end():m.end() + context_chars].strip()
            results.append(ExtractedFormula(
                latex=latex,
                display=True,
                context_before=ctx_before,
                context_after=ctx_after,
                line_number=line_no,
            ))

        # 提取行内公式
        for m in re.finditer(self._INLINE_RE, text):
            latex = m.group(1).strip()
            if not latex:
                continue
            start = m.start()
            line_no = text[:start].count("\n") + 1
            ctx_before = text[max(0, start - context_chars):start].strip()
            ctx_after = text[m.end():m.end() + context_chars].strip()
            results.append(ExtractedFormula(
                latex=latex,
                display=False,
                context_before=ctx_before,
                context_after=ctx_after,
                line_number=line_no,
            ))

        return results

    def extract_unique(self, text: str) -> list[str]:
        """提取所有唯一公式（去重），仅返回 LaTeX 字符串。"""
        formulas = self.extract(text)
        seen: set[str] = set()
        unique: list[str] = []
        for f in formulas:
            normalized = f.latex.replace(" ", "").strip()
            if normalized not in seen and len(normalized) > 2:
                seen.add(normalized)
                unique.append(f.latex)
        return unique
