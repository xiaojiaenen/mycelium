#!/bin/bash
# Read source file content based on type

FILE="$1"

if [ ! -f "$FILE" ]; then
    echo "Error: File not found: $FILE"
    exit 1
fi

EXTENSION="${FILE##*.}"
FILENAME=$(basename "$FILE")

echo "=== Source: $FILENAME ==="
echo "Type: $EXTENSION"
echo "Size: $(ls -lh "$FILE" | awk '{print $5}')"
echo "Modified: $(stat -f "%Sm" "$FILE")"
echo "========================"
echo ""

case "$EXTENSION" in
    txt|md|markdown)
        echo "[TEXT FILE]"
        cat "$FILE"
        ;;
    pdf)
        echo "[PDF FILE]"
        if command -v pdftotext &> /dev/null; then
            pdftotext "$FILE" -
        else
            echo "Error: pdftotext not installed"
            echo "Install: brew install poppler"
        fi
        ;;
    html|htm)
        echo "[HTML FILE]"
        if command -v lynx &> /dev/null; then
            lynx -dump "$FILE"
        elif command -v w3m &> /dev/null; then
            w3m -dump "$FILE"
        else
            echo "Error: lynx or w3m not installed"
            echo "Install: brew install lynx"
        fi
        ;;
    srt|vtt)
        echo "[SUBTITLE FILE]"
        cat "$FILE"
        ;;
    mp4|mkv|webm|avi)
        echo "[VIDEO FILE]"
        echo "Duration: $(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$FILE" 2>/dev/null || echo 'unknown')"
        echo ""
        echo "To extract subtitles, use video-captions skill:"
        echo "  python3 ~/.claude/skills/video-captions/scripts/extract.py \"$FILE\""
        ;;
    mp3|wav|flac|m4a)
        echo "[AUDIO FILE]"
        echo "Duration: $(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$FILE" 2>/dev/null || echo 'unknown')"
        echo ""
        echo "To transcribe, use video-captions skill:"
        echo "  python3 ~/.claude/skills/video-captions/scripts/extract.py \"$FILE\""
        ;;
    png|jpg|jpeg|gif|bmp|webp)
        echo "[IMAGE FILE]"
        if command -v tesseract &> /dev/null; then
            echo "OCR Text:"
            tesseract "$FILE" -
        else
            echo "Error: tesseract not installed"
            echo "Install: brew install tesseract"
        fi
        ;;
    docx)
        echo "[DOCX FILE]"
        if command -v pandoc &> /dev/null; then
            pandoc "$FILE" -t plain
        else
            echo "Error: pandoc not installed"
            echo "Install: brew install pandoc"
        fi
        ;;
    pptx)
        echo "[PPTX FILE]"
        if command -v pandoc &> /dev/null; then
            pandoc "$FILE" -t plain
        else
            echo "Error: pandoc not installed"
            echo "Install: brew install pandoc"
        fi
        ;;
    url)
        echo "[URL FILE]"
        URL=$(cat "$FILE" | grep -i "url=" | head -1 | cut -d= -f2)
        if [ -z "$URL" ]; then
            URL=$(cat "$FILE")
        fi
        echo "URL: $URL"
        echo ""
        if command -v curl &> /dev/null; then
            curl -s "$URL" | lynx -dump -stdin 2>/dev/null || curl -s "$URL"
        fi
        ;;
    *)
        echo "[UNKNOWN TYPE]"
        echo "Trying to read as text..."
        cat "$FILE" 2>/dev/null || echo "Cannot read file"
        ;;
esac
