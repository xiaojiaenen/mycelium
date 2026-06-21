#!/usr/bin/env python3
"""Initialize a new Mycelium knowledge base."""
import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import date

TODAY = date.today().isoformat()

INDEX_MD = f"""---
type: meta
title: "Wiki Index"
created: {TODAY}
tags:
  - meta
  - index
status: evergreen
---

# Wiki Index

Last updated: {TODAY}

---

## Sources

[Source notes will appear here]

---

## Concepts

[Concept notes will appear here]

---

## Entities

[Entity notes will appear here]

---

## Comparisons

[Comparison notes will appear here]

---

## Questions

[Question notes will appear here]

---

## Contradictions

[Contradiction notes will appear here]

---

## Topic Clusters

[Auto-generated topic clusters will appear here]
"""

INDEX_TAGS_MD = f"""---
type: meta
title: "Tag Index"
created: {TODAY}
tags:
  - meta
  - index
  - tags
status: evergreen
---

# Tag Index

Auto-generated from note frontmatter. Updated on every lint.

---

## Tags

[Tag clusters will appear here]
"""

INDEX_TOPICS_MD = f"""---
type: meta
title: "Topic Clusters"
created: {TODAY}
tags:
  - meta
  - index
  - topics
status: evergreen
---

# Topic Clusters

Auto-generated from wikilink density analysis. Updated on every lint.

---

## Clusters

[Topic clusters will appear here]
"""

LOG_MD = f"""---
type: meta
title: "Operation Log"
created: {TODAY}
tags:
  - meta
  - log
status: evergreen
---

# Operation Log

Append-only. New entries go at the TOP. Never edit past entries.

Entry format: `## [YYYY-MM-DD] operation | Title`

---

"""

HOT_MD = f"""---
type: meta
title: "Hot Cache"
created: {TODAY}
tags:
  - meta
  - hot-cache
status: evergreen
---

# Recent Context

Last updated: {TODAY}

## Key Facts
- [Most important recent fact]

## Recent Changes
- Wiki initialized

## Active Threads
- [Current research topic]
"""

GITIGNORE = """# OS files
.DS_Store
Thumbs.db

# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/

# IDE
.vscode/
.idea/

# Raw manifest (regenerated)
.raw/.manifest.json

# Temp files
*.tmp
*.bak
"""


def init_wiki(wiki_name: str, wiki_dir: str = "."):
    """Initialize a new Mycelium wiki."""
    base = Path(wiki_dir)

    print(f"Initializing Mycelium: {wiki_name}")
    print(f"Location: {base.resolve()}")

    # Create directory structure
    dirs = [
        base / ".raw",
        base / "wiki" / "sources",
        base / "wiki" / "concepts",
        base / "wiki" / "entities",
        base / "wiki" / "comparisons",
        base / "wiki" / "questions",
        base / "wiki" / "contradictions",
        base / "wiki" / "meta",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # Create markdown files
    files = {
        base / "wiki" / "index.md": INDEX_MD,
        base / "wiki" / "index-tags.md": INDEX_TAGS_MD,
        base / "wiki" / "index-topics.md": INDEX_TOPICS_MD,
        base / "wiki" / "log.md": LOG_MD,
        base / "wiki" / "hot.md": HOT_MD,
    }
    for path, content in files.items():
        path.write_text(content, encoding="utf-8")

    # Create CLAUDE.md
    claude_md = f"""# {wiki_name}: Mycelium Knowledge Base

Created: {TODAY}

## Structure

```
.raw/           # Source files (immutable)
wiki/
├── index.md    # Master catalog
├── index-tags.md    # Auto-generated tag index
├── index-topics.md  # Auto-generated topic clusters
├── log.md      # Operation log
├── hot.md      # Recent context cache
├── sources/    # Source summaries
├── concepts/   # Concept explanations
├── entities/   # People, orgs, products
├── comparisons/ # Side-by-side analyses
├── contradictions/ # Cross-source conflicts
└── questions/  # Filed answers
```

## Conventions

- All notes use YAML frontmatter: type, status, created, tags
- Wikilinks use [[Note Name]] format
- .raw/ contains source documents: never modify them
- wiki/index.md is the master catalog: update on every ingest
- wiki/log.md is append-only: never edit past entries
- New log entries go at the TOP of the file

## Operations

- **Ingest**: drop source in .raw/, say "ingest [filename]"
- **Query**: ask any question, Claude reads index first then drills in
- **Lint**: say "lint" for standard check, "lint --deep" for full analysis

## Note Types

| Type | Location | Purpose |
|------|----------|---------|
| source | wiki/sources/ | Summary of a source |
| concept | wiki/concepts/ | Explanation of an idea |
| entity | wiki/entities/ | Person/org/product |
| comparison | wiki/comparisons/ | Side-by-side analysis |
| contradiction | wiki/contradictions/ | Cross-source conflicts |
| question | wiki/questions/ | Filed answers |

## Git Workflow

This wiki is a git repository. Every ingest is auto-committed.
Use branches for exploratory research: `git checkout -b explore/topic`
"""
    (base / "CLAUDE.md").write_text(claude_md, encoding="utf-8")

    # Create .gitignore
    (base / ".gitignore").write_text(GITIGNORE, encoding="utf-8")

    # Initialize git
    try:
        subprocess.run(["git", "init", "-q"], cwd=str(base), check=True,
                       capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=str(base), check=True,
                       capture_output=True)
        subprocess.run(["git", "commit", "-q", "-m",
                        f"init: initialize wiki '{wiki_name}'"],
                       cwd=str(base), check=True, capture_output=True)
        print("\n✅ Git repository initialized")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n⚠️  Git not available, skipping git init")

    # Show result
    print(f"\n✅ Wiki initialized successfully!")
    print(f"\nNext steps:")
    print(f"1. Add source files to .raw/")
    print(f'2. Tell Claude: ingest [filename]')
    print(f'3. Ask questions: query: [question]')
    print(f'4. Health check: lint  or  lint --deep')


def main():
    parser = argparse.ArgumentParser(description="Initialize a new Mycelium wiki")
    parser.add_argument("name", nargs="?", default="My Knowledge Base",
                        help="Wiki name (default: My Knowledge Base)")
    parser.add_argument("--dir", "-d", default=".",
                        help="Directory to initialize in (default: current)")
    args = parser.parse_args()

    init_wiki(args.name, args.dir)


if __name__ == "__main__":
    main()
