#!/usr/bin/env python3
"""
Semantic search using sentence-transformers (optional dependency).
Default mode: disabled. Use --enable to activate.

Usage:
    python3 scripts/semantic.py "attention mechanism" --wiki-dir .
    python3 scripts/semantic.py "RLHF" --enable --top 5
"""
import re
import json
import argparse
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
from utils import parse_frontmatter


def check_deps() -> bool:
    """Check if sentence-transformers is available."""
    try:
        import sentence_transformers
        return True
    except ImportError:
        return False


def load_model():
    """Load sentence-transformers model."""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer('all-MiniLM-L6-v2')  # 80MB, fast


def load_pages(wiki_dir: Path) -> list:
    """Load all wiki pages."""
    pages = []
    wiki = wiki_dir / "wiki"

    for subdir in ['sources', 'concepts', 'entities', 'comparisons', 'questions', 'contradictions']:
        dir_path = wiki / subdir
        if not dir_path.exists():
            continue
        for md_file in dir_path.glob('*.md'):
            content = md_file.read_text(encoding='utf-8')
            fm = parse_frontmatter(content)

            # Extract text (skip frontmatter)
            body = re.sub(r'^---.*?---\n?', '', content, flags=re.DOTALL).strip()

            pages.append({
                "path": str(md_file.relative_to(wiki_dir)),
                "title": fm.get('title', md_file.stem),
                "type": fm.get('type', subdir.rstrip('s')),
                "text": body[:1000],  # Truncate for embedding
                "file": md_file.name,
            })

    return pages


def semantic_search(wiki_dir: str, query: str, top_k: int = 5, enable: bool = False):
    """Search using semantic similarity."""
    if not enable:
        print("ℹ️  Semantic search is disabled by default.")
        print("   Use --enable to activate (requires: pip install sentence-transformers)")
        print()
        print("   Falling back to keyword search...")
        # Fallback: just use TF-IDF from search.py
        import subprocess
        subprocess.run([
            sys.executable, str(Path(__file__).parent / "search.py"),
            query, "--wiki-dir", wiki_dir, "--summary", "--top", str(top_k)
        ])
        return

    if not check_deps():
        print("❌ sentence-transformers not installed.")
        print("   Run: pip install sentence-transformers")
        return

    base = Path(wiki_dir)
    pages = load_pages(base)

    if not pages:
        print("❌ No wiki pages found")
        return

    print(f"[semantic] Loading model...")
    model = load_model()

    print(f"[semantic] Encoding {len(pages)} pages...")
    texts = [p["text"] for p in pages]
    page_embeddings = model.encode(texts, show_progress_bar=False)

    print(f"[semantic] Searching...")
    query_embedding = model.encode([query])

    # Cosine similarity
    import numpy as np
    similarities = np.dot(page_embeddings, query_embedding.T).flatten()
    top_indices = similarities.argsort()[::-1][:top_k]

    print(f"\n🔍 Semantic search results for: \"{query}\"\n")
    for i, idx in enumerate(top_indices, 1):
        page = pages[idx]
        score = similarities[idx]
        print(f"{i}. [{page['type']}] {page['title']} (similarity: {score:.3f})")
        print(f"   {page['path']}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Semantic search for Mycelium wiki")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--dir", "-d", default=".", help="Wiki root directory")
    parser.add_argument("--top", "-n", type=int, default=5, help="Number of results")
    parser.add_argument("--enable", action="store_true",
                        help="Enable semantic search (requires sentence-transformers)")
    args = parser.parse_args()
    semantic_search(args.dir, args.query, args.top, args.enable)


if __name__ == "__main__":
    main()
