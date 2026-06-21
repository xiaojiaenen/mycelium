#!/usr/bin/env python3
"""Generate Obsidian Kanban board for research tasks."""
import argparse
from pathlib import Path
from datetime import date


KANBAN_TEMPLATE = """---
kanban-plugin: basic
---

## 📋 待读 (To Read)

- [ ]
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
"""


def create_kanban(wiki_dir: str = "."):
    """Create kanban board in wiki."""
    base = Path(wiki_dir)
    wiki = base / "wiki"
    meta_dir = wiki / "meta"
    meta_dir.mkdir(parents=True, exist_ok=True)

    filepath = meta_dir / "kanban.md"

    if filepath.exists():
        print(f"📖 Kanban already exists: {filepath}")
        content = filepath.read_text(encoding='utf-8')
        print(content)
        return

    filepath.write_text(KANBAN_TEMPLATE, encoding='utf-8')
    print(f"✅ Created: {filepath}")
    print(f"   Open in Obsidian with Kanban plugin")


def main():
    parser = argparse.ArgumentParser(description="Create research kanban board")
    parser.add_argument("--dir", "-d", default=".", help="Wiki root directory")
    args = parser.parse_args()
    create_kanban(args.dir)


if __name__ == "__main__":
    main()
