#!/usr/bin/env python3
"""
Simple wrapper for fetching web content.

Usage:
    python3 fetch.py <url>                    # Fetch and save to .raw/
    python3 fetch.py <url> -o output.md       # Save to specific path
    python3 fetch.py <url> --stealth          # Bypass anti-bot
    python3 fetch.py <url> --selector article # Use CSS selector
    python3 fetch.py <url> --raw              # Save raw HTML
"""

import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from fetch_web import main
except ImportError:
    print("Error: Cannot import fetch_web module")
    print("Make sure scrapling is installed:")
    print("  pip install 'scrapling[all]' && scrapling install")
    sys.exit(1)

if __name__ == "__main__":
    main()
