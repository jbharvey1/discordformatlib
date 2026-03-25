"""Render markdown as a styled HTML page and screenshot it via Playwright."""

import threading
import uuid
import tempfile
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from .payload import DiscordPayload
from .table import _tmp_path

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: 'Noto Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Segoe UI Symbol', 'Segoe UI Emoji', 'Arial Unicode MS', Helvetica, Arial, sans-serif;
    font-size: 15px;
    line-height: 1.6;
    color: #1a1a2e;
    background: #ffffff;
    padding: 32px 40px;
    max-width: 860px;
}
h1 { font-size: 1.9em; border-bottom: 2px solid #1a1a2e; padding-bottom: 6px; margin-bottom: 16px; margin-top: 24px; }
h2 { font-size: 1.45em; border-bottom: 1px solid #ccc; padding-bottom: 4px; margin-bottom: 12px; margin-top: 20px; }
h3 { font-size: 1.15em; margin-bottom: 8px; margin-top: 16px; }
h4, h5, h6 { margin-bottom: 6px; margin-top: 12px; }
p  { margin-bottom: 12px; }
ul, ol { margin-bottom: 12px; padding-left: 24px; }
li { margin-bottom: 4px; }
code {
    font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
    background: #f0f0f0;
    border: 1px solid #ddd;
    border-radius: 3px;
    padding: 1px 5px;
    font-size: 0.9em;
}
pre {
    background: #1e1e2e;
    color: #cdd6f4;
    border-radius: 6px;
    padding: 16px;
    overflow-x: auto;
    margin-bottom: 14px;
    font-size: 0.88em;
    line-height: 1.5;
}
pre code {
    background: none;
    border: none;
    padding: 0;
    color: inherit;
    font-size: inherit;
}
blockquote {
    border-left: 4px solid #1a1a2e;
    padding-left: 14px;
    color: #555;
    margin-bottom: 12px;
}
table { border-collapse: collapse; width: 100%; margin-bottom: 14px; }
th { background: #1a1a2e; color: #fff; padding: 8px 12px; text-align: left; }
td { padding: 7px 12px; border: 1px solid #ccc; }
tr:nth-child(even) td { background: #f4f4f4; }
hr { border: none; border-top: 1px solid #ccc; margin: 20px 0; }
a  { color: #2563eb; }
strong { font-weight: 700; }
em { font-style: italic; }
"""


# Unicode characters that headless Chromium may not render correctly
# are pre-converted to HTML entities before markdown parsing.
_CHAR_MAP = {
    "→": "&rarr;", "←": "&larr;", "↑": "&uarr;", "↓": "&darr;",
    "↔": "&harr;", "⇒": "&rArr;", "⇐": "&lArr;", "⇔": "&hArr;",
    "≥": "&ge;", "≤": "&le;", "≠": "&ne;", "≈": "&asymp;",
    "✓": "&#10003;", "✗": "&#10007;", "•": "&bull;", "…": "&hellip;",
    "—": "&mdash;", "–": "&ndash;",
}


def _sanitize(text: str) -> str:
    for char, entity in _CHAR_MAP.items():
        text = text.replace(char, entity)
    return text


def _md_to_html(md_text: str, title: str = "") -> str:
    import markdown as md_lib
    body = md_lib.markdown(
        _sanitize(md_text),
        extensions=["fenced_code", "tables", "nl2br", "sane_lists"],
    )
    heading = f"<h1>{title}</h1>" if title else ""
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head><body>{heading}{body}</body></html>"""


class _OneShot(BaseHTTPRequestHandler):
    html = ""

    def do_GET(self):
        data = self.html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *_):
        pass  # suppress request logs


def _serve_once(html: str, port: int) -> None:
    _OneShot.html = html
    server = HTTPServer(("127.0.0.1", port), _OneShot)
    server.handle_request()  # serve exactly one request then exit
    server.server_close()


def _find_free_port() -> int:
    import socket
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def render_markdown_image(md_text: str, title: str = "") -> str:
    """Convert markdown to a styled PNG via Playwright screenshot.

    Returns the path to the saved PNG file.
    """
    from playwright.sync_api import sync_playwright

    html  = _md_to_html(md_text, title=title)
    port  = _find_free_port()
    url   = f"http://127.0.0.1:{port}/"
    path  = _tmp_path()

    # Serve HTML in background thread — dies after one request
    t = threading.Thread(target=_serve_once, args=(html, port), daemon=True)
    t.start()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page    = browser.new_page(viewport={"width": 900, "height": 1200})
        page.goto(url, wait_until="networkidle")
        page.screenshot(path=path, full_page=True)
        browser.close()

    t.join(timeout=3)
    return path


def format_markdown_image(md_text: str, title: str = "") -> DiscordPayload:
    """Render markdown as a styled image. Returns DiscordPayload with file_path."""
    path = render_markdown_image(md_text, title=title)
    return DiscordPayload(file_path=path)
