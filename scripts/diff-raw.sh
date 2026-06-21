#!/bin/bash
# Detect new and modified files in .raw/

RAW_DIR="${1:-.raw}"
WIKI_DIR="wiki"
LOG_FILE="$WIKI_DIR/log.md"

if [ ! -d "$RAW_DIR" ]; then
    echo "Error: .raw/ directory not found"
    exit 1
fi

echo "=== Scanning $RAW_DIR ==="
echo ""

# Get all source files
echo "## All Source Files"
echo ""
find "$RAW_DIR" -type f | while read -r file; do
    filename=$(basename "$file")
    modified=$(stat -f "%Sm" "$file")
    size=$(ls -lh "$file" | awk '{print $5}')
    echo "- $filename ($size, modified: $modified)"
done

echo ""
echo "## Status Check"
echo ""

# Check which files have been ingested
echo "### Ingested Files"
echo ""
if [ -d "$WIKI_DIR/sources" ]; then
    find "$WIKI_DIR/sources" -name "*.md" -type f | while read -r wiki_file; do
        # Extract source filename from wiki page
        source_ref=$(grep -i "source_file\|字幕文件\|来源文件" "$wiki_file" 2>/dev/null | head -1)
        if [ -n "$source_ref" ]; then
            echo "- $(basename "$wiki_file") → $source_ref"
        fi
    done
else
    echo "No wiki/sources/ directory yet"
fi

echo ""
echo "### New Files (not ingested)"
echo ""
find "$RAW_DIR" -type f | while read -r file; do
    filename=$(basename "$file")
    # Check if there's a corresponding wiki page
    # Try multiple naming patterns
    found=0
    for pattern in "$filename" "${filename%.*}" "*${filename%.*}*"; do
        if find "$WIKI_DIR/sources" -name "*.md" 2>/dev/null | grep -qi "$pattern"; then
            found=1
            break
        fi
    done
    if [ "$found" -eq 0 ]; then
        echo "- $filename (NEW)"
    fi
done

echo ""
echo "### Modified Files (source newer than wiki)"
echo ""
find "$RAW_DIR" -type f | while read -r file; do
    filename=$(basename "$file")
    file_mod=$(stat -f "%m" "$file")

    # Find corresponding wiki page
    for wiki_file in "$WIKI_DIR/sources"/*.md; do
        if [ -f "$wiki_file" ]; then
            # Check if wiki page mentions this source
            if grep -qi "$filename" "$wiki_file" 2>/dev/null; then
                wiki_mod=$(stat -f "%m" "$wiki_file")
                if [ "$file_mod" -gt "$wiki_mod" ]; then
                    echo "- $filename (MODIFIED after wiki update)"
                fi
            fi
        fi
    done
done

echo ""
echo "## Summary"
echo ""

total=$(find "$RAW_DIR" -type f | wc -l | tr -d ' ')
ingested=$(find "$WIKI_DIR/sources" -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')

echo "- Total files in .raw/: $total"
echo "- Wiki source pages: $ingested"
echo "- Potential new files: $((total - ingested))"
