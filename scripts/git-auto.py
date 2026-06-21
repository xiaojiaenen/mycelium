#!/usr/bin/env python3
"""Auto-commit wiki changes with descriptive messages."""
import subprocess
import argparse
from pathlib import Path


def git_auto_commit(wiki_dir: str = ".", message: str = "auto: update wiki"):
    base = Path(wiki_dir)

    # Check if git repo
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                       cwd=str(base), check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ Not a git repository. Run init.py first.")
        return

    # Stage all
    subprocess.run(["git", "add", "-A"], cwd=str(base), check=True,
                   capture_output=True)

    # Check for changes
    result = subprocess.run(["git", "diff", "--cached", "--quiet"],
                            cwd=str(base), capture_output=True)
    if result.returncode == 0:
        print("No changes to commit.")
        return

    # Commit
    subprocess.run(["git", "commit", "-q", "-m", message],
                   cwd=str(base), check=True, capture_output=True)
    print(f"✅ Committed: {message}")


def main():
    parser = argparse.ArgumentParser(description="Auto-commit wiki changes")
    parser.add_argument("--dir", "-d", default=".", help="Wiki directory")
    parser.add_argument("-m", "--message", default="auto: update wiki",
                        help="Commit message")
    args = parser.parse_args()
    git_auto_commit(args.dir, args.message)


if __name__ == "__main__":
    main()
