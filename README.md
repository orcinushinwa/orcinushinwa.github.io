# 主页
[点击预览](https://orcinushinwa.github.io/)
---
## 计划
* 搬运《比斯特》系列并同步连载
* 重开《小椅子学校》连载？
* 开启《星之乙女Virgo》《海鸥是否吃薯片》等连载？

---

# 下面的东西全都是大肥鱼写的跟我没关系啊

## 这个站现在是怎么搭的

用的是 **Jekyll**（GitHub Pages 自带，不用装任何东西）。核心一句话：

> 页面 = 模板（`_layouts/`）+ 数据（每个页面开头的 `---` 那几行）+ 正文

站头、导航、面包屑、上一话/下一话、页脚，全站只写一次，放在 `_layouts/` 里。
所以**改一次模板，105 个页面会一起变**。

```
_config.yml          站点总配置（站名、作者、当前连载系列）
_data/series.yml     故事系列清单（比斯特、以后的新系列）
_layouts/
  default.html       外壳：<head>、站头、页脚 —— 想改页脚就改这里
  episode.html       章节页：页面标题、面包屑、上一话/下一话
  page.html          普通页：首页、关于、鸣谢、404
story-list/beast-story/*.html   每个故事页 = 开头几行 + 正文
style.css            全站样式
tools/               一次性迁移脚本和验收脚本（不发布）
```

### 新写一话

1. 复制上一话的文件（比如 `087.html` 复制成 `088.html`），打开后只会看到十几行字：
   ```
   ---
   layout: "episode"
   series: "beast"
   kind: "main"
   order: 88                 ← 第几话，排序和上一话/下一话都靠它
   label: "第088话"           ← 导航里显示的字
   title: "比斯特 第088话 标题"  ← 页面大标题和浏览器标签
   ---
   <p>正文第一段……</p>
   ```
2. 改 `order`、`label`、`title`，把正文换成新的。
3. 提交推送。目录、面包屑、上一话/下一话会自动更新（上一话的"下一话"也会自动接上）。

### 新写一篇番外

同样的文件，但开头多一个 `extra_no`（番外列表里的顺序，从 0 开始），把 `kind` 改成 `"extra"`，
并且用 `after` 说明"插在第几话后面"：

```
kind: "extra"
extra_no: 16
after: 87            ← 放在第087话和第088话之间
```

导航里它的"上一话/下一话"会自动指向 `after` 和 `after + 1` 这两话。

### 想改全站的东西

| 想改什么 | 改哪个文件 |
| --- | --- |
| 站名、作者、页脚、"当前连载系列" | `_config.yml` 或 `_layouts/default.html` |
| 顶部导航（首页／故事目录／关于作者） | `_layouts/default.html` |
| 面包屑、章节页结构 | `_layouts/episode.html` |
| 全站配色、字号 | `style.css` |
| 单个页面的特殊样式 | 那个页面开头加 `style: |` 再写 CSS |

### 开一个新系列

1. `_data/series.yml` 里加一段：
   ```yaml
   chairs:
     title: 小椅子学校
     url: /story-list/chairs/
   ```
2. 新页面里用 `series: "chairs"`，面包屑和导航就自动跟着走了。

### 本地检查（可选）

推送后 GitHub Pages 会自动构建，构建失败时旧页面会继续留在线上，不会白屏。
想先在本地看看效果，需要装 Python 的 `pyyaml` 和 `python-liquid`，然后：

```
python tools/preview.py
python -m http.server 8000 --directory _site_local
```

打开 http://localhost:8000/ 就能看到整站（不用装 Ruby）。

想核对"重构后有没有丢内容"：

```
python tools/verify.py
```

它会渲染整站并和 `tools/_orig/`（重构前的原始页面）逐页比对，确认没有内容丢失。

> `tools/_orig/`、`tools/_pylibs/`、`_site_local/` 只在本机留底，已写进 `.gitignore`，不会上传。
> 确认重构没问题后，`tools/_orig/` 可以整个删掉。
