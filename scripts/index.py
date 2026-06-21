#!/usr/bin/env python3
"""Rebuild wiki indexes: index-tags.md and index-topics.md."""
import argparse
from pathlib import Path
from collections import defaultdict

import sys
sys.path.insert(0, str(Path(__file__).parent))
from utils import TODAY, parse_frontmatter, extract_wikilinks


def rebuild_tags_index(wiki_dir: Path):
    """Build index-tags.md from note frontmatter tags."""
    tag_notes = defaultdict(list)

    for subdir in ['sources', 'concepts', 'entities', 'comparisons', 'questions', 'contradictions']:
        dir_path = wiki_dir / subdir
        if not dir_path.exists():
            continue
        for md_file in dir_path.glob('*.md'):
            content = md_file.read_text(encoding='utf-8')
            fm = parse_frontmatter(content)
            tags = fm.get('tags', [])
            if isinstance(tags, str):
                tags = [tags]
            title = fm.get('title', md_file.stem)
            for tag in tags:
                tag_notes[tag].append(f"[[{md_file.stem}]]")

    lines = [
        "---",
        "type: meta",
        'title: "Tag Index"',
        f"created: {TODAY}",
        "tags:",
        "  - meta",
        "  - index",
        "  - tags",
        "status: evergreen",
        "---",
        "",
        "# Tag Index",
        "",
        f"Last updated: {TODAY}",
        "",
        "---",
        "",
        "## Tags",
        "",
    ]

    for tag in sorted(tag_notes.keys()):
        notes = sorted(tag_notes[tag])
        lines.append(f"### {tag} ({len(notes)})")
        for n in notes:
            lines.append(f"- {n}")
        lines.append("")

    output = wiki_dir / "index-tags.md"
    output.write_text('\n'.join(lines), encoding='utf-8')
    print(f"✅ Rebuilt index-tags.md ({len(tag_notes)} tags)")


def rebuild_topics_index(wiki_dir: Path):
    """Build index-topics.md from wikilink density (simple clustering)."""
    # Build link graph
    notes = {}
    for subdir in ['sources', 'concepts', 'entities', 'comparisons', 'questions', 'contradictions']:
        dir_path = wiki_dir / subdir
        if not dir_path.exists():
            continue
        for md_file in dir_path.glob('*.md'):
            content = md_file.read_text(encoding='utf-8')
            fm = parse_frontmatter(content)
            links = extract_wikilinks(content)
            notes[md_file.stem] = {"fm": fm, "links": links, "subdir": subdir}

    # Simple clustering: group notes that share the most links
    # Use connected components approach
    visited = set()
    clusters = []

    def bfs(start):
        cluster = set()
        queue = [start]
        while queue:
            node = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            cluster.add(node)
            # Add neighbors (notes this one links to, or that link to it)
            if node in notes:
                for link in notes[node]["links"]:
                    if link in notes and link not in visited:
                        queue.append(link)
                # Also check reverse links
                for other, info in notes.items():
                    if node in info["links"] and other not in visited:
                        queue.append(other)
        return cluster

    for name in notes:
        if name not in visited:
            cluster = bfs(name)
            if len(cluster) > 1:  # Only show multi-note clusters
                clusters.append(cluster)

    # Sort clusters by size (largest first)
    clusters.sort(key=len, reverse=True)

    lines = [
        "---",
        "type: meta",
        'title: "Topic Clusters"',
        f"created: {TODAY}",
        "tags:",
        "  - meta",
        "  - index",
        "  - topics",
        "status: evergreen",
        "---",
        "",
        "# Topic Clusters",
        "",
        f"Last updated: {TODAY}",
        "",
        "---",
        "",
        "## Clusters",
        "",
    ]

    if not clusters:
        lines.append("No topic clusters found. Add more notes with [[wikilinks]] to create clusters.")
    else:
        for i, cluster in enumerate(clusters, 1):
            # Pick a name from the most connected note
            best = max(cluster, key=lambda n: len(notes.get(n, {}).get("links", [])))
            lines.append(f"### Cluster {i}: {best} ({len(cluster)} notes)")
            for name in sorted(cluster):
                subdir = notes[name]["subdir"]
                lines.append(f"- [[{name}]] ({subdir})")
            lines.append("")

    output = wiki_dir / "index-topics.md"
    output.write_text('\n'.join(lines), encoding='utf-8')
    print(f"✅ Rebuilt index-topics.md ({len(clusters)} clusters)")


def main():
    parser = argparse.ArgumentParser(description="Rebuild wiki indexes")
    parser.add_argument("--dir", "-d", default=".", help="Wiki root directory")
    parser.add_argument("--tags-only", action="store_true", help="Only rebuild tags index")
    parser.add_argument("--topics-only", action="store_true", help="Only rebuild topics index")
    args = parser.parse_args()

    wiki = Path(args.dir) / "wiki"
    if not wiki.exists():
        print(f"❌ wiki/ not found in {args.dir}")
        return

    if args.topics_only:
        rebuild_topics_index(wiki)
    elif args.tags_only:
        rebuild_tags_index(wiki)
    else:
        rebuild_tags_index(wiki)
        rebuild_topics_index(wiki)


if __name__ == "__main__":
    main()
