#!/bin/bash
# Comprehensive .raw/ management script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAW_DIR="${1:-.raw}"
WIKI_DIR="wiki"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

show_help() {
    echo "Usage: raw.sh [command] [options]"
    echo ""
    echo "Commands:"
    echo "  scan      Scan .raw/ for new/modified files"
    echo "  read      Read file content based on type"
    echo "  list      List all files in .raw/"
    echo "  types     Show file type statistics"
    echo "  status    Show ingest status"
    echo "  help      Show this help"
    echo ""
    echo "Examples:"
    echo "  raw.sh scan"
    echo "  raw.sh read article.pdf"
    echo "  raw.sh status"
}

scan_raw() {
    echo -e "${BLUE}=== Scanning $RAW_DIR ===${NC}"
    echo ""

    if [ ! -d "$RAW_DIR" ]; then
        echo -e "${RED}Error: $RAW_DIR not found${NC}"
        exit 1
    fi

    # Get all files
    FILES=$(find "$RAW_DIR" -type f -not -name ".*" | sort)
    TOTAL=$(echo "$FILES" | wc -l | tr -d ' ')

    echo -e "${GREEN}Found $TOTAL files${NC}"
    echo ""

    # Check each file
    NEW=0
    MODIFIED=0
    INGESTED=0

    echo "$FILES" | while read -r file; do
        filename=$(basename "$file")
        ext="${file##*.}"
        size=$(ls -lh "$file" | awk '{print $5}')
        modified=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$file")

        # Check if ingested
        ingested=0
        if [ -d "$WIKI_DIR/sources" ]; then
            for wiki_file in "$WIKI_DIR/sources"/*.md; do
                if [ -f "$wiki_file" ] && grep -qi "$filename" "$wiki_file" 2>/dev/null; then
                    ingested=1
                    break
                fi
            done
        fi

        if [ "$ingested" -eq 1 ]; then
            echo -e "  ${GREEN}✓${NC} $filename ($size, $modified) - ingested"
        else
            echo -e "  ${YELLOW}○${NC} $filename ($size, $modified) - ${YELLOW}NOT INGESTED${NC}"
        fi
    done

    echo ""
    echo -e "${BLUE}=== Summary ===${NC}"
    echo "Total files: $TOTAL"
}

read_file() {
    FILE="$1"

    if [ -z "$FILE" ]; then
        echo -e "${RED}Error: No file specified${NC}"
        echo "Usage: raw.sh read <filename>"
        exit 1
    fi

    # Try to find file in .raw/
    if [ -f "$RAW_DIR/$FILE" ]; then
        FILE="$RAW_DIR/$FILE"
    elif [ ! -f "$FILE" ]; then
        echo -e "${RED}Error: File not found: $FILE${NC}"
        exit 1
    fi

    bash "$SCRIPT_DIR/read-source.sh" "$FILE"
}

list_files() {
    echo -e "${BLUE}=== Files in $RAW_DIR ===${NC}"
    echo ""

    if [ ! -d "$RAW_DIR" ]; then
        echo -e "${RED}Error: $RAW_DIR not found${NC}"
        exit 1
    fi

    find "$RAW_DIR" -type f -not -name ".*" | sort | while read -r file; do
        filename=$(basename "$file")
        ext="${file##*.}"
        size=$(ls -lh "$file" | awk '{print $5}')
        modified=$(stat -f "%Sm" -t "%Y-%m-%d" "$file")
        echo "  $filename ($ext, $size, $modified)"
    done
}

show_types() {
    echo -e "${BLUE}=== File Types in $RAW_DIR ===${NC}"
    echo ""

    if [ ! -d "$RAW_DIR" ]; then
        echo -e "${RED}Error: $RAW_DIR not found${NC}"
        exit 1
    fi

    find "$RAW_DIR" -type f -not -name ".*" | while read -r file; do
        echo "${file##*.}"
    done | sort | uniq -c | sort -rn | while read -r count ext; do
        echo "  $count  $ext"
    done
}

show_status() {
    echo -e "${BLUE}=== Ingest Status ===${NC}"
    echo ""

    if [ ! -d "$RAW_DIR" ]; then
        echo -e "${RED}Error: $RAW_DIR not found${NC}"
        exit 1
    fi

    # Count files
    TOTAL=$(find "$RAW_DIR" -type f -not -name ".*" | wc -l | tr -d ' ')
    WIKI_PAGES=0
    if [ -d "$WIKI_DIR/sources" ]; then
        WIKI_PAGES=$(find "$WIKI_DIR/sources" -name "*.md" -type f | wc -l | tr -d ' ')
    fi

    echo "Files in .raw/: $TOTAL"
    echo "Wiki source pages: $WIKI_PAGES"
    echo ""

    # Check for uningested
    echo -e "${YELLOW}Uningested files:${NC}"
    find "$RAW_DIR" -type f -not -name ".*" | while read -r file; do
        filename=$(basename "$file")
        ingested=0
        if [ -d "$WIKI_DIR/sources" ]; then
            for wiki_file in "$WIKI_DIR/sources"/*.md; do
                if [ -f "$wiki_file" ] && grep -qi "$filename" "$wiki_file" 2>/dev/null; then
                    ingested=1
                    break
                fi
            done
        fi
        if [ "$ingested" -eq 0 ]; then
            echo "  - $filename"
        fi
    done
}

# Main command handling
case "${1:-help}" in
    scan)
        scan_raw
        ;;
    read)
        read_file "$2"
        ;;
    list)
        list_files
        ;;
    types)
        show_types
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
