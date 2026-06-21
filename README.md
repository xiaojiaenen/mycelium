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

# 全部装
pip install -e ".[all]"
```

## 怎么用？

装好后直接跟 Claude 说人话：

```
初始化一个研究笔记
```

```
这篇文章帮我整理一下 → ingest article.pdf
```

```
什么是注意力机制？ → query
```

```
帮我检查一下知识库 → lint --deep
```

```
对比一下 Transformer 和 RNN → query: ... → 对比
```

```
把总结做成幻灯片 → query: ... → 幻灯片
```

就这么简单。Claude 读取 Skill 指令，自动完成所有整理、关联、维护工作。

## 核心能力

### 📥 摄入素材

把文件丢进 `.raw/`，告诉 Claude 摄入。支持 PDF、Word、PPT、视频字幕、音频转写、网页、图片 OCR 等 30+ 格式。

Claude 会自动：
- 提取核心观点，创建结构化笔记
- 建立 `[[wikilink]]` 交叉引用
- 检测矛盾，创建冲突页面
- 追踪概念演进（版本 / 证据强度 / 置信度）
- Git 自动提交

### 🔍 提问查询

问任何问题，Claude 综合所有知识回答，并**自动存档**——每次提问都在增加知识库厚度。

### 🔬 健康检查

让 Claude 检查知识库：孤儿页、断链、矛盾、知识空白、过期内容、研究方向建议。

### 🔎 搜索

知识库大了之后，Claude 会自动使用内置搜索引擎（BM25 + 图分析 + 向量相似度）。

## 知识库长什么样？

```
wiki/
├── .raw/              # 你的原始素材（不可修改）
├── wiki/
│   ├── index.md       # 主索引
│   ├── sources/       # 源文档摘要
│   ├── concepts/      # 概念解释（带版本演进）
│   ├── entities/      # 人物/组织/产品
│   ├── comparisons/   # 对比分析
│   ├── contradictions/ # 跨来源矛盾
│   ├── questions/     # 查询回答（自动存档）
│   └── meta/          # 幻灯片、图表
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

## Obsidian 用户

用 Obsidian 打开 wiki 目录，还能获得：
- **Graph View** — 可视化知识结构
- **Dataview** — 10+ 预置动态查询
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
| 知识积累 | 每次从零开始 | 持续复利 |
| Token 成本 | 高（读原始文档） | 低（读 wiki 页面） |
| 维护 | 无（但质量差） | LLM 全权维护 |
| 版本追踪 | 无 | 概念演进追踪 |
| 搜索 | 需要向量数据库 | 内置 BM25 + 图搜索 |

## 文档

- [SKILL.md](SKILL.md) — Skill 定义（Claude 读取的操作指令）
- [REFERENCE.md](REFERENCE.md) — 笔记模板 + 质量标准
- [EXAMPLES.md](EXAMPLES.md) — 使用示例
- [docs/obsidian-guide.md](docs/obsidian-guide.md) — Obsidian 集成
- [docs/raw-guide.md](docs/raw-guide.md) — .raw/ 目录指南
- [docs/web-fetch.md](docs/web-fetch.md) — 网页抓取指南

## License

MIT
