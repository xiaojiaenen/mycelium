#!/usr/bin/env python3
"""Score source reliability and quality."""
import re
import argparse
from pathlib import Path
from collections import Counter

import sys
sys.path.insert(0, str(Path(__file__).parent))
from utils import parse_frontmatter


# Source type base scores
TYPE_SCORES = {
    "paper": 0.9,
    "book": 0.85,
    "document": 0.7,
    "article": 0.6,
    "webpage": 0.5,
    "transcript": 0.5,
    "subtitle": 0.4,
    "video": 0.4,
    "audio": 0.4,
    "image": 0.3,
}

# Scoring rules
def score_source(filepath: Path, content: str, fm: dict) -> dict:
    """Score a source note on multiple dimensions."""
    scores = {}

    # 1. Source type score
    source_type = fm.get("source_type", "article")
    scores["type"] = TYPE_SCORES.get(source_type, 0.5)

    # 2. Content quality score
    body = content
    word_count = len(body.split())
    has_structure = bool(re.search(r'^## ', body, re.MULTILINE))
    has_citations = bool(re.search(r'>.*—|来源|引用|Source', body))
    has_concepts = bool(re.search(r'\[\[', body))

    scores["structure"] = 0.3 if not has_structure else 0.7
    scores["citations"] = 0.2 if not has_citations else 0.8
    scores["crossref"] = 0.2 if not has_concepts else 0.8
    scores["length"] = min(1.0, word_count / 500)  # 500 words = full score

    # 3. Metadata completeness
    required = ["type", "title", "created", "tags", "status"]
    present = sum(1 for f in required if f in fm)
    scores["metadata"] = present / len(required)

    # 4. Status bonus
    status = fm.get("status", "draft")
    status_scores = {"evergreen": 1.0, "reviewed": 0.8, "developing": 0.6, "draft": 0.4}
    scores["status"] = status_scores.get(status, 0.5)

    # Weighted total
    weights = {"type": 0.2, "structure": 0.15, "citations": 0.15, "crossref": 0.15,
               "length": 0.1, "metadata": 0.1, "status": 0.15}
    total = sum(scores[k] * weights[k] for k in weights)

    return {
        "scores": scores,
        "total": round(total, 2),
        "grade": "A" if total >= 0.8 else "B" if total >= 0.6 else "C" if total >= 0.4 else "D",
    }


def score_sources(wiki_dir: str = ".", top_n: int = 10):
    """Score all sources and show ranking."""
    base = Path(wiki_dir)
    wiki = base / "wiki" / "sources"

    if not wiki.exists():
        print(f"❌ wiki/sources/ not found in {wiki_dir}")
        return

    results = []
    for md_file in wiki.glob('*.md'):
        content = md_file.read_text(encoding='utf-8')
        fm = parse_frontmatter(content)
        result = score_source(md_file, content, fm)
        results.append({
            "file": md_file.name,
            "title": fm.get("title", md_file.stem),
            **result,
        })

    results.sort(key=lambda x: x["total"], reverse=True)

    print(f"📊 Source Quality Scores\n")
    print(f"{'#':>3} {'Grade':>5} {'Score':>6}  {'Title':<40} File")
    print("-" * 80)

    for i, r in enumerate(results[:top_n], 1):
        print(f"{i:>3} {r['grade']:>5} {r['total']:>5.2f}  {r['title'][:38]:<40} {r['file']}")

    if len(results) > top_n:
        print(f"\n... and {len(results) - top_n} more sources")

    # Summary
    grades = Counter(r["grade"] for r in results)
    avg = sum(r["total"] for r in results) / len(results) if results else 0
    print(f"\n📊 Summary: {len(results)} sources | Avg: {avg:.2f} | "
          f"A: {grades.get('A', 0)} | B: {grades.get('B', 0)} | "
          f"C: {grades.get('C', 0)} | D: {grades.get('D', 0)}")


def main():
    parser = argparse.ArgumentParser(description="Score source reliability")
    parser.add_argument("--dir", "-d", default=".", help="Wiki root directory")
    parser.add_argument("--top", "-n", type=int, default=10, help="Show top N results")
    args = parser.parse_args()
    score_sources(args.dir, args.top)


if __name__ == "__main__":
    main()
