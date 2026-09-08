# bookmark-coorganizer

[English](README.md) · **简体中文**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.7+](https://img.shields.io/badge/Python-3.7+-green.svg)](https://www.python.org/)
[![Agent Skill](https://img.shields.io/badge/Agent-Cursor%20%2F%20Codex-111827.svg)](https://skills.sh/)

用 AI Agent **共创整理** Edge / Chrome 导出的 Netscape 收藏夹 HTML：盘点 → 按簇商量 → 预览 → 正式整理（可选失效检测 + 去重）。

共创规则写在书签旁的本地 `*.scheme.json`。**不会修改**原始收藏夹文件。

---

## 功能

- 解析 `NETSCAPE-Bookmark-file-1`（Edge / Chrome 导出）
- 共创流程，避免一键乱分
- 模式：`scheme`（你的规则）· `preserve`（保留原文件夹）· `auto`（通用默认）
- 可选并发失效检测（403 / SSL / 5xx 进存疑并保留）
- URL 去重；可再导入的 HTML + 报告 + CSV 清单

---

## 安装

一条命令（skills CLI）：

```bash
npx skills add rz20923/bookmark-coorganizer -g -y
```

之后更新：

```bash
npx skills update
```

在 Cursor 或 Codex 对话中挂上 **bookmark-coorganizer**，并给出收藏夹 `.html` 路径即可。

---

## 对话里怎么用

1. 挂上本 skill。
2. 发送例如：  
   `整理 c:\Users\...\favorites.html`
3. 查看盘点结果，按簇确认归类。
4. 你说「可以整理」后，产物写在 HTML 同目录。

---

## 引擎（随 skill 打包）

脚本在已安装 skill 内（`$SKILL/scripts/`）。一般由 Agent 调用，无需单独搭命令行环境。

```bash
# 仅盘点（只打 stdout，不写文件）
python $SKILL/scripts/organizer.py bookmarks.html --inventory

# 用 scheme 预览
python $SKILL/scripts/organizer.py bookmarks.html \
  --categories ./my.scheme.json --mode scheme --preview

# 正式整理（跳过失效检测可加 --no-check）
python $SKILL/scripts/organizer.py bookmarks.html \
  --categories ./my.scheme.json --mode scheme
```

失效检测可选依赖：

```bash
pip install -r $SKILL/requirements.txt
```

scheme 模板：[`examples/scheme_template.json`](examples/scheme_template.json)

---

## 目录结构

```text
bookmark-coorganizer/
├── SKILL.md                      # Agent 说明
├── README.md                     # 英文
├── README.zh-CN.md               # 本文件（中文）
├── categories.json               # --mode auto 默认规则
├── requirements.txt
├── examples/scheme_template.json
└── scripts/
    ├── organizer.py
    └── self_check.py
```

---

## 输出产物

默认写在输入 HTML 同目录：

| 文件 | 说明 |
|------|------|
| `*_整理后.html` | 导入 Edge / Chrome |
| `*_整理报告.md` | 概览 |
| `*_失效清单.csv` | 确定失效 |
| `*_存疑清单.csv` | 存疑（已保留） |
| `*_重复清单.csv` | 已去重项 |

---

## 隐私

收藏夹常含个人痕迹。请勿把私人 `favorites_*.html`、会话 `*.scheme.json` 或整理产物提交到公开仓库。

---

## 许可

[MIT](LICENSE) © 维护者
