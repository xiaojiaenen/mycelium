#!/usr/bin/env python3
"""
Fully automated ingest pipeline for Mycelium.
Read → Extract → Create notes → Update indexes → Generate diagrams → Git commit.

Usage:
    python3 scripts/auto_ingest.py <file>
    python3 scripts/auto_ingest.py <url>
    python3 scripts/auto_ingest.py --all        # Ingest all new files in .raw/
"""
import os
import re
import sys
import json
import subprocess
import argparse
from pathlib import Path
from datetime import date, datetime

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    TODAY, SUPPORTED_EXTENSIONS, ACRONYMS, MAX_SLUG_LENGTH,
    parse_frontmatter, extract_wikilinks, extract_keywords, slugify,
    title_from_slug, file_hash, is_video_url, is_url,
)

SCRIPTS_DIR = Path(__file__).parent


# ── Step 1: Read Source ──────────────────────────────────

def read_source(file_path: str) -> dict:
    """Read source file and extract metadata + content."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = path.suffix.lower()
    size = path.stat().st_size

    # Determine source type
    type_map = {
        '.md': 'article', '.txt': 'article', '.rst': 'article',
        '.pdf': 'paper', '.docx': 'document', '.pptx': 'presentation',
        '.srt': 'subtitle', '.vtt': 'subtitle', '.plain': 'transcript',
        '.mp4': 'video', '.mkv': 'video', '.webm': 'video',
        '.mp3': 'audio', '.wav': 'audio', '.m4a': 'audio',
        '.html': 'webpage', '.htm': 'webpage',
        '.epub': 'book',
        '.png': 'image', '.jpg': 'image', '.jpeg': 'image',
    }

    # Read content
    try:
        content = path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        content = f"[Binary file: {path.name}]"

    return {
        "path": str(path),
        "name": path.stem,
        "filename": path.name,
        "ext": ext,
        "size": size,
        "source_type": type_map.get(ext, 'article'),
        "content": content,
        "keywords": extract_keywords(content),
    }


def read_url(url: str) -> dict:
    """Read URL content via fetch-web.py or detect video."""
    if is_video_url(url):
        return {"type": "video", "url": url}

    # Try fetch-web.py
    fetch_script = SCRIPTS_DIR / "fetch-web.py"
    if fetch_script.exists():
        return {"type": "webpage", "url": url, "script": str(fetch_script)}

    return {"type": "webpage", "url": url}


# ── Step 2: Create Source Note ───────────────────────────

def create_source_note(source: dict, wiki_dir: Path) -> str:
    """Create source note in wiki/sources/."""
    sources_dir = wiki_dir / "sources"
    sources_dir.mkdir(parents=True, exist_ok=True)

    slug = slugify(source["name"])
    filename = f"{source['source_type']}-{slug}.md"
    filepath = sources_dir / filename

    tags = source.get("keywords", [])[:5]
    tags_str = json.dumps(tags, ensure_ascii=False) if tags else '["untagged"]'

    # Extract first paragraph as summary
    content = source.get("content", "")
    lines = content.strip().split('\n')
    summary_lines = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('---'):
            summary_lines.append(line)
            if len(' '.join(summary_lines)) > 100:
                break
    summary = ' '.join(summary_lines)[:200] if summary_lines else source["name"]

    note = f"""---
type: source
title: "{source['name']}"
source_type: {source['source_type']}
source_file: {source['filename']}
created: {TODAY}
tags: {tags_str}
status: draft
---

# {source['name']}

## 一句话总结
{summary}

## 元信息
- 文件：{source['filename']}
- 类型：{source['source_type']}
- 大小：{source['size'] / 1024:.1f} KB
- 摄入日期：{TODAY}

---

## 核心观点
<!-- LLM 会填充此部分 -->

## 关键概念
<!-- LLM 会填充此部分 -->

## 来源
- {source['filename']}
"""

    filepath.write_text(note, encoding='utf-8')
    print(f"  📄 Source note: {filepath.name}")
    return filename


# ── Step 3: Extract Keywords → Suggest Concepts ──────────

def suggest_concepts(source: dict, wiki_dir: Path) -> list:
    """Suggest concept names from keywords and existing wiki."""
    keywords = source.get("keywords", [])

    # Check existing concepts
    concepts_dir = wiki_dir / "concepts"
    existing = set()
    if concepts_dir.exists():
        for f in concepts_dir.glob('*.md'):
            existing.add(f.stem.lower())

    suggestions = []
    for kw in keywords:
        slug = slugify(kw)
        if slug and slug not in existing:
            suggestions.append(slug)

    return suggestions[:5]


def create_concept_stubs(suggestions: list, source_name: str, wiki_dir: Path):
    """Create stub concept notes for LLM to fill."""
    concepts_dir = wiki_dir / "concepts"
    concepts_dir.mkdir(parents=True, exist_ok=True)

    for slug in suggestions:
        filepath = concepts_dir / f"{slug}.md"
        if filepath.exists():
            continue

        # Title case for display
        words = slug.replace('-', ' ').split()
        ACRONYMS = {'rlhf', 'ppo', 'dpo', 'sft', 'moe', 'llm', 'gpt', 'bert', 'cv', 'nlp', 'ai', 'ml', 'rnn', 'cnn', 'lstm', 'gru'}
        title_words = [w.upper() if w.lower() in ACRONYMS else w.capitalize() for w in words]
        title = ' '.join(title_words)

        note = f"""---
type: concept
title: "{title}"
created: {TODAY}
tags: []
status: developing
version: 1
evidence_strength: weak
confidence: 0.3
last_verified: {TODAY}
---

# {title}

## 一句话定义
<!-- LLM 会填充此部分 -->

## 核心解释
<!-- LLM 会填充此部分 -->

## 来源
- [[{source_name}]]
"""

        filepath.write_text(note, encoding='utf-8')
        print(f"  💡 Concept stub: {filepath.name}")


# ── Step 4: Update Index ─────────────────────────────────

def update_index(source_file: str, concepts: list, wiki_dir: Path):
    """Update wiki/index.md with new entries."""
    index_path = wiki_dir / "index.md"
    if not index_path.exists():
        return

    content = index_path.read_text(encoding='utf-8')

    # Add source
    source_entry = f"- [[{Path(source_file).stem}]]"
    if source_entry not in content:
        # Remove placeholder if present
        content = content.replace("[Source notes will appear here]\n", "")
        content = content.replace(
            "## Sources\n\n",
            f"## Sources\n\n{source_entry}\n"
        )

    # Add concepts
    for concept in concepts:
        concept_entry = f"- [[{concept}]]"
        if concept_entry not in content:
            content = content.replace("[Concept notes will appear here]\n", "")
            content = content.replace(
                "## Concepts\n\n",
                f"## Concepts\n\n{concept_entry}\n"
            )

    # Update date
    content = re.sub(r'Last updated: \d{4}-\d{2}-\d{2}', f'Last updated: {TODAY}', content)

    index_path.write_text(content, encoding='utf-8')
    print(f"  📋 Updated index.md")


# ── Step 5: Update Log ───────────────────────────────────

def update_log(source_name: str, wiki_dir: Path):
    """Append to wiki/log.md."""
    log_path = wiki_dir / "log.md"
    if not log_path.exists():
        return

    content = log_path.read_text(encoding='utf-8')
    entry = f"## [{TODAY}] ingest | {source_name}\n\n- Source ingested\n- Index updated\n\n"

    # Insert after frontmatter
    parts = content.split('---\n', 2)
    if len(parts) >= 3:
        new_content = parts[0] + '---\n' + parts[1] + '---\n\n' + entry + parts[2]
    else:
        new_content = content + entry

    log_path.write_text(new_content, encoding='utf-8')
    print(f"  📝 Updated log.md")


# ── Step 6: Update Hot Cache ─────────────────────────────

def update_hot(source_name: str, keywords: list, wiki_dir: Path):
    """Update wiki/hot.md with recent context."""
    hot_path = wiki_dir / "hot.md"
    if not hot_path.exists():
        return

    content = hot_path.read_text(encoding='utf-8')

    # Update date
    content = re.sub(r'Last updated: \d{4}-\d{2}-\d{2}', f'Last updated: {TODAY}', content)

    # Update recent changes
    new_entry = f"- Ingested: {source_name}"
    if 'Wiki initialized' in content:
        content = content.replace('## Recent Changes\n- Wiki initialized',
                                  f'## Recent Changes\n{new_entry}')
    else:
        content = content.replace('## Recent Changes\n', f'## Recent Changes\n{new_entry}\n')

    # Update key facts with top keywords
    if keywords:
        facts = '\n'.join(f'- {kw}' for kw in keywords[:3])
        content = re.sub(r'## Key Facts\n- \[.*?\]', f'## Key Facts\n{facts}', content)

    hot_path.write_text(content, encoding='utf-8')
    print(f"  🔥 Updated hot.md")


# ── Step 7: Rebuild Indexes ──────────────────────────────

def rebuild_indexes(wiki_dir: Path):
    """Rebuild index-tags.md and index-topics.md."""
    try:
        subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "index.py"), "--dir", str(wiki_dir.parent)],
            capture_output=True, check=True
        )
        print(f"  📊 Rebuilt indexes")
    except Exception as e:
        print(f"  ⚠️  Index rebuild failed: {e}")


# ── Step 8: Generate Diagrams ────────────────────────────

def generate_diagrams(wiki_dir: Path):
    """Generate excalidraw and knowledge graph."""
    wiki_parent = wiki_dir.parent
    meta_dir = wiki_dir / "meta"
    meta_dir.mkdir(parents=True, exist_ok=True)

    # Excalidraw
    try:
        subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "excalidraw.py"), "--dir", str(wiki_parent)],
            capture_output=True, check=True
        )
        print(f"  🎨 Generated excalidraw")
    except Exception as e:
        print(f"  ⚠️  Excalidraw failed: {e}")

    # Knowledge graph
    try:
        subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "graph.py"), "--dir", str(wiki_parent)],
            capture_output=True, check=True
        )
        print(f"  🕸️  Generated knowledge graph")
    except Exception as e:
        print(f"  ⚠️  Graph failed: {e}")


# ── Step 9: Git Commit ───────────────────────────────────

def git_commit(wiki_dir: Path, source_name: str):
    """Auto-commit changes."""
    wiki_parent = wiki_dir.parent
    try:
        subprocess.run(["git", "add", "-A"], cwd=str(wiki_parent), check=True, capture_output=True)
        result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=str(wiki_parent))
        if result.returncode != 0:
            subprocess.run(
                ["git", "commit", "-q", "-m", f"ingest: {source_name}"],
                cwd=str(wiki_parent), check=True, capture_output=True
            )
            print(f"  📦 Git committed")
    except Exception as e:
        print(f"  ⚠️  Git failed: {e}")


# ── Main Pipeline ────────────────────────────────────────

def ingest_file(file_path: str, wiki_dir: str = "."):
    """Full ingest pipeline for a single file."""
    base = Path(wiki_dir)
    wiki = base / "wiki"

    if not wiki.exists():
        print(f"❌ wiki/ not found. Run: python3 scripts/init.py first")
        return

    print(f"\n{'='*50}")
    print(f"🍄 Mycelium Auto-Ingest")
    print(f"{'='*50}")

    # Step 1: Read
    print(f"\n📖 Step 1: Reading source...")
    source = read_source(file_path)
    print(f"  File: {source['filename']}")
    print(f"  Type: {source['source_type']}")
    print(f"  Keywords: {', '.join(source['keywords'][:5])}")

    # Step 2: Create source note
    print(f"\n📄 Step 2: Creating source note...")
    source_file = create_source_note(source, wiki)

    # Step 3: Suggest concepts
    print(f"\n💡 Step 3: Extracting concepts...")
    concepts = suggest_concepts(source, wiki)
    if concepts:
        create_concept_stubs(concepts, Path(source_file).stem, wiki)
    else:
        print(f"  (no new concepts to extract)")

    # Step 4: Update index
    print(f"\n📋 Step 4: Updating index...")
    update_index(source_file, concepts, wiki)

    # Step 5: Update log
    print(f"\n📝 Step 5: Updating log...")
    update_log(source["name"], wiki)

    # Step 6: Update hot cache
    print(f"\n🔥 Step 6: Updating hot cache...")
    update_hot(source["name"], source["keywords"], wiki)

    # Step 7: Rebuild indexes
    print(f"\n📊 Step 7: Rebuilding indexes...")
    rebuild_indexes(wiki)

    # Step 8: Generate diagrams
    print(f"\n🎨 Step 8: Generating diagrams...")
    generate_diagrams(wiki)

    # Step 9: Git commit
    print(f"\n📦 Step 9: Git commit...")
    git_commit(wiki, source["name"])

    print(f"\n{'='*50}")
    print(f"✅ Ingest complete: {source['filename']}")
    print(f"{'='*50}")

    # Next steps for LLM
    print(f"\n🤖 Next steps for LLM:")
    print(f"  1. Fill in source note: wiki/sources/{Path(source_file).stem}.md")
    print(f"  2. Fill in concept notes: wiki/concepts/")
    print(f"  3. Create entity notes if needed: wiki/entities/")
    print(f"  4. Run: python3 scripts/lint.py --dir {wiki_dir}")


def ingest_all(wiki_dir: str = "."):
    """Ingest all new files in .raw/."""
    base = Path(wiki_dir)
    raw_dir = base / ".raw"
    manifest_path = raw_dir / ".manifest.json"

    if not raw_dir.exists():
        print(f"❌ .raw/ not found in {wiki_dir}")
        return

    # Load manifest
    manifest = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))

    # Find new files
    supported = SUPPORTED_EXTENSIONS

    new_files = []
    for f in sorted(raw_dir.iterdir()):
        if f.is_file() and f.suffix.lower() in supported:
            if f.name not in manifest:
                new_files.append(f)

    if not new_files:
        print("✅ All files already ingested.")
        return

    print(f"📋 Found {len(new_files)} new file(s)\n")
    for f in new_files:
        print(f"  🆕 {f.name}")

    print(f"\nStarting batch ingest...\n")
    for f in new_files:
        try:
            ingest_file(str(f), wiki_dir)
        except Exception as e:
            print(f"\n❌ Failed to ingest {f.name}: {e}")
            continue

    # Save manifest
    for f in new_files:
        manifest[f.name] = {
            "hash": file_hash(str(f)),
            "ingested_at": datetime.now().isoformat(),
        }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description="Auto-ingest pipeline for Mycelium")
    parser.add_argument("target", nargs="?", help="File path, URL, or --all")
    parser.add_argument("--dir", "-d", default=".", help="Wiki root directory")
    args = parser.parse_args()

    if not args.target or args.target == "--all":
        ingest_all(args.dir)
    elif args.target.startswith("http://") or args.target.startswith("https://"):
        print("⚠️  URL ingest not yet automated. Use:")
        print(f"   python3 scripts/video.py \"{args.target}\" -o .raw")
        print(f"   python3 scripts/fetch-web.py \"{args.target}\"")
        print(f"   Then: python3 scripts/auto_ingest.py --all")
    else:
        ingest_file(args.target, args.dir)


if __name__ == "__main__":
    main()
