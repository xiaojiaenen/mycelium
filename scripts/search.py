#!/usr/bin/env python3
"""
Wiki Search — BM25 + Wikilink graph search for Mycelium.

Usage:
    python3 scripts/search.py "query"
    python3 scripts/search.py "query" --mode hybrid
    python3 scripts/search.py "query" --type concept
    python3 scripts/search.py "query" --top 10
"""

import argparse
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


def tokenize(text: str) -> list[str]:
    """Simple tokenizer: lowercase, split on non-alphanumeric, filter short tokens."""
    tokens = re.findall(r'[a-z0-9一-鿿]+', text.lower())
    return [t for t in tokens if len(t) > 1]


def compute_idf(doc_tokens: list[list[str]]) -> dict[str, float]:
    """Compute inverse document frequency."""
    n_docs = len(doc_tokens)
    df = Counter()
    for tokens in doc_tokens:
        df.update(set(tokens))
    return {t: math.log((n_docs - count + 0.5) / (count + 0.5) + 1) for t, count in df.items()}


def bm25_score(query_tokens: list[str], doc_tokens: list[str], idf: dict[str, float],
               avg_dl: float, k1: float = 1.5, b: float = 0.75) -> float:
    """Compute BM25 score for a document."""
    dl = len(doc_tokens)
    tf = Counter(doc_tokens)
    score = 0.0
    for qt in query_tokens:
        if qt in tf:
            term_freq = tf[qt]
            numerator = term_freq * (k1 + 1)
            denominator = term_freq + k1 * (1 - b + b * dl / avg_dl)
            score += idf.get(qt, 0) * numerator / denominator
    return score


def extract_wikilinks(content: str) -> set[str]:
    """Extract [[wikilinks]] from markdown content."""
    return set(re.findall(r'\[\[([^\]]+)\]\]', content))


def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown."""
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


def load_wiki(wiki_dir: str, type_filter: str = None) -> list[dict]:
    """Load all wiki pages."""
    pages = []
    wiki_path = Path(wiki_dir) / 'wiki'

    for subdir in ['sources', 'concepts', 'entities', 'comparisons', 'questions', 'contradictions']:
        dir_path = wiki_path / subdir
        if not dir_path.exists():
            continue
        for md_file in sorted(dir_path.glob('*.md')):
            content = md_file.read_text(encoding='utf-8')
            fm = parse_frontmatter(content)
            note_type = fm.get('type', subdir.rstrip('s'))

            if type_filter and note_type != type_filter:
                continue

            pages.append({
                'path': str(md_file),
                'relative': str(md_file.relative_to(wiki_path.parent)),
                'type': note_type,
                'title': fm.get('title', md_file.stem),
                'tags': fm.get('tags', []),
                'status': fm.get('status', ''),
                'frontmatter': fm,
                'content': content,
                'tokens': tokenize(content),
                'wikilinks': extract_wikilinks(content),
            })

    return pages


def build_link_graph(pages: list[dict]) -> dict[str, set[str]]:
    """Build directed link graph: page title → set of titles it links to."""
    title_to_path = {p['title']: p['relative'] for p in pages}
    graph = defaultdict(set)
    for page in pages:
        for link in page['wikilinks']:
            if link in title_to_path:
                graph[page['relative']].add(title_to_path[link])
    return graph


def compute_pagerank(graph: dict[str, set[str]], damping: float = 0.85, iterations: int = 20) -> dict[str, float]:
    """Simple PageRank for wikilink graph."""
    all_nodes = set(graph.keys())
    for targets in graph.values():
        all_nodes.update(targets)

    n = len(all_nodes)
    if n == 0:
        return {}

    pr = {node: 1.0 / n for node in all_nodes}

    for _ in range(iterations):
        new_pr = {}
        for node in all_nodes:
            incoming = [src for src, targets in graph.items() if node in targets]
            rank_sum = sum(pr[src] / len(graph[src]) for src in incoming if src in graph)
            new_pr[node] = (1 - damping) / n + damping * rank_sum
        pr = new_pr

    return pr


def vector_score(query: str, page_tokens_list: list[list[str]]) -> list[float]:
    """Compute cosine similarity using TF-IDF vectors (no external deps)."""
    # Build vocabulary
    vocab = {}
    for tokens in page_tokens_list:
        for t in set(tokens):
            if t not in vocab:
                vocab[t] = len(vocab)

    # IDF weights
    n_docs = len(page_tokens_list)
    idf = {}
    for term, idx in vocab.items():
        df = sum(1 for tokens in page_tokens_list if term in tokens)
        idf[term] = math.log((n_docs - df + 0.5) / (df + 0.5) + 1)

    # Query vector
    query_tokens = tokenize(query)
    query_vec = {}
    for t in query_tokens:
        if t in vocab:
            query_vec[t] = query_vec.get(t, 0) + idf.get(t, 1)

    query_norm = math.sqrt(sum(v * v for v in query_vec.values())) or 1

    # Document vectors and cosine similarity
    scores = []
    for tokens in page_tokens_list:
        doc_vec = {}
        for t in tokens:
            if t in vocab:
                doc_vec[t] = doc_vec.get(t, 0) + idf.get(t, 1)

        # Cosine similarity
        dot = sum(query_vec.get(t, 0) * doc_vec.get(t, 0) for t in query_vec)
        doc_norm = math.sqrt(sum(v * v for v in doc_vec.values())) or 1
        scores.append(dot / (query_norm * doc_norm))

    return scores


def search(wiki_dir: str, query: str, mode: str = 'hybrid', type_filter: str = None,
           top_k: int = 5, summary: bool = False) -> list[dict]:
    """Search wiki pages."""
    pages = load_wiki(wiki_dir, type_filter)
    if not pages:
        return []

    query_tokens = tokenize(query)
    if not query_tokens:
        return []

    # BM25 scoring
    all_tokens = [p['tokens'] for p in pages]
    avg_dl = sum(len(t) for t in all_tokens) / len(all_tokens) if all_tokens else 1
    idf = compute_idf(all_tokens)

    for page in pages:
        page['bm25'] = bm25_score(query_tokens, page['tokens'], idf, avg_dl)

    # Link scoring
    graph = build_link_graph(pages)
    pagerank = compute_pagerank(graph)

    for page in pages:
        page['link_score'] = pagerank.get(page['relative'], 0)

    # Vector scoring (for vector/hybrid modes)
    if mode in ('vector', 'hybrid'):
        vec_scores = vector_score(query, all_tokens)
        for i, page in enumerate(pages):
            page['vec_score'] = vec_scores[i]
    else:
        for page in pages:
            page['vec_score'] = 0

    # Combine scores
    if mode == 'bm25':
        for page in pages:
            page['score'] = page['bm25']
    elif mode == 'links':
        for page in pages:
            page['score'] = page['link_score']
    elif mode == 'vector':
        for page in pages:
            page['score'] = page['vec_score']
    else:  # hybrid
        max_bm25 = max((p['bm25'] for p in pages), default=1) or 1
        max_link = max((p['link_score'] for p in pages), default=1) or 1
        max_vec = max((p['vec_score'] for p in pages), default=1) or 1
        for page in pages:
            page['score'] = (0.5 * (page['bm25'] / max_bm25) +
                             0.25 * (page['link_score'] / max_link) +
                             0.25 * (page['vec_score'] / max_vec))

    # Sort and return top results
    pages.sort(key=lambda p: p['score'], reverse=True)

    results = []
    for page in pages[:top_k]:
        r = {
            'title': page['title'],
            'type': page['type'],
            'path': page['relative'],
            'score': round(page['score'], 4),
            'tags': page['tags'],
            'status': page['status'],
        }
        if not summary:
            r['bm25'] = round(page['bm25'], 4)
            r['link_score'] = round(page['link_score'], 4)
            r['vec_score'] = round(page.get('vec_score', 0), 4)
            r['wikilinks'] = list(page['wikilinks'])[:10]

        # Extract one-line summary from content (first non-heading, non-frontmatter line)
        content_lines = page['content'].split('\n')
        in_frontmatter = False
        for line in content_lines:
            if line.strip() == '---':
                in_frontmatter = not in_frontmatter
                continue
            if not in_frontmatter and line.strip() and not line.startswith('#'):
                r['summary'] = line.strip()[:120]
                break

        results.append(r)

    return results


def main():
    parser = argparse.ArgumentParser(description='Search Mycelium wiki')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--mode', choices=['hybrid', 'bm25', 'links', 'vector', 'semantic'], default='hybrid',
                        help='Search mode (default: hybrid, semantic needs sentence-transformers)')
    parser.add_argument('--type', dest='type_filter',
                        choices=['source', 'concept', 'entity', 'comparison', 'question', 'contradiction'],
                        help='Filter by note type')
    parser.add_argument('--top', type=int, default=5, help='Number of results (default: 5)')
    parser.add_argument('--summary', action='store_true', help='Output summary only (title + one-line)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--wiki-dir', default='.', help='Wiki root directory (default: .)')

    args = parser.parse_args()

    # Semantic mode: delegate to semantic.py
    if args.mode == 'semantic':
        import subprocess
        cmd = [sys.executable, str(Path(__file__).parent / "semantic.py"),
               args.query, "--dir", args.wiki_dir, "--top", str(args.top), "--enable"]
        subprocess.run(cmd)
        return

    results = search(args.wiki_dir, args.query, args.mode, args.type_filter, args.top, args.summary)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        if not results:
            print(f"No results found for: {args.query}")
            return

        print(f"Search results for: {args.query}")
        print(f"Mode: {args.mode} | Found: {len(results)}")
        print("-" * 60)

        for i, r in enumerate(results, 1):
            print(f"{i}. [{r['type']}] {r['title']}")
            if r.get('summary'):
                print(f"   {r['summary']}")
            if not args.summary:
                print(f"   Path: {r['path']}")
                print(f"   Score: {r['score']} (bm25: {r.get('bm25', '-')}, link: {r.get('link_score', '-')}, vec: {r.get('vec_score', '-')})")
                if r['tags']:
                    print(f"   Tags: {', '.join(r['tags'])}")
                if r.get('wikilinks'):
                    print(f"   Links: {', '.join(r['wikilinks'][:5])}")
            print()


if __name__ == '__main__':
    main()
