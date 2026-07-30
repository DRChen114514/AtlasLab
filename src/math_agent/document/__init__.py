"""Document Intelligence 模块 —— AtlasLab 文档解析入口。

统一处理 PDF (MinerU API / 本地回退)、DOCX、HTML、Markdown、LaTeX 等多格式文档，
输出结构化 Markdown + JSON + 元数据，供 Knowledge Pipeline 消费。
"""

from math_agent.document.parser import DocumentParser, ParsedDocument, parse_document
from math_agent.document.mineru import MinerUClient, MinerUResult, parse_via_mineru
from math_agent.document.structure import StructureParser, DocumentStructure
from math_agent.document.formulas import FormulaExtractor, ExtractedFormula
from math_agent.document.tables import TableExtractor, ExtractedTable
from math_agent.document.figures import FigureExtractor, ExtractedFigure
from math_agent.document.metadata import MetadataExtractor, DocumentMetadata

__all__ = [
    "DocumentParser",
    "ParsedDocument",
    "parse_document",
    "MinerUClient",
    "MinerUResult",
    "parse_via_mineru",
    "StructureParser",
    "DocumentStructure",
    "FormulaExtractor",
    "ExtractedFormula",
    "TableExtractor",
    "ExtractedTable",
    "FigureExtractor",
    "ExtractedFigure",
    "MetadataExtractor",
    "DocumentMetadata",
]
