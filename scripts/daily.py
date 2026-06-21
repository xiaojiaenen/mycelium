#!/usr/bin/env python3
"""Generate daily note for Mycelium wiki."""
import argparse
from pathlib import Path
from datetime import date, datetime


DAILY_TEMPLATE = """---
type: daily
title: "{date}"
created: {date}
tags: [daily]
status: evergreen
---

# {date} Daily Note

## 📥 Today's Ingest
<!-- What sources did you process today? -->

- [ ]

## 💡 Key Insights
<!-- What did you learn today? -->

-

## ❓ Open Questions
<!-- What questions came up? -->

-

## 🔗 Connections
<!-- How does today's learning connect to existing knowledge? -->

- [[existing-concept]] — new insight

## 📝 Notes
<!-- Free-form notes -->

"""

WEEKLY_TEMPLATE = """---
type: weekly
title: "Week {week_num}"
created: {date}
tags: [weekly]
status: evergreen
---

# Week {week_num} ({date})

## Summary
<!-- What were the main themes this week? -->

## Sources Ingested
<!-- List all sources from this week -->

## Key Concepts Learned
<!-- New concepts added to wiki -->

## Open Questions
<!-- Questions that remain unanswered -->

## Next Week
<!-- What to focus on next? -->

"""


def create_daily(wiki_dir: str = ".", target_date: str = None):
    """Create or open today's daily note."""
    base = Path(wiki_dir)
    wiki = base / "wiki"
    daily_dir = wiki / "daily"
    daily_dir.mkdir(parents=True, exist_ok=True)

    if target_date:
        d = datetime.strptime(target_date, "%Y-%m-%d").date()
    else:
        d = date.today()

    filename = f"{d.isoformat()}.md"
    filepath = daily_dir / filename

    if filepath.exists():
        print(f"📖 Opening existing: {filepath}")
        content = filepath.read_text(encoding='utf-8')
        print(content)
        return

    content = DAILY_TEMPLATE.replace("{date}", d.isoformat())
    filepath.write_text(content, encoding='utf-8')
    print(f"✅ Created: {filepath}")


def create_weekly(wiki_dir: str = ".", target_date: str = None):
    """Create or open this week's weekly note."""
    base = Path(wiki_dir)
    wiki = base / "wiki"
    weekly_dir = wiki / "weekly"
    weekly_dir.mkdir(parents=True, exist_ok=True)

    if target_date:
        d = datetime.strptime(target_date, "%Y-%m-%d").date()
    else:
        d = date.today()

    week_num = d.isocalendar()[1]
    filename = f"week-{week_num:02d}.md"
    filepath = weekly_dir / filename

    if filepath.exists():
        print(f"📖 Opening existing: {filepath}")
        content = filepath.read_text(encoding='utf-8')
        print(content)
        return

    content = WEEKLY_TEMPLATE.replace("{week_num}", str(week_num)).replace("{date}", d.isoformat())
    filepath.write_text(content, encoding='utf-8')
    print(f"✅ Created: {filepath}")


def main():
    parser = argparse.ArgumentParser(description="Create daily/weekly notes")
    parser.add_argument("type", choices=["daily", "weekly"], help="Note type")
    parser.add_argument("--dir", "-d", default=".", help="Wiki root directory")
    parser.add_argument("--date", default=None, help="Date (YYYY-MM-DD, default: today)")
    args = parser.parse_args()

    if args.type == "weekly":
        create_weekly(args.dir, args.date)
    else:
        create_daily(args.dir, args.date)


if __name__ == "__main__":
    main()
