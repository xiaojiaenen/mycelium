#!/usr/bin/env python3
"""Export Mycelium wiki to various formats."""
import re
import argparse
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
from utils import TODAY, TYPE_EMOJI, parse_frontmatter_with_body, WIKI_SUBDIRS


def collect_notes(wiki_dir: Path) -> dict:
    """Collect all notes grouped by type."""
    notes = {}
    for subdir in WIKI_SUBDIRS:
        dir_path = wiki_dir / subdir
        if not dir_path.exists():
            continue
        for md_file in sorted(dir_path.glob('*.md')):
            content = md_file.read_text(encoding='utf-8')
            fm, body = parse_frontmatter_with_body(content)
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

    lines = [
        f"# Mycelium Knowledge Base",
        f"",
        f"Exported: {TODAY}",
        f"",
        f"---",
        f"",
    ]

    type_order = ['source', 'concept', 'entity', 'comparison', 'contradiction', 'question']
    type_names = {
        'source': '📚 Sources',
        'concept': '💡 Concepts',
        'entity': '👤 Entities',
        'comparison': '⚖️ Comparisons',
        'contradiction': '⚡ Contradictions',
        'question': '❓ Questions',
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

    output = output or f"mycelium-export-{TODAY}.md"
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

    # Convert markdown to simple HTML
    def md_to_html(text: str) -> str:
        # Handle code blocks first to protect their content
        code_blocks = []
        def save_code(m):
            code_blocks.append(m.group(0))
            return f'__CODE_BLOCK_{len(code_blocks)-1}__'
        text = re.sub(r'```.*?\n(.*?)```', save_code, text, flags=re.DOTALL)

        # Handle inline elements
        text = re.sub(r'\[\[([^\]]+)\]\]', r'<a href="#\1">\1</a>', text)
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)

        # Handle block elements
        text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)

        # Handle lists
        lines = text.split('\n')
        in_list = False
        result = []
        for line in lines:
            if line.startswith('- '):
                if not in_list:
                    result.append('<ul>')
                    in_list = True
                result.append(f'<li>{line[2:]}</li>')
            else:
                if in_list:
                    result.append('</ul>')
                    in_list = False
                result.append(line)
        if in_list:
            result.append('</ul>')
        text = '\n'.join(result)

        # Restore code blocks
        for i, block in enumerate(code_blocks):
            text = text.replace(f'__CODE_BLOCK_{i}__', f'<pre><code>{block}</code></pre>')

        # Handle paragraphs (convert double newlines)
        text = re.sub(r'\n\n+', '</p><p>', text)
        text = f'<p>{text}</p>'
        text = text.replace('<p></p>', '')

        return text

    html_parts = [
        '<!DOCTYPE html>',
        '<html><head><meta charset="utf-8">',
        f'<title>Mycelium Export - {TODAY}</title>',
        '<style>',
        'body{font-family:system-ui,-apple-system,sans-serif;max-width:900px;margin:0 auto;padding:40px 20px;line-height:1.8;color:#1a1a1a;background:#fafafa}',
        'h1{border-bottom:3px solid #2563eb;padding-bottom:12px;color:#1e1e1e}',
        'h2{color:#2563eb;margin-top:2em}',
        'h3{color:#1d4ed8}',
        'ul{padding-left:1.5em}li{margin:6px 0}',
        'pre{background:#1e1e1e;color:#e9ecef;padding:16px;border-radius:8px;overflow-x:auto}',
        'code{font-family:monospace;font-size:0.9em}',
        '.note{margin:24px 0;padding:20px;background:#fff;border:1px solid #e5e7eb;border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,0.05)}',
        'a{color:#2563eb;text-decoration:none}a:hover{text-decoration:underline}',
        'p{margin:0.8em 0}',
        '</style></head><body>',
        f'<h1>🍄 Mycelium Knowledge Base</h1>',
        f'<p style="color:#6b7280">Exported: {TODAY}</p><hr>',
    ]

    type_order = ['source', 'concept', 'entity', 'comparison', 'contradiction', 'question']
    type_emoji = {'source': '📚', 'concept': '💡', 'entity': '👤', 'comparison': '⚖️', 'contradiction': '⚡', 'question': '❓'}

    for note_type in type_order:
        if note_type not in notes:
            continue
        emoji = type_emoji.get(note_type, '📄')
        html_parts.append(f'<h2>{emoji} {note_type.title()}s</h2>')
        for note in notes[note_type]:
            html_parts.append(f'<div class="note" id="{note["title"]}">')
            html_parts.append(f'<h3>{note["title"]}</h3>')
            html_parts.append(md_to_html(note['body']))
            html_parts.append('</div>')

    html_parts.append('</body></html>')

    output = output or f"mycelium-export-{TODAY}.html"
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
