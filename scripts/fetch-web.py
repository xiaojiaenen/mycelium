#!/usr/bin/env python3
"""
Fetch web articles and convert to Markdown using Scrapling.

Features:
- Auto-detect anti-bot protection
- Multiple extraction strategies
- Save as Markdown with metadata
- WeChat article support

Usage:
    python3 fetch-web.py <url> [--output <file>] [--selector <css>] [--stealth]
    python3 fetch-web.py https://example.com/article
    python3 fetch-web.py https://example.com/article --selector article
    python3 fetch-web.py https://protected-site.com/article --stealth
"""

import sys
import os
import re
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse


def is_wechat_url(url: str) -> bool:
    """Check if URL is a WeChat article."""
    return 'mp.weixin.qq.com' in url


def fetch_with_scrapling(url: str, stealth: bool = False, selector: str = None):
    """Fetch using Scrapling Python API."""
    try:
        if stealth:
            from scrapling.fetchers import StealthyFetcher
            print("[fetch] Using StealthyFetcher (anti-bot bypass)...")
            page = StealthyFetcher.fetch(
                url,
                headless=True,
                solve_cloudflare=True,
                network_idle=True,
            )
        else:
            from scrapling.fetchers import DynamicFetcher
            print("[fetch] Using DynamicFetcher (JS rendering)...")
            page = DynamicFetcher.fetch(
                url,
                headless=True,
                network_idle=True,
            )

        # Extract content using CSS selector if provided
        if selector:
            content = page.css(selector)
            if content:
                return content.getall(), page

        return page, page
    except Exception as e:
        print(f"[fetch] Scrapling error: {e}")
        return None, None


def fetch_with_curl(url: str) -> str:
    """Fetch using curl (fallback for WeChat and other special sites)."""
    print("[fetch] Using curl fallback...")

    headers = [
        '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        '-H', 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8',
    ]

    try:
        result = subprocess.run(
            ['curl', '-s', '-L', '-k', '--max-time', '30'] + headers + [url],
            capture_output=True, text=True, timeout=35
        )
        if result.returncode == 0 and len(result.stdout) > 1000:
            return result.stdout
        return None
    except Exception as e:
        print(f"[fetch] curl error: {e}")
        return None


def html_to_markdown(html: str) -> str:
    """Convert HTML to markdown."""
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
    for entity, char in [('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'), ('&quot;', '"'), ('&#39;', "'"), ('&nbsp;', ' ')]:
        text = text.replace(entity, char)

    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' +', ' ', text)

    return text.strip()


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
        result['content'] = html_to_markdown(content_html)
    else:
        # Fallback: try paragraphs
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, re.DOTALL)
        if paragraphs:
            result['content'] = '\n\n'.join(html_to_markdown(p) for p in paragraphs if len(p.strip()) > 20)

    return result


def extract_content_from_page(page, url: str) -> dict:
    """Extract content from Scrapling page object."""
    result = {
        'title': '',
        'content': '',
        'author': '',
        'date': '',
        'url': url,
    }

    # Try to get title
    title_selectors = ['h1', 'title', '[property="og:title"]', '.article-title', '.post-title']
    for sel in title_selectors:
        try:
            elem = page.css(sel)
            if elem:
                if sel == '[property="og:title"]':
                    result['title'] = elem.attrib.get('content', '')
                else:
                    result['title'] = elem[0].text.strip() if isinstance(elem, list) else elem.text.strip()
                if result['title']:
                    break
        except:
            continue

    # Try to get author
    author_selectors = ['[rel="author"]', '.author', '[property="article:author"]', '[name="author"]']
    for sel in author_selectors:
        try:
            elem = page.css(sel)
            if elem:
                if sel.startswith('['):
                    result['author'] = elem.attrib.get('content', '')
                else:
                    result['author'] = elem[0].text.strip() if isinstance(elem, list) else elem.text.strip()
                if result['author']:
                    break
        except:
            continue

    # Try to get date
    date_selectors = ['time', '[property="article:published_time"]', '.date', '.published']
    for sel in date_selectors:
        try:
            elem = page.css(sel)
            if elem:
                if sel.startswith('['):
                    result['date'] = elem.attrib.get('content', '')
                else:
                    result['date'] = elem[0].text.strip() if isinstance(elem, list) else elem.text.strip()
                    if not result['date']:
                        result['date'] = elem[0].attrib.get('datetime', '') if isinstance(elem, list) else elem.attrib.get('datetime', '')
                if result['date']:
                    break
        except:
            continue

    # Try to get content
    content_selectors = ['article', '.article-content', '.post-content', '.entry-content', '.content', 'main', '[role="main"]']
    for sel in content_selectors:
        try:
            elem = page.css(sel)
            if elem:
                content_elem = elem[0] if isinstance(elem, list) else elem
                # Use get_all_text() for recursive text extraction
                content = content_elem.get_all_text(strip=True) if hasattr(content_elem, 'get_all_text') else ''
                if len(content) > 100:
                    result['content'] = content
                    print(f"[extract] Found content using: {sel}")
                    break
        except:
            continue

    # Fallback: get all text from page
    if not result['content']:
        print("[extract] Using fallback: full page text")
        try:
            result['content'] = page.get_all_text(strip=True, valid_values=True)
        except:
            result['content'] = ''

    return result


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
  %(prog)s https://mp.weixin.qq.com/s/xxxxx
        """
    )
    parser.add_argument('url', help='URL to fetch')
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('-s', '--selector', help='CSS selector for content')
    parser.add_argument('--stealth', action='store_true', help='Use stealth mode (bypass anti-bot)')

    args = parser.parse_args()

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
    print("")

    article = None

    # Special handling for WeChat articles
    if is_wechat_url(args.url):
        print("[fetch] WeChat article detected, using curl...")
        html = fetch_with_curl(args.url)
        if html:
            article = extract_wechat_content(html, args.url)
            if article['content']:
                print(f"[extract] Successfully extracted WeChat article ({len(article['content'])} chars)")
            else:
                print("[extract] WeChat extraction failed")
                article = None

    # Try Scrapling for non-WeChat or if WeChat failed
    if article is None:
        page, raw_page = fetch_with_scrapling(args.url, args.stealth, args.selector)
        if page:
            article = extract_content_from_page(raw_page, args.url)
            print(f"[extract] Successfully extracted content ({len(article['content'])} chars)")
        else:
            # Fallback to curl
            print("[fetch] Scrapling failed, falling back to curl...")
            html = fetch_with_curl(args.url)
            if html:
                article = {
                    'title': '',
                    'content': html_to_markdown(html),
                    'author': '',
                    'date': '',
                    'url': args.url,
                }
                # Try to extract title
                title_match = re.search(r'<title[^>]*>([^<]+)</title>', html)
                if title_match:
                    article['title'] = title_match.group(1).strip()
            else:
                print("[error] Failed to fetch page")
                sys.exit(1)

    # Format as markdown
    markdown = to_markdown(article)

    # Show preview
    print("\n" + "=" * 60)
    print("Preview:")
    print("=" * 60)
    preview = markdown[:500] + "..." if len(markdown) > 500 else markdown
    print(preview)
    print("=" * 60)

    # Save
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown)
    print(f"\n[save] Saved to: {output_path}")

    # Summary
    print("\n[summary]")
    print(f"  Title: {article['title'] or '(not found)'}")
    print(f"  Author: {article['author'] or '(not found)'}")
    print(f"  Date: {article['date'] or '(not found)'}")
    print(f"  Content length: {len(article['content'])} chars")


if __name__ == "__main__":
    main()
