#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地渲染器（与 verify.py / preview.py 共用）。

它用真正的 Liquid 引擎按 _layouts/_data/_config.yml 渲染整站，
等价于 Jekyll 的“页面 = 布局 + 数据 + 正文”流程，只是不依赖 Ruby。

依赖：pyyaml、python-liquid。优先用系统里已装的，没装时退回 tools/_pylibs/。
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    import yaml  # noqa: F401
    from liquid import Environment  # noqa: F401
except ImportError:
    _libs = os.path.join(ROOT, "tools", "_pylibs")
    if os.path.isdir(_libs) and _libs not in sys.path:
        sys.path.insert(0, _libs)

import yaml  # noqa: E402
from liquid import Environment  # noqa: E402

FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
SKIP_DIRS = {".git", "tools", "_layouts", "_data", "_includes", "_site", "_site_local"}


def read_text(path):
    full = path if os.path.isabs(path) else os.path.join(ROOT, path)
    with open(full, encoding="utf-8", newline="") as f:
        return f.read().replace("\r\n", "\n")


def url_for(rel):
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel


def relative_url(value, *args):
    p = str(value)
    if p.startswith("http"):
        return p
    return "/" + p.lstrip("/")


def collect_pages():
    pages = {}
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if not name.endswith(".html"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, name), ROOT).replace(os.sep, "/")
            text = read_text(rel)
            m = FM_RE.match(text)
            if not m:
                raise SystemExit(f"missing front matter: {rel}")
            page = dict(yaml.safe_load(m.group(1)) or {})
            page["url"] = url_for(rel)
            page["path"] = rel
            pages[rel] = (page, text[m.end():])
    return pages


def load_site():
    """返回 (pages, render)。render(rel) 得到该页完整 HTML。"""
    pages = collect_pages()
    cfg = yaml.safe_load(read_text("_config.yml")) or {}
    series = yaml.safe_load(read_text("_data/series.yml")) or {}

    env = Environment()
    env.add_filter("relative_url", relative_url)
    site = {
        "title": cfg.get("title"),
        "author": cfg.get("author"),
        "current_series": cfg.get("current_series"),
        "url": cfg.get("url"),
        "baseurl": cfg.get("baseurl", ""),
        "data": {"series": series},
        "pages": [p for p, _ in pages.values()],
    }

    layouts = {}
    layout_dir = os.path.join(ROOT, "_layouts")
    for name in os.listdir(layout_dir):
        if name.endswith(".html"):
            text = read_text(os.path.join("_layouts", name))
            m = FM_RE.match(text)
            if m:
                layouts[name[:-5]] = (yaml.safe_load(m.group(1)) or {}, text[m.end():])
            else:
                layouts[name[:-5]] = ({}, text)

    def render(rel):
        page, body = pages[rel]
        ctx = {"site": site, "page": page}
        out = env.from_string(body).render(**ctx)
        name = page.get("layout")
        while name:
            data, lbody = layouts[name]
            out = env.from_string(lbody).render(**{**ctx, "content": out})
            name = data.get("layout")
        return out

    return pages, render
