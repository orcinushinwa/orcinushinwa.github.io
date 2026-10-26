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
所以**改一次模板，全站上百个页面会一起变**。

```
_config.yml          站点总配置（站名、作者、当前连载系列）
_data/series.yml     故事系列清单（比斯特、以后的新系列）
_layouts/
  default.html       外壳：<head>、站头、页脚 —— 想改页脚就改这里
  episode.html       章节页：页面标题、面包屑、上一话/下一话
  page.html          普通页：首页、关于、鸣谢、404
story-list/beast-story/*.html   每个故事页 = 开头几行 + 正文
style.css            全站样式
tools/               本地预览用的小脚本（不发布）
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

### 想让导航"跳号"或指向还没写的页面

默认规则是自动算的，但可以手动覆盖。四个字段，写哪个覆盖哪个：

```yaml
prev_label: "番外第c话"                              # 左侧显示的字
prev_url: "/story-list/beast-story/water-hyacinth.html"
next_label: "第070话"
next_url: "/story-list/beast-story/070.html"
```

用途举例：

- **番外刻意跳号**（月季接在 065 和 070 之间、风信子接在番外c之后、洋紫荆接在番外004之后）——就是靠这几个字段固定的
- **下一话还没写**：写 `next_label: "第088话"` + `next_url: ".../088.html"`，读者点进去会落到 404 催更页，这是刻意留的钩子

注意：**手动覆盖优先于自动计算**。所以跳号是一旦写了就一直生效；哪天不想跳了，把那两行删掉，导航会自动回到按 `order` / `after` 算出来的邻居。

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

### 下一话还没写的时候

导航里可以留一个**故意指向不存在页面的链接**，读者点进去会看到 404 催更页。用 `next_label` + `next_url` 两个字段：

```yaml
next_label: "第088话"
next_url: "/story-list/beast-story/088.html"
```

等 `088.html` 真的建好了，链接会自动变成真链接，这两行留着也不碍事（真下一话优先）。

### 本地检查（可选）

推送后 GitHub Pages 会自动构建，构建失败时旧页面会继续留在线上，不会白屏。
想先在本地看看效果，需要装 Python 的 `pyyaml` 和 `python-liquid`，然后双击仓库根目录的 `预览.cmd`（或运行）：

```
python tools/preview.py
```

它会把整站渲染到 `_site_local/`，然后直接用浏览器打开 `_site_local/index.html` 就行——页面里的链接都改成了相对路径，不需要起服务器。

> `_site_local/` 只是本机预览，已写进 `.gitignore`，不会上传。
