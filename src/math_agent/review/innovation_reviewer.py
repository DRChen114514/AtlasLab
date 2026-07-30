"""Innovation Reviewer —— 方案创新性评审。

检查：方法新颖性、与已有工作的区别、独特贡献、学术/实用价值。
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class InnovationReviewResult:
    score: float = 0.0
    approved: bool = False
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    novelty_score: float = 0.0
    contrib_clarity: float = 0.0


class InnovationReviewer:
    """创新评审器 —— 评估方案的创新性与独特贡献。

    用法:
        reviewer = InnovationReviewer()
        result = reviewer.review(solution_text)
    """

    def review(self, solution_text: str) -> InnovationReviewResult:
        """对解决方案进行创新性评审。

        Args:
            solution_text: 解决方案文本。

        Returns:
            InnovationReviewResult 包含创新评审结果。
        """
        issues: list[str] = []
        suggestions: list[str] = []

        # 检查创新相关关键词
        innovation_keywords = ["创新", "提出", "改进", "首次", "novel", "propose",
                               "improvement", "contribution", "original",
                               "distinct from", "不同于"]
        keyword_count = sum(
            1 for kw in innovation_keywords if kw.lower() in solution_text.lower()
        )
        if keyword_count < 2:
            issues.append("创新点表述不够明确，建议增加创新关键词")
            suggestions.append("明确说明方法的新颖之处，与已有方法对比")

        # 检查对比分析
        comparison_keywords = ["对比", "比较", "优于", "compare", "outperform",
                               "better than", "versus", "vs."]
        has_comparison = any(
            kw.lower() in solution_text.lower() for kw in comparison_keywords
        )
        if not has_comparison:
            issues.append("缺少与已有方法的对比分析")
            suggestions.append("增加与基准方法或文献方法的定量对比")

        novelty = 5.0 + keyword_count * 0.5
        contrib_clarity = 7.0 if has_comparison else 4.0
        approved = len(issues) == 0

        return InnovationReviewResult(
            score=8.0 if approved else max(0, 10.0 - len(issues) * 2),
            approved=approved,
            issues=issues,
            suggestions=suggestions,
            novelty_score=min(10.0, novelty),
            contrib_clarity=contrib_clarity,
        )
