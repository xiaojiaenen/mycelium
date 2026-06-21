#!/bin/bash
# Auto-commit wiki changes with descriptive messages

set -e

WIKI_DIR="${1:-.}"
MESSAGE="${2:-auto: update wiki}"

cd "$WIKI_DIR"

# Check if git repo
if ! git rev-parse --is-inside-work-tree &>/dev/null; then
    echo "Not a git repository. Run init.sh first."
    exit 1
fi

# Stage all changes
git add -A

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "No changes to commit."
    exit 0
fi

# Commit
git commit -q -m "$MESSAGE"
echo "✅ Committed: $MESSAGE"
