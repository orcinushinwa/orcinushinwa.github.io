#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一次性迁移脚本：把 109 个手写 HTML 页面改成 Jekyll 的“layout + front matter + 正文”。

- 每页的公共外壳（站头、导航、面包屑、页脚）删除，改由 _layouts/ 生成
- 每个故事页只剩 front matter（元数据）+ 正文，正文逐字节保留
- 原始文件已备份在 tools/_orig/

用法： python tools/migrate.py
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORY_DIR = "story-list/beast-story"
SERIES_SLUG = "beast"


def read(path):
    """总是从 tools/_orig 里的原始备份读取，重跑也安全。"""
    source = os.path.join(ROOT, "tools", "_orig", path)
    if not os.path.exists(source):
        source = os.path.join(ROOT, path)
    with open(source, encoding="utf-8", newline="") as f:
        return f.read().replace("\r\n", "\n")


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(text)


def q(value):
    """输出一个合法的 YAML 双引号字符串（保留首尾空格）。"""
    return json.dumps(value, ensure_ascii=False)


def front_matter(items):
    lines = ["---"]
    for key, value in items:
        if isinstance(value, str) and "\n" in value:
            lines.append(f"{key}: |")
            for line in value.split("\n"):
                lines.append("  " + line if line else "")
        elif isinstance(value, bool):
            lines.append(f"{key}: {'true' if value else 'false'}")
        elif isinstance(value, int):
            lines.append(f"{key}: {value}")
        else:
            lines.append(f"{key}: {q(value)}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def grab(pattern, text, flags=re.S):
    m = re.search(pattern, text, flags)
    if not m:
        raise SystemExit(f"pattern not found: {pattern[:60]}")
    return m


def page_title_of(text):
    return grab(r'<div id="page-title"[^>]*>\n(.*?)\n</div>', text).group(1)


def stem(url):
    """把 .../017.html 变成 017。"""
    return os.path.splitext(url.rstrip("/").split("/")[-1])[0]


def style_of(text):
    m = re.search(r"<style>\n(.*?)\n</style>", text, re.S)
    return m.group(1).rstrip("\n") if m else None


def trailing_script_of(text):
    """捕获写在 </body> 之前、页面容器之外的脚本（目前只有 iris.html）。"""
    m = re.search(r"<script>\n(.*?)\n</script>\n</body>", text, re.S)
    return m.group(1).rstrip("\n") if m else None


# ---------------------------------------------------------------- story pages
def parse_story(path, text, existing):
    title = page_title_of(text)
    nav = grab(r'<div class="footer-wikiwalk-nav"[^>]*>\n(.*?)\n</div>', text).group(1)
    first_line, _, rest = nav.partition("<br />")
    parts = first_line.split(" | ")
    if len(parts) != 3:
        raise SystemExit(f"unexpected nav in {path}: {nav!r}")
    prev_part, label, next_part = parts
    prev_link = re.search(r'<a href="([^"]*)">([^<]*)</a>', prev_part)
    next_link = re.search(r'<a href="([^"]*)">([^<]*)</a>', next_part)
    prev_name = stem(prev_link.group(1)) if prev_link else ""
    next_name = stem(next_link.group(1)) if next_link else ""
    next_label = ""
    if next_name and next_name not in existing:
        next_label = next_link.group(2).strip()
        next_name = ""
    body = text[
        grab(r'<div id="breadcrumbs">\n.*?\n</div>\n', text).end():
        text.index('<div class="footer-wikiwalk-nav"')
    ]
    nav_extra = rest.strip().replace("https://orcinushinwa.github.io", "")
    if nav_extra.endswith("</p>"):
        nav_extra = nav_extra[: -len("</p>")].rstrip()
    return dict(
        title=title,
        label=label.strip(),
        prev_prev=prev_name,
        next_next=next_name,
        next_label=next_label,
        nav_extra=nav_extra,
        script=trailing_script_of(text),
        body=body,
    )


def main():
    story_names = sorted(
        os.path.splitext(n)[0]
        for n in os.listdir(os.path.join(ROOT, STORY_DIR))
        if n.endswith(".html") and n != "index.html"
    )
    # 番外列表顺序＝现在目录页里的顺序
    index_text = read(f"{STORY_DIR}/index.html")
    extra_order = [
        m.group(1)
        for m in re.finditer(r'<li><a href="[^"]*?/([^"/]+)\.html">', index_text)
    ]
    extra_order = [n for n in extra_order if n in story_names and not n.isdigit()]

    meta = {}
    existing = set(story_names)
    for name in story_names:
        rel = f"{STORY_DIR}/{name}.html"
        meta[name] = parse_story(rel, read(rel), existing)

    extras = [n for n in extra_order]
    for name in story_names:
        if not name.isdigit() and name not in extras:
            raise SystemExit(f"extra page not listed on index: {name}")

    report = []
    for name in story_names:
        rel = f"{STORY_DIR}/{name}.html"
        m = meta[name]
        if name.isdigit():
            kind, order = "main", int(name)
            items = [
                ("layout", "episode"),
                ("series", SERIES_SLUG),
                ("kind", kind),
                ("order", order),
                ("label", m["label"]),
                ("title", m["title"]),
            ]
            if m["next_label"]:
                items.append(("next_label", m["next_label"]))
        else:
            prev_name = m["prev_prev"]
            if prev_name.isdigit():
                after = int(prev_name)
            elif m["next_next"].isdigit():
                after = int(m["next_next"]) - 1
            else:
                raise SystemExit(f"cannot place extra {name}")
            items = [
                ("layout", "episode"),
                ("series", SERIES_SLUG),
                ("kind", "extra"),
                ("extra_no", extras.index(name)),
                ("after", after),
                ("label", m["label"]),
                ("title", m["title"]),
            ]
            if name == "iris":
                # 面包屑末尾故意只写“鸢尾”，<title> 也不带“：夜蝠，银狼”
                items.append(("short_title", "比斯特 席特雷恩外传第一话 鸢尾"))
                items.append(("seo", "比斯特 席特雷恩外传第一话 鸢尾 - 虎鲸神话故事馆"))
        if m["nav_extra"]:  # cosmos / cosmos-bipinnatus 的 A-side / B-side 附加行
            items.append(("nav_extra", m["nav_extra"]))
        if m["script"]:
            items.append(("script", m["script"]))
        write(rel, front_matter(items) + m["body"])
        report.append((rel, "episode", ", ".join(k for k, _ in items)))

    # ------------------------------------------------------------ other pages
    simple = {
        "index.html": [("title_center", True), ("seo", "虎鲸神话故事馆")],
        "story-list/index.html": [],
        "about.html": [("seo", "关于作者 - 虎鲸神话故事馆")],
        "thanks.html": [("title_center", True)],
        "404.html": [
            ("title_center", True),
            ("content_center", True),
            ("permalink", "/404.html"),
            ("seo", "404 - 虎鲸神话故事馆"),
        ],
    }
    for rel, extra_items in simple.items():
        text = read(rel)
        body_start = text.index("<div id=\"page-content\"")
        body_start = text.index(">", body_start) + 1
        if text[body_start] == "\n":
            body_start += 1
        segment = text[body_start:text.index('<div id="page-options-area-bottom">')]
        body = segment[: segment.rindex("</div>")]
        items = [("layout", "page"), ("title", page_title_of(text))]
        items.extend(extra_items)
        style = style_of(text)
        if style:
            items.append(("style", style))
        script = trailing_script_of(text)
        if script:
            items.append(("script", script))
        write(rel, front_matter(items) + body)
        report.append((rel, "page", ", ".join(k for k, _ in items)))

    # -------------------------------------------------------- series index page
    text = read(f"{STORY_DIR}/index.html")
    body_start = text.index("<div id=\"page-content\"") 
    body_start = text.index(">", body_start) + 1
    if text[body_start] == "\n":
        body_start += 1
    segment = text[body_start:text.index('<div id="page-options-area-bottom">')]
    body = segment[: segment.rindex("</div>")]
    head_part = body.split("<h1>主系列故事列表</h1>")[0]
    new_body = (
        "{% assign main = site.pages | where: \"series\", \"beast\" | where: \"kind\", \"main\" | sort: \"order\" %}\n"
        '{% assign extras = site.pages | where: "series", "beast" | where: "kind", "extra" | sort: "extra_no" %}\n'
        + head_part
        + "<h1>主系列故事列表</h1>\n"
        "<div class=\"list-pages-box\">\n<ul>\n"
        "{% for m in main %}<li><a href=\"{{ m.url }}\">{{ m.short_title | default: m.title }}</a></li>\n{% endfor %}"
        "</ul>\n</div>\n"
        "<h1>番外故事列表</h1>\n"
        "<div class=\"list-pages-box\">\n<ul>\n"
        "{% for e in extras %}<li><a href=\"{{ e.url }}\">{{ e.short_title | default: e.title }}</a></li>\n{% endfor %}"
        "</ul>\n</div>\n"
        "</div>\n"
    )
    write(
        f"{STORY_DIR}/index.html",
        front_matter([("layout", "page"), ("title", page_title_of(text))]) + new_body,
    )
    report.append((f"{STORY_DIR}/index.html", "page", "title, generated lists"))

    print(f"converted {len(report)} pages")
    for rel, layout, keys in report:
        print(f"  {layout:8} {rel:45} {keys}")


if __name__ == "__main__":
    main()
