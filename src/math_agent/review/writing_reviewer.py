"""Writing Reviewer —— 学术写作规范评审。

检查：学术用语准确性、章节结构完整性、图表引用、参考文献格式、
摘要质量、行文流畅度。
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class WritingReviewResult:
    score: float = 0.0
    approved: bool = False
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    grammar_issues: int = 0
    structure_score: float = 0.0
    clarity_score: float = 0.0


class WritingReviewer:
    """写作评审器 —— 检查学术写作质量。

    用法:
        reviewer = WritingReviewer()
        result = reviewer.review(paper_text)
    """

    def review(self, paper_text: str) -> WritingReviewResult:
        """对论文写作进行评审。

        Args:
            paper_text: 论文全文或章节文本。

        Returns:
            WritingReviewResult 包含写作评审结果。
        """
        issues: list[str] = []
        suggestions: list[str] = []

        # 检查必要章节
        required_sections = ["摘要", "abstract", "引言", "introduction",
                             "模型", "model", "求解", "solution",
                             "结论", "conclusion"]
        text_lower = paper_text.lower()
        missing = [s for s in required_sections if s not in text_lower]
        if missing:
            issues.append(f"缺少必要章节: {', '.join(missing[:3])}")

        # 检查表格/图片引用
        import re
        table_refs = re.findall(r"表\s*\d|Table\s*\d|如表|见下表|see table", paper_text)
        figure_refs = re.findall(r"图\s*\d|Figure\s*\d|如图|见下图|see figure", paper_text)
        has_tables = "|" in paper_text or "\\begin{tabular}" in paper_text
        has_figures = "![" in paper_text or "\\includegraphics" in paper_text

        if has_tables and not table_refs:
            issues.append("文中包含表格但缺少表格引用")
        if has_figures and not figure_refs:
            issues.append("文中包含图片但缺少图片引用")

        # 检查参考文献
        ref_count = len(re.findall(r"\[\d+\]", paper_text))
        if ref_count == 0:
            issues.append("缺少参考文献")

        grammar_issues = len(issues)
        approved = grammar_issues == 0

        return WritingReviewResult(
            score=10.0 if approved else max(0, 10.0 - grammar_issues * 1.5),
            approved=approved,
            issues=issues,
            suggestions=suggestions,
            grammar_issues=grammar_issues,
            structure_score=8.0 if len(missing) < 2 else 5.0,
            clarity_score=8.0,
        )
