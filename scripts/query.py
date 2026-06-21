#!/usr/bin/env python3
"""
Query helper for Mycelium.
Reads index, finds relevant pages, returns context for LLM synthesis.
"""
import re
import argparse
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
from utils import parse_frontmatter, extract_wikilinks


def query(wiki_dir: str, question: str):
    """Find relevant pages for a question."""
    base = Path(wiki_dir)
    wiki = base / "wiki"

    if not wiki.exists():
        print(f"❌ wiki/ not found in {wiki_dir}")
        return

    # Read index first
    index_path = wiki / "index.md"
    if index_path.exists():
        print("📖 Reading index.md...")
        index_content = index_path.read_text(encoding='utf-8')
        # Extract all wikilinks from index
        index_links = extract_wikilinks(index_content)
        print(f"   Found {len(index_links)} pages in index")
    else:
        index_links = set()

    # Find pages matching question keywords
    keywords = set(question.lower().split())
    # Also check Chinese characters individually
    chinese_chars = set(re.findall(r'[一-鿿]', question))
    keywords.update(chinese_chars)

    matches = []
    for subdir in ['concepts', 'sources', 'entities', 'comparisons', 'questions', 'contradictions']:
        dir_path = wiki / subdir
        if not dir_path.exists():
            continue
        for md_file in dir_path.glob('*.md'):
            content = md_file.read_text(encoding='utf-8')
            fm = parse_frontmatter(content)
            title = fm.get('title', md_file.stem).lower()
            body_lower = content.lower()

            # Score: title match > body match
            score = 0
            for kw in keywords:
                if kw in title:
                    score += 10
                if kw in body_lower:
                    score += 1

            if score > 0:
                matches.append({
                    "path": md_file,
                    "title": fm.get('title', md_file.stem),
                    "type": fm.get('type', subdir.rstrip('s')),
                    "score": score,
                    "excerpt": content[:200],
                })

    # Sort by score
    matches.sort(key=lambda x: x["score"], reverse=True)

    if not matches:
        print(f"\n❌ No relevant pages found for: {question}")
        print(f"   Try: ingest some sources first")
        return

    # Show top matches
    top = matches[:10]
    print(f"\n🔍 Found {len(matches)} relevant pages (showing top {len(top)}):\n")

    for i, m in enumerate(top, 1):
        print(f"{i}. [{m['type']}] {m['title']} (score: {m['score']})")
        # Show first 100 chars of excerpt
        excerpt = m['excerpt'].replace('\n', ' ')[:100]
        print(f"   {excerpt}...")
        print()

    # Suggest what to read
    print("💡 Suggested: Ask Claude to read these pages and synthesize an answer.")


def main():
    parser = argparse.ArgumentParser(description="Query Mycelium wiki")
    parser.add_argument("question", help="Question to search for")
    parser.add_argument("--dir", "-d", default=".", help="Wiki root directory")
    args = parser.parse_args()
    query(args.dir, args.question)


if __name__ == "__main__":
    main()
