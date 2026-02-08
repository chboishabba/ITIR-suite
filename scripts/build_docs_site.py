#!/usr/bin/env python
"""
Build a lightweight HTML index for browsing all Markdown docs in this repo.

Notes:
- No external deps (python-markdown not assumed installed).
- Intended for local browsing via a simple HTTP server.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "docs" / "_site"


EXCLUDE_DIR_NAMES = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "runs",
    "dist",
    "build",
    ".mypy_cache",
}


@dataclass(frozen=True)
class DocEntry:
    path: str
    title: str
    size_bytes: int


def _iter_markdown_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.md"):
        parts = set(path.parts)
        if any(part in EXCLUDE_DIR_NAMES for part in parts):
            continue
        # Avoid generated site consuming itself.
        if "docs" in path.parts and "_site" in path.parts:
            continue
        yield path


def _first_heading(md_text: str) -> Optional[str]:
    for line in md_text.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip()
    return None


def build_manifest() -> List[DocEntry]:
    entries: List[DocEntry] = []
    for path in _iter_markdown_files(REPO_ROOT):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        title = _first_heading(text) or path.as_posix()
        rel = path.relative_to(REPO_ROOT).as_posix()
        entries.append(DocEntry(path=rel, title=title, size_bytes=path.stat().st_size))
    entries.sort(key=lambda e: e.path.lower())
    return entries


def write_site(entries: List[DocEntry]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    (OUT_DIR / "manifest.json").write_text(
        json.dumps([asdict(e) for e in entries], indent=2, sort_keys=True),
        encoding="utf-8",
    )

    (OUT_DIR / "styles.css").write_text(
        (
            "html,body{height:100%;margin:0;font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell,Noto Sans,sans-serif;}\n"
            "body{display:flex;background:#0b0d10;color:#e7eef7;}\n"
            ".sidebar{width:360px;max-width:40vw;min-width:280px;border-right:1px solid #1f2a37;display:flex;flex-direction:column;}\n"
            ".top{padding:14px 14px 10px 14px;border-bottom:1px solid #1f2a37;background:#0f141b;}\n"
            ".top h1{margin:0 0 8px 0;font-size:16px;letter-spacing:.2px;}\n"
            ".top .hint{font-size:12px;color:#9fb1c5;line-height:1.35;}\n"
            ".search{display:flex;gap:8px;margin-top:10px;}\n"
            "input[type=text]{flex:1;padding:10px 10px;border:1px solid #263244;border-radius:8px;background:#0b0d10;color:#e7eef7;}\n"
            "button{padding:10px 10px;border:1px solid #263244;border-radius:8px;background:#121a24;color:#e7eef7;cursor:pointer;}\n"
            "button:hover{background:#162132;}\n"
            ".list{overflow:auto;flex:1;}\n"
            ".item{padding:10px 14px;border-bottom:1px solid #121a24;cursor:pointer;}\n"
            ".item:hover{background:#0f141b;}\n"
            ".item .title{font-size:13px;margin:0 0 4px 0;}\n"
            ".item .path{font-size:11px;color:#9fb1c5;font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;}\n"
            ".main{flex:1;display:flex;flex-direction:column;min-width:0;}\n"
            ".mainTop{padding:14px;border-bottom:1px solid #1f2a37;background:#0f141b;display:flex;justify-content:space-between;align-items:center;gap:10px;}\n"
            ".mainTop .docTitle{font-size:14px;color:#e7eef7;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}\n"
            ".mainTop .docPath{font-size:11px;color:#9fb1c5;font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}\n"
            ".content{padding:18px;overflow:auto;}\n"
            ".content pre{background:#0b0d10;border:1px solid #263244;border-radius:10px;padding:14px;overflow:auto;}\n"
            ".content code{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;}\n"
            ".content h1,.content h2,.content h3{margin-top:22px;}\n"
            ".content a{color:#7dd3fc;}\n"
            ".pill{font-size:11px;color:#9fb1c5;border:1px solid #263244;border-radius:999px;padding:6px 10px;}\n"
            "@media (max-width: 900px){.sidebar{width:46vw;}.top h1{font-size:14px;}}\n"
        ),
        encoding="utf-8",
    )

    (OUT_DIR / "app.js").write_text(
        (
            "const $ = (sel) => document.querySelector(sel);\n"
            "const sidebar = $('#list');\n"
            "const search = $('#search');\n"
            "const clearBtn = $('#clear');\n"
            "const docTitle = $('#docTitle');\n"
            "const docPath = $('#docPath');\n"
            "const content = $('#content');\n"
            "const countPill = $('#countPill');\n"
            "\n"
            "function escapeHtml(s){\n"
            "  return s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');\n"
            "}\n"
            "\n"
            "// Minimal markdown renderer: headings + fenced code + inline code + links + lists.\n"
            "function renderMarkdown(md){\n"
            "  let out = '';\n"
            "  const lines = md.split(/\\r?\\n/);\n"
            "  let inCode = false;\n"
            "  let codeLang = '';\n"
            "  let listMode = null; // 'ul'|'ol'\n"
            "  const flushList = () => { if(listMode){ out += `</${listMode}>`; listMode = null; } };\n"
            "  for (let i=0;i<lines.length;i++){\n"
            "    const line = lines[i];\n"
            "    const fence = line.match(/^```\\s*([a-zA-Z0-9_-]+)?\\s*$/);\n"
            "    if (fence){\n"
            "      if (!inCode){ flushList(); inCode = true; codeLang = fence[1] || ''; out += `<pre><code class=\\\"lang-${escapeHtml(codeLang)}\\\">`; }\n"
            "      else { inCode = false; out += `</code></pre>`; }\n"
            "      continue;\n"
            "    }\n"
            "    if (inCode){ out += escapeHtml(line) + '\\n'; continue; }\n"
            "\n"
            "    const h = line.match(/^(#{1,3})\\s+(.*)$/);\n"
            "    if (h){\n"
            "      flushList();\n"
            "      const level = h[1].length;\n"
            "      out += `<h${level}>${inlineMd(h[2])}</h${level}>`;\n"
            "      continue;\n"
            "    }\n"
            "\n"
            "    const ol = line.match(/^\\s*\\d+\\.\\s+(.*)$/);\n"
            "    const ul = line.match(/^\\s*[-*]\\s+(.*)$/);\n"
            "    if (ol){\n"
            "      if (listMode !== 'ol'){ flushList(); listMode = 'ol'; out += '<ol>'; }\n"
            "      out += `<li>${inlineMd(ol[1])}</li>`;\n"
            "      continue;\n"
            "    }\n"
            "    if (ul){\n"
            "      if (listMode !== 'ul'){ flushList(); listMode = 'ul'; out += '<ul>'; }\n"
            "      out += `<li>${inlineMd(ul[1])}</li>`;\n"
            "      continue;\n"
            "    }\n"
            "\n"
            "    if (!line.trim()){ flushList(); out += '<div style=\\\"height:10px\\\"></div>'; continue; }\n"
            "    flushList();\n"
            "    out += `<p>${inlineMd(line)}</p>`;\n"
            "  }\n"
            "  flushList();\n"
            "  return out;\n"
            "}\n"
            "\n"
            "function inlineMd(text){\n"
            "  let s = escapeHtml(text);\n"
            "  // inline code\n"
            "  s = s.replace(/`([^`]+)`/g, '<code>$1</code>');\n"
            "  // links\n"
            "  s = s.replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g, '<a href=\"$2\" target=\"_blank\" rel=\"noreferrer\">$1</a>');\n"
            "  // bold\n"
            "  s = s.replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>');\n"
            "  return s;\n"
            "}\n"
            "\n"
            "function repoBase(){ return new URL('../..', window.location.href); }\n"
            "\n"
            "function setHash(path){\n"
            "  const u = new URL(window.location.href);\n"
            "  u.hash = '#' + encodeURIComponent(path);\n"
            "  history.replaceState(null, '', u);\n"
            "}\n"
            "\n"
            "async function loadDoc(entry){\n"
            "  docTitle.textContent = entry.title;\n"
            "  docPath.textContent = entry.path;\n"
            "  const url = new URL(entry.path, repoBase());\n"
            "  setHash(entry.path);\n"
            "  const resp = await fetch(url);\n"
            "  const md = await resp.text();\n"
            "  content.innerHTML = renderMarkdown(md);\n"
            "}\n"
            "\n"
            "function renderList(entries){\n"
            "  sidebar.innerHTML = '';\n"
            "  for (const e of entries){\n"
            "    const div = document.createElement('div');\n"
            "    div.className = 'item';\n"
            "    div.innerHTML = `<div class=\\\"title\\\">${escapeHtml(e.title)}</div><div class=\\\"path\\\">${escapeHtml(e.path)}</div>`;\n"
            "    div.addEventListener('click', () => loadDoc(e));\n"
            "    sidebar.appendChild(div);\n"
            "  }\n"
            "  countPill.textContent = `${entries.length} docs`;\n"
            "}\n"
            "\n"
            "async function main(){\n"
            "  const manifestUrl = new URL('./manifest.json', window.location.href);\n"
            "  const entries = await (await fetch(manifestUrl)).json();\n"
            "  let filtered = entries;\n"
            "  renderList(filtered);\n"
            "\n"
            "  const applyFilter = () => {\n"
            "    const q = (search.value || '').toLowerCase().trim();\n"
            "    if (!q){ filtered = entries; }\n"
            "    else {\n"
            "      filtered = entries.filter(e => e.path.toLowerCase().includes(q) || e.title.toLowerCase().includes(q));\n"
            "    }\n"
            "    renderList(filtered);\n"
            "  };\n"
            "  search.addEventListener('input', applyFilter);\n"
            "  clearBtn.addEventListener('click', () => { search.value=''; applyFilter(); });\n"
            "\n"
            "  const initial = decodeURIComponent((window.location.hash || '').replace(/^#/, ''));\n"
            "  if (initial){\n"
            "    const hit = entries.find(e => e.path === initial);\n"
            "    if (hit) await loadDoc(hit);\n"
            "  }\n"
            "}\n"
            "\n"
            "main().catch(err => {\n"
            "  content.innerHTML = `<pre>Failed to load docs.\\n\\nIf you opened this via file://, fetch() may be blocked.\\nRun: python -m http.server\\nThen open: /docs/_site/index.html\\n\\nError:\\n${escapeHtml(String(err))}</pre>`;\n"
            "});\n"
        ),
        encoding="utf-8",
    )

    (OUT_DIR / "index.html").write_text(
        (
            "<!doctype html>\n"
            "<html lang=\"en\">\n"
            "<head>\n"
            "  <meta charset=\"utf-8\" />\n"
            "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />\n"
            "  <title>ITIR Suite Docs</title>\n"
            "  <link rel=\"stylesheet\" href=\"./styles.css\" />\n"
            "</head>\n"
            "<body>\n"
            "  <div class=\"sidebar\">\n"
            "    <div class=\"top\">\n"
            "      <h1>ITIR Suite Docs</h1>\n"
            "      <div class=\"hint\">Browse all <code>*.md</code> in this repo. Best used via a local HTTP server: <code>python -m http.server</code> (repo root), then open <code>/docs/_site/index.html</code>.</div>\n"
            "      <div class=\"search\">\n"
            "        <input id=\"search\" type=\"text\" placeholder=\"Filter by path or title\" />\n"
            "        <button id=\"clear\" title=\"Clear filter\">Clear</button>\n"
            "      </div>\n"
            "      <div style=\"margin-top:10px;display:flex;gap:10px;align-items:center;\">\n"
            "        <span id=\"countPill\" class=\"pill\">…</span>\n"
            "      </div>\n"
            "    </div>\n"
            "    <div id=\"list\" class=\"list\"></div>\n"
            "  </div>\n"
            "  <div class=\"main\">\n"
            "    <div class=\"mainTop\">\n"
            "      <div style=\"min-width:0;\">\n"
            "        <div id=\"docTitle\" class=\"docTitle\">Select a document…</div>\n"
            "        <div id=\"docPath\" class=\"docPath\"></div>\n"
            "      </div>\n"
            "      <div class=\"pill\">meta-only</div>\n"
            "    </div>\n"
            "    <div id=\"content\" class=\"content\"></div>\n"
            "  </div>\n"
            "  <script src=\"./app.js\"></script>\n"
            "</body>\n"
            "</html>\n"
        ),
        encoding="utf-8",
    )


def main() -> int:
    entries = build_manifest()
    write_site(entries)
    print(f"Wrote {len(entries)} docs -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
