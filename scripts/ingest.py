#!/usr/bin/env python3
"""
Unified ingest entry point for Mycelium.
Detect file type → read content → output markdown ready for LLM processing.
"""
import sys
import importlib.util
import argparse
from pathlib import Path

# Reuse existing reader (filename has hyphen, need importlib)
_spec = importlib.util.spec_from_file_location(
    "ingest_raw", Path(__file__).parent / "ingest-raw.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
ContentReader = _mod.ContentReader
Manifest = _mod.Manifest
RawScanner = _mod.RawScanner
get_file_info = _mod.get_file_info
SUPPORTED_EXTENSIONS = _mod.SUPPORTED_EXTENSIONS


def ingest_file(file_path: str, wiki_dir: str = ".") -> dict:
    """Read a file and return structured info for LLM to create wiki notes."""
    path = Path(file_path)
    if not path.exists():
        # Try in .raw/
        path = Path(wiki_dir) / ".raw" / file_path
    if not path.exists():
        return {"error": f"File not found: {file_path}"}

    info = get_file_info(str(path))
    reader = ContentReader()
    content = reader.read(str(path))

    # Extract metadata from content (if available)
    metadata = {
        "file": info["name"],
        "type": info["extension"],
        "size": f"{info['size'] / 1024:.1f} KB",
        "content_length": len(content),
    }

    # Auto-detect source type from extension
    ext = info["extension"].lower()
    source_type_map = {
        ".md": "article", ".txt": "article", ".rst": "article",
        ".pdf": "paper", ".docx": "document", ".pptx": "presentation",
        ".srt": "subtitle", ".vtt": "subtitle", ".plain": "transcript",
        ".mp4": "video", ".mkv": "video", ".webm": "video",
        ".mp3": "audio", ".wav": "audio", ".m4a": "audio",
        ".html": "webpage", ".htm": "webpage",
        ".epub": "book",
        ".png": "image", ".jpg": "image", ".jpeg": "image",
    }
    metadata["source_type"] = source_type_map.get(ext, "article")

    # Output
    print(f"📄 File: {metadata['file']}")
    print(f"   Type: {metadata['source_type']} ({metadata['type']})")
    print(f"   Size: {metadata['size']}")
    print(f"   Content: {metadata['content_length']} chars")
    print()
    print("=" * 60)
    print(content[:5000])  # First 5000 chars
    if len(content) > 5000:
        print(f"\n... ({len(content) - 5000} more chars)")
    print("=" * 60)

    return metadata


def ingest_url(url: str, wiki_dir: str = ".") -> dict:
    """Download URL content and prepare for ingest."""
    raw_dir = Path(wiki_dir) / ".raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    # Check if it's a video URL
    import re
    video_patterns = [
        r"bilibili\.com/video/",
        r"(youtube\.com/watch|youtu\.be/)",
        r"douyin\.com/video/",
        r"tiktok\.com/",
    ]

    if any(re.search(p, url) for p in video_patterns):
        print(f"🎬 Video detected: {url}")
        print(f"   Use: python3 scripts/video.py \"{url}\" -o {raw_dir}")
        return {"type": "video", "url": url, "action": "use video.py"}

    # Web page - try fetch-web.py
    print(f"🌐 Web page: {url}")
    fetch_script = Path(__file__).parent / "fetch-web.py"
    if fetch_script.exists():
        print(f"   Use: python3 scripts/fetch-web.py \"{url}\"")
        return {"type": "webpage", "url": url, "action": "use fetch-web.py"}
    else:
        print(f"   fetch-web.py not found")
        return {"type": "webpage", "url": url, "action": "install scrapling"}


def ingest_all(wiki_dir: str = "."):
    """List all uningested files in .raw/."""
    raw_dir = Path(wiki_dir) / ".raw"
    manifest_path = raw_dir / ".manifest.json"

    if not raw_dir.exists():
        print(f"❌ .raw/ not found in {wiki_dir}")
        return

    manifest = Manifest(str(manifest_path))
    scanner = RawScanner(str(raw_dir))
    files = scanner.scan()

    new_files = []
    for f in files:
        name = f['name']
        file_hash = f.get('hash', '')
        if not manifest.is_ingested(name, file_hash):
            new_files.append(f)

    if not new_files:
        print("✅ All files already ingested.")
        return

    print(f"📋 {len(new_files)} file(s) to ingest:\n")
    for f in new_files:
        name = f['name']
        size = f.get('size', 0)
        size_str = f"{size / 1024:.1f} KB" if size > 1024 else f"{size} B"
        print(f"  🆕 {name:40s} {size_str:>10s}")

    print(f"\nTell Claude: ingest all")


def main():
    parser = argparse.ArgumentParser(description="Unified ingest entry point")
    parser.add_argument("target", nargs="?", help="File path, URL, or 'all'")
    parser.add_argument("--dir", "-d", default=".", help="Wiki root directory")
    args = parser.parse_args()

    if not args.target:
        ingest_all(args.dir)
        return

    target = args.target

    if target == "all":
        ingest_all(args.dir)
    elif target.startswith("http://") or target.startswith("https://"):
        ingest_url(target, args.dir)
    else:
        ingest_file(target, args.dir)


if __name__ == "__main__":
    main()
