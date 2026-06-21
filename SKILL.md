---
name: mycelium
description: >
  Build and maintain a persistent, compounding knowledge base using LLM.
  Ingest articles, PDFs, videos, web pages, podcasts into structured wiki notes
  with cross-references, contradiction detection, and concept evolution tracking.
  Query across all knowledge with answers automatically filed back into the wiki.
  Lint for consistency, knowledge gaps, stale claims, and research directions.
  Use this skill whenever the user mentions wiki, knowledge base, notes, research,
  organizing information, ingest, article summarization, reading notes, book notes,
  paper notes, podcast notes, video notes, competitive analysis, learning, studying,
  personal knowledge, Zettelkasten, second brain, or wants to build a knowledge
  system. Also use when the user drops files into a directory and wants them
  processed into structured notes, asks questions about previously ingested
  content, wants to compare concepts, needs a health check on existing notes,
  or says "ingest", "query", "lint", "what do you know about", "summarize",
  "explain", "compare", or "what have I read about".
---

# Mycelium 🍄

> *Like the fungal network beneath a forest — invisible, persistent, connecting everything.*

A persistent, compounding knowledge base powered by LLM. Inspired by Karpathy's LLM Wiki pattern.

## Core Concept

```
人类：思考、提问、决定方向
LLM：整理、关联、维护一致性
```

The wiki is a **persistent, compounding artifact**. Cross-references are pre-built, not computed at query time. Every query and ingest makes the wiki richer.

## Quick Start

Tell Claude what you want:

```bash
# Initialize a new wiki
"初始化一个研究笔记"

# Ingest a source
"ingest article.pdf"

# Ask a question
"什么是注意力机制？"

# Health check
"lint --deep"
```

Claude reads this skill file and handles everything automatically. You don't need to run scripts directly — just talk to Claude.

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
│   └── meta/          # Slides, charts, generated artifacts
└── CLAUDE.md          # Wiki rules and conventions
```

## Operations

### Ingest

Drop source in `.raw/`, tell Claude to ingest.

```bash
# Add source file
cp article.txt .raw/

# Tell Claude
"ingest article.txt"
```

**What happens:**
1. Read source file (auto-detect type)
2. Extract core insights (3-5)
3. Create source note in `wiki/sources/`
4. Identify key concepts → create/update `wiki/concepts/`
   - Track concept evolution: increment `version`, update `evidence_strength`, `confidence`
   - If concept contradicts existing notes → create `wiki/contradictions/`
5. Identify entities → create/update `wiki/entities/`
6. Cross-reference: link new notes to existing related pages
7. Update index, index-tags, index-topics, log, hot cache
8. Mark file as ingested in `.raw/.manifest`
9. Auto-commit to git: `git commit -m "ingest: [filename]"`

**Batch ingest:**
```bash
# Ingest multiple sources at once
"ingest all"              # Ingest everything in .raw/
"ingest new"              # Only new files (not yet ingested)
"ingest article-a.md article-b.pdf"  # Specific files
```
For batch ingest, LLM processes each source sequentially, updating the wiki incrementally. Review summaries between items for quality control.

**Image handling:**
When ingesting sources with images (articles, PDFs), follow this strategy:
1. First, read and process all **text content**
2. Then, separately view referenced images (if available locally)
3. Do NOT try to read inline image links in one pass — process text first, images after

### .raw/ Supported Types

| Type | Extensions | Read Method |
|------|-----------|-------------|
| Text | .txt, .md | Direct read |
| PDF | .pdf | markitdown |
| Web | .html | markitdown |
| Subtitle | .srt, .vtt | Direct read |
| Captions | .plain | Direct read |
| Video | .mp4, .mkv | video.py (faster-whisper) |
| Audio | .mp3, .wav | video.py (faster-whisper) |
| Image | .png, .jpg | markitdown (OCR) |
| Office | .docx, .pptx | markitdown |
| URL | .url | Scrapling fetch |

### Ingest from Video URL

When the user provides a video URL (YouTube, Bilibili, 抖音, TikTok):

```bash
# Step 1: Download and extract captions
python3 scripts/video.py "https://www.bilibili.com/video/BV1xxx" -o .raw

# Step 2: Tell Claude to ingest the resulting .plain file
"ingest 视频标题.plain"
```

The `video.py` script auto-detects hardware and selects the fastest model:
- **GPU**: uses `large-v3` (best quality)
- **CPU**: uses `base` (fast, good enough for most content)

Output formats: `plain` (default, best for LLM), `srt`, `txt`

### Fetch Web Articles

```bash
# Fetch from URL
python3 scripts/fetch-web.py https://example.com/article

# With CSS selector
python3 scripts/fetch-web.py https://example.com/article --selector article

# Bypass anti-bot
python3 scripts/fetch-web.py https://protected-site.com --stealth
```

**Scripts:**
- `python3 scripts/auto_ingest.py <file>` - **Full auto pipeline**: read → create notes → update index → generate diagrams → git commit
- `python3 scripts/auto_ingest.py --all` - Batch ingest all new files in .raw/
- `python3 scripts/ingest.py <file>` - Read file and show content for LLM processing
- `python3 scripts/ingest.py` - List all uningested files in .raw/
- `python3 scripts/video.py <url>` - Download video + extract captions
- `python3 scripts/fetch-web.py <url>` - Fetch web article to .raw/
- `python3 scripts/search.py <query>` - Search wiki (BM25 + PageRank + vector)
- `python3 scripts/semantic.py <query>` - Semantic search (optional, needs sentence-transformers)
- `python3/scripts/lint.py` - Check wiki health (orphans, broken links, stale notes)
- `python3 scripts/lint.py --deep` - Deep lint (+ weak evidence, drift detection)
- `python3 scripts/gaps.py` - Detect knowledge gaps (undefined concepts, weak areas)
- `python3 scripts/resolve.py list` - List unresolved contradictions
- `python3/scripts/resolve.py resolve <file>` - Mark contradiction as resolved
- `python3/scripts/source-score.py` - Score source reliability (A-D grading)
- `python3 scripts/index.py` - Rebuild index-tags.md and index-topics.md
- `python3 scripts/query.py <question>` - Find relevant pages for a question
- `python3 scripts/export.py` - Export wiki as single markdown file
- `python3 scripts/export.py -f html` - Export wiki as HTML
- `python3 scripts/watch.py` - Watch .raw/ for new files (poll every 5s)
- `python3 scripts/excalidraw.py` - Generate Excalidraw concept map
- `python3 scripts/graph.py` - Generate interactive HTML knowledge graph
- `python3 scripts/daily.py daily` - Create today's daily note
- `python3 scripts/daily.py weekly` - Create this week's weekly note
- `python3 scripts/kanban.py` - Create research kanban board
- `python3 scripts/canvas.py` - Generate Obsidian Canvas file

See [docs/raw-guide.md](docs/raw-guide.md) and [docs/web-fetch.md](docs/web-fetch.md) for detailed guide.

### Query

Ask any question. Claude reads wiki and answers. **Answers are filed back by default** — every query compounds the wiki.

```bash
"query: 关于Transformer你都知道什么"
"what do you know about attention mechanism"
```

**What happens:**
1. Read `wiki/index.md` first
2. Identify relevant pages (use `scripts/search.py` if wiki is large)
3. Read those pages
4. Synthesize answer with citations
5. **File answer to `wiki/questions/`** (default behavior)
6. Auto-commit: `git commit -m "query: [question summary]"`

**Output types** (user can specify):

| Output | Command | Location |
|--------|---------|----------|
| Question page | `query: ...` (default) | `wiki/questions/` |
| Comparison | `query: ... → 对比` | `wiki/comparisons/` |
| Slide deck | `query: ... → 幻灯片` | `wiki/meta/slides/` |
| Chart | `query: ... → 画图` | `wiki/meta/charts/` |

**Marp slide deck output:**
```bash
"query: Transformer架构总结 → 幻灯片"
# Generates wiki/meta/slides/transformer-summary.md (Marp format)
# Open in Obsidian with Marp plugin, or: marp --pptx output.md
```

**Chart output:**
```bash
"query: attention发展时间线 → 画图"
# Generates wiki/meta/charts/attention-timeline.py (matplotlib)
# Run: python3 wiki/meta/charts/attention-timeline.py
```

### Lint

Health check the wiki. Two modes:

```bash
"lint"           # Standard: structural checks
"lint --deep"    # Deep: + knowledge gaps, research directions, web search
```

**Standard lint checks:**
1. Orphan pages (no inbound links)
2. Broken links (links to nonexistent pages)
3. Stale notes (status: draft > 30 days)
4. Frontmatter completeness

**Deep lint adds:**
5. **Contradictions** — different pages make conflicting claims
   - Auto-create `wiki/contradictions/` pages for each conflict
   - Include both sides with sources
6. **Knowledge gaps** — concepts referenced but never defined
7. **Evidence strength** — concepts with only 1 source (weak)
8. **Knowledge drift detection** — concepts with `confidence < 0.3` flagged as unreliable, `last_verified > 180 days` flagged as stale, auto-suggest re-ingesting related sources
9. **Research directions** — based on current knowledge, what should be explored next
10. **Web search suggestions** — gaps fillable by external search
11. **Concept consolidation** — detect near-duplicate concepts and suggest merge
12. **Update indexes** — regenerate `index-tags.md` and `index-topics.md`

### Knowledge Gap Detection

```bash
python3 scripts/gaps.py --dir <wiki_dir>
```

Finds: undefined concepts (referenced but no page), weak evidence, orphan concepts, disconnected concepts. Automatically runs during `lint --deep` and after `auto_ingest.py`.

### Contradiction Resolution

```bash
python3 scripts/resolve.py list                           # List unresolved contradictions
python3 scripts/resolve.py resolve <file> -r "结论"       # Mark as resolved
```

### Source Reliability Scoring

```bash
python3 scripts/source-score.py --dir <wiki_dir>
```

Scores each source on: type, structure, citations, cross-references, metadata completeness, status. Outputs A-D grades. Automatically runs after `auto_ingest.py`.

### Evolution Timeline

```bash
python3 scripts/timeline.py --dir <wiki_dir>
```

Generates `wiki/meta/evolution-timeline.png` showing concept version growth and confidence vs evidence. Requires matplotlib. Automatically runs after `auto_ingest.py`.

### Statistics Dashboard

```bash
python3 scripts/stats.py --dir <wiki_dir>                # Generate HTML dashboard
python3 scripts/stats.py --dir <wiki_dir> --json          # Output stats as JSON
```

Generates `wiki/meta/dashboard.html` with note counts, type distribution, tag cloud, monthly growth.

### Semantic Search (Optional)

```bash
python3 scripts/semantic.py "query" --enable              # Requires sentence-transformers
python3 scripts/search.py "query" --mode semantic         # Also works
```

Falls back to BM25 if sentence-transformers not installed. Disabled by default to avoid heavy dependency.

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
# Enhanced frontmatter for concepts
version: 3                    # Increment on major updates
supersedes: [[old-version]]   # If this replaces an older concept
evidence_strength: strong     # weak (1 source) | moderate (2-3) | strong (4+)
confidence: 0.85             # 0-1, based on source agreement
last_verified: 2026-06-20    # Date of last verification
```

**Rules:**
- New source with supporting evidence → increment `version`, boost `confidence`
- New source with contradicting evidence → create `wiki/contradictions/`, lower `confidence`
- `last_verified` > 90 days → flag in deep lint

## Git Workflow

Every wiki is a git repository. Auto-commits on:
- `init` — initial commit
- `ingest` — `git commit -m "ingest: [filename]"`
- `query` — `git commit -m "query: [question summary]"`
- `lint --deep` — `git commit -m "lint: [fixes made]"`

**Exploratory branches:**
```bash
git checkout -b explore/multimodal   # Try new topic area
git checkout -b experiment/xyz       # Test hypothesis
# When satisfied, merge back:
git checkout main && git merge explore/multimodal
```

## Obsidian Integration

This wiki works beautifully with Obsidian:

- **Graph View** — see knowledge structure, find hubs and orphans
- **Dataview** — query frontmatter for dynamic views
- **Excalidraw** — concept maps generated by `excalidraw.py`
- **Canvas** — note canvases generated by `canvas.py`
- **Kanban** — research task board generated by `kanban.py`
- **Daily Notes** — daily/weekly notes generated by `daily.py`
- **Marp plugin** — render slide decks from wiki content
- **Web Clipper** — save articles directly to `.raw/`
- **Git plugin** — sync wiki across devices

**Generated files:**
- `wiki/meta/concept-map.excalidraw` — concept relationship diagram
- `wiki/meta/knowledge-graph.html` — interactive graph (open in browser)
- `wiki/meta/wiki-canvas.canvas` — Obsidian Canvas file
- `wiki/meta/kanban.md` — research task board
- `wiki/daily/YYYY-MM-DD.md` — daily note
- `wiki/weekly/week-XX.md` — weekly note

See [docs/obsidian-guide.md](docs/obsidian-guide.md) for setup and Dataview queries.

## Scaled Search

For wikis with 100+ pages, use the built-in search:

```bash
python3 scripts/search.py "attention mechanism"
python3 scripts/search.py "RLHF" --mode hybrid
python3 scripts/search.py "对比" --type comparison
python3 scripts/search.py "transformer" --summary          # Token-efficient: title + one-liner only
python3 scripts/search.py "RLHF" --mode vector             # Vector similarity search
```

| Mode | Description | Best for |
|------|-------------|----------|
| `hybrid` (default) | 50% BM25 + 25% PageRank + 25% Vector | General use |
| `bm25` | Keyword matching only | Exact term search |
| `links` | Wikilink graph only | Finding related pages |
| `vector` | TF-IDF cosine similarity | Semantic similarity |

Use `--summary` to reduce token cost: returns only title + one-line summary per result.

### Concept Merge/Split

When two concepts overlap significantly, merge them:

```bash
python3 scripts/merge-concepts.py merge "self-attention" "scaled-dot-product" --keep "self-attention"
python3 scripts/merge-concepts.py split "neural-network" --into "feedforward-network,recurrent-network"
```

Merge updates all wikilinks across the wiki and marks the superseded concept. Split creates new concept pages and marks the original as superseded.

## Templates

See [REFERENCE.md](REFERENCE.md) for detailed note templates, quality standards, and checklists.

## Bundled Resources

| Resource | When to read |
|----------|-------------|
| [REFERENCE.md](REFERENCE.md) | When creating/updating notes — contains templates, field definitions, quality standards, checklists |
| [EXAMPLES.md](EXAMPLES.md) | When unsure about workflow — contains 13 worked examples covering all operations |
| [docs/obsidian-guide.md](docs/obsidian-guide.md) | When user wants Obsidian setup, Dataview queries, or Marp integration |
| [docs/raw-guide.md](docs/raw-guide.md) | When user asks about .raw/ directory, supported types, or file management |
| [docs/web-fetch.md](docs/web-fetch.md) | When user wants to fetch web articles or needs help with Scrapling |

## Rules

1. **Never modify `.raw/`** — sources are immutable. This preserves provenance: you can always trace a wiki claim back to the exact source document. If the source updates, add the new version alongside the old, don't overwrite.

2. **Always use wikilinks** — `[[concept]]` format. Wikilinks create the cross-reference graph that makes the wiki more than a pile of notes. Without them, pages are isolated and the wiki loses its compounding power.

3. **Always update index** — after every ingest. The index is how the LLM finds relevant pages at query time. A stale index means missed connections and worse answers.

4. **Always update log** — append-only, new entries at top. The log provides a timeline of the wiki's evolution and helps the LLM understand recent activity when answering questions.

5. **Always update hot cache** — recent context summary. The hot cache gives the LLM quick access to what matters right now, without re-reading the full index.

6. **Use frontmatter** — type, status, created, tags. Structured metadata enables Dataview queries, search filtering, and automated lint checks.

7. **One concept per page** — atomic, linkable. A page about "attention mechanism" should not also be about "transformer architecture". Atomic pages can be composed in infinite combinations; monolithic pages cannot.

8. **Cite sources** — every claim has a source. Unsourced claims are noise. When new sources contradict old ones, citations let you identify exactly which evidence supports which position.

9. **Distinguish fact vs opinion** — mark uncertainty. The wiki should be reliable. Distinguishing "research shows X" from "I think X" prevents the LLM from treating speculation as established knowledge.

10. **File query answers** — default to saving, not just answering. This is the core compounding mechanism: every question asked makes the wiki richer for future questions. Without filing, knowledge evaporates into chat history.

11. **Track evolution** — concept version, evidence strength, confidence. Knowledge isn't static. Tracking how concepts evolve across sources prevents the wiki from becoming a snapshot of outdated thinking.

12. **Auto-commit git** — every operation creates a commit. Git gives you free version history, branching for experiments, and the ability to revert if an ingest goes wrong.

13. **Contradictions are features** — not bugs; document them explicitly. Contradictions between sources are the most interesting parts of a knowledge base. They reveal open questions and areas where consensus hasn't formed.

14. **Text before images** — when ingesting content with images, process all text first, then view images separately. LLMs can't efficiently process inline images and text in one pass. Text-first produces better summaries; images are then reviewed for additional context.

15. **Token-efficient search** — use `--summary` flag when searching large wikis to reduce token cost. At 100+ pages, loading full page content burns tokens without proportional value. Summary mode returns titles and one-liners, letting the LLM drill into only the relevant pages.

16. **Preserve math formulas** — when ingesting content with LaTeX math, keep the original `$...$` / `$$...$$` syntax. Don't convert formulas to text descriptions. Obsidian renders LaTeX natively via MathJax. If the source has no LaTeX (e.g., video subtitles), describe the formula in text and add the LaTeX version.

## See Also

- [REFERENCE.md](REFERENCE.md) — Note templates and quality standards
- [EXAMPLES.md](EXAMPLES.md) — Usage examples
- [docs/obsidian-guide.md](docs/obsidian-guide.md) — Obsidian integration
