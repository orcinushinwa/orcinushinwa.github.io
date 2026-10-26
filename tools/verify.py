#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迁移验收脚本：渲染新模板，和 tools/_orig/ 里的原始页面逐页比对。

- 空白差异、站内链接从绝对地址改成 /xxx，都视为等价
- 文字、图片、链接目标任何变化都会报出来
- “上一话/下一话”由模板生成，单独列出发生变化的页面

用法： python tools/verify.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from sitebuilder import ROOT, load_site, read_text  # noqa: E402

# 你手动修正过的地方：比对前把“原始文件”当成已修正，页面其余部分仍严格比对
KNOWN_FIXES = {
    "story-list/beast-story/001.html": [
        (
            "<title>比斯特 第001话 突然出现的怪物</title>",
            "<title>比斯特 第001话 突然出现的怪物 - 虎鲸神话故事馆</title>",
        )
    ],
}


def norm_url(m):
    value = m.group(2).replace("https://orcinushinwa.github.io", "")
    return f'{m.group(1)}="{value or "/"}"'


def norm(s):
    s = re.sub(r'(href|src)="([^"]*)"', norm_url, s)
    # 属性里多一个分号、标签之间多一个换行，都不影响显示
    s = re.sub(r'style="text-align: center;?"', 'style="text-align: center"', s)
    s = re.sub(r"\s*/>", ">", s)
    s = re.sub(r">\s+<", "><", s)
    return re.sub(r"\s+", " ", s).strip()


def strip_nav(text):
    return re.sub(
        r'<div class="footer-wikiwalk-nav"[^>]*>\n.*?\n</div>\n', "", text, flags=re.S
    )


def nav_of(text):
    m = re.search(r'<div class="footer-wikiwalk-nav"[^>]*>\n(.*?)\n</div>', text, re.S)
    return m.group(1).strip() if m else "(none)"


def first_diff(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            start = max(0, i - 60)
            return f"@{i} orig={a[start:i + 60]!r} new={b[start:i + 60]!r}"
    return f"length differs: {len(a)} vs {len(b)}"


def main():
    pages, render = load_site()
    bad, blank, nav_changed = [], [], []

    for rel in sorted(pages):
        original_path = os.path.join(ROOT, "tools", "_orig", rel)
        if not os.path.exists(original_path):
            bad.append((rel, "no original backup"))
            continue
        original = read_text(original_path)
        for old, new in KNOWN_FIXES.get(rel, []):
            original = original.replace(old, new)
        fm = re.match(r"^---\n.*?\n---\n", original, re.S)
        if fm:
            original = original[fm.end():]
        rendered = render(rel)

        if norm(strip_nav(original)) != norm(strip_nav(rendered)):
            bad.append((rel, first_diff(strip_nav(original), strip_nav(rendered))))
            continue
        if norm(nav_of(original)) != norm(nav_of(rendered)):
            nav_changed.append((rel, norm(nav_of(original)), norm(nav_of(rendered))))
        if original != rendered:
            blank.append(rel)

    print(f"pages checked  : {len(pages)}")
    print(f"byte identical : {len(pages) - len(blank) - len(bad)}")
    print(f"whitespace only: {len(blank)}")
    print(f"MISMATCH       : {len(bad)}")
    for rel, detail in bad[:10]:
        print(f"  - {rel}: {detail}")
    print()
    print(f"nav changed    : {len(nav_changed)}")
    for rel, before, after in nav_changed:
        print(f"  {rel}\n    old: {before}\n    new: {after}")

    if bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
