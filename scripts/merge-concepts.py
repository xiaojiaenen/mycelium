#!/usr/bin/env python3
"""
Merge or split concept notes in Mycelium.

Usage:
    # Merge two concepts into one
    python3 scripts/merge-concepts.py merge "concept-a" "concept-b" --keep "concept-a"

    # Split a concept into two
    python3 scripts/merge-concepts.py split "concept-name" --into "new-a,new-b"

    # Preview changes without modifying files
    python3 scripts/merge-concepts.py merge "concept-a" "concept-b" --keep "concept-a" --dry-run
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import parse_frontmatter_with_body, title_from_slug, slugify


def build_frontmatter(fm: dict) -> str:
    """Build YAML frontmatter string."""
    lines = ['---']
    for key, val in fm.items():
        if isinstance(val, list):
            items = ', '.join(str(v) for v in val)
            lines.append(f'{key}: [{items}]')
        else:
            lines.append(f'{key}: {val}')
    lines.append('---')
    return '\n'.join(lines)


def find_concept(wiki_dir: str, name: str) -> Path | None:
    """Find a concept file by name (with or without .md extension)."""
    wiki_path = Path(wiki_dir) / 'wiki' / 'concepts'
    # Try exact match
    candidate = wiki_path / f"{name}.md"
    if candidate.exists():
        return candidate
    # Try slugified
    slug = slugify(name)
    candidate = wiki_path / f"{slug}.md"
    if candidate.exists():
        return candidate
    # Try partial match
    for f in wiki_path.glob('*.md'):
        if slug in f.stem.lower():
            return f
    return None


def update_wikilinks(wiki_dir: str, old_name: str, new_name: str, dry_run: bool = False) -> int:
    """Replace [[old_name]] with [[new_name]] across all wiki pages."""
    wiki_path = Path(wiki_dir) / 'wiki'
    count = 0
    changes = []
    for md_file in wiki_path.rglob('*.md'):
        content = md_file.read_text(encoding='utf-8')
        if f'[[{old_name}]]' in content:
            if not dry_run:
                content = content.replace(f'[[{old_name}]]', f'[[{new_name}]]')
                md_file.write_text(content, encoding='utf-8')
            changes.append(str(md_file))
            count += 1
    return count


def merge_concepts(wiki_dir: str, name_a: str, name_b: str, keep: str, dry_run: bool = False):
    """Merge two concepts into one."""
    path_a = find_concept(wiki_dir, name_a)
    path_b = find_concept(wiki_dir, name_b)

    if not path_a:
        print(f"❌ Concept not found: {name_a}")
        sys.exit(1)
    if not path_b:
        print(f"❌ Concept not found: {name_b}")
        sys.exit(1)

    print(f"📄 Concept A: {path_a}")
    print(f"📄 Concept B: {path_b}")

    if dry_run:
        print("\n🔍 DRY RUN - No files will be modified\n")

    # Read both
    content_a = path_a.read_text(encoding='utf-8')
    content_b = path_b.read_text(encoding='utf-8')
    fm_a, body_a = parse_frontmatter_with_body(content_a)
    fm_b, body_b = parse_frontmatter_with_body(content_b)

    # Determine which to keep (compare by slug for robustness)
    keep_slug = slugify(keep)
    a_slug = slugify(name_a)
    b_slug = slugify(name_b)

    if keep_slug == a_slug or keep in (name_a, path_a.stem):
        primary, secondary = path_a, path_b
        fm_pri, body_pri = fm_a, body_a
        fm_sec, body_sec = fm_b, body_b
        name_pri, name_sec = name_a, name_b
    elif keep_slug == b_slug or keep in (name_b, path_b.stem):
        primary, secondary = path_b, path_a
        fm_pri, body_pri = fm_b, body_b
        fm_sec, body_sec = fm_a, body_a
        name_pri, name_sec = name_b, name_a
    else:
        print(f"❌ --keep value '{keep}' doesn't match either concept")
        print(f"   Concept A: {name_a} (slug: {a_slug})")
        print(f"   Concept B: {name_b} (slug: {b_slug})")
        sys.exit(1)

    # Merge frontmatter
    fm_pri['updated'] = fm_pri.get('created', '')
    fm_pri['version'] = str(int(fm_pri.get('version', '1')) + 1)

    # Merge supersedes
    supersedes = fm_pri.get('supersedes', [])
    if isinstance(supersedes, str):
        supersedes = [supersedes]
    supersedes.append(name_sec)
    fm_pri['supersedes'] = list(set(supersedes))

    # Merge aliases
    aliases = fm_pri.get('aliases', [])
    if isinstance(aliases, str):
        aliases = [aliases]
    aliases.append(name_sec)
    if fm_sec.get('aliases'):
        sec_aliases = fm_sec['aliases']
        if isinstance(sec_aliases, str):
            sec_aliases = [sec_aliases]
        aliases.extend(sec_aliases)
    fm_pri['aliases'] = list(set(aliases))

    # Merge tags
    tags = fm_pri.get('tags', [])
    if isinstance(tags, str):
        tags = [tags]
    sec_tags = fm_sec.get('tags', [])
    if isinstance(sec_tags, str):
        sec_tags = [sec_tags]
    tags.extend(sec_tags)
    fm_pri['tags'] = list(set(tags))

    # Build merged body
    merged_body = body_pri.rstrip()
    merged_body += f"\n\n---\n\n> Merged from [[{name_sec}]]. Key content has been integrated above.\n"

    # Write merged file
    merged_content = build_frontmatter(fm_pri) + '\n\n' + merged_body

    if dry_run:
        print(f"📝 Would write to: {primary}")
        print(f"   Version: {fm_pri['version']}")
        print(f"   Supersedes: {fm_pri['supersedes']}")
        print(f"   Aliases: {fm_pri['aliases']}")
    else:
        primary.write_text(merged_content, encoding='utf-8')
        print(f"✅ Merged into: {primary}")

    # Delete secondary
    if dry_run:
        print(f"🗑️  Would delete: {secondary}")
    else:
        secondary.unlink()
        print(f"🗑️  Deleted: {secondary}")

    # Update wikilinks across wiki
    count = update_wikilinks(wiki_dir, name_sec, name_pri, dry_run)
    if dry_run:
        print(f"🔗 Would update {count} files: [[{name_sec}]] → [[{name_pri}]]")
    else:
        print(f"🔗 Updated {count} files: [[{name_sec}]] → [[{name_pri}]]")

    # Update index
    index_path = Path(wiki_dir) / 'wiki' / 'index.md'
    if index_path.exists():
        index_content = index_path.read_text(encoding='utf-8')
        if name_sec in index_content:
            if dry_run:
                print(f"📋 Would update index.md")
            else:
                index_content = index_content.replace(name_sec, name_pri)
                index_path.write_text(index_content, encoding='utf-8')
                print("📋 Updated index.md")

    if dry_run:
        print(f"\n🔍 DRY RUN complete - no changes made")
    else:
        print(f"\n✅ Merge complete: [[{name_sec}]] → [[{name_pri}]]")


def split_concept(wiki_dir: str, name: str, into: list[str], dry_run: bool = False):
    """Split a concept into multiple new concepts."""
    path = find_concept(wiki_dir, name)
    if not path:
        print(f"❌ Concept not found: {name}")
        sys.exit(1)

    print(f"📄 Splitting: {path}")

    if dry_run:
        print("\n🔍 DRY RUN - No files will be modified\n")

    content = path.read_text(encoding='utf-8')
    fm, body = parse_frontmatter_with_body(content)

    # Split body by ## headings
    sections = re.split(r'\n(?=## )', body)

    if len(into) > len(sections):
        print(f"⚠️  Warning: {len(into)} target names but only {len(sections)} sections found")
        print(f"   Extra names will get the full content as fallback")

    wiki_path = Path(wiki_dir) / 'wiki' / 'concepts'

    for i, new_name in enumerate(into):
        # Determine content for this split
        if i < len(sections):
            split_body = sections[i].strip()
        else:
            split_body = body.strip()

        # Create new frontmatter
        new_fm = fm.copy()
        new_fm['title'] = title_from_slug(new_name)
        new_fm['version'] = '1'
        new_fm['supersedes'] = [name]
        new_fm['aliases'] = [name]

        slug = slugify(new_name)
        new_path = wiki_path / f"{slug}.md"

        new_content = build_frontmatter(new_fm) + '\n\n' + split_body

        if dry_run:
            print(f"  📝 Would create: {new_path}")
        else:
            new_path.write_text(new_content, encoding='utf-8')
            print(f"  ✅ Created: {new_path}")

    # Mark original as superseded
    fm['status'] = 'superseded'
    fm['superseded_by'] = into
    updated_content = build_frontmatter(fm) + '\n\n' + body

    if dry_run:
        print(f"  📝 Would mark original as superseded: {path}")
    else:
        path.write_text(updated_content, encoding='utf-8')
        print(f"  📝 Marked original as superseded: {path}")

    # Update wikilinks - use new_name (not slug) for wikilinks
    for new_name in into:
        count = update_wikilinks(wiki_dir, name, new_name, dry_run)
        if dry_run:
            print(f"  🔗 Would update {count} files: [[{name}]] → [[{new_name}]]")
        else:
            print(f"  🔗 Updated {count} files: [[{name}]] → [[{new_name}]]")

    if dry_run:
        print(f"\n🔍 DRY RUN complete - no changes made")
    else:
        print(f"\n✅ Split complete: [[{name}]] → {', '.join(f'[[{n}]]' for n in into)}")


def main():
    parser = argparse.ArgumentParser(description='Merge or split concept notes')
    parser.add_argument('--wiki-dir', default='.', help='Wiki root directory (default: .)')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without modifying files')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Merge command
    merge_parser = subparsers.add_parser('merge', help='Merge two concepts')
    merge_parser.add_argument('concept_a', help='First concept name')
    merge_parser.add_argument('concept_b', help='Second concept name')
    merge_parser.add_argument('--keep', required=True, help='Which concept to keep')

    # Split command
    split_parser = subparsers.add_parser('split', help='Split a concept into two')
    split_parser.add_argument('concept', help='Concept to split')
    split_parser.add_argument('--into', required=True, help='Comma-separated new names')

    args = parser.parse_args()

    if args.command == 'merge':
        merge_concepts(args.wiki_dir, args.concept_a, args.concept_b, args.keep, args.dry_run)
    elif args.command == 'split':
        into = [n.strip() for n in args.into.split(',')]
        split_concept(args.wiki_dir, args.concept, into, args.dry_run)


if __name__ == '__main__':
    main()
