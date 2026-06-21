#!/bin/bash
# Initialize a new Mycelium knowledge base

set -e

WIKI_NAME="${1:-My Knowledge Base}"
CURRENT_DIR="$(pwd)"

echo "Initializing Mycelium: $WIKI_NAME"
echo "Location: $CURRENT_DIR"

# Create directory structure
mkdir -p .raw
mkdir -p wiki/{sources,concepts,entities,comparisons,questions,contradictions,meta}

# Create index.md
cat > wiki/index.md << 'EOF'
---
type: meta
title: "Wiki Index"
created: YYYY-MM-DD
tags:
  - meta
  - index
status: evergreen
---

# Wiki Index

Last updated: YYYY-MM-DD

---

## Sources

[Source notes will appear here]

---

## Concepts

[Concept notes will appear here]

---

## Entities

[Entity notes will appear here]

---

## Comparisons

[Comparison notes will appear here]

---

## Questions

[Question notes will appear here]

---

## Contradictions

[Contradiction notes will appear here]

---

## Topic Clusters

[Auto-generated topic clusters will appear here]
EOF

# Create index-tags.md (auto-generated tag index)
cat > wiki/index-tags.md << 'EOF'
---
type: meta
title: "Tag Index"
created: YYYY-MM-DD
tags:
  - meta
  - index
  - tags
status: evergreen
---

# Tag Index

Auto-generated from note frontmatter. Updated on every lint.

---

## Tags

[Tag clusters will appear here]
EOF

# Create index-topics.md (auto-generated topic clusters)
cat > wiki/index-topics.md << 'EOF'
---
type: meta
title: "Topic Clusters"
created: YYYY-MM-DD
tags:
  - meta
  - index
  - topics
status: evergreen
---

# Topic Clusters

Auto-generated from wikilink density analysis. Updated on every lint.

---

## Clusters

[Topic clusters will appear here]
EOF

# Create log.md
cat > wiki/log.md << 'EOF'
---
type: meta
title: "Operation Log"
created: YYYY-MM-DD
tags:
  - meta
  - log
status: evergreen
---

# Operation Log

Append-only. New entries go at the TOP. Never edit past entries.

Entry format: `## [YYYY-MM-DD] operation | Title`

---

EOF

# Create hot.md
cat > wiki/hot.md << 'EOF'
---
type: meta
title: "Hot Cache"
created: YYYY-MM-DD
tags:
  - meta
  - hot-cache
status: evergreen
---

# Recent Context

Last updated: YYYY-MM-DD

## Key Facts
- [Most important recent fact]

## Recent Changes
- Wiki initialized

## Active Threads
- [Current research topic]
EOF

# Create CLAUDE.md
cat > CLAUDE.md << EOF
# $WIKI_NAME: Mycelium Knowledge Base

Created: $(date +%Y-%m-%d)

## Structure

\`\`\`
.raw/           # Source files (immutable)
wiki/
├── index.md    # Master catalog
├── index-tags.md    # Auto-generated tag index
├── index-topics.md  # Auto-generated topic clusters
├── log.md      # Operation log
├── hot.md      # Recent context cache
├── sources/    # Source summaries
├── concepts/   # Concept explanations
├── entities/   # People, orgs, products
├── comparisons/ # Side-by-side analyses
├── contradictions/ # Cross-source conflicts
└── questions/  # Filed answers
\`\`\`

## Conventions

- All notes use YAML frontmatter: type, status, created, tags
- Wikilinks use [[Note Name]] format
- .raw/ contains source documents: never modify them
- wiki/index.md is the master catalog: update on every ingest
- wiki/log.md is append-only: never edit past entries
- New log entries go at the TOP of the file

## Operations

- **Ingest**: drop source in .raw/, say "ingest [filename]"
- **Query**: ask any question, Claude reads index first then drills in
- **Lint**: say "lint" for standard check, "lint --deep" for full analysis
- **Deep Lint**: say "lint --deep" for knowledge gaps, research directions, contradictions analysis

## Note Types

| Type | Location | Purpose |
|------|----------|---------|
| source | wiki/sources/ | Summary of a source |
| concept | wiki/concepts/ | Explanation of an idea |
| entity | wiki/entities/ | Person/org/product |
| comparison | wiki/comparisons/ | Side-by-side analysis |
| contradiction | wiki/contradictions/ | Cross-source conflicts |
| question | wiki/questions/ | Filed answers |

## Query Output Types

Query results can be saved as:
- **Question page** (default) → wiki/questions/
- **Comparison table** → wiki/comparisons/
- **Marp slide deck** → wiki/meta/slides/
- **Chart/diagram** → wiki/meta/charts/

## Git Workflow

This wiki is a git repository. Every ingest is auto-committed.
Use branches for exploratory research: \`git checkout -b explore/topic\`

## Concept Evolution

Track how concepts evolve across sources:
- \`version\`: increment when major updates occur
- \`supersedes\`: link to older version if concept was replaced
- \`evidence_strength\`: weak | moderate | strong (based on source count)
- \`confidence\`: 0-1 (based on source agreement)
- \`last_verified\`: date of last verification
EOF

# Update index.md with creation date
sed -i '' "s/YYYY-MM-DD/$(date +%Y-%m-%d)/g" wiki/index.md
sed -i '' "s/YYYY-MM-DD/$(date +%Y-%m-%d)/g" wiki/index-tags.md
sed -i '' "s/YYYY-MM-DD/$(date +%Y-%m-%d)/g" wiki/index-topics.md
sed -i '' "s/YYYY-MM-DD/$(date +%Y-%m-%d)/g" wiki/log.md
sed -i '' "s/YYYY-MM-DD/$(date +%Y-%m-%d)/g" wiki/hot.md

# Initialize git repository
if command -v git &> /dev/null; then
    git init -q 2>/dev/null || true
    # Create .gitignore
    cat > .gitignore << 'GITIGNORE'
# OS files
.DS_Store
Thumbs.db

# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/

# IDE
.vscode/
.idea/

# Raw manifest ( regenerated )
.raw/.manifest.json

# Temp files
*.tmp
*.bak
GITIGNORE
    git add -A
    git commit -q -m "init: initialize wiki '$WIKI_NAME'"
    echo ""
    echo "✅ Git repository initialized"
fi

echo ""
echo "✅ Wiki initialized successfully!"
echo ""
echo "Directory structure:"
find . -type f -name "*.md" | sort | head -20
echo ""
echo "Next steps:"
echo "1. Add source files to .raw/"
echo "2. Tell Claude: ingest [filename]"
echo "3. Ask questions: query: [question]"
echo "4. Health check: lint  or  lint --deep"
echo "5. Git history: git log --oneline"
