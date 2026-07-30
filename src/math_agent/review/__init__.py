"""Reviewer System 模块 —— AtlasLab 多维度评审层。

五位评审专家覆盖不同维度：
- Math Reviewer：数学推导正确性、公式完整性、量纲一致性
- Logic Reviewer：逻辑链条完整性、前提-结论一致性
- Writing Reviewer：学术写作规范、结构清晰度、术语准确性
- Competition Reviewer：竞赛格式要求、评分标准对齐
- Innovation Reviewer：方案创新性、方法独特性

每个 Reviewer 均为独立模块，可单独调用或组合使用。
"""

from math_agent.review.math_reviewer import MathReviewer, MathReviewResult
from math_agent.review.logic_reviewer import LogicReviewer, LogicReviewResult
from math_agent.review.writing_reviewer import WritingReviewer, WritingReviewResult
from math_agent.review.competition_reviewer import CompetitionReviewer, CompetitionReviewResult
from math_agent.review.innovation_reviewer import InnovationReviewer, InnovationReviewResult

__all__ = [
    "MathReviewer",
    "MathReviewResult",
    "LogicReviewer",
    "LogicReviewResult",
    "WritingReviewer",
    "WritingReviewResult",
    "CompetitionReviewer",
    "CompetitionReviewResult",
    "InnovationReviewer",
    "InnovationReviewResult",
]
