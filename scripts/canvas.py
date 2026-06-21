#!/usr/bin/env python3
"""Generate Obsidian Canvas file from wiki notes."""
import json
import argparse
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    CANVAS_GRID_COLUMNS, CANVAS_COL_SPACING, CANVAS_ROW_SPACING,
    CANVAS_NODE_WIDTH, CANVAS_NODE_HEIGHT,
    parse_frontmatter, extract_wikilinks,
)


def generate_canvas(wiki_dir: str, output: str = None):
    """Generate Obsidian Canvas from wiki."""
    base = Path(wiki_dir)
    wiki = base / "wiki"

    if not wiki.exists():
        print(f"❌ wiki/ not found in {wiki_dir}")
        return

    nodes = []
    edges = []
    node_map = {}
    id_counter = 0

    type_colors = {
        "source": 1,
        "concept": 2,
        "entity": 3,
        "comparison": 4,
        "question": 5,
        "contradiction": 6,
    }

    for subdir in ['sources', 'concepts', 'entities', 'comparisons', 'questions', 'contradictions']:
        dir_path = wiki / subdir
        if not dir_path.exists():
            continue
        for md_file in dir_path.glob('*.md'):
            content = md_file.read_text(encoding='utf-8')
            fm = parse_frontmatter(content)
            name = fm.get('title', md_file.stem)
            note_type = fm.get('type', subdir.rstrip('s'))
            links = extract_wikilinks(content)
            color = type_colors.get(note_type, 1)

            nid = f"node-{id_counter}"
            id_counter += 1
            node_map[md_file.stem] = nid

            # Calculate position in a grid
            idx = id_counter - 1
            col = idx % 4
            row = idx // 4

            nodes.append({
                "id": nid,
                "type": "file",
                "file": f"wiki/{subdir}/{md_file.name}",
                "color": color,
                "x": col * 300,
                "y": row * 200,
                "width": 250,
                "height": 150,
            })

            for link in links:
                if link in node_map:
                    edges.append({
                        "id": f"edge-{id_counter}",
                        "fromNode": node_map[link],
                        "toNode": nid,
                    })
                    id_counter += 1

    canvas = {
        "nodes": nodes,
        "edges": edges,
    }

    output = output or str(base / "wiki" / "meta" / "wiki-canvas.canvas")
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(json.dumps(canvas, indent=2, ensure_ascii=False), encoding='utf-8')

    print(f"✅ Generated: {output}")
    print(f"   Nodes: {len(nodes)}")
    print(f"   Edges: {len(edges)}")


def main():
    parser = argparse.ArgumentParser(description="Generate Obsidian Canvas from wiki")
    parser.add_argument("--dir", "-d", default=".", help="Wiki root directory")
    parser.add_argument("--output", "-o", default=None, help="Output .canvas file path")
    args = parser.parse_args()
    generate_canvas(args.dir, args.output)


if __name__ == "__main__":
    main()
