# Obsidian 集成指南

Mycelium 与 Obsidian 深度集成，提供强大的知识浏览和查询体验。

## 安装配置

### 1. 打开 Wiki 为 Obsidian Vault

```bash
# 在 Obsidian 中打开 wiki 根目录
# File → Open Vault → 选择 wiki 目录
```

### 2. 推荐插件

| 插件 | 用途 | 必需 |
|------|------|------|
| **Dataview** | 动态查询 frontmatter | 推荐 |
| **Marp** | 渲染幻灯片 | 可选 |
| **Git** | 版本控制同步 | 推荐 |
| **Graph Analysis** | 知识图谱分析 | 可选 |
| **Tag Wrangler** | 标签管理 | 可选 |

### 3. 设置附件目录

```
Settings → Files & Links → Default location for new attachments
→ 选择 "In the folder specified below"
→ 填写: wiki/meta/attachments
```

## Dataview 查询

### 查看所有源笔记

```dataview
TABLE source_type AS "类型", status AS "状态", created AS "创建日期"
FROM "wiki/sources"
SORT created DESC
```

### 查看概念演进

```dataview
TABLE version AS "版本", evidence_strength AS "证据", confidence AS "置信度", last_verified AS "上次验证"
FROM "wiki/concepts"
WHERE version > 1
SORT version DESC
```

### 查看未解决的矛盾

```dataview
TABLE severity AS "严重度", status AS "状态"
FROM "wiki/contradictions"
WHERE status = "unresolved"
SORT severity ASC
```

### 查看弱证据概念

```dataview
TABLE evidence_strength AS "证据强度", confidence AS "置信度"
FROM "wiki/concepts"
WHERE evidence_strength = "weak"
SORT confidence ASC
```

### 最近添加的笔记

```dataview
TABLE type AS "类型", created AS "创建日期"
FROM "wiki"
WHERE type != "meta"
SORT created DESC
LIMIT 20
```

### 按标签查看笔记

```dataview
TABLE title AS "标题", type AS "类型"
FROM "wiki"
WHERE contains(tags, "machine-learning")
SORT title ASC
```

### 查看所有标签

```dataview
TABLE length(rows) AS "笔记数"
FROM "wiki"
FLATTEN tags AS tag
GROUP BY tag
SORT length(rows) DESC
```

### 待验证内容

```dataview
TABLE title AS "标题", status AS "状态"
FROM "wiki"
WHERE status = "draft" OR status = "unanswered"
SORT created ASC
```

### 过期验证的概念

```dataview
TABLE last_verified AS "上次验证", evidence_strength AS "证据"
FROM "wiki/concepts"
WHERE last_verified && date(today) - date(last_verified) > dur(90 days)
SORT last_verified ASC
```

### 幻灯片列表

```dataview
TABLE created AS "创建日期"
FROM "wiki/meta/slides"
SORT created DESC
```

## Graph View 优化

### 识别知识枢纽

在 Graph View 中，节点大小反映链接数量。枢纽节点（链接最多）是知识体系的核心：

- **index.md** — 主索引，连接所有分类
- **核心概念页** — 如 transformer.md、attention-mechanism.md
- **实体页** — 如 openai.md、google.md

### 发现孤儿页

Graph View 中没有连线的节点就是孤儿页。定期检查并建立链接。

### 主题聚类

Graph View 中紧密连接的节点群形成主题聚类。如果聚类之间缺少链接，说明知识体系需要更好的交叉引用。

## Web Clipper 工作流

### 安装 Obsidian Web Clipper

```bash
# Chrome/Firefox 扩展商店搜索 "Obsidian Web Clipper"
# 安装后配置：
# - Vault: 选择你的 wiki vault
# - 附件文件夹: wiki/meta/attachments
# - 模板: 选择 "Article" 或自定义
```

### 使用方法

1. 浏览到要保存的文章
2. 点击 Web Clipper 图标
3. 选择保存位置 → `.raw/` 文件夹
4. 回到 Claude Code，运行 `ingest [filename]`

### 图片下载工作流

Web Clipper 默认只保存文本。要下载图片到本地：

```bash
# 步骤 1: 设置附件目录
# Obsidian → Settings → Files & Links
# → Default location for new attachments
# → 设为: wiki/meta/attachments

# 步骤 2: 设置下载热键
# Obsidian → Settings → Hotkeys
# 搜索 "Download"
# 找到 "Download attachments for current file"
# 绑定热键: Ctrl+Shift+D (或 Cmd+Shift+D)

# 步骤 3: 使用
# 1. 用 Web Clipper 保存文章到 .raw/
# 2. 在 Obsidian 中打开该文件
# 3. 按热键 Ctrl+Shift+D 下载所有图片
# 4. 图片保存到 wiki/meta/attachments/
```

### LLM 读图策略

LLM 无法在一次 pass 中同时处理文本和内联图片。正确的工作流：

```
1. 先读文本内容 → ingest 处理文字部分
2. 再单独查看图片（如果需要）
   - 在 Obsidian 中打开文件，手动查看图片
   - 或告诉 Claude: "看一下 article.md 里的图片"
```

> "It's a bit clunky but works well enough." — Karpathy

## Marp 幻灯片

### 安装 Marp 插件

```bash
# Obsidian 社区插件搜索 "Marp"
# 安装并启用
```

### 从 Wiki 生成幻灯片

```bash
# 方法 1: 通过 query
"query: Transformer架构总结 → 幻灯片"
# 生成 wiki/meta/slides/transformer-summary.md

# 方法 2: 手动创建
# 在 wiki/meta/slides/ 下创建 .md 文件
# 使用 Marp frontmatter:
```

```markdown
---
marp: true
theme: default
paginate: true
---

# 标题

---

## 第一页

内容

---

## 第二页

更多内容
```

### 导出幻灯片

```bash
# 在 Obsidian 中打开 Marp 文件
# 命令面板: "Marp: Export slide deck"
# 选择格式: PDF / PPTX / HTML
```

## Git 同步

### 安装 Obsidian Git 插件

```bash
# 社区插件搜索 "Git"
# 安装并配置：
# - Auto backup interval: 30 分钟
# - Pull updates on startup: 开启
# - Push on backup: 开启
```

### 跨设备同步

```bash
# 设备 A: 正常使用，自动 commit + push
# 设备 B: 启动时自动 pull

# 手动同步：
# 命令面板: "Git: Pull" 或 "Git: Push"
```

## DataviewJS 高级查询

### 知识图谱统计

```dataviewjs
const pages = dv.pages('"wiki"').where(p => p.type !== "meta");
const types = {};
pages.forEach(p => {
    types[p.type] = (types[p.type] || 0) + 1;
});
dv.paragraph(Object.entries(types).map(([k, v]) => `- **${k}**: ${v}`).join('\n'));
```

### 概念置信度分布

```dataviewjs
const concepts = dv.pages('"wiki/concepts"');
const buckets = { strong: 0, moderate: 0, weak: 0, unknown: 0 };
concepts.forEach(c => {
    const str = c.evidence_strength || "unknown";
    buckets[str] = (buckets[str] || 0) + 1;
});
dv.paragraph(Object.entries(buckets).map(([k, v]) => `- **${k}**: ${v}`).join('\n'));
```

### 最活跃的研究领域

```dataviewjs
const sources = dv.pages('"wiki/sources"');
const tagCount = {};
sources.forEach(s => {
    (s.tags || []).forEach(t => {
        tagCount[t] = (tagCount[t] || 0) + 1;
    });
});
const sorted = Object.entries(tagCount).sort((a, b) => b[1] - a[1]).slice(0, 10);
dv.table(["标签", "来源数"], sorted);
```

## 常见问题

### Q: Graph View 太乱怎么办？

A: 
1. 使用 Graph View 的 "Filter" 功能，只显示特定类型
2. 调整 "Cutoff" 滑块，只显示链接较多的节点
3. 使用 Group 功能按 type 分组着色

### Q: Dataview 查询不显示结果？

A:
1. 确认文件有正确的 YAML frontmatter
2. 检查字段名拼写（大小写敏感）
3. 重启 Obsidian 刷新索引

### Q: 图片不显示？

A:
1. 确认图片在 `wiki/meta/attachments/` 中
2. 使用相对路径引用：`![[image.png]]`
3. 检查 Files & Links 设置

### Q: Git 冲突怎么办？

A:
```bash
# 在终端中解决冲突
cd wiki/
git status  # 查看冲突文件
# 手动编辑冲突文件
git add .
git commit -m "resolve: merge conflict"
```
