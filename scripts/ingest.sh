#!/bin/bash
# Smart ingest: detect new/modified files and prepare for LLM processing

RAW_DIR="${1:-.raw}"
WIKI_DIR="wiki"
MANIFEST_FILE=".raw/.manifest"

# Create manifest if not exists
if [ ! -f "$MANIFEST_FILE" ]; then
    touch "$MANIFEST_FILE"
fi

echo "=== Mycelium Ingest Scanner ==="
echo ""

# Function to get file hash
get_hash() {
    md5 -q "$1" 2>/dev/null || md5sum "$1" 2>/dev/null | cut -d' ' -f1
}

# Function to check if file is in manifest
in_manifest() {
    grep -q "^$1:" "$MANIFEST_FILE" 2>/dev/null
}

# Function to get manifest hash
get_manifest_hash() {
    grep "^$1:" "$MANIFEST_FILE" 2>/dev/null | cut -d: -f2
}

# Function to update manifest
update_manifest() {
    local file="$1"
    local hash="$2"
    local timestamp=$(date +%Y-%m-%d)

    # Remove old entry
    sed -i '' "/^$(basename "$file"):/d" "$MANIFEST_FILE" 2>/dev/null

    # Add new entry
    echo "$(basename "$file"):$hash:$timestamp" >> "$MANIFEST_FILE"
}

# Scan for changes
NEW_FILES=""
MODIFIED_FILES=""
UNCHANGED_FILES=""

echo "## Scanning $RAW_DIR..."
echo ""

find "$RAW_DIR" -type f -not -name ".*" | sort | while read -r file; do
    filename=$(basename "$file")
    current_hash=$(get_hash "$file")

    if in_manifest "$filename"; then
        manifest_hash=$(get_manifest_hash "$filename")
        if [ "$current_hash" != "$manifest_hash" ]; then
            echo "📝 MODIFIED: $filename"
            MODIFIED_FILES="$MODIFIED_FILES $file"
        else
            echo "✓  UNCHANGED: $filename"
            UNCHANGED_FILES="$UNCHANGED_FILES $file"
        fi
    else
        echo "🆕 NEW: $filename"
        NEW_FILES="$NEW_FILES $file"
    fi
done

echo ""
echo "## Summary"
echo ""
echo "- New files: $(echo "$NEW_FILES" | wc -w | tr -d ' ')"
echo "- Modified files: $(echo "$MODIFIED_FILES" | wc -w | tr -d ' ')"
echo "- Unchanged files: $(echo "$UNCHANGED_FILES" | wc -w | tr -d ' ')"

echo ""
echo "## Files to Process"
echo ""

# Output files that need processing
if [ -n "$NEW_FILES" ]; then
    echo "### New Files (need full ingest)"
    for file in $NEW_FILES; do
        echo "- $(basename "$file")"
    done
    echo ""
fi

if [ -n "$MODIFIED_FILES" ]; then
    echo "### Modified Files (need update)"
    for file in $MODIFIED_FILES; do
        echo "- $(basename "$file")"
    done
    echo ""
fi

# Show file types
echo "## File Types"
echo ""
find "$RAW_DIR" -type f -not -name ".*" | while read -r file; do
    ext="${file##*.}"
    echo "$ext"
done | sort | uniq -c | sort -rn

echo ""
echo "## Next Steps"
echo ""
echo "Tell Claude:"
echo "  1. \"ingest new\" - Process only new files"
echo "  2. \"ingest modified\" - Process only modified files"
echo "  3. \"ingest all\" - Process everything"
echo "  4. \"ingest [filename]\" - Process specific file"
