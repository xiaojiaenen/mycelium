#!/usr/bin/env python3
"""
Read source files and convert to Markdown using markitdown.

Supported formats:
- PDF (.pdf)
- Word (.docx)
- PowerPoint (.pptx)
- Excel (.xlsx)
- HTML (.html, .htm)
- Images (.png, .jpg, .gif, .bmp, .webp) - with OCR
- Audio (.mp3, .wav, .m4a) - with transcription
- Markdown (.md)
- Text (.txt)
- CSV (.csv)
- JSON (.json)
- XML (.xml)
- ZIP (.zip)
- EPUB (.epub)
- YouTube URL
"""

import sys
import os
from pathlib import Path

def read_with_markitdown(file_path: str, output_format: str = "md") -> str:
    """Read file and convert to markdown."""
    try:
        from markitdown import MarkItDown
        md = MarkItDown()
        result = md.convert(file_path)
        return result.text_content
    except Exception as e:
        return f"Error converting file: {e}"


def get_file_info(file_path: str) -> dict:
    """Get file metadata."""
    path = Path(file_path)
    stat = path.stat()
    return {
        "name": path.name,
        "extension": path.suffix.lower(),
        "size": stat.st_size,
        "size_human": format_size(stat.st_size),
        "modified": stat.st_mtime,
    }


def format_size(size: int) -> str:
    """Format file size in human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def main():
    if len(sys.argv) < 2:
        print("Usage: read-source.py <file> [--info] [--output <file>]")
        print("")
        print("Examples:")
        print("  read-source.py article.pdf")
        print("  read-source.py video.mp4 --info")
        print("  read-source.py article.html --output article.md")
        sys.exit(1)

    file_path = sys.argv[1]
    show_info = "--info" in sys.argv
    output_file = None

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]

    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    # Show file info
    info = get_file_info(file_path)
    print(f"=== Source: {info['name']} ===")
    print(f"Type: {info['extension']}")
    print(f"Size: {info['size_human']}")
    print("=" * (len(info['name']) + 12))
    print("")

    if show_info:
        return

    # Convert to markdown
    print(f"Converting to Markdown...")
    print("")
    content = read_with_markitdown(file_path)

    if output_file:
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved to: {output_file}")
    else:
        # Print to stdout
        print(content)


if __name__ == "__main__":
    main()
