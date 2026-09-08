# bookmark-coorganizer · 收藏夹共创整理

面向 Edge / Chrome 导出的 Netscape 收藏夹 HTML 的整理工具，并可作为 **Cursor Agent Skill** 使用。

和「一套通用分类直接套上去」不同：Skill 会先**盘点你有哪些站**，再**一簇一簇和你商量放哪**，确认后再生成可导入的收藏夹。分类规则写在你本地的 scheme 文件里，不会污染 Skill 本体。

> 当前仓库为**私有**，自测通过后再改为公开。

---

## 能做什么

- 解析 `NETSCAPE-Bookmark-file-1` 格式（Edge / Chrome 导出）
- 三种模式：`scheme`（共创规则）· `preserve`（保留原文件夹）· `auto`（通用规则库）
- 可选并发失效检测（温和策略：只删确定失效；403/SSL/5xx 进存疑清单）
- URL 去重；输出可再导入浏览器的 HTML + 报告 / CSV 清单

---

## 快速开始（命令行）

```bash
git clone https://github.com/rz20923/bookmark-coorganizer.git
cd bookmark-coorganizer
pip install -r requirements.txt

# 预览（不写文件、不联网）
python organizer.py 你的收藏夹.html --categories categories.json --mode auto --preview

# 正式整理（默认做失效检测；跳过则加 --no-check）
python organizer.py 你的收藏夹.html --categories categories.json --mode auto
```

共创分类时，把讨论结果存成 `*.scheme.json`（见 `examples/scheme_template.json`），然后：

```bash
python organizer.py 你的收藏夹.html --categories ./我的方案.scheme.json --mode scheme --preview
```

---

## 安装为 Cursor Skill

```bash
# 个人全局
cp -r . ~/.cursor/skills/bookmark-coorganizer

# Windows PowerShell
Copy-Item -Recurse . $HOME\.cursor\skills\bookmark-coorganizer
```

在对话里提到「整理收藏夹」并附上 HTML 路径即可触发。Agent 应按 `SKILL.md` **先访谈再整理**。

---

## 仓库里有什么

| 路径 | 说明 |
|---|---|
| `SKILL.md` | Agent 共创流程（给 Cursor 读） |
| `organizer.py` | 整理引擎 |
| `categories.json` | 通用默认规则库（`auto` 模式） |
| `examples/scheme_template.json` | 自定义 scheme 模板（勿提交私人收藏夹） |
| `self_check.py` | 最小自检 |
| `tools/gen_categories.py` | 重建通用规则库的辅助脚本（可选） |

**不要**把个人 `favorites_*.html`、会话 `*.scheme.json`、整理产物提交进公开仓库（已在 `.gitignore`）。

---

## 输出产物

| 文件 | 说明 |
|---|---|
| `*_整理后.html` | 导入 Edge/Chrome |
| `*_整理报告.md` | 概览与结构 |
| `*_失效清单.csv` / `*_存疑清单.csv` / `*_重复清单.csv` | 明细 |

---

## 许可

MIT © 维护者
