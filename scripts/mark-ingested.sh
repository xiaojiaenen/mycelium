#!/bin/bash
# Mark file as ingested in manifest

RAW_DIR="${1:-.raw}"
FILE="$2"
MANIFEST_FILE="$RAW_DIR/.manifest"

if [ -z "$FILE" ]; then
    echo "Usage: mark-ingested.sh [raw_dir] <filename>"
    exit 1
fi

# Get file hash
if [ -f "$RAW_DIR/$FILE" ]; then
    FILE_PATH="$RAW_DIR/$FILE"
elif [ -f "$FILE" ]; then
    FILE_PATH="$FILE"
    FILE=$(basename "$FILE")
else
    echo "Error: File not found: $FILE"
    exit 1
fi

# Calculate hash
HASH=$(md5 -q "$FILE_PATH" 2>/dev/null || md5sum "$FILE_PATH" 2>/dev/null | cut -d' ' -f1)
TIMESTAMP=$(date +%Y-%m-%d)

# Create manifest if not exists
touch "$MANIFEST_FILE"

# Remove old entry if exists
sed -i '' "/^${FILE}:/d" "$MANIFEST_FILE" 2>/dev/null

# Add new entry
echo "${FILE}:${HASH}:${TIMESTAMP}" >> "$MANIFEST_FILE"

echo "✓ Marked as ingested: $FILE"
echo "  Hash: $HASH"
echo "  Date: $TIMESTAMP"
