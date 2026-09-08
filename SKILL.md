---
name: bookmark-coorganizer
description: >-
  Co-organizes Edge/Chrome Netscape bookmark HTML: inventory sites into clusters,
  discuss placement group-by-group with the user, then preview and organize with
  dead-link checks and dedupe. Use for 收藏夹/书签整理, favorites HTML cleanup,
  or dead bookmark links.
---

# Bookmark co-organizer

> 收藏夹共创整理

Co-create a folder taxonomy for any Netscape bookmark HTML, then run the bundled script to preview / organize.

`$SKILL` = directory that contains this `SKILL.md` (usually `~/.cursor/skills/bookmark-coorganizer` or `~/.agents/skills/bookmark-coorganizer`). Engine: `$SKILL/scripts/organizer.py`. Never assume an author machine path like `C:\26tag\...`.

## Hard rules

> 硬性规则

1. **Chat first, write files sparingly.** During inventory/discussion: only run bundled scripts and read stdout. **Do not** create temp inventory scripts or scratch JSON in the workspace or skill dir.
2. **No full organize until the user confirms.** Before that, `--preview` at most.
3. **Do not dump the full taxonomy at once.** Order: inventory → cluster by affinity → discuss cluster-by-cluster → assemble categories → preview → organize.
4. Each cluster: name **concrete sites**, state the shared theme, ask “standalone folder or merge into an existing one?”
5. Write co-created rules only beside the user’s bookmark HTML as `*.scheme.json`. **Do not** edit `$SKILL/categories.json` unless updating shared defaults.

> 1. 盘点/讨论只跑自带脚本看 stdout。2. 确认前最多 `--preview`。3. 禁止一次甩完整分类表。4. 每簇用具体站名商量。5. scheme 写在书签旁。

## When writing to disk is allowed

> 何时才允许写盘

| When | Allowed writes |
|------|----------------|
| Clusters settled; ready to preview | `*.scheme.json` next to the HTML ([examples/scheme_template.json](examples/scheme_template.json)) |
| User says OK to organize (e.g. 「可以整理」) | Drop `--preview`; outputs next to the HTML |
| Any other time | **No file writes** |

## Scripts

> 自带脚本

Windows: `$env:PYTHONIOENCODING='utf-8'`

```bash
python $SKILL/scripts/organizer.py <bookmarks.html> --inventory

python $SKILL/scripts/organizer.py <bookmarks.html> \
  --categories <same-dir-as-html>/<name>.scheme.json \
  --mode scheme --preview

python $SKILL/scripts/organizer.py <bookmarks.html> \
  --categories <same-dir-as-html>/<name>.scheme.json \
  --mode scheme
```

Add `--no-check` to skip dead-link checks. Modes: `scheme` (default path) · `preserve` · `auto` (`$SKILL/categories.json`).

Python 3.7+. Optional: `pip install -r $SKILL/requirements.txt` for dead-link checks.

## Workflow

> 工作流

1. **Inventory** — `--inventory`; show counts, folders, clusters (3–8 sites + theme). No final category names yet.
2. **Discuss** — agreed-rules table in chat; a few clusters per turn; then ask about dead-link checks.
3. **Persist → preview** — write scheme → `--mode scheme --preview`; edit that scheme only.
4. **Organize** — after confirmation, drop `--preview`.

## Notes

> 注意

Do not modify the original HTML. 403 / SSL / 5xx → keep as doubtful. Bookmarks are private — do not publish them.
