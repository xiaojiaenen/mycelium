#!/usr/bin/env python3
"""Manage .raw/ directory: scan, read, list, types, status."""
import os
import sys
import json
import argparse
from pathlib import Path
from collections import Counter

import sys as _sys
_sys.path.insert(0, str(Path(__file__).parent))
from utils import SUPPORTED_EXTENSIONS, file_hash

MANIFEST_FILE = ".manifest.json"


class Manifest:
    def __init__(self, path: str):
        self.path = Path(path)
        self.data = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            return json.loads(self.path.read_text(encoding="utf-8"))
        return {}

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False),
                             encoding="utf-8")

    def is_ingested(self, file_path: str) -> bool:
        return file_path in self.data

    def mark(self, file_path: str, wiki_page: str = ""):
        file_hash = self._hash(file_path)
        self.data[file_path] = {
            "hash": file_hash,
            "ingested_at": __import__("datetime").datetime.now().isoformat(),
            "wiki_page": wiki_page,
        }
        self.save()

    def get_hash(self, file_path: str) -> str:
        if file_path in self.data:
            return self.data[file_path].get("hash", "")
        return ""

    @staticmethod
    def _hash(file_path: str) -> str:
        h = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()


def scan(raw_dir: str = ".raw"):
    """Scan .raw/ for files and show status."""
    raw_path = Path(raw_dir)
    if not raw_path.exists():
        print(f"Directory not found: {raw_dir}")
        return

    manifest = Manifest(str(raw_path / MANIFEST_FILE))

    files = []
    for f in sorted(raw_path.iterdir()):
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(f)

    if not files:
        print(f"No supported files found in {raw_dir}")
        return

    new_count = modified_count = ingested_count = 0

    print(f"📁 Scanning {raw_dir}/\n")
    for f in files:
        rel = f.name
        current_hash = Manifest._hash(str(f))
        stored_hash = manifest.get_hash(rel)

        if not manifest.is_ingested(rel):
            print(f"  🆕 NEW       {rel}")
            new_count += 1
        elif current_hash != stored_hash:
            print(f"  📝 MODIFIED  {rel}")
            modified_count += 1
        else:
            print(f"  ✅ INGESTED  {rel}")
            ingested_count += 1

    print(f"\nSummary: {len(files)} files | {new_count} new | {modified_count} modified | {ingested_count} ingested")


def list_files(raw_dir: str = ".raw"):
    """List all supported files in .raw/."""
    raw_path = Path(raw_dir)
    if not raw_path.exists():
        print(f"Directory not found: {raw_dir}")
        return

    files = [f for f in sorted(raw_path.iterdir())
             if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS]

    if not files:
        print(f"No supported files in {raw_dir}")
        return

    for f in files:
        size = f.stat().st_size
        if size > 1024 * 1024:
            size_str = f"{size / 1024 / 1024:.1f} MB"
        elif size > 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size} B"
        print(f"  {f.name:40s} {size_str:>10s}")

    print(f"\nTotal: {len(files)} files")


def types(raw_dir: str = ".raw"):
    """Show file type statistics."""
    raw_path = Path(raw_dir)
    if not raw_path.exists():
        print(f"Directory not found: {raw_dir}")
        return

    counter = Counter()
    for f in raw_path.iterdir():
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
            counter[f.suffix.lower()] += 1

    if not counter:
        print(f"No supported files in {raw_dir}")
        return

    print(f"📊 File types in {raw_dir}/\n")
    for ext, count in counter.most_common():
        print(f"  {ext:10s} {count}")
    print(f"\nTotal: {sum(counter.values())} files")


def read_file(file_path: str, raw_dir: str = ".raw"):
    """Read and display a file's content."""
    path = Path(file_path)
    if not path.exists():
        path = Path(raw_dir) / file_path
    if not path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    info = {
        "name": path.name,
        "type": path.suffix,
        "size": path.stat().st_size,
    }

    print(f"=== {info['name']} ===")
    print(f"Type: {info['type']}")
    print(f"Size: {info['size'] / 1024:.1f} KB")
    print("=" * 40)
    print()

    try:
        content = path.read_text(encoding="utf-8")
        print(content)
    except UnicodeDecodeError:
        print(f"[Binary file — {info['type']} format]")


def main():
    parser = argparse.ArgumentParser(description="Manage Mycelium .raw/ directory")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("scan", help="Scan for new/modified files")
    sub.add_parser("list", help="List all files")
    sub.add_parser("types", help="Show file type statistics")

    read_p = sub.add_parser("read", help="Read file content")
    read_p.add_argument("file", help="File name or path")

    parser.add_argument("--dir", "-d", default=".raw", help="Raw directory (default: .raw)")

    args = parser.parse_args()

    if args.command == "scan":
        scan(args.dir)
    elif args.command == "list":
        list_files(args.dir)
    elif args.command == "types":
        types(args.dir)
    elif args.command == "read":
        read_file(args.file, args.dir)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
