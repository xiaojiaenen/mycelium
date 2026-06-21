# Mycelium 🍄

> *像森林地下的菌丝网络——看不见，但无处不在，连接万物。*

一个 Claude Code **Skill**——跟 Claude 说话，就能构建持久化、持续复利的知识库。

灵感来自 Karpathy 的 [LLM Wiki 模式](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)。

## 安装

```bash
npx skills add xiaojiaenen/mycelium
```

装完就能用。不需要配置，不需要跑脚本。

### 依赖安装（按需）

```bash
# 基础（文件读取）
pip install "markitdown[pdf,docx,pptx,html,xlsx]"

# 视频转写
pip install faster-whisper yt-dlp

# 网页抓取
pip install "scrapling[all]"

# 图表生成
pip install matplotlib

# 语义搜索（可选，默认关闭）
pip install sentence-transformers

# 全部装
pip install -e ".[all]"
```

## 怎么用？

装好后直接跟 Claude 说人话：

```
初始化一个研究笔记
```

```
ingest article.pdf
```

```
ingest https://www.bilibili.com/video/BV1xxx
```

```
什么是注意力机制？
```

```
lint --deep
```

```
对比一下 Transformer 和 RNN → 对比
```

```
把总结做成幻灯片 → 幻灯片
```

```
把总结画成图 → 画图
```

就这么简单。Claude 读取 Skill 指令，自动完成所有整理、关联、维护工作。

## 核心能力

### 📥 全自动摄入

一条命令完成所有事：

```bash
python3 scripts/auto_ingest.py article.pdf
```

自动执行 9 步：读取 → 创建笔记 → 提取概念 → 更新索引 → 生成图表 → 评分 → 检测空白 → 生成演化图 → git commit。

支持 30+ 格式：PDF、Word、PPT、视频、音频、图片 OCR、网页、电子书。

### 🔍 提问查询

问任何问题，Claude 综合所有知识回答，**自动存档到 wiki**。

输出类型：问答页 / 对比分析 / Marp 幻灯片 / matplotlib 图表。

### 🔬 健康检查

```
lint            # 标准：孤儿页、断链、过期笔记
lint --deep     # 深度：+ 矛盾检测、知识空白、漂移检测、研究方向
```

### 🎯 知识管理

| 功能 | 说明 |
|------|------|
| 矛盾检测 | 不同来源的冲突自动创建 contradiction 页面 |
| 矛盾解决 | `resolve.py` 引导解决流程 |
| 知识空白 | `gaps.py` 发现未定义概念、弱证据、孤立页 |
| 来源评分 | `source-score.py` 自动打分（A-D 等级） |
| 概念演进 | `timeline.py` 可视化版本/置信度变化 |
| 统计仪表盘 | `stats.py` 生成阅读统计 HTML |

### 📊 可视化

| 输出 | 命令 | 格式 |
|------|------|------|
| 概念关系图 | `excalidraw.py` | `.excalidraw`（Obsidian 打开） |
| 知识图谱 | `graph.py` | `.html`（浏览器交互） |
| 演化时间线 | `timeline.py` | `.png`（matplotlib） |
| 统计仪表盘 | `stats.py` | `.html`（深色主题） |
| Obsidian Canvas | `canvas.py` | `.canvas` |

### 🔎 搜索

```bash
python3 scripts/search.py "attention"              # BM25 + PageRank + 向量
python3 scripts/search.py "attention" --mode semantic --enable  # 语义搜索（需安装）
python3 scripts/search.py "attention" --summary     # token 高效模式
```

## 知识库结构

```
wiki/
├── .raw/              # 原始素材（不可修改）
├── wiki/
│   ├── index.md       # 主索引
│   ├── index-tags.md  # 标签索引（自动生成）
│   ├── index-topics.md # 主题聚类（自动生�
│   ├── log.md         # 操作日志
│   ├── hot.md         # 近期上下文
│   ├── daily/         # 日记
│   ├── weekly/        # 周记
│   ├── sources/       # 源文档摘要
│   ├── concepts/      # 概念（带版本演进）
│   ├── entities/      # 人物/组织/产品
│   ├── comparisons/   # 对比分析
│   ├── contradictions/ # 跨来源矛盾
│   ├── questions/     # 查询回答（自动存档）
│   └── meta/          # 图表、幻灯片、仪表盘
│       ├── concept-map.excalidraw
│       ├── knowledge-graph.html
│       ├── evolution-timeline.png
│       ├── dashboard.html
│       ├── kanban.md
│       └── wiki-canvas.canvas
└── CLAUDE.md          # Wiki 规则（自动生成）
```

## 6 种笔记类型

| 类型 | 用途 |
|------|------|
| source | 源文档摘要 |
| concept | 概念解释（带版本/置信度追踪） |
| entity | 人物/组织/产品 |
| comparison | 对比分析 |
| contradiction | 跨来源矛盾冲突 |
| question | 查询回答（自动存档） |

## Obsidian 集成

用 Obsidian 打开 wiki 目录，还能获得：
- **Graph View** — 可视化知识结构
- **Dataview** — 10+ 预置动态查询
- **Excalidraw** — 概念关系图
- **Canvas** — 知识画布
- **Kanban** — 研究任务看板
- **Daily Notes** — 每日知识记录
- **Marp 插件** — 渲染幻灯片
- **Web Clipper** — 浏览器一键保存文章
- **Git 插件** — 跨设备同步

详见 [docs/obsidian-guide.md](docs/obsidian-guide.md)

## 为什么有效？

> 最累人的不是阅读和思考，而是**簿记**：更新交叉引用、保持摘要最新、标注矛盾、维护一致性。人类放弃维护 Wiki，是因为维护负担增长速度快于价值。LLM 不会厌倦，不会忘记更新交叉引用，一次操作可以触达 15 个文件。
>
> — Andrej Karpathy

**隐喻：** Obsidian 是 IDE，LLM 是程序员，Wiki 是代码库。你浏览和审查，LLM 编写和维护。

## Mycelium vs RAG

| 维度 | RAG | Mycelium |
|------|-----|----------|
| 交叉引用 | 查询时计算 | 预建好 |
| 矛盾检测 | 不检测 | 自动标记 + 冲突页 |
| 知识空白 | 不检测 | 自动发现 + 建议 |
| 知识积累 | 每次从零开始 | 持续复利 |
| Token 成本 | 高（读原始文档） | 低（读 wiki 页面） |
| 维护 | 无（但质量差） | LLM 全权维护 |
| 版本追踪 | 无 | 概念演进追踪 |
| 搜索 | 需要向量数据库 | BM25 + 图搜索 + 可选语义 |
| 可视化 | 无 | 图谱/时间线/仪表盘 |

## 文档

- [SKILL.md](SKILL.md) — Skill 定义
- [REFERENCE.md](REFERENCE.md) — 笔记模板 + 质量标准
- [EXAMPLES.md](EXAMPLES.md) — 使用示例
- [docs/obsidian-guide.md](docs/obsidian-guide.md) — Obsidian 集成
- [docs/raw-guide.md](docs/raw-guide.md) — .raw/ 目录指南
- [docs/web-fetch.md](docs/web-fetch.md) — 网页抓取指南

## License

MIT
