#!/usr/bin/env python3
"""
Example: Read various file types using markitdown.

This demonstrates how the ingest system reads different file formats.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from ingest_raw import ContentReader, get_file_info, format_size


def test_read(file_path: str):
    """Test reading a file."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    info = get_file_info(file_path)
    print(f"\n{'='*60}")
    print(f"File: {info['name']}")
    print(f"Type: {info['extension']}")
    print(f"Size: {format_size(info['size'])}")
    print(f"{'='*60}\n")

    reader = ContentReader()

    # Try markitdown first
    try:
        content = reader.read(file_path)
        print("Content (via markitdown):")
        print("-" * 40)
        # Show first 500 chars
        if len(content) > 500:
            print(content[:500])
            print(f"\n... ({len(content)} chars total)")
        else:
            print(content)
    except Exception as e:
        print(f"markitdown failed: {e}")
        print("\nFallback to plain text:")
        content = reader.read_as_text(file_path)
        if len(content) > 500:
            print(content[:500])
            print(f"\n... ({len(content)} chars total)")
        else:
            print(content)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: test-read.py <file1> [file2] ...")
        print("\nExample:")
        print("  test-read.py article.pdf document.docx webpage.html")
        sys.exit(1)

    for file_path in sys.argv[1:]:
        test_read(file_path)
