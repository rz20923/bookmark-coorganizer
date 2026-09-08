---
name: bookmark-coorganizer
description: >-
  Co-organizes Edge/Chrome Netscape bookmark HTML: inventory sites into clusters,
  discuss placement group-by-group with the user, then preview and organize with
  dead-link checks and dedupe. Use for 收藏夹/书签整理, favorites HTML cleanup,
  or dead bookmark links.
---

# 收藏夹共创整理 Skill（bookmark-coorganizer）

任意 Edge/Chrome `NETSCAPE-Bookmark-file-1` HTML → 与用户共创分类 → 三层结构 + 可选失效检测 + 去重。

## 硬性规则

1. **禁止一上来就正式整理**；确认前最多 `--preview`。
2. **禁止一次性甩完整分类表。** 顺序：
   **盘点 → 按共同点聚簇 → 一簇一簇商量 → 拼成大类 → 预览 → 整理。**
3. 每簇用**具体网站名**，点出共同点，问「单独成类还是并进已有类」。
4. **会话规则写到用户书签文件旁**（如 `我的收藏夹.scheme.json`），**不要改本 Skill 仓库里的 `categories.json`**，除非在修通用规则。

## 依赖

- Python 3.7+；失效检测需 `pip install -r requirements.txt`
- 本目录：`organizer.py`、`categories.json`（通用默认规则）、`self_check.py`

## 流程

### 1. 盘点

展示总条数、原顶层文件夹、站点簇（每簇 3～8 个代表站 + 共同点）。先不要给最终大类名。

### 2. 逐步讨论

维护「已定规则」表。每轮只推进若干簇。全部归置完再问是否做失效检测。

### 3. 落盘 → 预览

将已定规则写成**用户工作区**的 scheme 文件（可参考 `examples/scheme_template.json`）：

```bash
python <本skill>/organizer.py <收藏夹.html> \
  --categories <用户目录>/<名>.scheme.json \
  --mode scheme --preview
```

### 4. 正式整理

用户说「可以整理」后去掉 `--preview`；跳过检测加 `--no-check`。

产物写在输入 HTML 同目录：`*_整理后.html`、报告、失效/存疑/重复清单。

## 引擎模式

| 模式 | 用途 |
|---|---|
| `scheme` | 共创后的路径/域名规则（推荐默认路径） |
| `preserve` | 几乎只保留原文件夹 + 去重/检测 |
| `auto` | 使用仓库自带通用 `categories.json` 重分 |

## 注意

原文件不改；403/SSL/5xx 默认进存疑保留；收藏夹含隐私，勿提交公开仓库。
