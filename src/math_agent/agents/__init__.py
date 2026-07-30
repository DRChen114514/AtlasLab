"""Agent Layer 模块 —— AtlasLab Agent 编排层。

Planning → Modeling → Experiment → Writing → Review 的 Agent 体系。
当前为过渡层，重新导出 nodes/ 中已实现的节点函数，同时为 V3
的独立 Agent 架构预留命名空间。

Planning Agents:
- analyst: 题目理解与 Blueprint 生成
- blueprint_critic: Blueprint 审查

Modeling Agents:
- modeler: 建模（准备/推导/一致性检查）
- model_critic: 模型审查
- model_code_consistency: 模型-代码一致性验证

Experiment Agents:
- coder: 代码生成与执行
- sensitivity: 敏感性分析
- figure_pipeline: 图表生成

Writing Agents:
- writer: 论文写作（大纲/逐章）
- paper_critic: 论文审查
- table_assembler: 表格装配

Review Agents:
- evaluation: 量化评分
- human_review: 人工评审入口
- latex_node: LaTeX 编译
- finalizer: 最终收口
"""
from math_agent.nodes.analyst import analyst_node
from math_agent.nodes.blueprint_critic import blueprint_critic_node
from math_agent.nodes.modeler import (
    modeler_prepare_node,
    modeler_derivation_node,
    modeler_consistency_node,
)
from math_agent.nodes.model_critic import model_critic_node
from math_agent.nodes.coder import (
    coder_prepare_node,
    coder_generate_node,
    coder_execute_node,
)
from math_agent.nodes.model_code_consistency import model_code_consistency_node
from math_agent.nodes.sensitivity import (
    sensitivity_plan_node,
    sensitivity_code_generate_node,
    sensitivity_code_execute_node,
    sensitivity_interpret_node,
)
from math_agent.nodes.figure_pipeline import (
    figure_prepare_node,
    figure_critic_node,
    figure_analysis_node,
)
from math_agent.nodes.writer import writer_node, writer_section_node
from math_agent.nodes.paper_critic import paper_critic_node
from math_agent.nodes.evaluation import evaluation_node
from math_agent.nodes.human_review import human_review_node
from math_agent.nodes.latex_node import latex_node
from math_agent.nodes.finalizer import finalizer_node
from math_agent.nodes.table_assembler import table_assembler_node

__all__ = [
    "analyst_node",
    "blueprint_critic_node",
    "modeler_prepare_node",
    "modeler_derivation_node",
    "modeler_consistency_node",
    "model_critic_node",
    "coder_prepare_node",
    "coder_generate_node",
    "coder_execute_node",
    "model_code_consistency_node",
    "sensitivity_plan_node",
    "sensitivity_code_generate_node",
    "sensitivity_code_execute_node",
    "sensitivity_interpret_node",
    "figure_prepare_node",
    "figure_critic_node",
    "figure_analysis_node",
    "writer_node",
    "writer_section_node",
    "paper_critic_node",
    "evaluation_node",
    "human_review_node",
    "latex_node",
    "finalizer_node",
    "table_assembler_node",
]
