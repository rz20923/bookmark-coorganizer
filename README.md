# bookmark-coorganizer

**Bookmark co-organizer** · 收藏夹共创整理

Cursor / Codex **Agent Skill** only. Scripts ship inside this folder — install once, then organize in chat. No separate app, no clone workflow.

> 仅作 Agent Skill：装进 skills 目录即可，对话里整理收藏夹。

## Install

**Cursor**

```bash
Copy-Item -Recurse -Force . $HOME\.cursor\skills\bookmark-coorganizer
```

**Codex**

```bash
Copy-Item -Recurse -Force . $HOME\.agents\skills\bookmark-coorganizer
```

In chat: attach this skill + your Netscape favorites HTML path.

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
