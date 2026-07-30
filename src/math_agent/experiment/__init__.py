"""Experiment Center 模块 —— AtlasLab 实验管理中心。

统一管理参数、数据、模型、日志、图像、指标、随机种子、版本号。
支持自动对比、消融实验、鲁棒性分析。
"""

from math_agent.experiment.manager import (
    ExperimentManager,
    ExperimentConfig,
    ExperimentRun,
    ExperimentResult,
)
from math_agent.experiment.models import (
    ParamSweep,
    AblationStudy,
    RobustnessTest,
    ComparisonReport,
)

__all__ = [
    "ExperimentManager",
    "ExperimentConfig",
    "ExperimentRun",
    "ExperimentResult",
    "ParamSweep",
    "AblationStudy",
    "RobustnessTest",
    "ComparisonReport",
]
