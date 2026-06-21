#!/usr/bin/env python3
"""Export Mycelium wiki to various formats."""
import re
import argparse
from pathlib import Path
from datetime import date


def parse_frontmatter(content: str) -> dict:
    match = re.match(r'^---\n(.*?)\n---\n?(.*)', content, re.DOTALL)
    if not match:
        return {}, content
    fm = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, _, val = line.partition(':')
            val = val.strip().strip('"').strip("'")
            fm[key.strip()] = val
    return fm, match.group(2)


def collect_notes(wiki_dir: Path) -> dict:
    """Collect all notes grouped by type."""
    notes = {}
    for subdir in ['sources', 'concepts', 'entities', 'comparisons', 'questions', 'contradictions']:
        dir_path = wiki_dir / subdir
        if not dir_path.exists():
            continue
        for md_file in sorted(dir_path.glob('*.md')):
            content = md_file.read_text(encoding='utf-8')
            fm, body = parse_frontmatter(content)
            note_type = fm.get('type', subdir.rstrip('s'))
            title = fm.get('title', md_file.stem)
            if note_type not in notes:
                notes[note_type] = []
            notes[note_type].append({
                "title": title,
                "file": md_file.name,
                "frontmatter": fm,
                "body": body.strip(),
            })
    return notes


def export_markdown(wiki_dir: str = ".", output: str = None):
    """Export entire wiki as a single markdown file."""
    base = Path(wiki_dir)
    wiki = base / "wiki"

    if not wiki.exists():
        print(f"❌ wiki/ not found in {wiki_dir}")
        return

    notes = collect_notes(wiki)
    today = date.today().isoformat()

    lines = [
        f"# Mycelium Knowledge Base",
        f"",
        f"Exported: {today}",
        f"",
        f"---",
        f"",
    ]

    type_order = ['sources', 'concepts', 'entities', 'comparisons', 'contradictions', 'questions']
    type_names = {
        'sources': '📚 Sources',
        'concepts': '💡 Concepts',
        'entities': '👤 Entities',
        'comparisons': '⚖️ Comparisons',
        'contradictions': '⚡ Contradictions',
        'questions': '❓ Questions',
    }

    for note_type in type_order:
        if note_type not in notes:
            continue
        lines.append(f"# {type_names.get(note_type, note_type)}")
        lines.append("")
        for note in notes[note_type]:
            lines.append(f"## {note['title']}")
            lines.append("")
            lines.append(note['body'])
            lines.append("")
            lines.append("---")
            lines.append("")

    output = output or f"mycelium-export-{today}.md"
    Path(output).write_text('\n'.join(lines), encoding='utf-8')
    print(f"✅ Exported to: {output}")
    print(f"   Notes: {sum(len(v) for v in notes.values())}")
    print(f"   Types: {', '.join(notes.keys())}")


def export_html(wiki_dir: str = ".", output: str = None):
    """Export wiki as a single HTML file."""
    base = Path(wiki_dir)
    wiki = base / "wiki"

    if not wiki.exists():
        print(f"❌ wiki/ not found in {wiki_dir}")
        return

    notes = collect_notes(wiki)
    today = date.today().isoformat()

    # Convert markdown to simple HTML
    def md_to_html(text: str) -> str:
        text = re.sub(r'\[\[([^\]]+)\]\]', r'<a href="#\1">\1</a>', text)
        text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'^- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
        text = re.sub(r'```.*?\n(.*?)```', r'<pre><code>\1</code></pre>', text, flags=re.DOTALL)
        text = text.replace('\n', '<br>\n')
        return text

    html_parts = [
        '<!DOCTYPE html>',
        '<html><head><meta charset="utf-8">',
        f'<title>Mycelium Export - {today}</title>',
        '<style>body{font-family:system-ui;max-width:800px;margin:0 auto;padding:20px;line-height:1.6}',
        'h1{border-bottom:2px solid #333}h2{color:#2563eb}h3{color:#1d4ed8}',
        'li{margin:4px 0}pre{background:#f5f5f5;padding:10px;border-radius:4px}',
        '.note{margin:20px 0;padding:15px;border:1px solid #ddd;border-radius:8px}',
        'a{color:#2563eb}</style></head><body>',
        f'<h1>🍄 Mycelium Knowledge Base</h1>',
        f'<p>Exported: {today}</p><hr>',
    ]

    type_order = ['sources', 'concepts', 'entities', 'comparisons', 'contradictions', 'questions']

    for note_type in type_order:
        if note_type not in notes:
            continue
        html_parts.append(f'<h2>{note_type.title()}</h2>')
        for note in notes[note_type]:
            html_parts.append(f'<div class="note" id="{note["title"]}">')
            html_parts.append(f'<h3>{note["title"]}</h3>')
            html_parts.append(md_to_html(note['body']))
            html_parts.append('</div>')

    html_parts.append('</body></html>')

    output = output or f"mycelium-export-{today}.html"
    Path(output).write_text('\n'.join(html_parts), encoding='utf-8')
    print(f"✅ Exported to: {output}")


def main():
    parser = argparse.ArgumentParser(description="Export Mycelium wiki")
    parser.add_argument("--dir", "-d", default=".", help="Wiki root directory")
    parser.add_argument("--format", "-f", default="markdown", choices=["markdown", "html"],
                        help="Export format (default: markdown)")
    parser.add_argument("--output", "-o", default=None, help="Output file path")
    args = parser.parse_args()

    if args.format == "html":
        export_html(args.dir, args.output)
    else:
        export_markdown(args.dir, args.output)


if __name__ == "__main__":
    main()
