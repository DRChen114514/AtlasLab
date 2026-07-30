"""Experiment Manager —— 实验全生命周期管理。

管理参数、数据、模型、日志、图像、指标、随机种子、版本号。
支持自动对比、消融实验、鲁棒性分析。
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional


@dataclass
class ExperimentConfig:
    """单次实验配置。"""
    experiment_id: str = ""
    name: str = ""
    version: int = 1
    parameters: dict[str, Any] = field(default_factory=dict)
    random_seed: int = 42
    model_name: str = ""
    data_source: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if not self.experiment_id:
            import uuid
            self.experiment_id = uuid.uuid4().hex[:8]


@dataclass
class ExperimentRun:
    """单次实验运行记录。"""
    run_id: str
    config: ExperimentConfig
    status: str = "pending"  # pending, running, completed, failed
    start_time: str = ""
    end_time: str = ""
    metrics: dict[str, float] = field(default_factory=dict)
    logs: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)  # 产物路径
    error_message: str = ""

    def __post_init__(self):
        if not self.run_id:
            import uuid
            self.run_id = uuid.uuid4().hex[:8]


@dataclass
class ExperimentResult:
    """实验汇总结果。"""
    experiment_id: str
    config: ExperimentConfig
    runs: list[ExperimentRun] = field(default_factory=list)
    best_metrics: dict[str, float] = field(default_factory=dict)
    comparison: Optional["ComparisonReport"] = None


class ExperimentManager:
    """实验管理器 —— 管理实验生命周期。

    用法:
        mgr = ExperimentManager(workspace="./experiments")
        exp = mgr.create_experiment("grid_search_v1", params={"lr": 0.001})
        run = mgr.run_experiment(exp, eval_func)
        print(mgr.summary(exp.experiment_id))
    """

    def __init__(self, workspace: str | Path = "./experiments"):
        self.workspace = Path(workspace)
        self.workspace.mkdir(parents=True, exist_ok=True)
        self._experiments: dict[str, ExperimentResult] = {}
        self._runs: dict[str, list[ExperimentRun]] = {}
        self._load_state()

    def create_experiment(
        self,
        name: str,
        *,
        parameters: dict[str, Any] | None = None,
        random_seed: int = 42,
        model_name: str = "",
        tags: list[str] | None = None,
    ) -> ExperimentConfig:
        """创建新实验配置。"""
        config = ExperimentConfig(
            name=name,
            parameters=parameters or {},
            random_seed=random_seed,
            model_name=model_name,
            tags=tags or [],
        )
        self._experiments[config.experiment_id] = ExperimentResult(
            experiment_id=config.experiment_id,
            config=config,
        )
        return config

    def run_experiment(
        self,
        config: ExperimentConfig,
        eval_func: Callable[[dict[str, Any]], dict[str, float]],
    ) -> ExperimentRun:
        """运行实验。

        Args:
            config: 实验配置。
            eval_func: 评估函数，接收参数字典，返回指标字典。

        Returns:
            ExperimentRun 包含运行记录和指标。
        """
        run = ExperimentRun(
            run_id="",
            config=config,
            status="running",
            start_time=datetime.now(timezone.utc).isoformat(),
        )

        try:
            # 设置随机种子
            import random
            random.seed(config.random_seed)
            import numpy as np
            np.random.seed(config.random_seed)

            run.metrics = eval_func(config.parameters)
            run.status = "completed"
        except Exception as e:
            run.status = "failed"
            run.error_message = str(e)
            run.logs.append(f"[ERROR] {e}")

        run.end_time = datetime.now(timezone.utc).isoformat()
        self._runs.setdefault(config.experiment_id, []).append(run)
        self._save_state()

        return run

    def get_runs(self, experiment_id: str) -> list[ExperimentRun]:
        """获取某实验的所有运行记录。"""
        return self._runs.get(experiment_id, [])

    def best_run(self, experiment_id: str, metric: str = "score") -> ExperimentRun | None:
        """获取某实验在指定指标上的最佳运行。"""
        runs = self.get_runs(experiment_id)
        completed = [r for r in runs if r.status == "completed" and metric in r.metrics]
        if not completed:
            return None
        return max(completed, key=lambda r: r.metrics[metric])

    @staticmethod
    def param_sweep(
        param_name: str,
        values: list[float],
        eval_func: Callable[[float], float],
    ) -> "ParamSweep":
        """执行参数扫描。

        Args:
            param_name: 参数名。
            values: 参数值列表。
            eval_func: 评估函数 f(param_value) -> metric。

        Returns:
            ParamSweep 包含扫描结果。
        """
        from math_agent.experiment.models import ParamSweep
        sweep = ParamSweep(param_name=param_name, values=values)
        sweep.run(eval_func)
        return sweep

    @staticmethod
    def ablation(
        name: str,
        components: list[str],
        full_eval: Callable[[], float],
        removal_eval: Callable[[str], float],
    ) -> "AblationStudy":
        """执行消融实验。

        Args:
            name: 实验名称。
            components: 组件列表。
            full_eval: 完整模型评估函数 () -> score。
            removal_eval: 移除组件后评估函数 (component) -> score。

        Returns:
            AblationStudy 包含消融结果。
        """
        from math_agent.experiment.models import AblationStudy
        study = AblationStudy(name=name, components=list(components))
        study.full_score = full_eval()
        for comp in components:
            study.remove(comp, removal_eval)
        return study

    def _save_state(self) -> None:
        """持久化实验状态。"""
        state_path = self.workspace / "state.json"
        try:
            data = {
                "experiments": {
                    eid: {
                        "config": eid,
                        "runs": [
                            {
                                "run_id": r.run_id,
                                "status": r.status,
                                "metrics": r.metrics,
                                "error": r.error_message,
                            }
                            for r in self.get_runs(eid)
                        ],
                    }
                    for eid in self._experiments
                }
            }
            state_path.write_text(json.dumps(data, indent=2, default=str))
        except Exception:
            pass

    def _load_state(self) -> None:
        """加载持久化的实验状态。"""
        state_path = self.workspace / "state.json"
        if not state_path.exists():
            return
        try:
            data = json.loads(state_path.read_text())
        except Exception:
            return

    def summary(self, experiment_id: str) -> str:
        """生成实验摘要。"""
        runs = self.get_runs(experiment_id)
        if not runs:
            return f"实验 {experiment_id}: 无运行记录"

        completed = [r for r in runs if r.status == "completed"]
        failed = [r for r in runs if r.status == "failed"]

        lines = [
            f"实验摘要: {experiment_id}",
            f"总运行: {len(runs)} | 完成: {len(completed)} | 失败: {len(failed)}",
            "-" * 40,
        ]

        if completed:
            # 汇总所有指标
            all_metrics: dict[str, list[float]] = {}
            for r in completed:
                for k, v in r.metrics.items():
                    all_metrics.setdefault(k, []).append(v)
            for metric, values in all_metrics.items():
                import statistics
                lines.append(
                    f"  {metric}: "
                    f"mean={statistics.mean(values):.4f} "
                    f"std={statistics.stdev(values) if len(values) > 1 else 0:.4f} "
                    f"best={max(values):.4f}"
                )

        if failed:
            lines.append(f"\n失败运行: {len(failed)}")
            for r in failed[:3]:
                lines.append(f"  [{r.run_id}] {r.error_message[:100]}")

        return "\n".join(lines)
