"""Knowledge Pipeline 模块 —— AtlasLab 知识管理层。

维护多个知识库：数模模型库、历届优秀论文、教材、算法模板、代码模板、
Prompt Library、数据集索引。提供统一的知识检索接口，支持向量搜索、
BM25、Reranker 和混合检索。
"""

from math_agent.knowledge.base import (
    KnowledgeBase,
    KnowledgeItem,
    KnowledgeSource,
    KnowledgeQuery,
    KnowledgeResult,
    MultiKnowledgeBase,
    ModelLibraryKB,
    PaperLibraryKB,
    AlgorithmTemplateKB,
    CodeTemplateKB,
    PromptLibraryKB,
)

__all__ = [
    "KnowledgeBase",
    "KnowledgeItem",
    "KnowledgeSource",
    "KnowledgeQuery",
    "KnowledgeResult",
    "MultiKnowledgeBase",
    "ModelLibraryKB",
    "PaperLibraryKB",
    "AlgorithmTemplateKB",
    "CodeTemplateKB",
    "PromptLibraryKB",
]
