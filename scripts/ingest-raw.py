#!/usr/bin/env python3
"""
Smart ingest: scan .raw/ directory and prepare files for LLM processing.

Features:
- Auto-detect new/modified files using manifest
- Convert files to markdown using markitdown
- Track ingest status
"""

import os
import sys
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Supported extensions
SUPPORTED_EXTENSIONS = {
    # Text
    '.txt', '.md', '.markdown', '.rst',
    # Documents
    '.pdf', '.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls',
    # Web
    '.html', '.htm', '.mhtml',
    # Data
    '.csv', '.json', '.xml', '.yaml', '.yml',
    # Subtitles
    '.srt', '.vtt', '.ass', '.sub',
    # Ebooks
    '.epub',
    # Images (OCR)
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff',
    # Audio (transcription)
    '.mp3', '.wav', '.m4a', '.flac', '.ogg',
    # Video (subtitle extraction)
    '.mp4', '.mkv', '.webm', '.avi', '.mov',
    # Archives
    '.zip',
}


def get_file_hash(file_path: str) -> str:
    """Calculate MD5 hash of file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_file_info(file_path: str) -> Dict:
    """Get file metadata."""
    path = Path(file_path)
    stat = path.stat()
    return {
        "name": path.name,
        "path": str(path),
        "extension": path.suffix.lower(),
        "size": stat.st_size,
        "modified": stat.st_mtime,
        "hash": get_file_hash(file_path),
    }


def format_size(size: int) -> str:
    """Format file size in human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


class Manifest:
    """Track ingested files."""

    def __init__(self, manifest_path: str):
        self.path = Path(manifest_path)
        self.data = self._load()

    def _load(self) -> Dict:
        """Load manifest from file."""
        if self.path.exists():
            with open(self.path, 'r') as f:
                return json.load(f)
        return {}

    def save(self):
        """Save manifest to file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, 'w') as f:
            json.dump(self.data, f, indent=2)

    def is_ingested(self, file_name: str, file_hash: str) -> bool:
        """Check if file is already ingested with same hash."""
        if file_name in self.data:
            return self.data[file_name].get('hash') == file_hash
        return False

    def mark_ingested(self, file_name: str, file_hash: str, wiki_page: str = None):
        """Mark file as ingested."""
        self.data[file_name] = {
            'hash': file_hash,
            'ingested_at': datetime.now().isoformat(),
            'wiki_page': wiki_page,
        }
        self.save()

    def get_ingested(self, file_name: str) -> Optional[Dict]:
        """Get ingest info for file."""
        return self.data.get(file_name)


class RawScanner:
    """Scan .raw/ directory for files."""

    def __init__(self, raw_dir: str):
        self.raw_dir = Path(raw_dir)

    def scan(self) -> List[Dict]:
        """Scan for all supported files."""
        files = []
        if not self.raw_dir.exists():
            return files

        for file_path in self.raw_dir.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                ext = file_path.suffix.lower()
                if ext in SUPPORTED_EXTENSIONS:
                    files.append(get_file_info(str(file_path)))

        return sorted(files, key=lambda x: x['name'])

    def get_new_files(self, manifest: Manifest) -> List[Dict]:
        """Get files not yet ingested."""
        all_files = self.scan()
        new_files = []
        for file_info in all_files:
            if not manifest.is_ingested(file_info['name'], file_info['hash']):
                new_files.append(file_info)
        return new_files

    def get_modified_files(self, manifest: Manifest) -> List[Dict]:
        """Get files that changed since last ingest."""
        all_files = self.scan()
        modified_files = []
        for file_info in all_files:
            ingested = manifest.get_ingested(file_info['name'])
            if ingested and ingested.get('hash') != file_info['hash']:
                modified_files.append(file_info)
        return modified_files


class ContentReader:
    """Read file content using markitdown."""

    def __init__(self):
        self._md = None

    @property
    def md(self):
        if self._md is None:
            try:
                from markitdown import MarkItDown
                self._md = MarkItDown()
            except ImportError:
                print("Error: markitdown not installed")
                print("Install: pip install markitdown")
                sys.exit(1)
        return self._md

    def read(self, file_path: str) -> str:
        """Read file and convert to markdown."""
        try:
            result = self.md.convert(file_path)
            return result.text_content
        except Exception as e:
            return f"Error converting file: {e}"

    def read_as_text(self, file_path: str) -> str:
        """Read file as plain text (fallback)."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                return f"Error reading file: {e}"


def print_scan_results(files: List[Dict], manifest: Manifest, raw_dir: str):
    """Print scan results in a nice format."""
    scanner = RawScanner(raw_dir)
    new_files = scanner.get_new_files(manifest)
    modified_files = scanner.get_modified_files(manifest)

    print(f"=== Scanning {raw_dir} ===")
    print("")

    # File type statistics
    type_counts = {}
    for f in files:
        ext = f['extension']
        type_counts[ext] = type_counts.get(ext, 0) + 1

    print("File types:")
    for ext, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {ext}: {count}")
    print("")

    # Status for each file
    print("Files:")
    for f in files:
        name = f['name']
        size = format_size(f['size'])
        ext = f['extension']

        if any(nf['name'] == name for nf in new_files):
            status = "🆕 NEW"
        elif any(mf['name'] == name for mf in modified_files):
            status = "📝 MODIFIED"
        else:
            status = "✓  INGESTED"

        print(f"  {status}  {name} ({size})")

    print("")
    print("=== Summary ===")
    print(f"Total files: {len(files)}")
    print(f"New: {len(new_files)}")
    print(f"Modified: {len(modified_files)}")
    print(f"Ingested: {len(files) - len(new_files) - len(modified_files)}")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  ingest-raw.py scan [raw_dir]           - Scan for files")
        print("  ingest-raw.py read <file>               - Read file content")
        print("  ingest-raw.py new [raw_dir]             - List new files")
        print("  ingest-raw.py mark <file> [wiki_page]   - Mark as ingested")
        print("")
        print("Examples:")
        print("  ingest-raw.py scan")
        print("  ingest-raw.py read article.pdf")
        print("  ingest-raw.py new")
        print("  ingest-raw.py mark article.pdf wiki/sources/article.md")
        sys.exit(1)

    command = sys.argv[1]
    raw_dir = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('-') else '.raw'
    manifest = Manifest(os.path.join(raw_dir, '.manifest.json'))

    if command == 'scan':
        scanner = RawScanner(raw_dir)
        files = scanner.scan()
        print_scan_results(files, manifest, raw_dir)

    elif command == 'read':
        if len(sys.argv) < 3:
            print("Error: No file specified")
            sys.exit(1)
        file_path = sys.argv[2]
        if not os.path.exists(file_path):
            # Try in .raw/
            file_path = os.path.join(raw_dir, file_path)
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}")
            sys.exit(1)

        reader = ContentReader()
        info = get_file_info(file_path)
        print(f"=== {info['name']} ===")
        print(f"Type: {info['extension']}")
        print(f"Size: {format_size(info['size'])}")
        print("=" * (len(info['name']) + 8))
        print("")
        content = reader.read(file_path)
        print(content)

    elif command == 'new':
        scanner = RawScanner(raw_dir)
        new_files = scanner.get_new_files(manifest)
        if not new_files:
            print("No new files found.")
        else:
            print(f"New files ({len(new_files)}):")
            for f in new_files:
                print(f"  - {f['name']} ({format_size(f['size'])})")

    elif command == 'mark':
        if len(sys.argv) < 3:
            print("Error: No file specified")
            sys.exit(1)
        file_name = sys.argv[2]
        wiki_page = sys.argv[3] if len(sys.argv) > 3 else None

        # Find file in .raw/
        file_path = os.path.join(raw_dir, file_name)
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}")
            sys.exit(1)

        file_info = get_file_info(file_path)
        manifest.mark_ingested(file_name, file_info['hash'], wiki_page)
        print(f"✓ Marked as ingested: {file_name}")
        if wiki_page:
            print(f"  Wiki page: {wiki_page}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
