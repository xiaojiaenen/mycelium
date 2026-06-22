---
name: mycelium
description: >
  Build and maintain a persistent, compounding knowledge base powered by LLM.
  Ingest articles, PDFs, videos, web pages into structured wiki notes with
  cross-references, contradiction detection, and concept evolution tracking.
  Query across all knowledge with answers automatically filed back into the wiki.

  Use this skill when the user wants to:
  - Ingest files into a knowledge base (ingest, add source, process file)
  - Query existing knowledge (what do I know about, search my notes)
  - Check wiki health (lint, find gaps, check consistency)
  - Visualize knowledge (graph, timeline, dashboard)
  - Work with daily notes, kanban, or export wiki content

  Do NOT use for: simple file reading, one-off summaries without storage,
  code documentation, or when no wiki directory exists.
---

# Mycelium 🍄

> *Like the fungal network beneath a forest — invisible, persistent, connecting everything.*

A persistent, compounding knowledge base powered by LLM. Inspired by Karpathy's LLM Wiki pattern.

Wiki 默认在**当前工作目录**。脚本在 skill 的 `scripts/` 目录下，Claude 会自动找到。

## Core Concept

```
人类：思考、提问、决定方向
LLM：整理、关联、维护一致性
```

The wiki is a **persistent, compounding artifact**. Cross-references are pre-built, not computed at query time. Every query and ingest makes the wiki richer.

## Quick Start

```bash
# 初始化 wiki（当前目录）
"初始化一个研究笔记"

# 摄入素材
"ingest article.pdf"

# 提问
"什么是注意力机制？"

# 健康检查
"lint --deep"
```

Claude 自动完成一切。脚本路径自动解析，wiki 默认在当前目录。

## Directory Structure

```
wiki/
├── .raw/              # Source files (immutable, LLM never modifies)
├── wiki/
│   ├── index.md       # Master catalog
│   ├── index-tags.md  # Auto-generated tag index
│   ├── index-topics.md # Auto-generated topic clusters
│   ├── log.md         # Operation log
│   ├── hot.md         # Recent context cache
│   ├── sources/       # Source summaries
│   ├── concepts/      # Concept explanations
│   ├── entities/      # People, orgs, products
│   ├── comparisons/   # Side-by-side analyses
│   ├── contradictions/ # Cross-source conflicts
│   ├── questions/     # Filed answers
│   ├── daily/         # Daily notes
│   ├── weekly/        # Weekly notes
│   └── meta/          # Slides, charts, generated artifacts
└── CLAUDE.md          # Wiki rules and conventions
```

## Operations

### Ingest

Drop source in `.raw/`, tell Claude to ingest.

**What happens:**
1. Read source file (auto-detect type)
2. Extract core insights (3-5)
3. Create source note in `wiki/sources/`
4. Identify key concepts → create/update `wiki/concepts/`
5. Identify entities → create/update `wiki/entities/`
6. Cross-reference: link new notes to existing related pages
7. Update index, log, hot cache
8. Auto-commit to git

**Batch ingest:**
```bash
"ingest all"              # Ingest everything in .raw/
"ingest new"              # Only new files (not yet ingested)
"ingest article-a.md article-b.pdf"  # Specific files
```

**Important:** For video URLs (bilibili/youtube/douyin/tiktok), use `video.py` NOT `fetch-web.py`. See [references/scripts-reference.md](references/scripts-reference.md) for URL routing.

### Query

Ask any question. Claude reads wiki and answers. **Answers are filed back by default** — every query compounds the wiki.

**Output types:**
- `query: ...` → Question page (default)
- `query: ... → 对比` → Comparison
- `query: ... → 幻灯片` → Slide deck (Marp)
- `query: ... → 画图` → Chart (matplotlib)

### Lint

Health check the wiki:

```bash
"lint"           # Standard: structural checks
"lint --deep"    # Deep: + knowledge gaps, contradictions, drift detection
```

**Standard:** orphan pages, broken links, stale notes, frontmatter completeness.

**Deep adds:** contradictions detection, knowledge gaps, evidence strength, drift detection, research directions, concept consolidation.

## Note Types

| Type | Location | Purpose |
|------|----------|---------|
| source | `wiki/sources/` | Summary of a source |
| concept | `wiki/concepts/` | Explanation of an idea |
| entity | `wiki/entities/` | Person/org/product |
| comparison | `wiki/comparisons/` | Side-by-side analysis |
| contradiction | `wiki/contradictions/` | Cross-source conflicts |
| question | `wiki/questions/` | Filed answers |

## Concept Evolution

When ingesting new sources, track how concepts evolve:

```yaml
version: 3                    # Increment on major updates
supersedes: [[old-version]]   # If this replaces an older concept
evidence_strength: strong     # weak (1 source) | moderate (2-3) | strong (4+)
confidence: 0.85             # 0-1, based on source agreement
last_verified: 2026-06-20    # Date of last verification
```

## Git Workflow

Every wiki is a git repository. Auto-commits on init, ingest, query, lint.

## Obsidian Integration

This wiki works beautifully with Obsidian: Graph View, Dataview, Excalidraw, Canvas, Kanban, Daily Notes, Marp plugin, Web Clipper, Git plugin.

See [references/obsidian-guide.md](references/obsidian-guide.md) for setup.

## Rules

1. **Never modify `.raw/`** — sources are immutable
2. **Always use wikilinks** — `[[concept]]` format
3. **Always update index** — after every ingest
4. **Always update log** — append-only, new entries at top
5. **Always update hot cache** — recent context summary
6. **Use frontmatter** — type, status, created, tags
7. **One concept per page** — atomic, linkable
8. **Cite sources** — every claim has a source
9. **Distinguish fact vs opinion** — mark uncertainty
10. **File query answers** — default to saving, not just answering
11. **Track evolution** — concept version, evidence strength, confidence
12. **Auto-commit git** — every operation creates a commit
13. **Contradictions are features** — document them explicitly
14. **Text before images** — process text first, images after
15. **Token-efficient search** — use `--summary` flag for large wikis
16. **Preserve math formulas** — keep LaTeX syntax
17. **Route URLs correctly** — video URLs use video.py, not fetch-web.py

## Bundled Resources

| Resource | When to read |
|----------|-------------|
| [references/scripts-reference.md](references/scripts-reference.md) | When using scripts — complete command reference |
| [references/obsidian-guide.md](references/obsidian-guide.md) | When user wants Obsidian setup or Dataview queries |
| [references/raw-guide.md](references/raw-guide.md) | When user asks about .raw/ directory or supported types |
| [references/web-fetch.md](references/web-fetch.md) | When user wants to fetch web articles |
| [REFERENCE.md](REFERENCE.md) | When creating/updating notes — templates and quality standards |
| [EXAMPLES.md](EXAMPLES.md) | When unsure about workflow — 13 worked examples |

## See Also

- [REFERENCE.md](REFERENCE.md) — Note templates and quality standards
- [EXAMPLES.md](EXAMPLES.md) — Usage examples
