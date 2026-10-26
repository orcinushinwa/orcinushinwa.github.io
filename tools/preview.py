#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地预览：把整站渲染到 _site_local/，然后直接双击 _site_local/index.html 就能看。

    python tools/preview.py            （或双击仓库根目录的 预览.cmd）

生成的页面用的是相对链接（所以 file:// 直接打开也能正确显示样式和跳转），
只影响预览，不影响 GitHub Pages 上的正式地址。
"""
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from sitebuilder import ROOT, load_site  # noqa: E402

OUT = os.path.join(ROOT, "_site_local")


def relativize(html, rel):
    """/story-list/ 这类站内绝对路径改成相对于当前页面的路径。"""
    prefix = "../" * rel.count("/")

    def repl(m):
        url = m.group(2)
        if not url.startswith("/") or url.startswith("//"):
            return m.group(0)
        target = url[1:] or "index.html"
        if target.endswith("/"):
            target += "index.html"
        return f'{m.group(1)}="{prefix}{target}"'

    return re.sub(r'(href|src)="([^"]*)"', repl, html)


def main():
    pages, render = load_site()
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)

    for rel in pages:
        html = relativize(render(rel), rel)
        target = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8", newline="\n") as f:
            f.write(html)

    for name in ("style.css", "logo.svg"):
        shutil.copyfile(os.path.join(ROOT, name), os.path.join(OUT, name))

    print(f"已生成 {len(pages)} 个页面到 _site_local/")
    print(f"用浏览器打开： {os.path.join(OUT, 'index.html')}")


if __name__ == "__main__":
    main()
