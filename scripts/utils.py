#!/usr/bin/env python3
"""Shared constants and utilities for Mycelium scripts."""
import re
from pathlib import Path
from collections import Counter
from datetime import date, datetime

TODAY = date.today().isoformat()

# ── File Extensions ──────────────────────────────────────

SUPPORTED_EXTENSIONS = {
    # Text
    '.txt', '.md', '.markdown', '.rst',
    # Documents
    '.pdf', '.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls',
    # Web
    '.html', '.htm', '.mhtml',
    # Data
    '.csv', '.json', '.xml', '.yaml', '.yml',
    # Subtitles / Captions
    '.srt', '.vtt', '.ass', '.sub', '.plain',
    # Ebooks
    '.epub',
    # Images (OCR)
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff',
    # Audio
    '.mp3', '.wav', '.m4a', '.flac', '.ogg',
    # Video
    '.mp4', '.mkv', '.webm', '.avi', '.mov',
    # Archives
    '.zip',
}

# ── Video URL Patterns ───────────────────────────────────

VIDEO_URL_PATTERNS = {
    "bilibili": r"bilibili\.com/video/",
    "youtube": r"(youtube\.com/watch|youtu\.be/)",
    "douyin": r"douyin\.com/video/",
    "tiktok": r"tiktok\.com/",
}

def is_video_url(url: str) -> bool:
    return any(re.search(p, url) for p in VIDEO_URL_PATTERNS.values())

def is_url(text: str) -> bool:
    return text.startswith("http://") or text.startswith("https://")

# ── Acronyms (title case) ───────────────────────────────

ACRONYMS = {
    'rlhf', 'ppo', 'dpo', 'sft', 'moe', 'llm', 'gpt', 'bert',
    'cv', 'nlp', 'ai', 'ml', 'rnn', 'cnn', 'lstm', 'gru',
    'rl', 'rlaif', 'sora', 'clip', 'vit', 'gan', 'vae', 'vae',
    'pdf', 'url', 'api', 'cli', 'mcp', 'rag', 'ocr', 'fft',
}

# ── Type Colors ──────────────────────────────────────────

TYPE_COLORS = {
    "source": "#a5d8ff",
    "concept": "#b2f2bb",
    "entity": "#ffec99",
    "comparison": "#ffc9c9",
    "question": "#d0bfff",
    "contradiction": "#ffd8a8",
}

TYPE_EMOJI = {
    "source": "📚",
    "concept": "💡",
    "entity": "👤",
    "comparison": "⚖️",
    "question": "❓",
    "contradiction": "⚡",
}

# ── Search Scoring ───────────────────────────────────────

BM25_WEIGHT = 0.5
LINK_WEIGHT = 0.25
VECTOR_WEIGHT = 0.25

BM25_K1 = 1.5
BM25_B = 0.75

PAGERANK_DAMPING = 0.85
PAGERANK_ITERATIONS = 20

# ── Layout Constants ─────────────────────────────────────

# Excalidraw
EXCALIDRAW_CANVAS_WIDTH = 1200
EXCALIDRAW_CANVAS_HEIGHT = 800
EXCALIDRAW_LAYOUT_RADIUS = 200
EXCALIDRAW_SIMULATION_ITERATIONS = 50
EXCALIDRAW_REPULSION = 5000
EXCALIDRAW_FORCE_STEP = 0.1
EXCALIDRAW_IDEAL_EDGE = 150
EXCALIDRAW_EDGE_ELASTICITY = 0.01

# Canvas
CANVAS_GRID_COLUMNS = 4
CANVAS_COL_SPACING = 300
CANVAS_ROW_SPACING = 200
CANVAS_NODE_WIDTH = 250
CANVAS_NODE_HEIGHT = 150

# ── Thresholds ───────────────────────────────────────────

STALE_THRESHOLD_DAYS = 30
MAX_SLUG_LENGTH = 50
PREVIEW_MAX_CHARS = 5000
HASH_CHUNK_SIZE = 8192

# ── Video ────────────────────────────────────────────────

DEFAULT_WHISPER_MODEL_GPU = "large-v3"
DEFAULT_WHISPER_MODEL_CPU = "small"
DOWNLOAD_TIMEOUT = 300
RETRY_DELAY = 5
DEFAULT_BROWSER = "chrome"

HF_MIRROR = "https://hf-mirror.com"

FILLERS = {"嗯", "啊", "哦", "呃", "um", "uh", "ah", "oh", "hmm"}

# ── Stopwords ────────────────────────────────────────────

STOPWORDS = {
    'the', 'and', 'for', 'that', 'this', 'with', 'from', 'are', 'was',
    'were', 'been', 'have', 'has', 'had', 'not', 'but', 'can', 'will',
    'just', 'also', 'than', 'its', 'into', 'more', 'some', 'would',
    'could', 'other', 'which', 'their', 'about', 'would', 'there',
    '这些', '那些', '一个', '可以', '没有', '不是', '就是', '已经',
    '因为', '所以', '如果', '但是', '或者', '而且', '虽然', '只是',
}

# ── Excalidraw ───────────────────────────────────────────

EXCALIDRAW_SOURCE = "mycelium"

# ── Utility Functions ────────────────────────────────────

def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown content."""
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, _, val = line.partition(':')
            val = val.strip().strip('"').strip("'")
            if val.startswith('[') and val.endswith(']'):
                val = [v.strip().strip('"').strip("'") for v in val[1:-1].split(',') if v.strip()]
            fm[key.strip()] = val
    return fm


def extract_wikilinks(content: str) -> list:
    """Extract [[wikilinks]] from markdown content."""
    return re.findall(r'\[\[([^\]]+)\]\]', content)


def slugify(name: str) -> str:
    """Convert name to filename-safe slug."""
    slug = name.lower().replace(' ', '-').replace('_', '-')
    slug = re.sub(r'[^a-z0-9一-鿿-]', '', slug)
    return slug[:MAX_SLUG_LENGTH]


def title_from_slug(slug: str) -> str:
    """Convert slug to display title, preserving acronyms."""
    words = slug.replace('-', ' ').split()
    title_words = [w.upper() if w.lower() in ACRONYMS else w.capitalize() for w in words]
    return ' '.join(title_words)


def extract_keywords(text: str, top_n: int = 10) -> list:
    """Extract keywords from text (simple TF approach)."""
    words = []
    words.extend(re.findall(r'[a-zA-Z]{3,}', text.lower()))
    words.extend(re.findall(r'[一-鿿]{2,4}', text))
    words = [w for w in words if w not in STOPWORDS]
    counter = Counter(words)
    return [w for w, _ in counter.most_common(top_n)]


def file_hash(file_path: str) -> str:
    """Compute MD5 hash of a file."""
    h = __import__('hashlib').md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(HASH_CHUNK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()
