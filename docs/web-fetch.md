# Web Fetch Guide

使用 Scrapling 抓取网页文章并转换为 Markdown。

## 安装依赖

```bash
pip install "scrapling[all]"
scrapling install  # 下载浏览器依赖
```

## 基本用法

### 抓取普通网页

```bash
python3 scripts/fetch-web.py https://example.com/article
```

### 保存到指定位置

```bash
python3 scripts/fetch-web.py https://example.com/article -o article.md
```

### 使用 CSS 选择器

```bash
# 只抓取 article 标签内容
python3 scripts/fetch-web.py https://example.com/article --selector article

# 使用更精确的选择器
python3 scripts/fetch-web.py https://example.com/article --selector '.article-content'
```

### 绕过反爬保护

```bash
# 使用隐身模式（处理 Cloudflare 等）
python3 scripts/fetch-web.py https://protected-site.com/article --stealth
```

### 保存原始 HTML

```bash
python3 scripts/fetch-web.py https://example.com/article --raw
```

## 高级用法

### Python API

```python
from scripts.fetch_web import fetch_page, extract_article, to_markdown

# 获取页面
page = fetch_page('https://example.com/article', stealth=False)

# 提取文章
article = extract_article(page, 'https://example.com/article')

# 转换为 Markdown
markdown = to_markdown(article)
print(markdown)
```

### 自定义选择器

```python
from scripts.fetch_web import fetch_page, extract_article

page = fetch_page('https://example.com/article')

# 使用特定选择器
article = extract_article(
    page,
    'https://example.com/article',
    selector='#main-content'
)
```

## 支持的网站类型

| 类型 | 模式 | 示例 |
|------|------|------|
| 普通网页 | 默认 | 新闻、博客 |
| 反爬网站 | `--stealth` | Cloudflare 保护 |
| 动态页面 | `--stealth` | JavaScript 渲染 |
| 需要登录 | 暂不支持 | - |

## 提取策略

脚本按以下顺序尝试提取内容：

1. **用户指定的选择器**（如果提供）
2. **常见文章选择器**
   - `article`
   - `.article-content`
   - `.post-content`
   - `.entry-content`
   - `main`
3. **文本密度算法**（类似 Readability）
4. **原始文本**（兜底）

## 输出格式

生成的 Markdown 包含：

```markdown
# 标题

## 元信息
- 来源：URL
- 作者：作者名
- 日期：发布日期
- 抓取时间：YYYY-MM-DD HH:MM

---

正文内容...
```

## 常见问题

### Q: 抓取失败怎么办？

A: 尝试以下方法：

1. 使用 `--stealth` 模式
2. 检查网络连接
3. 使用 `--selector` 指定内容区域
4. 使用 `--raw` 保存原始 HTML 手动处理

### Q: 内容提取不完整？

A: 尝试：

1. 使用 `--selector` 指定更精确的选择器
2. 使用 `--raw` 查看原始 HTML 结构
3. 反馈问题以便改进提取逻辑

### Q: 如何处理需要登录的网站？

A: 目前不支持登录。可以：

1. 使用浏览器扩展（如 Obsidian Web Clipper）
2. 手动复制内容
3. 保存为 HTML 后处理

### Q: 支持哪些语言？

A: 支持所有语言，自动保留原文格式。

## 示例

### 抓取技术博客

```bash
python3 scripts/fetch-web.py https://blog.example.com/post/123 --selector '.post-body'
```

### 抓取新闻文章

```bash
python3 scripts/fetch-web.py https://news.example.com/article --selector 'article'
```

### 抓取受保护的网站

```bash
python3 scripts/fetch-web.py https://protected.example.com/article --stealth
```
