"""Knowledge Base 核心实现 —— 知识库管理与检索。

统一管理多个知识库：数模模型库、历届论文、教材、算法模板、代码模板、
Prompt Library、数据集索引。
"""
from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class KnowledgeItem:
    """知识库中的单条知识。"""
    id: str
    title: str
    content: str
    source_type: str  # "model_lib", "paper", "textbook", "algorithm", "code", "prompt"
    source_path: str = ""
    tags: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    content_hash: str = ""
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.content_hash:
            self.content_hash = hashlib.sha256(
                self.content.encode("utf-8")
            ).hexdigest()[:16]


@dataclass
class KnowledgeSource:
    """知识来源描述。"""
    name: str
    source_type: str
    path: str
    file_count: int = 0
    item_count: int = 0
    last_ingested: str = ""


@dataclass
class KnowledgeQuery:
    """知识检索查询。"""
    text: str
    source_types: list[str] | None = None
    top_k: int = 10
    min_score: float = 0.0
    use_hybrid: bool = True  # 向量 + BM25 混合检索


@dataclass
class KnowledgeResult:
    """知识检索结果。"""
    item: KnowledgeItem
    score: float
    retrieval_method: str  # "vector", "bm25", "hybrid"


class KnowledgeBase(ABC):
    """知识库抽象基类。

    每个具体知识库实现检索、添加、删除、统计等接口。
    """

    def __init__(self, name: str, source_type: str):
        self.name = name
        self.source_type = source_type

    @abstractmethod
    def search(self, query: KnowledgeQuery) -> list[KnowledgeResult]:
        """检索知识。"""
        ...

    @abstractmethod
    def add(self, item: KnowledgeItem) -> str:
        """添加知识条目，返回条目 ID。"""
        ...

    @abstractmethod
    def remove(self, item_id: str) -> bool:
        """删除知识条目。"""
        ...

    @abstractmethod
    def count(self) -> int:
        """知识条目总数。"""
        ...

    @abstractmethod
    def clear(self) -> None:
        """清空知识库。"""
        ...


class InMemoryKB(KnowledgeBase):
    """内存知识库 —— 轻量级实现，用于开发和测试。"""

    def __init__(self, name: str, source_type: str):
        super().__init__(name, source_type)
        self._items: dict[str, KnowledgeItem] = {}
        self._tags_index: dict[str, set[str]] = {}

    def search(self, query: KnowledgeQuery) -> list[KnowledgeResult]:
        """基于关键词和标签的简单匹配搜索。"""
        results: list[KnowledgeResult] = []
        query_lower = query.text.lower()
        query_words = set(query_lower.split())

        for item in self._items.values():
            if query.source_types and item.source_type not in query.source_types:
                continue

            score = 0.0
            content_lower = item.content.lower()
            title_lower = item.title.lower()

            # 标题匹配权重更高
            if query_lower in title_lower:
                score += 3.0
            # 内容关键词匹配
            matched = sum(1 for w in query_words if w in content_lower)
            if matched:
                score += matched * 1.0
            # 标签匹配
            tag_matched = sum(1 for t in item.tags if t.lower() in query_lower)
            if tag_matched:
                score += tag_matched * 2.0

            if score >= query.min_score:
                results.append(KnowledgeResult(
                    item=item,
                    score=score,
                    retrieval_method="keyword",
                ))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:query.top_k]

    def add(self, item: KnowledgeItem) -> str:
        self._items[item.id] = item
        for tag in item.tags:
            self._tags_index.setdefault(tag, set()).add(item.id)
        return item.id

    def remove(self, item_id: str) -> bool:
        if item_id not in self._items:
            return False
        item = self._items.pop(item_id)
        for tag in item.tags:
            if tag in self._tags_index:
                self._tags_index[tag].discard(item_id)
        return True

    def count(self) -> int:
        return len(self._items)

    def clear(self) -> None:
        self._items.clear()
        self._tags_index.clear()


class ModelLibraryKB(InMemoryKB):
    """数模模型库 —— 常见数学模型、算法、解题框架。"""

    def __init__(self):
        super().__init__("model_library", "model_lib")


class PaperLibraryKB(InMemoryKB):
    """优秀论文库 —— 历届竞赛获奖论文。"""

    def __init__(self):
        super().__init__("paper_library", "paper")


class AlgorithmTemplateKB(InMemoryKB):
    """算法模板库 —— GA, PSO, NSGA-II, Monte Carlo 等标准实现。"""

    def __init__(self):
        super().__init__("algorithm_templates", "algorithm")


class CodeTemplateKB(InMemoryKB):
    """代码模板库 —— Python/C++ 常用代码模板。"""

    def __init__(self):
        super().__init__("code_templates", "code")


class PromptLibraryKB(InMemoryKB):
    """Prompt 库 —— 各 Agent 节点的提示词模板与最佳实践。"""

    def __init__(self):
        super().__init__("prompt_library", "prompt")


class MultiKnowledgeBase:
    """多知识库联合检索管理器。

    用法:
        mkb = MultiKnowledgeBase()
        mkb.register(ModelLibraryKB())
        mkb.register(PaperLibraryKB())
        results = mkb.search(KnowledgeQuery("线性规划"))
    """

    def __init__(self):
        self._bases: dict[str, KnowledgeBase] = {}

    def register(self, kb: KnowledgeBase) -> None:
        """注册一个知识库。"""
        self._bases[kb.name] = kb

    def unregister(self, name: str) -> KnowledgeBase | None:
        """注销一个知识库。"""
        return self._bases.pop(name, None)

    def search(self, query: KnowledgeQuery) -> list[KnowledgeResult]:
        """联合检索所有已注册的知识库。"""
        all_results: list[KnowledgeResult] = []
        for kb in self._bases.values():
            all_results.extend(kb.search(query))
        all_results.sort(key=lambda r: r.score, reverse=True)
        return all_results[:query.top_k]

    def stats(self) -> dict:
        """各知识库统计信息。"""
        return {name: kb.count() for name, kb in self._bases.items()}

    def clear_all(self) -> None:
        """清空所有知识库。"""
        for kb in self._bases.values():
            kb.clear()
