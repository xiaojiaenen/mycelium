#!/usr/bin/env python3
"""
Watch .raw/ directory for new files and auto-trigger ingest.
Cross-platform: uses polling (no OS-specific deps).
"""
import os
import sys
import time
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import SUPPORTED_EXTENSIONS, file_hash

MANIFEST_FILE = ".manifest.json"


def get_file_hash(file_path: str) -> str:
    h = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(manifest_path: Path) -> dict:
    if manifest_path.exists():
        import json
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    return {}


def save_manifest(manifest_path: Path, data: dict):
    import json
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def scan_files(raw_dir: Path) -> dict:
    """Return {filename: md5_hash} for all supported files."""
    files = {}
    for f in raw_dir.iterdir():
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
            files[f.name] = get_file_hash(str(f))
    return files


def watch(wiki_dir: str = ".", interval: int = 5, callback=None):
    """Watch .raw/ for new files, poll every `interval` seconds."""
    base = Path(wiki_dir)
    raw_dir = base / ".raw"
    manifest_path = raw_dir / MANIFEST_FILE

    if not raw_dir.exists():
        print(f"❌ .raw/ not found in {wiki_dir}")
        return

    manifest = load_manifest(manifest_path)
    current_files = scan_files(raw_dir)

    print(f"👀 Watching .raw/ every {interval}s (Ctrl+C to stop)")
    print(f"   Directory: {raw_dir.resolve()}")
    print(f"   Files tracked: {len(manifest)}")
    print()

    try:
        while True:
            time.sleep(interval)
            new_files = scan_files(raw_dir)

            # Detect new files
            for name, hash_val in new_files.items():
                if name not in manifest:
                    print(f"🆕 New: {name}")
                    if callback:
                        callback(str(raw_dir / name), wiki_dir)
                    else:
                        print(f"   → Run: python3 scripts/ingest-raw.py read {raw_dir / name}")

            # Detect modified files
            for name, hash_val in new_files.items():
                if name in manifest and manifest[name].get("hash") != hash_val:
                    print(f"📝 Modified: {name}")
                    if callback:
                        callback(str(raw_dir / name), wiki_dir)

            current_files = new_files

    except KeyboardInterrupt:
        print("\n\nStopped watching.")


def main():
    parser = argparse.ArgumentParser(description="Watch .raw/ for new files")
    parser.add_argument("--dir", "-d", default=".", help="Wiki root directory")
    parser.add_argument("--interval", "-i", type=int, default=5,
                        help="Poll interval in seconds (default: 5)")
    args = parser.parse_args()
    watch(args.dir, args.interval)


if __name__ == "__main__":
    main()
