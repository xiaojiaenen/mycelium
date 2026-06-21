#!/usr/bin/env python3
"""Detect new and modified files in .raw/ compared to ingested wiki pages."""
import json
import argparse
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
from utils import SUPPORTED_EXTENSIONS

MANIFEST_FILE = ".manifest.json"


def diff_raw(wiki_dir: str = "."):
    base = Path(wiki_dir)
    raw_dir = base / ".raw"
    sources_dir = base / "wiki" / "sources"
    manifest_path = raw_dir / MANIFEST_FILE

    if not raw_dir.exists():
        print(f".raw/ not found in {wiki_dir}")
        return

    # Load manifest
    manifest = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    # Get raw files
    raw_files = {f.name for f in raw_dir.iterdir()
                 if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS}

    # Get ingested source pages
    ingested = set()
    if sources_dir.exists():
        for f in sources_dir.glob("*.md"):
            # Try to find source_file in frontmatter
            content = f.read_text(encoding="utf-8")
            for line in content.split("\n"):
                if "source_file:" in line or "来源：" in line:
                    ingested.add(f.stem)
                    break

    # File type classification
    READY_EXT = {'.txt', '.md', '.plain', '.srt', '.vtt'}  # LLM can read directly
    NEEDS_PROCESS = {'.pdf', '.docx', '.pptx', '.html', '.htm', '.epub'}  # markitdown
    NEEDS_VIDEO = {'.mp4', '.mkv', '.webm', '.avi', '.mov'}  # video.py
    NEEDS_AUDIO = {'.mp3', '.wav', '.m4a', '.flac', '.ogg'}  # video.py
    NEEDS_OCR = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}  # markitdown OCR

    new_files = []
    for name in sorted(raw_files):
        stem = Path(name).stem
        if name not in manifest and stem not in ingested:
            new_files.append(name)

    print(f"📊 Diff: .raw/ vs wiki/sources/\n")
    print(f"  Total .raw/ files:  {len(raw_files)}")
    print(f"  Ingested:           {len(raw_files) - len(new_files)}")
    print(f"  New (to ingest):    {len(new_files)}")

    if new_files:
        # Group by processing needed
        ready = []
        needs_process = []
        needs_video = []

        for f in new_files:
            ext = Path(f).suffix.lower()
            if ext in READY_EXT:
                ready.append(f)
            elif ext in NEEDS_VIDEO or ext in NEEDS_AUDIO:
                needs_video.append(f)
            else:
                needs_process.append(f)

        if ready:
            print(f"\n  ✅ Ready for ingest ({len(ready)}):")
            for f in ready:
                print(f"    {f}")

        if needs_process:
            print(f"\n  🔧 Needs processing ({len(needs_process)}):")
            for f in needs_process:
                ext = Path(f).suffix.lower()
                if ext in NEEDS_OCR:
                    print(f"    {f}  → markitdown (OCR)")
                else:
                    print(f"    {f}  → markitdown")

        if needs_video:
            print(f"\n  🎬 Needs transcription ({len(needs_video)}):")
            for f in needs_video:
                print(f"    {f}  → python3 scripts/video.py {f} -o .raw")


def main():
    parser = argparse.ArgumentParser(description="Detect new/modified files in .raw/")
    parser.add_argument("--dir", "-d", default=".", help="Wiki root directory (default: .)")
    args = parser.parse_args()
    diff_raw(args.dir)


if __name__ == "__main__":
    main()
