# Mycelium Examples

## Example 1: Ingest an Article

### Input

```
.raw/transformer-attention-is-all-you-need.md
```

### Tell Claude

```
ingest transformer-attention-is-all-you-need.md
```

### Output

```
wiki/
├── sources/
│   └── article-transformer-attention.md
├── concepts/
│   ├── transformer.md (new, version: 1, evidence: weak)
│   ├── attention-mechanism.md (new, version: 1, evidence: weak)
│   ├── self-attention.md (new)
│   ├── multi-head-attention.md (new)
│   └── positional-encoding.md (new)
└── entities/
    └── vaswani-et-al.md (new)
```

**Git:** `git commit -m "ingest: article-transformer-attention.md"`

---

## Example 2: Ingest a Video

### Input

```
.raw/3b1b-neural-networks.mp4
.raw/3b1b-neural-networks.srt (subtitles)
```

### Tell Claude

```
ingest 3b1b neural networks video
```

### Output

```
wiki/
├── sources/
│   └── video-3b1b-neural-networks.md
├── concepts/
│   ├── neural-network.md (new or update, version++)
│   ├── activation-function.md (new or update)
│   ├── sigmoid.md (new)
│   ├── relu.md (new)
│   └── backpropagation.md (new)
```

---

## Example 3: Query (Default — Filing Answer)

### Tell Claude

```
query: 什么是注意力机制
```

### Claude Does

1. Read `wiki/index.md`
2. Find `wiki/concepts/attention-mechanism.md`
3. Read it + related pages
4. Synthesize answer with citations
5. **Save to `wiki/questions/what-is-attention-mechanism.md`**

### Output

```
wiki/questions/what-is-attention-mechanism.md (new)
```

**Git:** `git commit -m "query: 什么是注意力机制"`

---

## Example 4: Query → Comparison

### Tell Claude

```
query: Transformer vs RNN → 对比
```

### Output

```
wiki/comparisons/transformer-vs-rnn.md (new)
```

The comparison includes:
- Side-by-side table
- Strengths/weaknesses
- Use cases
- Sources

---

## Example 5: Query → Slide Deck

### Tell Claude

```
query: Transformer架构总结 → 幻灯片
```

### Output

```
wiki/meta/slides/transformer-summary.md (Marp format)
```

**To present:**
```bash
# In Obsidian with Marp plugin: open file and press "Present"
# Or export: marp --pptx wiki/meta/slides/transformer-summary.md
```

---

## Example 6: Query → Chart

### Tell Claude

```
query: attention发展时间线 → 画图
```

### Output

```
wiki/meta/charts/attention-timeline-chart.py (matplotlib)
```

**To generate:**
```bash
python3 wiki/meta/charts/attention-timeline-chart.py
# Outputs: wiki/meta/charts/attention-timeline.png
```

---

## Example 7: Lint (Standard)

### Tell Claude

```
lint
```

### Output

```
## Wiki Health Report

### Orphan Pages (2)
- wiki/concepts/gradient-clipping.md - no inbound links
- wiki/sources/article-old-rnn.md - no inbound links

### Broken Links (1)
- wiki/concepts/lstm.md references [[gated-unit]] which doesn't exist

### Stale Notes (3)
- wiki/concepts/gan.md - status: draft, created 60 days ago

### Frontmatter Issues (1)
- wiki/entities/google.md - missing 'tags' field
```

---

## Example 8: Lint Deep

### Tell Claude

```
lint --deep
```

### Output

```
## Deep Wiki Health Report

[Standard checks above]

### Contradictions (2)

1. **Scaling Laws Debate** → wiki/contradictions/scaling-laws-conflict.md (created)
   - 立场 A: "Bigger models always better" — [[source-chinchilla]], [[source-gpt4-paper]]
   - 立场 B: "Data quality matters more" — [[concept-data-centric-ai]], [[source-lima-paper]]

2. **RLHF Alternatives** → wiki/contradictions/rlhf-alternatives-conflict.md (created)
   - 立场 A: "RLHF is essential for alignment"
   - 立场 B: "DPO/RLAIF can replace RLHF"

### Knowledge Gaps (3)
- Referenced but undefined: [[emergent-abilities]]
- Referenced but undefined: [[scaling-laws]]
- Weak evidence (1 source): [[mixture-of-experts]]

### Stale Verification (5)
- wiki/concepts/transformer.md — last_verified: 2026-01-15 (156 days ago)
- wiki/concepts/attention-mechanism.md — last_verified: 2026-02-01

### Research Directions
1. Based on your current knowledge of [X], consider exploring [Y]
2. The contradiction between [A] and [B] could be resolved by examining [C]
3. Web search suggestion: "latest developments in [topic]"

### Index Updates
- index-tags.md regenerated (45 tags, 12 clusters)
- index-topics.md regenerated (8 topic clusters)
```

---

## Example 9: Multi-source Synthesis

### Scenario

You've ingested 3 articles about attention mechanisms.

### Tell Claude

```
query: 综合所有关于注意力机制的来源，给我一个完整的总结
```

### Claude Does

1. Read `wiki/index.md`
2. Find all sources mentioning attention
3. Read them all
4. Synthesize across sources
5. Note agreements and disagreements
6. Save to `wiki/questions/attention-mechanism-synthesis.md`

### Output

```
## 注意力机制综合总结

### 核心概念
[综合定义]

### 来源对比

| 来源 | 观点 | 差异 |
|------|------|------|
| Article A | ... | ... |
| Article B | ... | ... |
| Video C | ... | ... |

### 共识
- [所有来源都同意的点]

### 分歧
- [来源间有分歧的点] → 创建 contradiction page

### 我的综合
[你的理解和判断]
```

---

## Example 10: Concept Evolution

### Day 1: First Ingest

```bash
cp rlhf-paper.pdf .raw/
"ingest rlhf-paper.pdf"
```

```
wiki/concepts/rlhf.md:
  version: 1
  evidence_strength: weak
  confidence: 0.5
  last_verified: 2026-06-20
```

### Day 15: Second Source

```bash
cp dpo-paper.pdf .raw/
"ingest dpo-paper.pdf"
```

```
wiki/concepts/rlhf.md:
  version: 2 (updated)
  evidence_strength: moderate (2 sources)
  confidence: 0.7 (increased)
  last_verified: 2026-07-05

wiki/concepts/direct-preference-optimization.md (new)
```

### Day 30: Contradiction Found

```bash
cp lima-paper.pdf .raw/
"ingest lima-paper.pdf"
```

```
wiki/concepts/rlhf.md:
  version: 3 (updated)
  evidence_strength: strong (3 sources)
  confidence: 0.6 (lowered due to contradiction)
  last_verified: 2026-07-20

wiki/contradictions/rlhf-necessity-conflict.md (new)
  status: unresolved
  severity: high
```

---

## Example 11: Building a Research Wiki

### Day 1

```bash
# Initialize (auto git init)
bash scripts/init.sh "Transformer Research"

# Ingest first paper
cp attention-is-all-you-need.pdf .raw/
"ingest the transformer paper"
# Git: init commit + ingest commit
```

### Day 2

```bash
# Ingest related paper
cp bert.pdf .raw/
"ingest BERT paper"
# Git: ingest commit

# Query (answer auto-filed)
"query: BERT和原始Transformer有什么区别"
# Git: query commit
```

### Day 3

```bash
# Ingest blog post
cp illustrated-transformer.md .raw/
"ingest illustrated transformer blog"

# Deep lint
"lint --deep"
# Creates contradiction pages, updates indexes
# Git: lint commit
```

### Week 2

```bash
# Wiki now has 20+ pages, use search
python3 scripts/search.py "attention mechanism"

# Query for gaps
"query: 我们还缺什么知识"
# → Saves research directions to wiki/questions/

# Check evolution
# In Obsidian: Dataview shows weak-evidence concepts
```

### Exploratory Branch

```bash
git checkout -b explore/multimodal
# Ingest multimodal sources
cp clip-paper.pdf .raw/
"ingest CLIP paper"
# Git: commit on explore branch

# Happy with results? Merge back
git checkout main
git merge explore/multimodal
```

---

## Example 12: Personal Knowledge Base

### Setup

```bash
bash scripts/init.sh "My Learning Wiki"
```

### Ingest Various Sources

```bash
# Article
cp medium-article.md .raw/
"ingest this article"

# Podcast notes
cp lex-fridman-episode-notes.md .raw/
"ingest these podcast notes"

# Meeting notes
cp team-meeting-notes.md .raw/
"ingest meeting notes"
```

### Query for Connections

```
query: 最近学的东西有什么共同点
```

### Obsidian Views

Open in Obsidian and use Dataview:

```dataview
TABLE type AS "类型", tags AS "标签"
FROM "wiki"
WHERE type != "meta"
SORT created DESC
LIMIT 20
```

---

## Example 13: Competitive Analysis Wiki

### Setup

```bash
bash scripts/init.sh "AI Chatbot Market Analysis"
```

### Ingest Competitor Info

```bash
cp chatgpt-overview.md .raw/
"ingest ChatGPT overview"

cp claude-overview.md .raw/
"ingest Claude overview"

cp gemini-overview.md .raw/
"ingest Gemini overview"
```

### Query → Comparison

```
query: 对比ChatGPT、Claude、Gemini的优缺点 → 对比
```

### Output

Comparison note created: `wiki/comparisons/chatgpt-vs-claude-vs-gemini.md`

### Deep Lint

```
lint --deep
```

Output includes:
- Contradictions between sources
- Missing information about each competitor
- Research suggestions: "Consider ingesting: pricing pages, API docs, benchmark results"

---

## Tips

1. **Start small** — Ingest 3-5 sources first, then expand
2. **Query often** — Every query auto-files and compounds the wiki
3. **Lint regularly** — Every 10-15 ingests, use `lint --deep` monthly
4. **Use Obsidian** — Graph view + Dataview makes the wiki come alive
5. **Branch for experiments** — Use git branches for exploratory research
6. **Track evolution** — Watch concept versions and confidence scores grow
7. **Embrace contradictions** — They're features, not bugs; resolve them over time
