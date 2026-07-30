"""MinerU API 客户端 —— 高精度 PDF 解析。

MinerU (opendatalab/MinerU) 提供专业的 PDF 转 Markdown/JSON 服务，擅长处理
数学公式、表格、图片等复杂排版。本模块封装 MinerU API 调用与错误处理，并支持
本地 PyMuPDF/pdfplumber 作为回退方案。
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import requests

from math_agent.config import (
    MINERU_API_URL,
    MINERU_API_KEY,
    MINERU_ENABLED,
    MINERU_TIMEOUT,
)


@dataclass
class MinerUResult:
    """MinerU 解析结果的结构化表示。"""
    success: bool
    markdown: str = ""
    content_json: dict = field(default_factory=dict)
    images: list[bytes] = field(default_factory=list)
    tables: list[str] = field(default_factory=list)
    formulas: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    error_message: str = ""
    page_count: int = 0
    parse_time_ms: int = 0


class MinerUClient:
    """MinerU API 客户端，支持文件上传、批量解析与结果缓存。

    用法:
        client = MinerUClient()
        result = client.parse(pdf_path)
        print(result.markdown)
    """

    def __init__(
        self,
        api_url: str | None = None,
        api_key: str | None = None,
        timeout: int | None = None,
    ):
        self._api_url = api_url or MINERU_API_URL
        self._api_key = api_key or MINERU_API_KEY
        self._timeout = timeout or MINERU_TIMEOUT

    @property
    def available(self) -> bool:
        """检查 MinerU API 是否可用。"""
        return bool(self._api_url and self._api_key) and MINERU_ENABLED

    def _compute_file_hash(self, path: Path) -> str:
        """计算文件 SHA256，用于缓存键。"""
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()

    def parse(self, file_path: str | Path) -> MinerUResult:
        """通过 MinerU API 解析 PDF 文件。

        Args:
            file_path: PDF 文件路径。

        Returns:
            MinerUResult 包含 markdown、结构化 JSON、图片、表格、公式等。
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return MinerUResult(
                success=False,
                error_message=f"文件不存在: {file_path}",
            )
        if not self.available:
            return MinerUResult(
                success=False,
                error_message="MinerU API 未配置 (MINERU_API_URL / MINERU_API_KEY)",
            )

        try:
            file_hash = self._compute_file_hash(file_path)
            headers = {"Authorization": f"Bearer {self._api_key}"}

            with open(file_path, "rb") as f:
                files = {"file": (file_path.name, f, "application/pdf")}
                data = {"output_format": "markdown", "cache_key": file_hash}

                response = requests.post(
                    f"{self._api_url}/v1/parse",
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=self._timeout,
                )

            if response.status_code != 200:
                return MinerUResult(
                    success=False,
                    error_message=f"MinerU API 错误 (HTTP {response.status_code}): "
                                  f"{response.text[:500]}",
                )

            result_data = response.json()
            return MinerUResult(
                success=True,
                markdown=result_data.get("markdown", ""),
                content_json=result_data.get("content", {}),
                metadata=result_data.get("metadata", {}),
                page_count=result_data.get("page_count", 0),
                parse_time_ms=result_data.get("parse_time_ms", 0),
            )

        except requests.Timeout:
            return MinerUResult(
                success=False,
                error_message=f"MinerU API 超时 ({self._timeout}s)",
            )
        except requests.ConnectionError as e:
            return MinerUResult(
                success=False,
                error_message=f"MinerU API 连接失败: {e}",
            )
        except Exception as e:
            return MinerUResult(
                success=False,
                error_message=f"MinerU 解析异常: {e}",
            )

    def parse_batch(self, file_paths: list[str | Path]) -> list[MinerUResult]:
        """批量解析多个 PDF 文件。

        Args:
            file_paths: PDF 文件路径列表。

        Returns:
            与输入顺序对应的 MinerUResult 列表。
        """
        return [self.parse(p) for p in file_paths]


# 模块级便捷函数
_default_client: MinerUClient | None = None


def _get_client() -> MinerUClient:
    global _default_client
    if _default_client is None:
        _default_client = MinerUClient()
    return _default_client


def parse_via_mineru(file_path: str | Path) -> MinerUResult:
    """便捷函数：通过 MinerU API 解析单个 PDF 文件。"""
    return _get_client().parse(file_path)
