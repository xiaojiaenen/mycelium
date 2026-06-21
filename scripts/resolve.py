#!/usr/bin/env python3
"""
Contradiction resolution workflow.
Guides through resolving contradictions found in the wiki.
"""
import re
import argparse
from pathlib import Path
from datetime import date

import sys
sys.path.insert(0, str(Path(__file__).parent))
from utils import parse_frontmatter, TODAY


def list_contradictions(wiki_dir: str = "."):
    """List all unresolved contradictions."""
    base = Path(wiki_dir)
    wiki = base / "wiki" / "contradictions"

    if not wiki.exists():
        print("✅ No contradictions found.")
        return []

    contradictions = []
    for md_file in wiki.glob('*.md'):
        content = md_file.read_text(encoding='utf-8')
        fm = parse_frontmatter(content)
        status = fm.get('status', 'unresolved')

        if status == 'unresolved':
            contradictions.append({
                "file": md_file.name,
                "title": fm.get('title', md_file.stem),
                "severity": fm.get('severity', 'unknown'),
                "content": content,
            })

    if not contradictions:
        print("✅ All contradictions resolved!")
        return []

    print(f"⚡ Unresolved Contradictions: {len(contradictions)}\n")
    for i, c in enumerate(contradictions, 1):
        print(f"{i}. {c['title']} (severity: {c['severity']})")
        print(f"   File: {c['file']}")

        # Extract stance descriptions
        stance_a = re.search(r'## 立场 A.*?\n(.*?)(?=\n## |\Z)', c['content'], re.DOTALL)
        stance_b = re.search(r'## 立场 B.*?\n(.*?)(?=\n## |\Z)', c['content'], re.DOTALL)
        if stance_a:
            print(f"   A: {stance_a.group(1).strip()[:80]}...")
        if stance_b:
            print(f"   B: {stance_b.group(1).strip()[:80]}...")
        print()

    return contradictions


def resolve(wiki_dir: str, filename: str, resolution: str, notes: str = ""):
    """Mark a contradiction as resolved."""
    base = Path(wiki_dir)
    filepath = base / "wiki" / "contradictions" / filename

    if not filepath.exists():
        print(f"❌ Not found: {filename}")
        return

    content = filepath.read_text(encoding='utf-8')
    fm = parse_frontmatter(content)

    # Update frontmatter
    content = re.sub(
        r'status: unresolved',
        'status: resolved',
        content
    )

    # Add resolution section
    resolution_section = f"""

---

## Resolution

**Date:** {TODAY}
**Resolution:** {resolution}
**Notes:** {notes}

"""
    content = content.rstrip() + resolution_section

    filepath.write_text(content, encoding='utf-8')
    print(f"✅ Resolved: {filename}")
    print(f"   Resolution: {resolution}")


def main():
    parser = argparse.ArgumentParser(description="Contradiction resolution workflow")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List unresolved contradictions")

    resolve_p = sub.add_parser("resolve", help="Mark contradiction as resolved")
    resolve_p.add_argument("file", help="Contradiction filename")
    resolve_p.add_argument("--resolution", "-r", required=True, help="Resolution description")
    resolve_p.add_argument("--notes", "-n", default="", help="Additional notes")

    parser.add_argument("--dir", "-d", default=".", help="Wiki root directory")

    args = parser.parse_args()

    if args.command == "resolve":
        resolve(args.dir, args.file, args.resolution, args.notes)
    else:
        list_contradictions(args.dir)


if __name__ == "__main__":
    main()
