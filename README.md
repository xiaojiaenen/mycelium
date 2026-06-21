# Mycelium 🍄

> *Like the fungal network beneath a forest — invisible, persistent, connecting everything.*

A persistent, compounding knowledge base powered by LLM. Inspired by Karpathy's [LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

## What Is This?

A system for building knowledge bases with LLMs. Instead of RAG (retrieve from raw docs each time), you incrementally build a structured wiki that gets richer with every source added.

```
人类：思考、提问、决定方向
LLM：整理、关联、维护一致性
```

The wiki is a **persistent, compounding artifact**. Cross-references are pre-built, not computed at query time. Every query and ingest makes the wiki richer.

> **The Metaphor:** Obsidian is the IDE. The LLM is the programmer. The wiki is the codebase. You browse and review; the LLM writes and maintains.

## Quick Start

```bash
# Initialize a new wiki in current directory (auto git init)
bash scripts/init.sh "My Research Wiki"

# Add source files
cp article.txt .raw/

# Tell Claude to ingest
"ingest article.txt"

# Ask questions (answer auto-filed to wiki)
"query: 关于X你都知道什么"

# Deep health check
"lint --deep"
```

## Directory Structure

```
wiki/
├── .raw/              # Source files (immutable)
├── wiki/
│   ├── index.md       # Master catalog
│   ├── index-tags.md  # Auto-generated tag index
│   ├── index-topics.md # Auto-generated topic clusters
│   ├── log.md         # Operation log
│   ├── hot.md         # Recent context cache
│   ├── sources/       # Source summaries
│   ├── concepts/      # Concept explanations (with evolution tracking)
│   ├── entities/      # People, orgs, products
│   ├── comparisons/   # Side-by-side analyses
│   ├── contradictions/ # Cross-source conflicts
│   ├── questions/     # Filed answers
│   └── meta/          # Slides, charts, generated artifacts
│       ├── slides/    # Marp slide decks
│       └── charts/    # matplotlib charts
└── CLAUDE.md          # Wiki rules
```

## Operations

### Ingest

Drop source in `.raw/`, tell Claude to ingest.

```bash
cp article.pdf .raw/
"ingest article.pdf"
```

Claude will:
1. Read the source
2. Create a structured summary
3. Extract key concepts → create/update concept pages
4. Identify entities → create/update entity pages
5. **Check contradictions** → create contradiction pages if found
6. **Track concept evolution** → update version, evidence_strength, confidence
7. Update index, index-tags, index-topics, log, hot cache
8. **Auto-commit to git**

### Query

Ask any question against the wiki. **Answers are filed back by default**.

```bash
"query: 什么是注意力机制"
"query: Transformer vs RNN → 对比"
"query: 架构总结 → 幻灯片"
"query: 发展时间线 → 画图"
```

| Output Type | Command | Location |
|-------------|---------|----------|
| Question page | `query: ...` (default) | `wiki/questions/` |
| Comparison | `→ 对比` | `wiki/comparisons/` |
| Slide deck | `→ 幻灯片` | `wiki/meta/slides/` |
| Chart | `→ 画图` | `wiki/meta/charts/` |

### Lint

Health check the wiki. Two modes:

```bash
"lint"           # Standard: structural checks
"lint --deep"    # Deep: + contradictions, knowledge gaps, research directions
```

Deep lint adds:
- **Contradictions** — auto-create conflict pages with both sides + sources
- **Knowledge gaps** — concepts referenced but never defined
- **Evidence strength** — concepts with only 1 source
- **Research directions** — what to explore next
- **Stale verification** — concepts not verified in 90+ days
- **Web search suggestions** — gaps fillable by external search
- **Index regeneration** — update tag and topic indexes

### Search

For wikis with 100+ pages:

```bash
python3 scripts/search.py "attention mechanism"
python3 scripts/search.py "RLHF" --mode hybrid
python3 scripts/search.py "对比" --type comparison --top 10
```

BM25 + wikilink graph analysis. Results ranked by relevance and connectivity.

## Note Types

| Type | Location | Purpose |
|------|----------|---------|
| source | `wiki/sources/` | Summary of a source |
| concept | `wiki/concepts/` | Explanation of an idea (with evolution tracking) |
| entity | `wiki/entities/` | Person/org/product |
| comparison | `wiki/comparisons/` | Side-by-side analysis |
| contradiction | `wiki/contradictions/` | Cross-source conflicts |
| question | `wiki/questions/` | Filed answers |

## Concept Evolution

Track how concepts evolve across sources:

```yaml
version: 3                    # Increment on major updates
supersedes: [[old-version]]   # Older version this replaces
evidence_strength: strong     # weak (1) | moderate (2-3) | strong (4+)
confidence: 0.85             # 0-1, based on source agreement
last_verified: 2026-06-20    # Date of last verification
```

## Git Workflow

Every wiki is a git repository:
- **Auto-commit** on every ingest, query, and lint
- **Exploratory branches** for research: `git checkout -b explore/topic`
- **Version history** of your knowledge base evolution

## Obsidian Integration

Works beautifully with Obsidian:
- **Graph View** — see knowledge structure
- **Dataview** — query frontmatter for dynamic views
- **Marp plugin** — render slide decks
- **Web Clipper** — save articles to `.raw/`
- **Git plugin** — sync across devices

See [docs/obsidian-guide.md](docs/obsidian-guide.md) for setup and Dataview queries.

## Documentation

- [SKILL.md](SKILL.md) — Skill instructions
- [REFERENCE.md](REFERENCE.md) — Note templates and quality standards
- [EXAMPLES.md](EXAMPLES.md) — Usage examples
- [docs/obsidian-guide.md](docs/obsidian-guide.md) — Obsidian integration
- [docs/raw-guide.md](docs/raw-guide.md) — .raw/ directory guide
- [docs/web-fetch.md](docs/web-fetch.md) — Web scraping guide

## Why This Works

From Karpathy:

> The maintenance burden (cross-references, keeping summaries current, noting contradictions, maintaining consistency) is what kills human-maintained wikis. LLMs don't get bored, don't forget to update a cross-reference, and can touch 15 files in one pass.

The human curates sources, directs analysis, asks questions, and thinks about meaning. The LLM's job is everything else.

## vs RAG

| Aspect | RAG | Mycelium |
|--------|-----|----------|
| Cross-references | Built at query time | Pre-built |
| Contradictions | Not detected | Flagged + conflict pages |
| Synthesis | Per-query | Compounds over time |
| Token cost | High (raw docs) | Low (wiki pages) |
| Maintenance | None (but poor quality) | LLM handles it |
| Version tracking | None | Concept evolution |
| Search | Vector DB needed | BM25 + graph (built-in) |

## License

MIT
