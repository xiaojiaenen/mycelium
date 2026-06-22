# .raw/ 目录使用指南

## 概述

`.raw/` 是源文件的存放目录。文件一旦放入，**不要修改**（immutable）。LLM 会读取这些文件并生成 wiki 笔记。

## 支持的文件类型

| 类型 | 扩展名 | 获取内容方式 | 依赖工具 |
|------|--------|-------------|----------|
| 文本 | .txt, .md | 直接读取 | 无 |
| PDF | .pdf | 提取文本 | `brew install poppler` |
| 网页 | .html | 提取正文 | `brew install lynx` |
| 字幕 | .srt, .vtt | 直接读取 | 无 |
| 视频 | .mp4, .mkv | 提取字幕 | whisper |
| 音频 | .mp3, .wav | 转文字 | whisper |
| 图片 | .png, .jpg | OCR识别 | `brew install tesseract` |
| Office | .docx, .pptx | 提取文本 | `brew install pandoc` |
| 链接 | .url | 下载网页 | curl |

## 使用方法

### 1. 添加文件

```bash
# 直接复制
cp article.txt .raw/
cp paper.pdf .raw/

# 下载网页
echo "https://example.com/article" > .raw/article.url

# 下载视频字幕
yt-dlp --write-sub --skip-download -o ".raw/%(title)s" "https://youtube.com/watch?v=xxx"
```

### 2. 查看文件状态

```bash
# 扫描所有文件
bash scripts/raw.sh scan

# 查看哪些未 ingest
bash scripts/raw.sh status

# 列出所有文件
bash scripts/raw.sh list

# 查看文件类型统计
bash scripts/raw.sh types
```

### 3. 读取文件内容

```bash
# 读取特定文件
bash scripts/raw.sh read article.pdf
bash scripts/raw.sh read video.srt
```

### 4. 标记已 ingest

```bash
# ingest 完成后标记
bash scripts/mark-ingested.sh .raw article.txt
```

## 文件修改策略

### 原则：不修改

`.raw/` 中的文件应该是**不可变的**。如果源文件更新了：

1. **保留原文件**作为历史版本
2. **添加新版本**，用版本号区分

```bash
# 原文件
.raw/article-v1.md

# 更新版本
.raw/article-v2.md
```

### 为什么？

1. **可追溯**：知道知识的来源
2. **可回滚**：如果新版本有问题
3. **一致性**：wiki 页面引用的是特定版本

### 如果必须修改？

如果文件有错误需要修正：

```bash
# 1. 备份原文件
cp .raw/article.md .raw/article.md.bak

# 2. 修改文件
vim .raw/article.md

# 3. 重新 ingest
"ingest article.md"

# 4. wiki 会自动更新
```

## 新增文件检测

### 自动检测

```bash
# 扫描新增文件
bash scripts/ingest.sh
```

输出示例：
```
🆕 NEW: new-article.md
✓  UNCHANGED: old-article.md
📝 MODIFIED: updated-article.md
```

### 手动检查

```bash
# 查看 .raw/ 中所有文件
find .raw -type f | sort

# 查看已 ingest 的文件
grep "source_file\|来源" wiki/sources/*.md

# 对比差异
diff <(find .raw -type f -exec basename {} \; | sort) \
     <(grep -h "source_file" wiki/sources/*.md | sort)
```

## 文件命名规范

### 推荐格式

```
[类型]-[简短描述].[扩展名]
```

### 示例

```
article-transformer-attention.md
video-3b1b-neural-networks.mp4
paper-bert-2018.pdf
book-deep-learning-ch1.md
meeting-2026-06-20.txt
```

### 避免

- 空格（用连字符代替）
- 特殊字符
- 过长的文件名
- 中文文件名（可选，英文更通用）

## 常见问题

### Q: 文件太大怎么办？

A: 对于大文件（视频、长文档），考虑：
1. 只提取需要的部分
2. 分章节 ingest
3. 使用摘要版本

### Q: 文件格式不支持？

A: 转换为支持的格式：
```bash
# 例如：将 Word 转为文本
pandoc document.docx -t plain -o document.txt
```

### Q: 如何处理重复文件？

A: 使用 manifest 检测：
```bash
# 查看 manifest
cat .raw/.manifest

# 检测重复
md5 -r .raw/* | sort | uniq -d
```

### Q: 文件被误删了？

A: 使用 git 恢复：
```bash
git checkout -- .raw/deleted-file.md
```
