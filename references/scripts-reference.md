# Scripts Reference

Complete list of available scripts. All scripts are in `scripts/` directory.

## Content Ingestion

| Script | Command | Description |
|--------|---------|-------------|
| auto_ingest.py | `python3 scripts/auto_ingest.py <file>` | Full auto pipeline: read → create notes → update index → generate diagrams → git commit |
| auto_ingest.py | `python3 scripts/auto_ingest.py --all` | Batch ingest all new files in .raw/ |
| ingest.py | `python3 scripts/ingest.py <file>` | Read file and show content for LLM processing |
| ingest.py | `python3 scripts/ingest.py` | List all uningested files in .raw/ |
| video.py | `python3 scripts/video.py <url>` | Download video + extract captions (YouTube, Bilibili, 抖音, TikTok) |
| fetch-web.py | `python3 scripts/fetch-web.py <url>` | Fetch web article to .raw/ |

## Search & Query

| Script | Command | Description |
|--------|---------|-------------|
| search.py | `python3 scripts/search.py <query>` | Search wiki (BM25 + PageRank + vector) |
| search.py | `python3 scripts/search.py <query> --summary` | Token-efficient: title + one-liner only |
| search.py | `python3 scripts/search.py <query> --mode vector` | Vector similarity search |
| semantic.py | `python3 scripts/semantic.py <query>` | Semantic search (optional, needs sentence-transformers) |
| query.py | `python3 scripts/query.py <question>` | Find relevant pages for a question |

## Health & Maintenance

| Script | Command | Description |
|--------|---------|-------------|
| lint.py | `python3 scripts/lint.py` | Check wiki health (orphans, broken links, stale notes) |
| lint.py | `python3 scripts/lint.py --deep` | Deep lint (+ weak evidence, drift detection) |
| gaps.py | `python3 scripts/gaps.py` | Detect knowledge gaps (undefined concepts, weak areas) |
| resolve.py | `python3 scripts/resolve.py list` | List unresolved contradictions |
| resolve.py | `python3 scripts/resolve.py resolve <file>` | Mark contradiction as resolved |
| source-score.py | `python3 scripts/source-score.py` | Score source reliability (A-D grading) |
| index.py | `python3 scripts/index.py` | Rebuild index-tags.md and index-topics.md |
| merge-concepts.py | `python3 scripts/merge-concepts.py merge "a" "b" --keep "a"` | Merge two concepts |
| merge-concepts.py | `python3 scripts/merge-concepts.py split "name" --into "a,b"` | Split a concept |

## Visualization

| Script | Command | Description |
|--------|---------|-------------|
| graph.py | `python3 scripts/graph.py` | Generate interactive HTML knowledge graph |
| excalidraw.py | `python3 scripts/excalidraw.py` | Generate Excalidraw concept map |
| canvas.py | `python3 scripts/canvas.py` | Generate Obsidian Canvas file |
| timeline.py | `python3 scripts/timeline.py` | Generate concept evolution timeline (PNG) |
| stats.py | `python3 scripts/stats.py` | Generate HTML dashboard |
| stats.py | `python3 scripts/stats.py --json` | Output stats as JSON |

## Daily Tools

| Script | Command | Description |
|--------|---------|-------------|
| daily.py | `python3 scripts/daily.py daily` | Create today's daily note |
| daily.py | `python3 scripts/daily.py weekly` | Create this week's weekly note |
| kanban.py | `python3 scripts/kanban.py` | Create research kanban board |
| export.py | `python3 scripts/export.py` | Export wiki as single markdown file |
| export.py | `python3 scripts/export.py -f html` | Export wiki as HTML |

## URL Routing

When user provides a URL, check the URL pattern FIRST:

| URL pattern | Tool | Command |
|-------------|------|---------|
| `bilibili.com/video/` | video.py | `python3 scripts/video.py "<url>" -o .raw` |
| `youtube.com/watch` or `youtu.be/` | video.py | `python3 scripts/video.py "<url>" -o .raw` |
| `douyin.com/video/` | video.py | `python3 scripts/video.py "<url>" -o .raw` |
| `tiktok.com/` | video.py | `python3 scripts/video.py "<url>" -o .raw` |
| All other URLs | fetch-web.py | `python3 scripts/fetch-web.py "<url>"` |

**NEVER use fetch-web.py for video URLs** — it only scrapes the webpage metadata, not the video content.
