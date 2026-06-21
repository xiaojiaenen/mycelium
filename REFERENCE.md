# Mycelium Reference

## Note Templates

### Source Note Template

```markdown
---
type: source
title: "标题"
source_type: article|video|book|paper|conversation
source_url: "URL或来源"
created: YYYY-MM-DD
tags: [tag1, tag2]
status: draft|reviewed|evergreen
---

# 标题

## 元信息
- 来源：[URL或出处]
- 作者：[作者]
- 日期：[发布日期]
- 类型：[文章/视频/书籍/论文]
- 字幕文件：[如果是视频]

---

## 一句话总结
[用一句话概括核心内容]

## 核心观点（3-5个）
1. [观点1]
2. [观点2]
3. [观点3]

## 详细内容

### [主题1]
[详细解释，包含原文引用]

> "原文引用" — [来源位置]

### [主题2]
[详细解释]

### [主题3]
[详细解释]

---

## 关键概念
- [[概念1]] - [一句话解释]
- [[概念2]] - [一句话解释]
- [[概念3]] - [一句话解释]

## 引用原文（重要段落）

> "重要原文1" — [位置]

> "重要原文2" — [位置]

> "重要原文3" — [位置]

---

## 我的思考
[可选：对内容的评价、疑问、联想]

## 相关链接
- [[相关概念1]]
- [[相关概念2]]
- [[相关来源1]]

## 待验证
- [ ] [需要验证的观点1]
- [ ] [需要验证的观点2]
```

---

### Concept Note Template

```markdown
---
type: concept
title: "概念名称"
title_en: "English Name"
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
status: developing|mature|evergreen
aliases: [别名1, 别名2]
version: 1
supersedes: []
evidence_strength: weak|moderate|strong
confidence: 0.5
last_verified: YYYY-MM-DD
---

# 概念名称

## 一句话定义
[用一句话解释这个概念是什么]

## 核心解释

### 是什么
[详细定义和解释]

### 不是什么
[常见误解和澄清]

### 为什么重要
[这个概念的价值和意义]

---

## 详细内容

### [子主题1]
[详细解释]

### [子主题2]
[详细解释]

### [子主题3]
[详细解释]

---

## 示例

### 示例1
[具体例子]

### 示例2
[具体例子]

---

## 对比

| 特性 | 本概念 | 相似概念A | 相似概念B |
|------|--------|-----------|-----------|
| [特性1] | ... | ... | ... |
| [特性2] | ... | ... | ... |

---

## 来源
- [[来源1]] - [相关段落]
- [[来源2]] - [相关段落]

## 相关概念
- [[相关概念1]] - [关系说明]
- [[相关概念2]] - [关系说明]

## 应用场景
1. [场景1]
2. [场景2]

## 常见问题
**Q: [问题1]**
A: [回答]

**Q: [问题2]**
A: [回答]
```

**Evolution Fields:**

| Field | Type | Description |
|-------|------|-------------|
| version | int | Increment on major updates (1, 2, 3...) |
| supersedes | array | Wikilinks to older versions this replaces |
| evidence_strength | enum | `weak` (1 source), `moderate` (2-3), `strong` (4+) |
| confidence | float | 0-1, based on source agreement |
| last_verified | date | When this concept was last verified against sources |
| updated | date | Last modification date |

---

### Entity Note Template

```markdown
---
type: entity
title: "实体名称"
entity_type: person|organization|product|project
created: YYYY-MM-DD
tags: [tag1, tag2]
status: developing|mature|evergreen
---

# 实体名称

## 基本信息
- 类型：[人物/组织/产品/项目]
- [关键属性1]：[值]
- [关键属性2]：[值]

---

## 简介
[一段话介绍]

## 详细信息

### [方面1]
[详细说明]

### [方面2]
[详细说明]

---

## 相关事件
- [日期]：[事件描述]
- [日期]：[事件描述]

## 相关概念
- [[概念1]] - [关系]
- [[概念2]] - [关系]

## 相关实体
- [[实体1]] - [关系]
- [[实体2]] - [关系]

## 来源
- [[来源1]]
- [[来源2]]
```

---

### Comparison Note Template

```markdown
---
type: comparison
title: "A vs B"
created: YYYY-MM-DD
tags: [tag1, tag2]
status: developing|mature|evergreen
---

# A vs B

## 一句话结论
[哪个更好/更适合什么场景]

## 详细对比

| 维度 | A | B | 胜出 |
|------|---|---|------|
| [维度1] | ... | ... | A/B/平 |
| [维度2] | ... | ... | A/B/平 |
| [维度3] | ... | ... | A/B/平 |

## 详细分析

### [维度1]
[详细对比分析]

### [维度2]
[详细对比分析]

---

## 适用场景

### 选A当
- [场景1]
- [场景2]

### 选B当
- [场景1]
- [场景2]

---

## 来源
- [[来源1]]
- [[来源2]]

## 相关对比
- [[其他对比1]]
- [[其他对比2]]
```

---

### Contradiction Note Template

```markdown
---
type: contradiction
title: "矛盾主题"
created: YYYY-MM-DD
tags: [tag1, tag2]
status: unresolved|resolved|superseded
severity: low|medium|high
---

# 矛盾主题

## 一句话描述
[这个矛盾是什么]

---

## 立场 A

### 主张
[立场 A 的核心主张]

### 证据
- [证据1] — [[来源1]]
- [证据2] — [[来源2]]

### 支持理由
[为什么这个立场有道理]

---

## 立场 B

### 主张
[立场 B 的核心主张]

### 证据
- [证据1] — [[来源3]]
- [证据2] — [[来源4]]

### 支持理由
[为什么这个立场有道理]

---

## 分析

### 共识点
- [双方都同意的部分]

### 核心分歧
- [根本分歧在哪里]

### 证据权重

| 来源 | 立场 | 可信度 | 时效性 |
|------|------|--------|--------|
| [[来源1]] | A | 高/中/低 | 新/旧 |
| [[来源3]] | B | 高/中/低 | 新/旧 |

### 当前判断
[基于证据权重的暂时结论，标注不确定性]

---

## 待验证
- [ ] [新证据可能改变判断的点]
- [ ] [需要更多来源确认的点]

## 相关矛盾
- [[其他矛盾1]]
- [[其他矛盾2]]

## 相关概念
- [[概念1]]
- [[概念2]]
```

**Fields:**

| Field | Values | Description |
|-------|--------|-------------|
| status | `unresolved`, `resolved`, `superseded` | Current state |
| severity | `low`, `medium`, `high` | Impact on wiki knowledge |

---

### Question Note Template

```markdown
---
type: question
title: "问题"
created: YYYY-MM-DD
tags: [tag1, tag2]
status: answered|unanswered|partial
---

# 问题

## 问题
[完整的问题描述]

## 简短回答
[一句话回答]

## 详细回答
[完整回答，包含推理过程]

## 证据

### 支持证据
- [证据1] — [[来源1]]
- [证据2] — [[来源2]]

### 反对证据
- [证据1] — [[来源1]]

## 不确定性
- [不确定的点1]
- [不确定的点2]

## 相关问题
- [[问题1]]
- [[问题2]]

## 来源
- [[来源1]]
- [[来源2]]
```

---

### Slide Deck Template (Marp)

When query output is `→ 幻灯片`, generate a Marp markdown file:

```markdown
---
marp: true
theme: default
paginate: true
---

# 标题

副标题和日期

---

## 核心观点 1

[内容]

- 要点 1
- 要点 2

---

## 核心观点 2

[内容]

---

## 总结

- 总结要点 1
- 总结要点 2
- 总结要点 3

---

# 谢谢

相关概念：[[概念1]], [[概念2]]
来源：[[来源1]]
```

**Generate with:**
```bash
# From wiki content
marp --pptx wiki/meta/slides/output.md
# Or open in Obsidian with Marp plugin
```

---

### Chart Template (matplotlib)

When query output is `→ 画图`, generate a Python script:

```python
#!/usr/bin/env python3
"""Chart: [description]"""
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']

# Data from wiki sources
data = {...}

fig, ax = plt.subplots(figsize=(10, 6))
# ... plot logic ...

ax.set_title('[Title]')
ax.set_xlabel('[X Label]')
ax.set_ylabel('[Y Label]')
plt.tight_layout()
plt.savefig('wiki/meta/charts/[name].png', dpi=150)
plt.show()
```

---

## Quality Standards

### 必须满足 (Required)

1. **有来源** - 每个观点标注出处
2. **有链接** - 相关概念相互引用
3. **有结构** - 使用固定模板
4. **有定义** - 概念有一句话定义
5. **有frontmatter** - type, status, created, tags

### 应该满足 (Should)

1. **有示例** - 抽象概念配具体例子
2. **有对比** - 相似概念做区分
3. **有来源原文** - 重要引用保留原文
4. **有待验证** - 不确定的内容标注
5. **有英文名** - 便于搜索和交流
6. **有版本追踪** - 概念有 version, evidence_strength, confidence

### 可以满足 (May)

1. **有思考** - 个人评价和联想
2. **有问题** - 开放性问题
3. **有应用** - 实际使用场景
4. **有别名** - 便于搜索

---

## Ingest Checklist

```
1. [ ] 读源文件
2. [ ] 提取核心观点（3-5个）
3. [ ] 创建 source 笔记
4. [ ] 识别关键概念
5. [ ] 为每个概念创建/更新 concept 笔记
   - [ ] 更新 version, evidence_strength, confidence
   - [ ] 更新 last_verified
6. [ ] 识别实体
7. [ ] 创建/更新 entity 笔记
8. [ ] 检查矛盾 → 创建 contradiction 笔记（如有）
9. [ ] 交叉引用：链接到已有的相关页面
10. [ ] 更新 wiki/index.md
11. [ ] 更新 wiki/index-tags.md
12. [ ] 更新 wiki/index-topics.md
13. [ ] 更新 wiki/log.md
14. [ ] 更新 wiki/hot.md
15. [ ] Git commit
```

---

## Query Checklist

```
1. [ ] 读 wiki/index.md（或用 search.py）
2. [ ] 识别相关页面
3. [ ] 读相关页面
4. [ ] 综合回答
5. [ ] 标注来源
6. [ ] 存为新页面到 wiki/questions/（默认）
   - 或存为 comparison / slides / chart
7. [ ] Git commit
```

---

## Lint Checklist

```
Standard:
1. [ ] 检查孤立页面（无链接指向）
2. [ ] 检查断链（链接指向不存在的页面）
3. [ ] 检查过期（status: draft 超过30天）
4. [ ] 检查 frontmatter 完整性

Deep (lint --deep):
5. [ ] 检查矛盾 → 创建 contradiction 笔记
6. [ ] 检查知识空白（引用但未定义的概念）
7. [ ] 检查证据强度（只有1个来源的概念）
8. [ ] 检查过期验证（last_verified > 90天）
9. [ ] 知识漂移检测（confidence < 0.3 标记为不可靠，last_verified > 180天 标记为过期）
10. [ ] 概念合并建议（检测近似重复概念，建议 merge）
11. [ ] 建议研究方向
12. [ ] 建议新来源（可 web search 补全）
13. [ ] 更新 index-tags.md
14. [ ] 更新 index-topics.md
15. [ ] Git commit
```

---

## File Naming Convention

```
# Source notes
[来源类型]-[简短标题].md
例：article-transformer-attention.md
例：video-3b1b-neural-networks.md
例：book-deep-learning-ch1.md

# Concept notes
[概念名].md (小写，连字符分隔)
例：attention-mechanism.md
例：backpropagation.md

# Entity notes
[实体名].md (小写，连字符分隔)
例：andrew-ng.md
例：openai.md

# Contradiction notes
[主题]-conflict.md
例：scaling-laws-conflict.md
例：rlhf-alternatives-conflict.md

# Slide decks
[主题]-slides.md
例：transformer-slides.md

# Charts
[主题]-chart.py
例：attention-timeline-chart.py
```

---

## Frontmatter Fields

| Field | Required | Values | Description |
|-------|----------|--------|-------------|
| type | Yes | source, concept, entity, comparison, contradiction, question | Note type |
| title | Yes | string | Note title |
| created | Yes | YYYY-MM-DD | Creation date |
| tags | Yes | array | Categorization tags |
| status | Yes | draft, reviewed, evergreen, developing, mature, unresolved, resolved | Note status |
| source_type | For source | article, video, book, paper, conversation | Source type |
| source_url | For source | string | Source URL |
| entity_type | For entity | person, organization, product, project | Entity type |
| aliases | Optional | array | Alternative names |
| title_en | Optional | string | English title |
| version | For concept | int | Evolution version number |
| supersedes | For concept | array | Older versions this replaces |
| evidence_strength | For concept | weak, moderate, strong | Based on source count |
| confidence | For concept | float 0-1 | Based on source agreement |
| last_verified | For concept | YYYY-MM-DD | Last verification date |
| updated | Optional | YYYY-MM-DD | Last modification date |
| severity | For contradiction | low, medium, high | Impact level |
| superseded_by | For concept | array | New concepts that replace this one (after split) |
| status | For concept | developing, mature, evergreen, superseded | Note status (superseded after merge/split) |
