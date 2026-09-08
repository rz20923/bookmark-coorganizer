# bookmark-coorganizer

**English** · [简体中文](README.zh-CN.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.7+](https://img.shields.io/badge/Python-3.7+-green.svg)](https://www.python.org/)
[![Agent Skill](https://img.shields.io/badge/Agent-Cursor%20%2F%20Codex-111827.svg)](https://skills.sh/)

Co-organize Edge / Chrome Netscape bookmark HTML with an AI agent: inventory → discuss clusters with you → preview → organize (optional dead-link check + dedupe).

Your co-created rules stay in a local `*.scheme.json` next to your HTML. The original favorites file is never modified.

---

## Features

- Parse `NETSCAPE-Bookmark-file-1` exports (Edge / Chrome)
- Collaborative workflow — no blind auto-sort dump
- Modes: `scheme` (your rules) · `preserve` (keep folders) · `auto` (shared defaults)
- Optional concurrent dead-link checks (403 / SSL / 5xx kept as *doubtful*)
- URL dedupe; importable HTML + report + CSV lists

---

## Install

One command (skills CLI):

```bash
npx skills add rz20923/bookmark-coorganizer -g -y
```

Update later:

```bash
npx skills update
```

Then in Cursor or Codex: attach **bookmark-coorganizer** and pass your favorites `.html` path.

---

## Quick start (in chat)

1. Attach this skill.
2. Send something like:  
   `Organize c:\Users\...\favorites.html`
3. Review inventory clusters; agree on placement group by group.
4. When you say it’s OK to organize, the agent writes outputs next to your HTML.

---

## Engine (bundled)

Scripts live inside the installed skill (`$SKILL/scripts/`). The agent runs them for you; you normally don’t need a separate CLI setup.

```bash
# Inventory only (stdout, no writes)
python $SKILL/scripts/organizer.py bookmarks.html --inventory

# Preview with your scheme
python $SKILL/scripts/organizer.py bookmarks.html \
  --categories ./my.scheme.json --mode scheme --preview

# Organize (add --no-check to skip dead-link checks)
python $SKILL/scripts/organizer.py bookmarks.html \
  --categories ./my.scheme.json --mode scheme
```

Optional dependency for link checks:

```bash
pip install -r $SKILL/requirements.txt
```

Scheme template: [`examples/scheme_template.json`](examples/scheme_template.json)

---

## Package layout

```text
bookmark-coorganizer/
├── SKILL.md                      # Agent instructions
├── README.md                     # This file (English)
├── README.zh-CN.md               # Chinese
├── categories.json               # Defaults for --mode auto
├── requirements.txt
├── examples/scheme_template.json
└── scripts/
    ├── organizer.py
    └── self_check.py
```

---

## Outputs

Written next to the input HTML by default:

| File | Description |
|------|-------------|
| `*_整理后.html` | Import into Edge / Chrome |
| `*_整理报告.md` | Summary |
| `*_失效清单.csv` | Confirmed dead links |
| `*_存疑清单.csv` | Doubtful (kept) |
| `*_重复清单.csv` | Duplicates removed |

---

## Privacy

Bookmark files often contain personal history. Do **not** commit private `favorites_*.html`, session `*.scheme.json`, or organize outputs to a public repo.

---

## License

[MIT](LICENSE) © maintainers
