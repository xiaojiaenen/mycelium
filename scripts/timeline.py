#!/usr/bin/env python3
"""Generate concept evolution timeline chart."""
import re
import argparse
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
from utils import parse_frontmatter, TYPE_COLORS

# Version colors
VERSION_COLORS = {
    1: '#a5d8ff',   # Blue - initial
    2: '#ffec99',   # Yellow - moderate evolution
    3: '#b2f2bb',   # Green - well evolved
}


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
    except ImportError:
        print("❌ matplotlib not installed. Run: pip install matplotlib")
        return

    data = get_timeline_data(base)
    if not data:
        print("❌ No concept notes found")
        return

    # Filter concepts with version > 1 (have evolution)
    evolved = {k: v for k, v in data.items() if v['version'] > 1}
    has_evolution = len(evolved) > 0

    if not has_evolution:
        print("ℹ️  No concept evolution detected yet (all version 1)")
        print("   Concepts evolve when new sources are ingested.")
        print("   Showing all concepts overview instead.\n")
        # Show all concepts
        chart_data = data
        chart_title = 'Concept Overview'
    else:
        chart_data = evolved
        chart_title = 'Concept Evolution'

    # Sort by version (most evolved first)
    sorted_concepts = sorted(chart_data.values(), key=lambda x: x['version'], reverse=True)

    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    fig.suptitle('🍄 Mycelium Knowledge Evolution', fontsize=16, fontweight='bold', y=0.98)

    # Chart 1: Version bar chart
    names = [c['name'][:25] for c in sorted_concepts[:12]]
    versions = [c['version'] for c in sorted_concepts[:12]]
    colors = [VERSION_COLORS.get(min(v, 3), '#a5d8ff') for v in versions]

    bars = ax1.barh(names, versions, color=colors, edgecolor='#444', linewidth=0.8, height=0.6)
    ax1.set_xlabel('Version', fontsize=11)
    ax1.set_title(chart_title, fontsize=13, fontweight='bold', pad=15)
    ax1.invert_yaxis()
    ax1.set_xlim(0, max(versions) + 1)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # Add version labels
    for bar, v in zip(bars, versions):
        ax1.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                f'v{v}', va='center', fontsize=10, fontweight='bold')

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

    scatter = ax2.scatter(strengths, confidences, c=scatter_colors, s=120,
                         edgecolors='#444', linewidth=0.8, alpha=0.9, zorder=5)
    ax2.set_xlabel('Evidence Strength', fontsize=11)
    ax2.set_ylabel('Confidence', fontsize=11)
    ax2.set_title('Confidence vs Evidence', fontsize=13, fontweight='bold', pad=15)
    ax2.set_xticks([1, 2, 3])
    ax2.set_xticklabels(['Weak', 'Moderate', 'Strong'])
    ax2.set_ylim(0, 1.1)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.grid(True, alpha=0.2)

    # Add concept labels with better positioning
    for i, c in enumerate(all_concepts):
        name = c['name'][:20]
        # Offset labels to avoid overlap
        offset_y = 0.03 if i % 2 == 0 else -0.05
        ax2.annotate(name, (strengths[i], confidences[i]),
                    fontsize=8, alpha=0.8, ha='center',
                    xytext=(0, 10 + (i % 3) * 8),
                    textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7, edgecolor='none'))

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    output = output or str(base / "wiki" / "meta" / "evolution-timeline.png")
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"✅ Generated: {output}")
    print(f"   Concepts: {len(data)}")
    if has_evolution:
        print(f"   Evolved (v>1): {len(evolved)}")


def main():
    parser = argparse.ArgumentParser(description="Generate concept evolution timeline")
    parser.add_argument("--dir", "-d", default=".", help="Wiki root directory")
    parser.add_argument("--output", "-o", default=None, help="Output PNG file path")
    args = parser.parse_args()
    generate_timeline_chart(args.dir, args.output)


if __name__ == "__main__":
    main()
