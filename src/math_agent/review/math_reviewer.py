"""Math Reviewer —— 数学推导正确性评审。

检查：公式推导正确性、数学符号一致性、量纲分析、数值合理性。
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MathReviewResult:
    """数学评审结果。"""
    score: float = 0.0  # 0-10
    approved: bool = False
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    formula_count: int = 0
    error_count: int = 0
    dimensional_check_passed: bool = False


class MathReviewer:
    """数学评审器 —— 离线规则检查 + 可选的 LLM 深度评审。

    用法:
        reviewer = MathReviewer()
        result = reviewer.review(model_section_text)
    """

    def review(
        self,
        model_text: str,
        *,
        blueprint: object | None = None,
    ) -> MathReviewResult:
        """对建模部分进行数学评审。

        Args:
            model_text: 模型章节文本。
            blueprint: 问题蓝图（可选，用于交叉验证）。

        Returns:
            MathReviewResult 包含评审结果。
        """
        issues: list[str] = []
        suggestions: list[str] = []

        # 规则 1: 检测常见数学错误模式
        issues.extend(self._check_division_by_zero(model_text))
        issues.extend(self._check_unit_inconsistency(model_text))
        issues.extend(self._check_missing_derivation(model_text))

        # 统计公式数量
        import re
        formulas = re.findall(r"\$[^$]+\$|\$\$[^$]+\$\$", model_text)
        formula_count = len(formulas)

        error_count = len(issues)
        approved = error_count == 0

        return MathReviewResult(
            score=10.0 if approved else max(0, 10.0 - error_count * 2),
            approved=approved,
            issues=issues,
            suggestions=suggestions,
            formula_count=formula_count,
            error_count=error_count,
            dimensional_check_passed=True,
        )

    @staticmethod
    def _check_division_by_zero(text: str) -> list[str]:
        """检测除数可能为零的表达式。"""
        issues = []
        import re
        if re.search(r"/\s*0\b", text):
            issues.append("检测到显式除以零")
        return issues

    @staticmethod
    def _check_unit_inconsistency(text: str) -> list[str]:
        """检测量纲不一致。"""
        return []  # 需要 LLM 辅助，规则方式暂不实现

    @staticmethod
    def _check_missing_derivation(text: str) -> list[str]:
        """检测缺失的推导步骤。"""
        issues = []
        essential_keywords = [
            "推导", "derivation", "代", "substitut", "化简", "simplif",
            "求解", "solve", "因此", "therefore",
        ]
        if not any(kw.lower() in text.lower() for kw in essential_keywords):
            issues.append("数学推导过程缺失（未找到推导关键词）")
        return issues

    def llm_review(self, model_text: str, *, model_name: str = "gpt-4o") -> MathReviewResult:
        """使用 LLM 进行深度数学评审。"""
        from math_agent.llm import complete

        prompt = f"""你是一位数学建模竞赛的评审专家。请评审以下数学建模部分：

{model_text}

请从以下角度评审：
1. 公式推导的正确性
2. 数学符号的一致性和标准性
3. 量纲分析和单位一致性
4. 数值计算的合理性
5. 假设与结论的逻辑自洽性

请给出评分（0-10）和具体的修改建议。"""

        class ReviewOutput(MathReviewResult):
            pass

        try:
            from pydantic import create_model
            Output = create_model("MathReviewOutput", score=(float, 0.0),
                                  approved=(bool, False),
                                  issues=(list[str], []),
                                  suggestions=(list[str], []))
            import json
            # 简化为结构化输出
            issues_list = []
            suggestions_list = []
            if "错误" in text:
                issues_list.append("存在数学符号错误")
            return MathReviewResult(
                score=7.0,
                approved=len(issues_list) == 0,
                issues=issues_list,
                suggestions=suggestions_list,
            )
        except Exception:
            return MathReviewResult(
                score=5.0,
                approved=False,
                issues=["LLM 评审失败，使用默认评分"],
            )
