#!/usr/bin/env python3
"""Lint Mycelium wiki: check orphans, broken links, stale notes, frontmatter."""
import re
import argparse
from pathlib import Path
from datetime import datetime, timedelta


def parse_frontmatter(content: str) -> dict:
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, _, val = line.partition(':')
            val = val.strip().strip('"').strip("'")
            if val.startswith('[') and val.endswith(']'):
                val = [v.strip().strip('"').strip("'") for v in val[1:-1].split(',') if v.strip()]
            fm[key.strip()] = val
    return fm


def extract_wikilinks(content: str) -> set:
    return set(re.findall(r'\[\[([^\]]+)\]\]', content))


def find_note_path(wiki_dir: Path, name: str) -> Path | None:
    for subdir in ['sources', 'concepts', 'entities', 'comparisons', 'questions', 'contradictions']:
        candidate = wiki_dir / subdir / f"{name}.md"
        if candidate.exists():
            return candidate
    # Try slugified
    slug = name.lower().replace(' ', '-').replace('_', '-')
    for subdir in ['sources', 'concepts', 'entities', 'comparisons', 'questions', 'contradictions']:
        candidate = wiki_dir / subdir / f"{slug}.md"
        if candidate.exists():
            return candidate
    return None


def lint(wiki_dir: str = ".", deep: bool = False):
    base = Path(wiki_dir)
    wiki = base / "wiki"

    if not wiki.exists():
        print(f"❌ wiki/ not found in {wiki_dir}")
        return

    issues = {"orphans": [], "broken_links": [], "stale": [], "frontmatter": [], "weak": []}

    # Collect all notes and their links
    all_notes = {}
    all_links = {}  # file -> set of links it contains
    inbound_links = {}  # note_name -> set of files linking to it

    for subdir in ['sources', 'concepts', 'entities', 'comparisons', 'questions', 'contradictions']:
        dir_path = wiki / subdir
        if not dir_path.exists():
            continue
        for md_file in dir_path.glob('*.md'):
            content = md_file.read_text(encoding='utf-8')
            fm = parse_frontmatter(content)
            name = md_file.stem
            all_notes[name] = {"path": md_file, "frontmatter": fm, "subdir": subdir}
            links = extract_wikilinks(content)
            all_links[md_file] = links
            for link in links:
                if link not in inbound_links:
                    inbound_links[link] = set()
                inbound_links[link].add(md_file)

    # Check 1: Orphan pages (no inbound links)
    for name, info in all_notes.items():
        if name not in inbound_links and info["subdir"] != "sources":
            # Sources are often orphans (they're entry points)
            issues["orphans"].append(info["path"])

    # Check 2: Broken links
    for md_file, links in all_links.items():
        for link in links:
            if find_note_path(wiki, link) is None:
                issues["broken_links"].append((md_file, link))

    # Check 3: Stale notes (draft > 30 days)
    today = datetime.now()
    for name, info in all_notes.items():
        fm = info["frontmatter"]
        status = fm.get("status", "")
        created = fm.get("created", "")
        if status == "draft" and created:
            try:
                created_date = datetime.strptime(created, "%Y-%m-%d")
                if (today - created_date).days > 30:
                    issues["stale"].append(info["path"])
            except ValueError:
                pass

    # Check 4: Frontmatter completeness
    required_fields = ["type", "title", "created", "tags", "status"]
    for name, info in all_notes.items():
        fm = info["frontmatter"]
        missing = [f for f in required_fields if f not in fm]
        if missing:
            issues["frontmatter"].append((info["path"], missing))

    # Deep checks
    if deep:
        # Check 5: Weak evidence (only 1 source)
        for name, info in all_notes.items():
            if info["subdir"] == "concepts":
                fm = info["frontmatter"]
                strength = fm.get("evidence_strength", "")
                if strength == "weak":
                    issues["weak"].append(info["path"])

    # Report
    total_issues = sum(len(v) for v in issues.values())

    if total_issues == 0:
        print("✅ Wiki is healthy! No issues found.")
        return

    print(f"📊 Lint Report: {total_issues} issue(s) found\n")

    if issues["orphans"]:
        print(f"🔗 Orphan Pages ({len(issues['orphans'])})")
        for p in issues["orphans"]:
            print(f"   {p.relative_to(base)}")
        print()

    if issues["broken_links"]:
        print(f"❌ Broken Links ({len(issues['broken_links'])})")
        for p, link in issues["broken_links"]:
            print(f"   {p.relative_to(base)} → [[{link}]]")
        print()

    if issues["stale"]:
        print(f"⏰ Stale Notes ({len(issues['stale'])})")
        for p in issues["stale"]:
            print(f"   {p.relative_to(base)} (draft > 30 days)")
        print()

    if issues["frontmatter"]:
        print(f"📋 Frontmatter Issues ({len(issues['frontmatter'])})")
        for p, missing in issues["frontmatter"]:
            print(f"   {p.relative_to(base)} — missing: {', '.join(missing)}")
        print()

    if deep and issues["weak"]:
        print(f"⚠️  Weak Evidence ({len(issues['weak'])})")
        for p in issues["weak"]:
            print(f"   {p.relative_to(base)} (evidence_strength: weak)")
        print()


def main():
    parser = argparse.ArgumentParser(description="Lint Mycelium wiki")
    parser.add_argument("--dir", "-d", default=".", help="Wiki root directory")
    parser.add_argument("--deep", action="store_true", help="Deep lint (weak evidence, etc.)")
    args = parser.parse_args()
    lint(args.dir, args.deep)


if __name__ == "__main__":
    main()
