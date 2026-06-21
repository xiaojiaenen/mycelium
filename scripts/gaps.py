#!/usr/bin/env python3
"""Detect knowledge gaps in Mycelium wiki."""
import re
import argparse
from pathlib import Path
from collections import defaultdict

import sys
sys.path.insert(0, str(Path(__file__).parent))
from utils import parse_frontmatter, extract_wikilinks


def detect_gaps(wiki_dir: str = "."):
    """Find knowledge gaps: undefined concepts, weak areas, missing connections."""
    base = Path(wiki_dir)
    wiki = base / "wiki"

    if not wiki.exists():
        print(f"❌ wiki/ not found in {wiki_dir}")
        return

    # Collect all notes and links
    notes = {}
    all_defined = set()
    all_referenced = defaultdict(list)

    for subdir in ['sources', 'concepts', 'entities', 'comparisons', 'questions', 'contradictions']:
        dir_path = wiki / subdir
        if not dir_path.exists():
            continue
        for md_file in dir_path.glob('*.md'):
            content = md_file.read_text(encoding='utf-8')
            fm = parse_frontmatter(content)
            name = md_file.stem
            links = extract_wikilinks(content)
            notes[name] = {"path": md_file, "fm": fm, "links": links, "subdir": subdir}
            all_defined.add(name)
            for link in links:
                all_referenced[link].append(name)

    # Gap 1: Referenced but undefined concepts
    undefined = []
    for ref, sources in all_referenced.items():
        if ref not in all_defined:
            undefined.append({"name": ref, "referenced_by": sources})

    # Gap 2: Single-source concepts (only one source supports them)
    single_source = []
    for name, info in notes.items():
        if info["subdir"] == "concepts":
            # Count sources linking to this concept
            source_count = sum(1 for s in info["links"]
                             if notes.get(s, {}).get("subdir") == "sources")
            if source_count <= 1:
                fm = info["fm"]
                strength = fm.get("evidence_strength", "unknown")
                if strength in ("weak", "unknown"):
                    single_source.append({
                        "name": name,
                        "sources": source_count,
                        "strength": strength,
                    })

    # Gap 3: Orphan concepts (no inbound links from other concepts)
    orphans = []
    for name, info in notes.items():
        if info["subdir"] == "concepts":
            inbound_concepts = [s for s in all_referenced.get(name, [])
                              if notes.get(s, {}).get("subdir") in ("concepts", "sources")]
            if len(inbound_concepts) == 0:
                orphans.append(name)

    # Gap 4: Concepts with no outbound links
    disconnected = []
    for name, info in notes.items():
        if info["subdir"] == "concepts" and len(info["links"]) == 0:
            disconnected.append(name)

    # Gap 5: Topics with few concepts
    tag_concepts = defaultdict(list)
    for name, info in notes.items():
        if info["subdir"] == "concepts":
            tags = info["fm"].get("tags", [])
            if isinstance(tags, str):
                tags = [tags]
            for tag in tags:
                tag_concepts[tag].append(name)

    thin_topics = {t: cs for t, cs in tag_concepts.items() if len(cs) == 1}

    # Report
    total_gaps = len(undefined) + len(single_source) + len(orphans) + len(disconnected)

    if total_gaps == 0:
        print("✅ No knowledge gaps found!")
        return

    print(f"📊 Knowledge Gap Report: {total_gaps} gap(s)\n")

    if undefined:
        print(f"🔗 Referenced but Undefined ({len(undefined)})")
        print(f"   These concepts are mentioned but have no page:\n")
        for g in undefined[:10]:
            refs = ', '.join(f'[[{s}]]' for s in g['referenced_by'][:3])
            print(f"   ❓ [[{g['name']}]] — referenced by {refs}")
        if len(undefined) > 10:
            print(f"   ... and {len(undefined) - 10} more")
        print()

    if single_source:
        print(f"⚠️  Weak Evidence ({len(single_source)})")
        print(f"   These concepts have only 1 source:\n")
        for g in single_source[:10]:
            print(f"   📄 [[{g['name']}]] — {g['sources']} source(s)")
        if len(single_source) > 10:
            print(f"   ... and {len(single_source) - 10} more")
        print()

    if orphans:
        print(f"🏝️  Orphan Concepts ({len(orphans)})")
        print(f"   These concepts have no links from other concepts/sources:\n")
        for name in orphans[:10]:
            print(f"   🔗 [[{name}]]")
        if len(orphans) > 10:
            print(f"   ... and {len(orphans) - 10} more")
        print()

    if disconnected:
        print(f"🔌 Disconnected ({len(disconnected)})")
        print(f"   These concepts don't link to anything:\n")
        for name in disconnected[:10]:
            print(f"   🔗 [[{name}]]")
        print()

    # Suggestions
    print("💡 Suggestions:")
    if undefined:
        names = ', '.join('[[{}]]'.format(g['name']) for g in undefined[:3])
        print(f"   - Create pages for: {names}")
    if single_source:
        names = ', '.join('[[{}]]'.format(g['name']) for g in single_source[:3])
        print(f"   - Find more sources for: {names}")
    if orphans:
        names = ', '.join('[[{}]]'.format(n) for n in orphans[:3])
        print(f"   - Add cross-references to: {names}")


def main():
    parser = argparse.ArgumentParser(description="Detect knowledge gaps")
    parser.add_argument("--dir", "-d", default=".", help="Wiki root directory")
    args = parser.parse_args()
    detect_gaps(args.dir)


if __name__ == "__main__":
    main()
