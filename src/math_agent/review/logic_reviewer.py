"""Logic Reviewer —— 逻辑链条完整性评审。

检查：前提-结论一致性、推理链完整性、论证充分性、避免循环论证。
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LogicReviewResult:
    """逻辑评审结果。"""
    score: float = 0.0
    approved: bool = False
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    logical_gaps: int = 0
    circular_reasoning_detected: bool = False


class LogicReviewer:
    """逻辑评审器 —— 检查论文逻辑链条。

    用法:
        reviewer = LogicReviewer()
        result = reviewer.review(paper_text)
    """

    def review(self, paper_text: str) -> LogicReviewResult:
        """对论文进行逻辑评审。

        Args:
            paper_text: 论文全文。

        Returns:
            LogicReviewResult 包含逻辑评审结果。
        """
        issues: list[str] = []
        suggestions: list[str] = []

        # 检查逻辑连接词是否存在
        logical_connectors = ["因此", "所以", "因为", "由于", "从而", "由此",
                              "therefore", "thus", "hence", "because", "since",
                              "consequently", "as a result"]
        has_connectors = any(c.lower() in paper_text.lower() for c in logical_connectors)
        if not has_connectors:
            issues.append("缺少逻辑连接词，推理链条不清晰")

        # 检查假设与结论的关联
        assumptions_section = self._find_section(paper_text, ["假设", "assumption"])
        conclusion_section = self._find_section(paper_text, ["结论", "conclusion"])
        if not assumptions_section and not conclusion_section:
            issues.append("论文缺少假设或结论章节")

        # 检测循环论证
        if self._detect_circular(paper_text):
            issues.append("疑似循环论证")
            suggestions.append("避免用结论证明前提，确保推理链是单向的")

        logical_gaps = len(issues)
        approved = logical_gaps == 0

        return LogicReviewResult(
            score=10.0 if approved else max(0, 10.0 - logical_gaps * 2),
            approved=approved,
            issues=issues,
            suggestions=suggestions,
            logical_gaps=logical_gaps,
            circular_reasoning_detected=self._detect_circular(paper_text),
        )

    @staticmethod
    def _find_section(text: str, keywords: list[str]) -> bool:
        """检查是否存在某章节关键词。"""
        text_lower = text.lower()
        return any(kw.lower() in text_lower for kw in keywords)

    @staticmethod
    def _detect_circular(text: str) -> bool:
        """检测循环论证的简单模式。"""
        import re
        # "A 因为 B" / "B 因为 A" 循环模式
        patterns = [
            r"因为(.{1,50})所以\1",
        ]
        for pat in patterns:
            if re.search(pat, text):
                return True
        return False
