#!/usr/bin/env python3
"""
Video processing for Mycelium.
Download videos from URLs and extract captions using faster-whisper.
Supports: YouTube, Bilibili, 抖音, TikTok, and local files.
Cross-platform: macOS, Linux, Windows.
"""
import os
import sys
import re
import time
import argparse
import subprocess
import platform
from pathlib import Path

# Fix OpenMP conflict on macOS
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

HF_MIRROR = "https://hf-mirror.com"
MAX_RETRIES = 3

URL_PATTERNS = {
    "bilibili": r"bilibili\.com/video/",
    "youtube": r"(youtube\.com/watch|youtu\.be/)",
    "douyin": r"douyin\.com/video/",
    "tiktok": r"tiktok\.com/",
}


def is_url(text: str) -> bool:
    return text.startswith("http://") or text.startswith("https://")


def is_video_url(url: str) -> bool:
    return any(re.search(p, url) for p in URL_PATTERNS.values())


def check_yt_dlp() -> bool:
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def download_video(url: str, output_dir: str = ".") -> str:
    """Download video using yt-dlp with retry."""
    print(f"[download] Downloading: {url}")

    for attempt in range(MAX_RETRIES):
        try:
            cmd = [
                "yt-dlp",
                "-o", os.path.join(output_dir, "%(title)s.%(ext)s"),
                "--no-playlist",
                url,
            ]
            # Try with browser cookies on macOS/Linux
            if platform.system() != "Windows":
                try:
                    cmd.insert(1, "--cookies-from-browser")
                    cmd.insert(2, "chrome")
                except Exception:
                    pass

            result = subprocess.run(cmd, capture_output=True, text=True,
                                    check=True, timeout=300)

            for line in result.stdout.split("\n"):
                if "[download] Destination:" in line:
                    return line.split("Destination:")[-1].strip()
                elif "[Merger] Merging formats into" in line:
                    return line.split("into")[-1].strip().strip('"')

            # Fallback: find most recent video file
            video_extensions = [".mp4", ".mkv", ".webm", ".flv"]
            files = sorted(
                [f for f in os.listdir(output_dir)
                 if any(f.endswith(ext) for ext in video_extensions)],
                key=lambda x: os.path.getmtime(os.path.join(output_dir, x)),
                reverse=True,
            )
            if files:
                return os.path.join(output_dir, files[0])

            raise Exception("Could not determine downloaded file path")

        except subprocess.TimeoutExpired:
            print(f"[download] Timeout on attempt {attempt + 1}/{MAX_RETRIES}")
        except subprocess.CalledProcessError as e:
            print(f"[download] Error on attempt {attempt + 1}: {e.stderr[:100] if e.stderr else ''}")

        if attempt < MAX_RETRIES - 1:
            print(f"[download] Retrying in 5 seconds...")
            time.sleep(5)

    raise Exception(f"Failed to download after {MAX_RETRIES} attempts")


def load_model(model_size: str, device: str = "auto"):
    """Load whisper model with retry and mirror fallback."""
    for attempt in range(MAX_RETRIES):
        try:
            if "HF_ENDPOINT" in os.environ:
                return _load(model_size, device)
            print(f"[model] Loading {model_size}...")
            try:
                return _load(model_size, device)
            except Exception as e:
                print(f"[model] Official site failed: {e}")
                print(f"[model] Falling back to mirror: {HF_MIRROR}")
                os.environ["HF_ENDPOINT"] = HF_MIRROR
                return _load(model_size, device)
        except Exception as e:
            print(f"[model] Error on attempt {attempt + 1}: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(5)
    raise Exception(f"Failed to load model after {MAX_RETRIES} attempts")


def _load(model_size: str, device: str = "auto"):
    from faster_whisper import WhisperModel

    if device == "auto":
        try:
            import torch
            if torch.cuda.is_available():
                device, compute_type = "cuda", "float16"
            else:
                device, compute_type = "cpu", "int8"
        except ImportError:
            device, compute_type = "cpu", "int8"
    elif device == "cuda":
        compute_type = "float16"
    else:
        compute_type = "int8"

    return WhisperModel(model_size, device=device, compute_type=compute_type)


def auto_select_model() -> str:
    """Select appropriate model based on hardware."""
    try:
        import torch
        if torch.cuda.is_available():
            return "large-v3"  # GPU: use best model
    except ImportError:
        pass

    # CPU only: use fast model
    machine = platform.machine().lower()
    if machine in ("arm64", "aarch64"):
        return "base"  # Apple Silicon: base is fast enough
    else:
        return "base"  # Other CPU: use base for speed


def detect_language(model, audio_path: str) -> tuple:
    print("[detect] Detecting language...")
    _, info = model.transcribe(audio_path, task="transcribe")
    print(f"[detect] Detected: {info.language} ({info.language_probability:.0%})")
    return info.language, info.language_probability


def post_process_segments(segments: list) -> list:
    if not segments:
        return segments
    processed = []
    prev_text = ""
    FILLERS = {"嗯", "啊", "哦", "呃", "um", "uh", "ah", "oh", "hmm"}
    for seg in segments:
        text = seg.text.strip()
        if not text or text == prev_text:
            continue
        if seg.end - seg.start < 0.5 and text.lower() in FILLERS:
            continue
        processed.append(seg)
        prev_text = text
    return processed


def format_srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(segments: list, output_file: str):
    with open(output_file, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            f.write(f"{i}\n{format_srt_time(seg.start)} --> {format_srt_time(seg.end)}\n{seg.text.strip()}\n\n")


def write_txt(segments: list, output_file: str):
    with open(output_file, "w", encoding="utf-8") as f:
        for seg in segments:
            f.write(f"[{seg.start:.1f}s -> {seg.end:.1f}s] {seg.text.strip()}\n")


def write_plain(segments: list, output_file: str):
    """Write plain text without timestamps — best for LLM ingest."""
    with open(output_file, "w", encoding="utf-8") as f:
        for seg in segments:
            f.write(seg.text.strip() + "\n")


def extract(video_path: str, language: str = None, model_size: str = "large-v3",
            output_format: str = "srt", device: str = "auto", post_process: bool = True,
            output_dir: str = None, output_name: str = None) -> str:
    """Extract captions from video file or URL."""
    if is_url(video_path):
        if not check_yt_dlp():
            raise Exception("yt-dlp not installed. Run: pip install yt-dlp")
        video_path = download_video(video_path, output_dir or ".")

    if output_name:
        output_file = os.path.join(output_dir or ".", f"{output_name}.{output_format}")
    elif output_dir:
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_file = os.path.join(output_dir, f"{base_name}.{output_format}")
    else:
        output_file = video_path.rsplit(".", 1)[0] + f".{output_format}"

    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)

    model = load_model(model_size, device)

    if language is None:
        language, _ = detect_language(model, video_path)

    print(f"[transcribe] Transcribing (language: {language})...")
    start_time = time.time()
    segments, info = model.transcribe(video_path, language=language)

    # Stream segments with progress
    segments_list = []
    for seg in segments:
        segments_list.append(seg)
        if len(segments_list) % 50 == 0:
            elapsed = time.time() - start_time
            print(f"[transcribe]   ... {len(segments_list)} segments ({elapsed:.0f}s)")

    elapsed = time.time() - start_time
    print(f"[transcribe] Done: {len(segments_list)} segments in {elapsed:.0f}s")

    if post_process:
        original = len(segments_list)
        segments_list = post_process_segments(segments_list)
        removed = original - len(segments_list)
        if removed:
            print(f"[post-process] Removed {removed} duplicate/filler segments")

    writers = {"srt": write_srt, "txt": write_txt, "plain": write_plain}
    writer = writers.get(output_format, write_srt)
    writer(segments_list, output_file)

    elapsed = time.time() - start_time
    print(f"✅ Saved: {output_file}")
    print(f"   Time: {elapsed:.1f}s | Segments: {len(segments_list)}")

    return output_file


def main():
    parser = argparse.ArgumentParser(
        description="Extract captions from video or URL for Mycelium")
    parser.add_argument("sources", nargs="+",
                        help="Video file paths or URLs (YouTube/Bilibili/抖音/TikTok)")
    parser.add_argument("-l", "--language", default=None,
                        help="Language code (auto-detect if not specified)")
    parser.add_argument("-m", "--model", default="auto",
                        help="Model: base/small/medium/large-v3/auto (default: auto — picks fast model for your hardware)")
    parser.add_argument("-f", "--format", default="plain",
                        choices=["srt", "txt", "plain"],
                        help="Output format (default: plain, best for LLM ingest)")
    parser.add_argument("-d", "--device", default="auto",
                        choices=["auto", "cpu", "cuda"],
                        help="Device (default: auto)")
    parser.add_argument("-o", "--output-dir", default=None,
                        help="Output directory")
    parser.add_argument("-n", "--output-name", default=None,
                        help="Custom output filename (single file only)")
    args = parser.parse_args()

    if args.output_name and len(args.sources) > 1:
        print("Error: --output-name cannot be used with multiple sources")
        sys.exit(1)

    # Auto-select model if needed
    model_size = args.model
    if model_size == "auto":
        model_size = auto_select_model()
        print(f"[model] Auto-selected: {model_size}")

    for source in args.sources:
        try:
            extract(
                source,
                language=args.language,
                model_size=model_size,
                output_format=args.format,
                device=args.device,
                output_dir=args.output_dir,
                output_name=args.output_name,
            )
        except Exception as e:
            print(f"Error processing {source}: {e}", file=sys.stderr)
            continue


if __name__ == "__main__":
    main()
