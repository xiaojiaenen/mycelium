#!/usr/bin/env python3
"""
Fetch web articles and convert to Markdown using Scrapling.

Features:
- Auto-detect anti-bot protection
- Multiple extraction strategies
- Save as Markdown with metadata

Usage:
    python3 fetch-web.py <url> [--output <file>] [--selector <css>] [--stealth]
    python3 fetch-web.py https://example.com/article
    python3 fetch-web.py https://example.com/article --selector article
    python3 fetch-web.py https://protected-site.com/article --stealth
"""

import sys
import os
import re
import argparse
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, urljoin


def check_scrapling():
    """Check if Scrapling is installed."""
    try:
        import scrapling
        return True
    except ImportError:
        print("Error: Scrapling not installed")
        print("Install: pip install 'scrapling[all]' && scrapling install")
        return False


def is_wechat_url(url: str) -> bool:
    """Check if URL is a WeChat article."""
    return 'mp.weixin.qq.com' in url


def fetch_wechat_with_curl(url: str) -> str:
    """Fetch WeChat article using curl (more reliable than Scrapling for WeChat)."""
    import subprocess

    print("[fetch] Detected WeChat URL, using curl fallback...")

    headers = [
        '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        '-H', 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8',
    ]

    try:
        result = subprocess.run(
            ['curl', '-s', '-L', '-k', '--max-time', '30'] + headers + [url],
            capture_output=True,
            text=True,
            timeout=35
        )

        if result.returncode == 0 and len(result.stdout) > 1000:
            return result.stdout
        else:
            print(f"[fetch] curl failed: return code {result.returncode}, output length: {len(result.stdout)}")
            return None
    except Exception as e:
        print(f"[fetch] curl error: {e}")
        return None


def extract_wechat_content(html: str, url: str) -> dict:
    """Extract content from WeChat article HTML."""
    result = {
        'title': '',
        'content': '',
        'author': '',
        'date': '',
        'url': url,
    }

    # Extract title
    title_match = re.search(r'var\s+msg_title\s*=\s*["\']([^"\']+)["\']', html)
    if not title_match:
        title_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    if title_match:
        result['title'] = title_match.group(1).strip()

    # Extract author
    author_match = re.search(r'var\s+nickname\s*=\s*["\']([^"\']+)["\']', html)
    if not author_match:
        author_match = re.search(r'class="rich_media_meta_nickname"[^>]*>([^<]+)<', html)
    if author_match:
        result['author'] = author_match.group(1).strip()

    # Extract date
    date_match = re.search(r'var\s+ct\s*=\s*["\'](\d+)["\']', html)
    if date_match:
        import datetime
        timestamp = int(date_match.group(1))
        result['date'] = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

    # Extract content from #js_content
    content_match = re.search(r'id="js_content"[^>]*>(.*?)</div>\s*</div>\s*<div[^>]*class="rich_media_tool"', html, re.DOTALL)
    if not content_match:
        content_match = re.search(r'id="js_content"[^>]*>(.*?)<!--', html, re.DOTALL)
    if not content_match:
        content_match = re.search(r'id="js_content"[^>]*>(.*?)</div>', html, re.DOTALL)

    if content_match:
        content_html = content_match.group(1)
        # Convert HTML to markdown-like text
        content = html_to_markdown(content_html)
        result['content'] = content
    else:
        # Fallback: try to find any substantial content
        print("[extract] Could not find #js_content, trying fallback...")
        # Look for paragraphs
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, re.DOTALL)
        if paragraphs:
            result['content'] = '\n\n'.join(html_to_markdown(p) for p in paragraphs if len(p.strip()) > 20)

    return result


def html_to_markdown(html: str) -> str:
    """Convert HTML to markdown."""
    import re

    # Remove HTML comments
    text = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)

    # Handle headings
    for i in range(6, 0, -1):
        text = re.sub(f'<h{i}[^>]*>(.*?)</h{i}>', r'\n' + '#' * i + r' \1\n', text, flags=re.DOTALL)

    # Handle bold/strong
    text = re.sub(r'<(strong|b)[^>]*>(.*?)</\1>', r'**\2**', text, flags=re.DOTALL)

    # Handle italic/em
    text = re.sub(r'<(em|i)[^>]*>(.*?)</\1>', r'*\2*', text, flags=re.DOTALL)

    # Handle links
    text = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', text, flags=re.DOTALL)

    # Handle images
    text = re.sub(r'<img[^>]*data-src="([^"]*)"[^>]*/?\s*>', r'![](\1)', text)
    text = re.sub(r'<img[^>]*src="([^"]*)"[^>]*/?\s*>', r'![](\1)', text)

    # Handle lists
    text = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1', text, flags=re.DOTALL)
    text = re.sub(r'<ul[^>]*>(.*?)</ul>', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'<ol[^>]*>(.*?)</ol>', r'\1', text, flags=re.DOTALL)

    # Handle blockquotes
    text = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', r'\n> \1\n', text, flags=re.DOTALL)

    # Handle code blocks
    text = re.sub(r'<pre[^>]*>(.*?)</pre>', r'\n```\n\1\n```\n', text, flags=re.DOTALL)
    text = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', text, flags=re.DOTALL)

    # Handle paragraphs
    text = re.sub(r'<p[^>]*>(.*?)</p>', r'\n\1\n', text, flags=re.DOTALL)

    # Handle line breaks
    text = re.sub(r'<br\s*/?\s*>', '\n', text)

    # Handle sections/divs
    text = re.sub(r'<(section|div)[^>]*>(.*?)</\1>', r'\n\2\n', text, flags=re.DOTALL)

    # Remove remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Decode HTML entities
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    text = text.replace('&nbsp;', ' ')

    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' +', ' ', text)

    return text.strip()


def fetch_page(url: str, stealth: bool = False, headless: bool = True):
    """Fetch page using Scrapling."""
    try:
        if stealth:
            from scrapling.fetchers import StealthyFetcher
            print(f"[fetch] Using stealth mode...")
            page = StealthyFetcher.fetch(
                url,
                headless=headless,
                solve_cloudflare=True,
                network_idle=True,
            )
        else:
            from scrapling.fetchers import Fetcher
            print(f"[fetch] Using fast mode...")
            page = Fetcher.get(url, impersonate='chrome')

        return page
    except Exception as e:
        print(f"[fetch] Error: {e}")
        return None


def extract_article(page, url: str, selector: str = None) -> dict:
    """Extract article content from page."""
    result = {
        'title': '',
        'content': '',
        'author': '',
        'date': '',
        'url': url,
    }

    # Try to find title
    title_selectors = [
        'h1',
        'article h1',
        '.article-title',
        '.post-title',
        '[property="og:title"]',
        'title',
    ]

    for sel in title_selectors:
        try:
            elem = page.css(sel)
            if elem:
                if sel == '[property="og:title"]':
                    result['title'] = elem.attrib.get('content', '')
                else:
                    result['title'] = elem[0].text.strip()
                if result['title']:
                    break
        except:
            continue

    # Try to find author
    author_selectors = [
        '[rel="author"]',
        '.author',
        '.byline',
        '[property="article:author"]',
        '[name="author"]',
    ]

    for sel in author_selectors:
        try:
            elem = page.css(sel)
            if elem:
                if sel.startswith('['):
                    result['author'] = elem.attrib.get('content', '')
                else:
                    result['author'] = elem[0].text.strip()
                if result['author']:
                    break
        except:
            continue

    # Try to find date
    date_selectors = [
        'time',
        '[property="article:published_time"]',
        '.date',
        '.published',
        '[name="pubdate"]',
    ]

    for sel in date_selectors:
        try:
            elem = page.css(sel)
            if elem:
                if sel.startswith('['):
                    result['date'] = elem.attrib.get('content', '')
                else:
                    result['date'] = elem[0].text.strip()
                    # Also check datetime attribute
                    if not result['date']:
                        result['date'] = elem[0].attrib.get('datetime', '')
                if result['date']:
                    break
        except:
            continue

    # Extract main content
    content_selectors = [
        selector,  # User-specified selector first
        'article',
        '.article-content',
        '.post-content',
        '.entry-content',
        '.content',
        'main',
        '[role="main"]',
        '.story-body',
        '#article-body',
    ]

    # Filter out None
    content_selectors = [s for s in content_selectors if s]

    for sel in content_selectors:
        try:
            elem = page.css(sel)
            if elem:
                # Get the first match
                content_elem = elem[0] if isinstance(elem, list) else elem

                # Extract text with structure
                content = extract_structured_text(content_elem)
                if len(content) > 100:  # Minimum content length
                    result['content'] = content
                    print(f"[extract] Found content using: {sel}")
                    break
        except Exception as e:
            continue

    # Fallback: get all text from body
    if not result['content']:
        print("[extract] Using fallback: body text")
        try:
            body = page.css('body')
            if body:
                result['content'] = extract_structured_text(body[0])
        except:
            pass

    return result


def extract_structured_text(element) -> str:
    """Extract text preserving structure (headings, paragraphs, lists)."""
    lines = []

    # Walk through all child elements
    for child in element.css('*'):
        tag = child.tag.lower() if hasattr(child, 'tag') else ''
        text = child.text.strip() if hasattr(child, 'text') else ''

        if not text:
            continue

        # Handle different tags
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(tag[1])
            lines.append(f"\n{'#' * level} {text}\n")
        elif tag == 'p':
            lines.append(f"\n{text}\n")
        elif tag == 'li':
            lines.append(f"- {text}")
        elif tag == 'blockquote':
            lines.append(f"\n> {text}\n")
        elif tag == 'pre':
            lines.append(f"\n```\n{text}\n```\n")
        elif tag == 'code':
            # Check if inside pre
            parent_tag = child.parent.tag.lower() if hasattr(child, 'parent') and hasattr(child.parent, 'tag') else ''
            if parent_tag != 'pre':
                lines.append(f"`{text}`")
        elif tag in ['strong', 'b']:
            lines.append(f"**{text}**")
        elif tag in ['em', 'i']:
            lines.append(f"*{text}*")
        elif tag == 'a':
            href = child.attrib.get('href', '')
            if href:
                lines.append(f"[{text}]({href})")
            else:
                lines.append(text)
        elif tag in ['div', 'section', 'article']:
            # Only add if it's a direct text node
            if child.children_count == 0 if hasattr(child, 'children_count') else True:
                lines.append(text)

    # Join and clean up
    content = '\n'.join(lines)

    # Remove excessive newlines
    content = re.sub(r'\n{3,}', '\n\n', content)

    return content.strip()


def extract_with_fallbacks(page, url: str, selector: str = None) -> dict:
    """Try multiple extraction strategies."""
    # Strategy 1: CSS selectors
    result = extract_article(page, url, selector)

    # Strategy 2: If content is too short, try readability-like approach
    if len(result['content']) < 200:
        print("[extract] Content too short, trying alternative extraction...")
        result['content'] = extract_by_density(page)

    # Strategy 3: If still short, get all text
    if len(result['content']) < 200:
        print("[extract] Using raw text extraction...")
        result['content'] = page.text if hasattr(page, 'text') else ''

    return result


def extract_by_density(page) -> str:
    """Extract content by text density (readability-like)."""
    candidates = []

    # Find all divs with substantial text
    for div in page.css('div, article, section, main'):
        text = div.text.strip() if hasattr(div, 'text') else ''
        if len(text) > 200:
            # Calculate text density
            tags = len(div.css('*'))
            text_len = len(text)
            density = text_len / max(tags, 1)
            candidates.append((density, text_len, div, text))

    # Sort by density * length
    candidates.sort(key=lambda x: x[0] * x[1], reverse=True)

    if candidates:
        return candidates[0][3]

    return ''


def to_markdown(article: dict) -> str:
    """Convert article to markdown format."""
    lines = []

    # Title
    if article['title']:
        lines.append(f"# {article['title']}")
        lines.append("")

    # Metadata
    lines.append("## 元信息")
    lines.append(f"- 来源：{article['url']}")
    if article['author']:
        lines.append(f"- 作者：{article['author']}")
    if article['date']:
        lines.append(f"- 日期：{article['date']}")
    lines.append(f"- 抓取时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Content
    if article['content']:
        lines.append(article['content'])
    else:
        lines.append("*无法提取正文内容*")

    return '\n'.join(lines)


def save_markdown(content: str, output_path: str):
    """Save content to markdown file."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[save] Saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Fetch web articles and convert to Markdown',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://example.com/article
  %(prog)s https://example.com/article -o article.md
  %(prog)s https://example.com/article --selector article
  %(prog)s https://protected-site.com --stealth
        """
    )
    parser.add_argument('url', help='URL to fetch')
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('-s', '--selector', help='CSS selector for content')
    parser.add_argument('--stealth', action='store_true', help='Use stealth mode (bypass anti-bot)')
    parser.add_argument('--headless', action='store_true', default=True, help='Run browser headless')
    parser.add_argument('--raw', action='store_true', help='Save raw HTML instead of markdown')

    args = parser.parse_args()

    # Check Scrapling
    if not check_scrapling():
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        # Generate filename from URL
        parsed = urlparse(args.url)
        domain = parsed.netloc.replace('www.', '')
        path = parsed.path.strip('/').replace('/', '-')
        if path:
            filename = f"{domain}-{path}.md"
        else:
            filename = f"{domain}.md"
        output_path = os.path.join('.raw', filename)

    # Ensure .raw directory exists
    if not args.output:
        os.makedirs('.raw', exist_ok=True)

    print(f"[info] URL: {args.url}")
    print(f"[info] Output: {output_path}")
    print(f"[info] Stealth: {args.stealth}")
    print("")

    # Special handling for WeChat articles
    article = None
    if is_wechat_url(args.url):
        print("[fetch] WeChat article detected, trying curl first...")
        html = fetch_wechat_with_curl(args.url)
        if html:
            article = extract_wechat_content(html, args.url)
            if article['content']:
                print(f"[extract] Successfully extracted WeChat article ({len(article['content'])} chars)")
            else:
                print("[extract] curl fetched but extraction failed, falling back to Scrapling...")
                article = None

    # Fallback to Scrapling if WeChat extraction failed or not WeChat
    if article is None:
        # Fetch page
        page = fetch_page(args.url, stealth=args.stealth, headless=args.headless)
        if not page:
            print("[error] Failed to fetch page")
            sys.exit(1)

        # Save raw HTML if requested
        if args.raw:
            raw_path = output_path.replace('.md', '.html')
            with open(raw_path, 'w', encoding='utf-8') as f:
                f.write(page.html if hasattr(page, 'html') else str(page))
            print(f"[save] Saved raw HTML to: {raw_path}")
            return

        # Extract article
        print("[extract] Extracting article content...")
        article = extract_with_fallbacks(page, args.url, args.selector)

    # Convert to markdown
    markdown = to_markdown(article)

    # Show preview
    print("\n" + "=" * 60)
    print("Preview:")
    print("=" * 60)
    preview = markdown[:500] + "..." if len(markdown) > 500 else markdown
    print(preview)
    print("=" * 60)

    # Save
    save_markdown(markdown, output_path)

    # Summary
    print("\n[summary]")
    print(f"  Title: {article['title'] or '(not found)'}")
    print(f"  Author: {article['author'] or '(not found)'}")
    print(f"  Date: {article['date'] or '(not found)'}")
    print(f"  Content length: {len(article['content'])} chars")


if __name__ == "__main__":
    main()
