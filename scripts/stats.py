#!/usr/bin/env python3
"""Generate reading statistics and dashboard."""
import re
import json
import argparse
from pathlib import Path
from datetime import date, datetime
from collections import Counter, defaultdict

import sys
sys.path.insert(0, str(Path(__file__).parent))
from utils import parse_frontmatter, TODAY


def collect_stats(wiki_dir: Path) -> dict:
    """Collect comprehensive wiki statistics."""
    wiki = wiki_dir / "wiki"

    stats = {
        "total_notes": 0,
        "by_type": Counter(),
        "by_status": Counter(),
        "by_month": Counter(),
        "top_tags": Counter(),
        "sources_count": 0,
        "concepts_count": 0,
        "total_links": 0,
        "avg_links_per_note": 0,
        "strong_evidence": 0,
        "weak_evidence": 0,
        "evolved_concepts": 0,
    }

    all_notes = []
    for subdir in ['sources', 'concepts', 'entities', 'comparisons', 'questions', 'contradictions']:
        dir_path = wiki / subdir
        if not dir_path.exists():
            continue
        for md_file in dir_path.glob('*.md'):
            content = md_file.read_text(encoding='utf-8')
            fm = parse_frontmatter(content)

            note_type = fm.get('type', subdir.rstrip('s'))
            status = fm.get('status', 'unknown')
            created = fm.get('created', '')
            tags = fm.get('tags', [])
            if isinstance(tags, str):
                tags = [tags]

            links = re.findall(r'\[\[([^\]]+)\]\]', content)
            version = int(fm.get('version', '1'))
            evidence = fm.get('evidence_strength', '')

            stats["total_notes"] += 1
            stats["by_type"][note_type] += 1
            stats["by_status"][status] += 1
            stats["total_links"] += len(links)

            if created:
                month = created[:7]  # YYYY-MM
                stats["by_month"][month] += 1

            for tag in tags:
                if tag:
                    stats["top_tags"][tag] += 1

            if note_type == 'source':
                stats["sources_count"] += 1
            elif note_type == 'concept':
                stats["concepts_count"] += 1
                if version > 1:
                    stats["evolved_concepts"] += 1
                if evidence == 'strong':
                    stats["strong_evidence"] += 1
                elif evidence == 'weak':
                    stats["weak_evidence"] += 1

            all_notes.append({"fm": fm, "links": links})

    if stats["total_notes"] > 0:
        stats["avg_links_per_note"] = round(stats["total_links"] / stats["total_notes"], 1)

    return stats


def generate_dashboard(wiki_dir: str = ".", output: str = None):
    """Generate HTML dashboard."""
    base = Path(wiki_dir)
    stats = collect_stats(base)

    # Build HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Mycelium Dashboard</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: system-ui, sans-serif; background: #1a1b26; color: #fff; padding: 30px; }}
h1 {{ margin-bottom: 30px; font-size: 24px; }}
.grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }}
.card {{ background: rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; text-align: center; }}
.card .value {{ font-size: 36px; font-weight: bold; color: #7aa2f7; }}
.card .label {{ font-size: 13px; color: #aaa; margin-top: 5px; }}
.section {{ margin-bottom: 30px; }}
.section h2 {{ font-size: 18px; margin-bottom: 15px; color: #7aa2f7; }}
.bar {{ display: flex; align-items: center; margin: 8px 0; }}
.bar-label {{ width: 120px; font-size: 13px; color: #aaa; }}
.bar-fill {{ height: 20px; border-radius: 4px; min-width: 2px; }}
.bar-value {{ margin-left: 10px; font-size: 13px; color: #aaa; }}
.tag {{ display: inline-block; background: rgba(122,162,247,0.2); color: #7aa2f7;
         padding: 4px 10px; border-radius: 12px; margin: 3px; font-size: 12px; }}
</style>
</head>
<body>
<h1>🍄 Mycelium Dashboard</h1>

<div class="grid">
    <div class="card"><div class="value">{stats['total_notes']}</div><div class="label">Total Notes</div></div>
    <div class="card"><div class="value">{stats['sources_count']}</div><div class="label">Sources</div></div>
    <div class="card"><div class="value">{stats['concepts_count']}</div><div class="label">Concepts</div></div>
    <div class="card"><div class="value">{stats['avg_links_per_note']}</div><div class="label">Avg Links/Note</div></div>
</div>

<div class="grid">
    <div class="card"><div class="value">{stats['evolved_concepts']}</div><div class="label">Evolved Concepts</div></div>
    <div class="card"><div class="value">{stats['strong_evidence']}</div><div class="label">Strong Evidence</div></div>
    <div class="card"><div class="value">{stats['weak_evidence']}</div><div class="label">Weak Evidence</div></div>
    <div class="card"><div class="value">{stats['total_links']}</div><div class="label">Total Links</div></div>
</div>

<div class="section">
    <h2>📊 By Type</h2>
"""

    type_colors = {"source": "#a5d8ff", "concept": "#b2f2bb", "entity": "#ffec99",
                   "comparison": "#ffc9c9", "question": "#d0bfff", "contradiction": "#ffd8a8"}

    max_count = max(stats["by_type"].values()) if stats["by_type"] else 1
    for note_type, count in stats["by_type"].most_common():
        color = type_colors.get(note_type, "#e9ecef")
        width = int(count / max_count * 100)
        html += f'    <div class="bar"><span class="bar-label">{note_type}</span><div class="bar-fill" style="width:{width}%;background:{color}"></div><span class="bar-value">{count}</span></div>\n'

    html += """</div>

<div class="section">
    <h2>📋 By Status</h2>
"""

    max_count = max(stats["by_status"].values()) if stats["by_status"] else 1
    for status, count in stats["by_status"].most_common():
        width = int(count / max_count * 100)
        html += f'    <div class="bar"><span class="bar-label">{status}</span><div class="bar-fill" style="width:{width}%;background:#7aa2f7"></div><span class="bar-value">{count}</span></div>\n'

    html += """</div>

<div class="section">
    <h2>🏷️ Top Tags</h2>
    <div>
"""

    for tag, count in stats["top_tags"].most_common(15):
        html += f'        <span class="tag">{tag} ({count})</span>\n'

    html += """    </div>
</div>

<div class="section">
    <h2>📅 Monthly Growth</h2>
"""

    if stats["by_month"]:
        months = sorted(stats["by_month"].keys())
        max_count = max(stats["by_month"].values())
        for month in months:
            count = stats["by_month"][month]
            width = int(count / max_count * 100)
            html += f'    <div class="bar"><span class="bar-label">{month}</span><div class="bar-fill" style="width:{width}%;background:#9ece6a"></div><span class="bar-value">{count}</span></div>\n'

    html += f"""</div>

<div style="text-align:center;color:#555;margin-top:30px;font-size:12px">
    Generated: {TODAY} | Mycelium Knowledge Base
</div>
</body>
</html>"""

    output = output or str(base / "wiki" / "meta" / "dashboard.html")
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(html, encoding='utf-8')

    print(f"✅ Generated: {output}")
    print(f"   Notes: {stats['total_notes']} | Sources: {stats['sources_count']} | Concepts: {stats['concepts_count']}")
    print(f"   Links: {stats['total_links']} | Evolved: {stats['evolved_concepts']}")


def main():
    parser = argparse.ArgumentParser(description="Generate wiki statistics dashboard")
    parser.add_argument("--dir", "-d", default=".", help="Wiki root directory")
    parser.add_argument("--output", "-o", default=None, help="Output HTML file path")
    parser.add_argument("--json", action="store_true", help="Output stats as JSON")
    args = parser.parse_args()

    if args.json:
        base = Path(args.dir)
        stats = collect_stats(base)
        # Convert Counter to dict for JSON
        stats = {k: dict(v) if hasattr(v, 'most_common') else v for k, v in stats.items()}
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    else:
        generate_dashboard(args.dir, args.output)


if __name__ == "__main__":
    main()
