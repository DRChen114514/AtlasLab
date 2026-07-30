#!/usr/bin/env python3
"""AtlasLab 启动器 —— 原生桌面应用窗口。

内置 PDF → Markdown 自动转换。上传 PDF 即转为 .md 文本，
供赛题理解和建模流水线消费。

用法:
  python3 launch_beacon_v3.py
"""
from __future__ import annotations

import argparse
import cgi
import http.server
import io
import json
import os
import re
import socket
import sys
import tempfile
import threading
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
DEFAULT_PORT = 18080


def find_free_port(start: int = 18080) -> int:
    for port in range(start, start + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return start


def extract_pdf_text(file_bytes: bytes, filename: str) -> dict:
    """从 PDF 字节流提取文本，转为 Markdown。

    优先 PyMuPDF (fitz)，回退 pypdf。
    返回 {"markdown": str, "page_count": int, "filename": str}
    """
    text_parts = []
    page_count = 0

    # 尝试 PyMuPDF
    try:
        import fitz
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        page_count = doc.page_count
        for page in doc:
            t = page.get_text()
            if t.strip():
                text_parts.append(t.strip())
        doc.close()
        if text_parts:
            return _build_result(text_parts, page_count, filename)
    except (ImportError, Exception):
        pass

    # 回退 pypdf
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        page_count = len(reader.pages)
        for page in reader.pages:
            t = page.extract_text()
            if t and t.strip():
                text_parts.append(t.strip())
        if text_parts:
            return _build_result(text_parts, page_count, filename)
    except Exception:
        pass

    # 都失败了
    return {"markdown": "", "page_count": 0, "filename": filename,
            "error": "无法提取 PDF 文本（需要 PyMuPDF 或 pypdf）"}


def _build_result(text_parts: list[str], page_count: int, filename: str) -> dict:
    """将提取的文本构建为 Markdown。"""
    raw = "\n\n".join(text_parts)
    # 清理：移除空字符、替换常见乱码
    raw = raw.replace("\x00", "").replace("\ufffd", "")
    # 尝试识别标题（以大写字母开头的短行 → ###）
    md_lines = []
    for line in raw.split("\n"):
        stripped = line.strip()
        if not stripped:
            md_lines.append("")
            continue
        # 检测可能的标题
        if (len(stripped) < 80 and len(stripped) > 3
                and not stripped.endswith(".")
                and (stripped[0].isupper() or '\u4e00' <= stripped[0] <= '\u9fff')):
            # 如果上一行是空行，可能是标题
            md_lines.append(f"### {stripped}")
        else:
            md_lines.append(stripped)

    markdown = "\n\n".join(md_lines)
    return {
        "markdown": markdown,
        "text": raw,
        "page_count": page_count,
        "filename": filename,
    }


class AtlasLabHandler(http.server.SimpleHTTPRequestHandler):
    """静态文件 + PDF 转换 API。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)

    def do_POST(self):
        if self.path == "/api/convert-pdf":
            self._handle_convert_pdf()
            return
        self.send_error(404)

    def _handle_convert_pdf(self):
        """接收 PDF 文件，返回 Markdown 文本。"""
        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            self._json_error(400, "需要 multipart/form-data")
            return

        # 解析 multipart
        boundary = content_type.split("boundary=")[-1]
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))

        # 简单 multipart 解析
        parts = body.split(f"--{boundary}".encode())
        file_bytes = None
        filename = "upload.pdf"
        for part in parts:
            if b"Content-Disposition" not in part:
                continue
            header_end = part.find(b"\r\n\r\n")
            if header_end < 0:
                continue
            headers = part[:header_end].decode("utf-8", errors="ignore")
            content = part[header_end + 4:]
            if content.endswith(b"\r\n"):
                content = content[:-2]

            if 'name="file"' in headers:
                file_bytes = content
                fn_match = re.search(r'filename="([^"]*)"', headers)
                if fn_match:
                    filename = fn_match.group(1)
                break

        if not file_bytes:
            self._json_error(400, "未收到文件")
            return

        result = extract_pdf_text(file_bytes, filename)
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))

    def _json_error(self, status: int, message: str):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}, ensure_ascii=False).encode("utf-8"))

    def log_message(self, fmt, *args):
        if "convert-pdf" in str(args):
            print(f"  [convert] PDF → MD", flush=True)


def start_http_server(port: int) -> str:
    """在后台线程启动 HTTP 服务器。"""
    server = http.server.HTTPServer(("127.0.0.1", port), AtlasLabHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return f"http://127.0.0.1:{port}/doc-intel.html"


def main():
    parser = argparse.ArgumentParser(description="AtlasLab 桌面应用")
    parser.add_argument("--port", type=int, default=None, help="HTTP 端口")
    args = parser.parse_args()

    port = args.port or find_free_port(DEFAULT_PORT)
    url = start_http_server(port)

    print(f"AtlasLab · http://127.0.0.1:{port}")
    print(f"文档智能 → {url}")
    print("PDF 自动转 MD 已启用 (/api/convert-pdf)")

    try:
        from PyQt6.QtWidgets import QApplication, QMainWindow
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        from PyQt6.QtCore import QUrl

        app = QApplication(sys.argv)
        app.setApplicationName("AtlasLab")

        window = QMainWindow()
        window.setWindowTitle("AtlasLab · 文档智能 & 赛题配置")
        window.resize(1200, 800)
        window.setMinimumSize(900, 600)

        web = QWebEngineView()
        web.setUrl(QUrl(url))
        window.setCentralWidget(web)

        screen = app.primaryScreen().geometry()
        window.move((screen.width() - 1200) // 2, (screen.height() - 800) // 2)
        window.show()

        print("PyQt6 原生窗口已打开")
        sys.exit(app.exec())

    except ImportError:
        import webbrowser
        webbrowser.open(url)
        print(f"浏览器已打开: {url}")
        print("按 Ctrl+C 退出")
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
