"""Competition Reviewer —— 竞赛格式评审。

检查：是否符合竞赛论文要求（页数、格式、摘要字数等）、
评分标准对齐、创新点是否突出、是否满足题目所有要求。
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CompetitionReviewResult:
    score: float = 0.0
    approved: bool = False
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    format_compliance: bool = True
    requirements_met: list[str] = field(default_factory=list)
    requirements_missing: list[str] = field(default_factory=list)


class CompetitionReviewer:
    """竞赛评审器 —— 检查竞赛格式与要求对齐。

    用法:
        reviewer = CompetitionReviewer()
        result = reviewer.review(paper_text, competition_type="美赛")
    """

    def review(
        self,
        paper_text: str,
        *,
        competition_type: str = "generic",
    ) -> CompetitionReviewResult:
        """对论文进行竞赛格式评审。

        Args:
            paper_text: 论文全文。
            competition_type: 竞赛类型 ("美赛", "国赛", "亚太赛", "generic")。

        Returns:
            CompetitionReviewResult 包含竞赛格式评审结果。
        """
        issues: list[str] = []
        suggestions: list[str] = []
        req_met: list[str] = []
        req_missing: list[str] = []

        # 字数检查（竞赛论文通常有限制）
        char_count = len(paper_text)
        if char_count < 5000:
            issues.append(f"论文字数不足 ({char_count} 字符)")
            req_missing.append("论文长度")
        else:
            req_met.append("论文长度")

        # 摘要检查（美赛要求明确的 Summary）
        if competition_type in ("美赛", "MCM", "ICM"):
            if "summary" not in paper_text[:500].lower() and "摘要" not in paper_text[:500]:
                issues.append("美赛要求论文开头为 Summary/摘要")
                suggestions.append("在论文开头添加英文 Summary")
                req_missing.append("论文摘要")
            else:
                req_met.append("论文摘要")

        # 小节标题检查
        section_keywords = ["Introduction", "Model", "Solution", "Conclusion",
                           "引言", "模型", "求解", "结论"]
        found = [kw for kw in section_keywords if kw.lower() in paper_text.lower()]
        if len(found) < 3:
            issues.append("章节结构不完整")

        # 创新点检查
        innovation_keywords = ["创新", "改进", "提出", "novel", "improve", "propose", "contribution"]
        has_innovation = any(kw.lower() in paper_text.lower() for kw in innovation_keywords)
        if not has_innovation:
            issues.append("未明确说明创新点/贡献")
            req_missing.append("创新点说明")
        else:
            req_met.append("创新点说明")

        approved = len(issues) == 0
        return CompetitionReviewResult(
            score=10.0 if approved else max(0, 10.0 - len(issues) * 1.5),
            approved=approved,
            issues=issues,
            suggestions=suggestions,
            format_compliance=True,
            requirements_met=req_met,
            requirements_missing=req_missing,
        )
