# bookmark-coorganizer

**Bookmark co-organizer** · 收藏夹共创整理

A Cursor / Codex **Agent Skill**. Users install it once with the skills CLI — no zip, no author folder paths.

> 用户用一条命令安装；对话里整理收藏夹即可。

## Install (normal way)

```bash
npx skills add rz20923/bookmark-coorganizer -g -y
```

That puts the skill under `~/.cursor/skills/` (and/or Codex’s skills dir). Then in chat, attach **bookmark-coorganizer** and give your favorites HTML path.

Update later:

```bash
npx skills update
```

## Package

```
SKILL.md
categories.json
requirements.txt
examples/scheme_template.json
scripts/organizer.py
scripts/self_check.py
```

## License

MIT
