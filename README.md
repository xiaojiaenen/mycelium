# Mycelium 🍄

> *像森林地下的菌丝网络——看不见，但无处不在，连接万物。*

一个基于 LLM 的**持久化、持续复利**的知识库系统。灵感来自 Karpathy 的 [LLM Wiki 模式](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)。

## 这是什么？

传统 RAG 每次都从原始文档重新检索。Mycelium 不同：你增量构建一个结构化 Wiki，**每加一篇素材，知识库就更厚一层**。

```
人类：思考、提问、决定方向
LLM：整理、关联、维护一致性
```

Wiki 是一个**持久复利的 artifact**。交叉引用预建好，矛盾自动标记，综合反映所有已读内容。你很少自己写 Wiki——LLM 负责一切。

> **隐喻：** Obsidian 是 IDE，LLM 是程序员，Wiki 是代码库。你浏览和审查，LLM 编写和维护。

## 快速开始

```bash
# 1. 初始化知识库（自动 git init）
bash scripts/init.sh "我的研究笔记"

# 2. 放入素材
cp article.pdf .raw/

# 3. 告诉 Claude
"ingest article.pdf"

# 4. 提问（回答自动存档）
"query: 关于 Transformer 你都知道什么"

# 5. 深度健康检查
"lint --deep"
```

## 目录结构

```
wiki/
├── .raw/              # 原始素材（不可修改）
├── wiki/
│   ├── index.md       # 主索引
│   ├── index-tags.md  # 标签索引（自动生成）
│   ├── index-topics.md # 主题聚类（自动生成）
│   ├── log.md         # 操作日志
│   ├── hot.md         # 近期上下文缓存
│   ├── sources/       # 源文档摘要
│   ├── concepts/      # 概念解释（带版本演进）
│   ├── entities/      # 人物/组织/产品
│   ├── comparisons/   # 对比分析
│   ├── contradictions/ # 跨来源矛盾
│   ├── questions/     # 查询回答（自动存档）
│   └── meta/          # 幻灯片、图表等生成物
│       ├── slides/    # Marp 幻灯片
│       └── charts/    # matplotlib 图表
└── CLAUDE.md          # Wiki 规则
```

## 核心操作

### 📥 Ingest — 摄入

把素材放进 `.raw/`，告诉 Claude 摄入。

```bash
cp article.pdf .raw/
"ingest article.pdf"
```

LLM 会自动：
1. 读取源文件
2. 提取 3-5 个核心观点
3. 创建结构化笔记（source / concept / entity）
4. 建立 `[[wikilink]]` 交叉引用
5. 检测矛盾 → 创建 contradiction 笔记
6. 追踪概念演进（版本号 / 证据强度 / 置信度）
7. 更新 index、index-tags、index-topics、log、hot cache
8. Git 自动提交

### 🔍 Query — 查询

问任何问题。**回答默认自动存档**——每次查询都在增加知识库厚度。

```bash
"query: 什么是注意力机制"
"query: Transformer vs RNN → 对比"
"query: 架构总结 → 幻灯片"
"query: 发展时间线 → 画图"
```

| 输出类型 | 命令 | 存储位置 |
|---------|------|---------|
| 问答页 | `query: ...`（默认） | `wiki/questions/` |
| 对比分析 | `→ 对比` | `wiki/comparisons/` |
| 幻灯片 | `→ 幻灯片` | `wiki/meta/slides/` |
| 图表 | `→ 画图` | `wiki/meta/charts/` |

### 🔬 Lint — 健康检查

```bash
"lint"           # 标准检查：孤儿页、断链、过期笔记
"lint --deep"    # 深度检查：+ 矛盾检测、知识空白、研究方向
```

深度检查额外包含：
- **矛盾检测** — 自动创建冲突页面，包含双方立场 + 来源
- **知识空白** — 引用但未定义的概念
- **证据强度** — 只有 1 个来源的概念
- **研究方向** — 基于现有知识建议下一步探索
- **过期验证** — 超过 90 天未验证的概念
- **Web search 建议** — 可通过外部搜索补全的空白
- **索引重建** — 更新 tag 和 topic 索引

### 🔎 Search — 搜索

100+ 页时使用内置搜索引擎：

```bash
python3 scripts/search.py "attention mechanism"
python3 scripts/search.py "RLHF" --mode hybrid
python3 scripts/search.py "对比" --type comparison --top 10
python3 scripts/search.py "transformer" --summary          # token 高效模式
python3 scripts/search.py "RLHF" --mode vector             # 向量相似度搜索
```

BM25 + PageRank + 向量相似度，三路混合排序。

## 6 种笔记类型

| 类型 | 目录 | 用途 |
|------|------|------|
| source | `wiki/sources/` | 源文档摘要 |
| concept | `wiki/concepts/` | 概念解释（带版本/置信度追踪） |
| entity | `wiki/entities/` | 人物/组织/产品 |
| comparison | `wiki/comparisons/` | 对比分析 |
| contradiction | `wiki/contradictions/` | 跨来源矛盾冲突 |
| question | `wiki/questions/` | 查询回答（自动存档） |

## 概念演进追踪

每次摄入新来源，自动更新概念的演进状态：

```yaml
version: 3                    # 版本号，重大更新时递增
supersedes: [[old-version]]   # 替代的旧版本
evidence_strength: strong     # weak(1来源) | moderate(2-3) | strong(4+)
confidence: 0.85             # 0-1，基于来源一致性
last_verified: 2026-06-20    # 上次验证日期
```

## Git 工作流

每次操作自动提交，支持探索性分支：

```bash
git checkout -b explore/multimodal   # 尝试新领域
git checkout -b experiment/xyz       # 验证假设
# 满意后合并：
git checkout main && git merge explore/multimodal
```

## Obsidian 集成

在 Obsidian 中打开 wiki 目录即可获得：

- **Graph View** — 可视化知识结构
- **Dataview** — 10+ 预置动态查询
- **Marp 插件** — 渲染幻灯片
- **Web Clipper** — 浏览器一键保存文章
- **Git 插件** — 跨设备同步

详见 [docs/obsidian-guide.md](docs/obsidian-guide.md)

## 工具链

| 脚本 | 用途 |
|------|------|
| `init.sh` | 初始化知识库（自动 git init） |
| `ingest-raw.py` | 扫描/读取/标记 .raw/ 文件 |
| `fetch-web.py` | 网页抓取（Scrapling，绕 Cloudflare） |
| `search.py` | BM25 + PageRank + 向量搜索 |
| `merge-concepts.py` | 概念合并/拆分 |
| `git-auto.sh` | 自动 git commit |
| `raw.sh` | .raw/ 管理工具 |
| `read-source.py` | 文件读取转 markdown |

## 安装为 Claude Code Skill

```bash
# 推送到 GitHub 后
npx skills add xiaojiaenen/mycelium
```

## Mycelium vs RAG

| 维度 | RAG | Mycelium |
|------|-----|----------|
| 交叉引用 | 查询时计算 | 预建好 |
| 矛盾检测 | 不检测 | 自动标记 + 冲突页 |
| 知识积累 | 每次从零开始 | 持续复利 |
| Token 成本 | 高（读原始文档） | 低（读 wiki 页面） |
| 维护 | 无（但质量差） | LLM 全权维护 |
| 版本追踪 | 无 | 概念演进追踪 |
| 搜索 | 需要向量数据库 | 内置 BM25 + 图搜索 |

## 为什么有效？

> 最累人的不是阅读和思考，而是**簿记**：更新交叉引用、保持摘要最新、标注矛盾、维护一致性。人类放弃维护 Wiki，是因为维护负担增长速度快于价值。LLM 不会厌倦，不会忘记更新交叉引用，一次操作可以触达 15 个文件。
>
> — Andrej Karpathy

人类负责：策划素材、引导分析、提出好问题、思考意义。

LLM 负责：其余一切。

## 文档

- [SKILL.md](SKILL.md) — 技能定义（操作指令）
- [REFERENCE.md](REFERENCE.md) — 笔记模板 + 质量标准
- [EXAMPLES.md](EXAMPLES.md) — 13 个使用示例
- [docs/obsidian-guide.md](docs/obsidian-guide.md) — Obsidian 集成指南
- [docs/raw-guide.md](docs/raw-guide.md) — .raw/ 目录使用指南
- [docs/web-fetch.md](docs/web-fetch.md) — 网页抓取指南

## License

MIT
