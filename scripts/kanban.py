#!/usr/bin/env python3
"""Generate Obsidian Kanban board for research tasks."""
import argparse
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
from utils import TODAY


KANBAN_TEMPLATE = """---
kanban-plugin: basic
---

## 📋 待读 (To Read)

- [ ] Add sources to read here
- [ ]

## 📖 阅读中 (Reading)

- [ ]

## ✅ 已读 (Read)

- [ ]

## 🔧 待整理 (To Process)

- [ ]

## 📝 已整理 (Processed)

- [ ]

## 💡 待深入 (To Explore)

- [ ]

---
kanban-plugin: basic

> Created: {date}
"""


def create_kanban(wiki_dir: str = ".", force: bool = False):
    """Create kanban board in wiki."""
    base = Path(wiki_dir)
    wiki = base / "wiki"
    meta_dir = wiki / "meta"
    meta_dir.mkdir(parents=True, exist_ok=True)

    filepath = meta_dir / "kanban.md"

    if filepath.exists() and not force:
        print(f"📖 Kanban already exists: {filepath}")
        print(f"   Use --force to recreate")
        content = filepath.read_text(encoding='utf-8')
        print(content)
        return

    content = KANBAN_TEMPLATE.replace("{date}", TODAY)
    filepath.write_text(content, encoding='utf-8')
    print(f"✅ Created: {filepath}")
    print(f"   Open in Obsidian with Kanban plugin")


def main():
    parser = argparse.ArgumentParser(description="Create research kanban board")
    parser.add_argument("--dir", "-d", default=".", help="Wiki root directory")
    parser.add_argument("--force", "-f", action="store_true", help="Recreate kanban even if exists")
    args = parser.parse_args()
    create_kanban(args.dir, args.force)


if __name__ == "__main__":
    main()
