#!/usr/bin/env python3
"""Generate reading statistics and dashboard."""
import re
import json
import argparse
from pathlib import Path
from collections import Counter, defaultdict

import sys
sys.path.insert(0, str(Path(__file__).parent))
from utils import parse_frontmatter, TODAY, TYPE_COLORS, WIKI_SUBDIRS


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

    for subdir in WIKI_SUBDIRS:
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

    if stats["total_notes"] > 0:
        stats["avg_links_per_note"] = round(stats["total_links"] / stats["total_notes"], 1)

    return stats


def generate_dashboard(wiki_dir: str = ".", output: str = None):
    """Generate HTML dashboard."""
    base = Path(wiki_dir)
    stats = collect_stats(base)

    # Prepare chart data
    type_data = []
    for note_type, count in stats["by_type"].most_common():
        type_data.append({
            "label": note_type.title(),
            "value": count,
            "color": TYPE_COLORS.get(note_type, "#e9ecef"),
        })

    status_data = []
    for status, count in stats["by_status"].most_common():
        status_data.append({"label": status, "value": count})

    month_data = []
    for month in sorted(stats["by_month"].keys()):
        month_data.append({"label": month, "value": stats["by_month"][month]})

    tag_data = []
    for tag, count in stats["top_tags"].most_common(15):
        tag_data.append({"label": tag, "value": count})

    # Build HTML with modern design
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mycelium Dashboard</title>
<style>
:root {{
    --bg-primary: #0f0f1a;
    --bg-secondary: #1a1b2e;
    --bg-card: rgba(255,255,255,0.03);
    --border: rgba(255,255,255,0.08);
    --text-primary: #e9ecef;
    --text-secondary: #8b8fa3;
    --accent: #7aa2f7;
    --accent-green: #9ece6a;
    --accent-orange: #ff9e64;
    --accent-red: #f7768e;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    padding: 40px;
    min-height: 100vh;
}}
.container {{ max-width: 1200px; margin: 0 auto; }}
h1 {{
    font-size: 28px;
    font-weight: 600;
    margin-bottom: 8px;
    background: linear-gradient(135deg, #7aa2f7, #bb9af7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}
.subtitle {{ color: var(--text-secondary); margin-bottom: 40px; font-size: 14px; }}

.stats-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 40px;
}}
.stat-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    transition: all 0.3s ease;
}}
.stat-card:hover {{
    background: rgba(255,255,255,0.05);
    border-color: var(--accent);
    transform: translateY(-2px);
}}
.stat-value {{
    font-size: 36px;
    font-weight: 700;
    color: var(--accent);
    line-height: 1.2;
}}
.stat-label {{
    font-size: 13px;
    color: var(--text-secondary);
    margin-top: 6px;
}}

.charts-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 24px;
    margin-bottom: 40px;
}}
.chart-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px;
}}
.chart-title {{
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 20px;
    color: var(--text-primary);
}}

.bar {{ display: flex; align-items: center; margin: 10px 0; }}
.bar-label {{
    width: 120px;
    font-size: 13px;
    color: var(--text-secondary);
    flex-shrink: 0;
}}
.bar-track {{
    flex: 1;
    height: 24px;
    background: rgba(255,255,255,0.05);
    border-radius: 6px;
    overflow: hidden;
    position: relative;
}}
.bar-fill {{
    height: 100%;
    border-radius: 6px;
    min-width: 4px;
    transition: width 0.6s ease;
}}
.bar-value {{
    width: 50px;
    text-align: right;
    font-size: 13px;
    color: var(--text-secondary);
    margin-left: 12px;
}}

.tags-container {{ display: flex; flex-wrap: wrap; gap: 8px; }}
.tag {{
    display: inline-flex;
    align-items: center;
    background: rgba(122,162,247,0.15);
    color: var(--accent);
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 13px;
    transition: all 0.2s ease;
}}
.tag:hover {{
    background: rgba(122,162,247,0.25);
    transform: scale(1.05);
}}
.tag-count {{
    font-size: 11px;
    opacity: 0.7;
    margin-left: 6px;
}}

.empty-state {{
    text-align: center;
    padding: 40px;
    color: var(--text-secondary);
}}

.footer {{
    text-align: center;
    color: var(--text-secondary);
    font-size: 12px;
    padding: 20px;
    border-top: 1px solid var(--border);
    margin-top: 40px;
}}
</style>
</head>
<body>
<div class="container">
    <h1>🍄 Mycelium Dashboard</h1>
    <p class="subtitle">Knowledge Base Analytics • {TODAY}</p>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">{stats['total_notes']}</div>
            <div class="stat-label">Total Notes</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats['sources_count']}</div>
            <div class="stat-label">Sources</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats['concepts_count']}</div>
            <div class="stat-label">Concepts</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats['avg_links_per_note']}</div>
            <div class="stat-label">Avg Links/Note</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats['evolved_concepts']}</div>
            <div class="stat-label">Evolved Concepts</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats['strong_evidence']}</div>
            <div class="stat-label">Strong Evidence</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats['weak_evidence']}</div>
            <div class="stat-label">Weak Evidence</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats['total_links']}</div>
            <div class="stat-label">Total Links</div>
        </div>
    </div>

    <div class="charts-grid">
"""

    # Type distribution chart
    if type_data:
        max_val = max(d["value"] for d in type_data)
        html += """        <div class="chart-card">
            <div class="chart-title">📊 Notes by Type</div>
"""
        for d in type_data:
            width = max(int(d["value"] / max_val * 100), 3) if max_val > 0 else 3
            html += f"""            <div class="bar">
                <span class="bar-label">{d['label']}</span>
                <div class="bar-track">
                    <div class="bar-fill" style="width:{width}%;background:{d['color']}"></div>
                </div>
                <span class="bar-value">{d['value']}</span>
            </div>
"""
        html += "        </div>\n"

    # Status distribution chart
    if status_data:
        max_val = max(d["value"] for d in status_data)
        html += """        <div class="chart-card">
            <div class="chart-title">📋 Notes by Status</div>
"""
        status_colors = {
            'read': '#9ece6a', 'reading': '#ff9e64', 'to-read': '#7aa2f7',
            'processed': '#bb9af7', 'unprocessed': '#f7768e',
        }
        for d in status_data:
            width = max(int(d["value"] / max_val * 100), 3) if max_val > 0 else 3
            color = status_colors.get(d['label'], '#7aa2f7')
            html += f"""            <div class="bar">
                <span class="bar-label">{d['label']}</span>
                <div class="bar-track">
                    <div class="bar-fill" style="width:{width}%;background:{color}"></div>
                </div>
                <span class="bar-value">{d['value']}</span>
            </div>
"""
        html += "        </div>\n"

    # Monthly growth chart
    if month_data:
        max_val = max(d["value"] for d in month_data)
        html += """        <div class="chart-card">
            <div class="chart-title">📅 Monthly Growth</div>
"""
        for d in month_data[-12:]:  # Last 12 months
            width = max(int(d["value"] / max_val * 100), 3) if max_val > 0 else 3
            html += f"""            <div class="bar">
                <span class="bar-label">{d['label']}</span>
                <div class="bar-track">
                    <div class="bar-fill" style="width:{width}%;background:var(--accent-green)"></div>
                </div>
                <span class="bar-value">{d['value']}</span>
            </div>
"""
        html += "        </div>\n"

    # Tags chart
    if tag_data:
        html += """        <div class="chart-card">
            <div class="chart-title">🏷️ Top Tags</div>
            <div class="tags-container">
"""
        for d in tag_data:
            html += f'                <span class="tag">{d["label"]}<span class="tag-count">({d["value"]})</span></span>\n'
        html += """            </div>
        </div>
"""

    html += """    </div>

    <div class="footer">
        Generated by Mycelium Knowledge Base System
    </div>
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
