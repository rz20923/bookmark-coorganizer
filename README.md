# bookmark-coorganizer

**Bookmark co-organizer** · 收藏夹共创整理

Cursor / Codex **Agent Skill** only. Scripts ship **inside the installed skill folder**. Users never need the author’s machine path (e.g. `C:\26tag\...`).

> 仅作 Agent Skill。用户机器上只有 `~\.cursor\skills\bookmark-coorganizer`（或 Codex 对应目录），没有开发者本机路径。

## Where it lives after install

| App | Skill path (`$SKILL`) |
|-----|------------------------|
| Cursor | `~\.cursor\skills\bookmark-coorganizer` |
| Codex | `~\.agents\skills\bookmark-coorganizer` |

In chat, attach this skill and give a Netscape favorites HTML path. The agent runs `$SKILL/scripts/organizer.py` from **that** folder.

## Install (users)

Get the skill package somehow (Cursor skill install / download zip / share from author), then place the whole folder at the path above.

If you already have the skill folder open in a terminal (the folder that contains `SKILL.md`), you can copy it:

```powershell
# Cursor — run from inside the skill folder (the one with SKILL.md), not from system32
Copy-Item -Recurse -Force . $HOME\.cursor\skills\bookmark-coorganizer

# Codex
Copy-Item -Recurse -Force . $HOME\.agents\skills\bookmark-coorganizer
```

Do **not** use `C:\26tag\bookmark-coorganizer` unless you are the maintainer of this repo on that machine.

## Package

```
SKILL.md
categories.json
requirements.txt          # optional; for dead-link checks
examples/scheme_template.json
scripts/organizer.py
scripts/self_check.py
```

## License

MIT
