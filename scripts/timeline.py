#!/usr/bin/env python3
"""Generate concept evolution timeline chart."""
import re
import argparse
from pathlib import Path
from datetime import date

import sys
sys.path.insert(0, str(Path(__file__).parent))
from utils import parse_frontmatter, TYPE_COLORS


def get_timeline_data(wiki_dir: Path) -> dict:
    """Extract evolution data from concept notes."""
    concepts_dir = wiki_dir / "wiki" / "concepts"
    if not concepts_dir.exists():
        return {}

    data = {}
    for md_file in concepts_dir.glob('*.md'):
        content = md_file.read_text(encoding='utf-8')
        fm = parse_frontmatter(content)

        name = fm.get('title', md_file.stem)
        version = int(fm.get('version', '1'))
        confidence = float(fm.get('confidence', '0.5'))
        strength = fm.get('evidence_strength', 'weak')
        created = fm.get('created', '')
        last_verified = fm.get('last_verified', created)

        data[md_file.stem] = {
            "name": name,
            "version": version,
            "confidence": confidence,
            "strength": strength,
            "created": created,
            "last_verified": last_verified,
        }

    return data


def generate_timeline_chart(wiki_dir: str = ".", output: str = None):
    """Generate matplotlib timeline chart."""
    base = Path(wiki_dir)

    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
    except ImportError:
        print("❌ matplotlib not installed. Run: pip install matplotlib")
        return

    data = get_timeline_data(base)
    if not data:
        print("❌ No concept notes found")
        return

    # Filter concepts with version > 1 (have evolution)
    evolved = {k: v for k, v in data.items() if v['version'] > 1}

    if not evolved:
        print("ℹ️  No concept evolution detected yet (all version 1)")
        print("   Concepts evolve when new sources are ingested.")
        # Show all concepts as a bar chart instead
        evolved = data

    # Sort by version (most evolved first)
    sorted_concepts = sorted(evolved.values(), key=lambda x: x['version'], reverse=True)

    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('🍄 Mycelium Knowledge Evolution', fontsize=14, fontweight='bold')

    # Chart 1: Version bar chart
    names = [c['name'][:20] for c in sorted_concepts[:10]]
    versions = [c['version'] for c in sorted_concepts[:10]]
    colors = ['#b2f2bb' if v >= 3 else '#ffec99' if v >= 2 else '#a5d8ff' for v in versions]

    bars = ax1.barh(names, versions, color=colors, edgecolor='#333', linewidth=0.5)
    ax1.set_xlabel('Version')
    ax1.set_title('Concept Evolution')
    ax1.invert_yaxis()

    # Add version labels
    for bar, v in zip(bars, versions):
        ax1.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                f'v{v}', va='center', fontsize=10)

    # Chart 2: Confidence vs Evidence scatter
    all_concepts = list(data.values())
    confidences = [c['confidence'] for c in all_concepts]
    strength_map = {'weak': 1, 'moderate': 2, 'strong': 3}
    strengths = [strength_map.get(c['strength'], 0) for c in all_concepts]

    scatter_colors = []
    for c in all_concepts:
        if c['strength'] == 'strong':
            scatter_colors.append('#b2f2bb')
        elif c['strength'] == 'moderate':
            scatter_colors.append('#ffec99')
        else:
            scatter_colors.append('#ffc9c9')

    ax2.scatter(strengths, confidences, c=scatter_colors, s=100, edgecolors='#333', linewidth=0.5)
    ax2.set_xlabel('Evidence Strength')
    ax2.set_ylabel('Confidence')
    ax2.set_title('Confidence vs Evidence')
    ax2.set_xticks([1, 2, 3])
    ax2.set_xticklabels(['Weak', 'Moderate', 'Strong'])
    ax2.set_ylim(0, 1.1)

    # Add concept labels
    for i, c in enumerate(all_concepts):
        ax2.annotate(c['name'][:15], (strengths[i], confidences[i]),
                    fontsize=7, alpha=0.7, ha='center', va='bottom')

    plt.tight_layout()

    output = output or str(base / "wiki" / "meta" / "evolution-timeline.png")
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"✅ Generated: {output}")
    print(f"   Concepts: {len(data)}")
    print(f"   Evolved (v>1): {len(evolved)}")


def main():
    parser = argparse.ArgumentParser(description="Generate concept evolution timeline")
    parser.add_argument("--dir", "-d", default=".", help="Wiki root directory")
    parser.add_argument("--output", "-o", default=None, help="Output PNG file path")
    args = parser.parse_args()
    generate_timeline_chart(args.dir, args.output)


if __name__ == "__main__":
    main()
