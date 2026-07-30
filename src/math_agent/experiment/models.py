"""实验数据模型 —— ParamSweep, AblationStudy, RobustnessTest, ComparisonReport。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class ParamSweep:
    """参数扫描配置。"""
    param_name: str
    values: list[float]
    metric: str = "accuracy"
    default_value: float = 0.0
    results: dict[float, float] = field(default_factory=dict)

    def run(self, eval_func) -> dict[float, float]:
        """对每个参数值运行评估函数。"""
        for val in self.values:
            self.results[val] = eval_func(val)
        return self.results

    def best_value(self) -> tuple[float, float]:
        """返回 (最佳参数值, 最大指标值)。"""
        if not self.results:
            return (self.default_value, 0.0)
        return max(self.results.items(), key=lambda kv: kv[1])

    def summary(self) -> str:
        """生成参数扫描摘要。"""
        lines = [f"参数扫描: {self.param_name}", f"指标: {self.metric}", "-" * 40]
        for val, metric_val in sorted(self.results.items()):
            lines.append(f"  {self.param_name}={val:.4f}  {self.metric}={metric_val:.4f}")
        best_val, best_metric = self.best_value()
        lines.append(f"\n最优: {self.param_name}={best_val:.4f} ({self.metric}={best_metric:.4f})")
        return "\n".join(lines)


@dataclass
class AblationStudy:
    """消融实验。"""
    name: str
    components: list[str] = field(default_factory=list)

    # 完整模型性能
    full_score: float = 0.0

    # 移除某组件后的性能 {component: score}
    removal_scores: dict[str, float] = field(default_factory=dict)

    def remove(self, component: str, eval_func) -> float:
        """评估移除某组件后的性能。"""
        score = eval_func(component)
        self.removal_scores[component] = score
        return score

    def component_importance(self) -> dict[str, float]:
        """计算各组件的重要性 = 完整模型 - 移除后。"""
        return {
            comp: self.full_score - score
            for comp, score in self.removal_scores.items()
        }

    def summary(self) -> str:
        """生成消融实验摘要。"""
        lines = [f"消融实验: {self.name}", f"完整模型分数: {self.full_score:.4f}", "-" * 40]
        importance = self.component_importance()
        for comp, imp in sorted(importance.items(), key=lambda kv: kv[1], reverse=True):
            lines.append(
                f"  移除 {comp}: {self.removal_scores[comp]:.4f} (重要性: {imp:+.4f})"
            )
        return "\n".join(lines)


@dataclass
class RobustnessTest:
    """鲁棒性分析。"""
    name: str
    noise_levels: list[float] = field(default_factory=list)
    scores: dict[float, float] = field(default_factory=dict)
    baseline_score: float = 0.0

    def test(self, noise_level: float, eval_func) -> float:
        """在给定噪声水平下评估。"""
        score = eval_func(noise_level)
        self.scores[noise_level] = score
        return score

    def degradation(self) -> dict[float, float]:
        """计算各噪声水平下的性能退化。"""
        return {
            noise: self.baseline_score - score
            for noise, score in self.scores.items()
        }

    def summary(self) -> str:
        """生成鲁棒性分析摘要。"""
        lines = [f"鲁棒性分析: {self.name}", f"基线分数: {self.baseline_score:.4f}", "-" * 40]
        degradation = self.degradation()
        for noise, deg in sorted(degradation.items()):
            lines.append(
                f"  噪声 {noise:.2f}: {self.scores[noise]:.4f} (退化: {deg:+.4f})"
            )
        return "\n".join(lines)


@dataclass
class ComparisonReport:
    """模型/方案对比报告。"""
    models: list[str] = field(default_factory=list)
    metrics: list[str] = field(default_factory=list)

    # {model: {metric: value}}
    scores: dict[str, dict[str, float]] = field(default_factory=dict)

    def add_result(self, model: str, metric: str, value: float) -> None:
        """添加一个模型-指标对。"""
        if model not in self.scores:
            self.scores[model] = {}
        self.scores[model][metric] = value
        if model not in self.models:
            self.models.append(model)
        if metric not in self.metrics:
            self.metrics.append(metric)

    def winner(self, metric: str) -> str | None:
        """找出某指标的最佳模型。"""
        best_model = None
        best_score = float("-inf")
        for model, scores in self.scores.items():
            if metric in scores and scores[metric] > best_score:
                best_score = scores[metric]
                best_model = model
        return best_model

    def to_markdown_table(self) -> str:
        """生成 Markdown 格式的对比表。"""
        if not self.models or not self.metrics:
            return "(空)"

        header = "| 模型 | " + " | ".join(self.metrics) + " |"
        sep = "| --- | " + " | ".join(["---"] * len(self.metrics)) + " |"

        rows = []
        for model in self.models:
            vals = [
                f"{self.scores.get(model, {}).get(m, 0.0):.4f}"
                for m in self.metrics
            ]
            rows.append(f"| {model} | {' | '.join(vals)} |")

        return "\n".join([header, sep] + rows)
