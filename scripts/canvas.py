#!/usr/bin/env python3
"""Generate Obsidian Canvas file from wiki notes."""
import json
import argparse
import math
import random
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    CANVAS_COL_SPACING, CANVAS_ROW_SPACING,
    CANVAS_NODE_WIDTH, CANVAS_NODE_HEIGHT,
    TYPE_COLORS, build_graph,
)

# Obsidian Canvas color indices
CANVAS_COLORS = {
    "source": "1",      # Red
    "concept": "2",     # Orange
    "entity": "3",      # Yellow
    "comparison": "4",  # Green
    "question": "5",    # Cyan
    "contradiction": "6", # Purple
}


def force_layout(nodes: dict, edges: list, width: int = 2000, height: int = 1500) -> dict:
    """Force-directed layout for Canvas nodes."""
    random.seed(42)
    node_list = list(nodes.keys())
    if not node_list:
        return {}

    # Initialize positions in a circle
    positions = {}
    for i, name in enumerate(node_list):
        angle = 2 * math.pi * i / len(node_list)
        radius = min(width, height) * 0.3
        positions[name] = {
            "x": width / 2 + radius * math.cos(angle),
            "y": height / 2 + radius * math.sin(angle),
        }

    # Build adjacency for faster lookup
    adj = {n: set() for n in node_list}
    for edge in edges:
        s, t = edge["source"], edge["target"]
        if s in adj and t in adj:
            adj[s].add(t)
            adj[t].add(s)

    # Force simulation
    for _ in range(80):
        # Repulsion between all nodes
        for i, a in enumerate(node_list):
            for b in node_list[i + 1:]:
                dx = positions[a]["x"] - positions[b]["x"]
                dy = positions[a]["y"] - positions[b]["y"]
                dist = max(math.sqrt(dx ** 2 + dy ** 2), 1)
                force = 8000 / dist
                fx = force * dx / dist
                fy = force * dy / dist
                positions[a]["x"] += fx * 0.05
                positions[a]["y"] += fy * 0.05
                positions[b]["x"] -= fx * 0.05
                positions[b]["y"] -= fy * 0.05

        # Attraction along edges
        for edge in edges:
            s, t = edge["source"], edge["target"]
            if s in positions and t in positions:
                dx = positions[t]["x"] - positions[s]["x"]
                dy = positions[t]["y"] - positions[s]["y"]
                dist = max(math.sqrt(dx ** 2 + dy ** 2), 1)
                force = (dist - 200) * 0.005
                fx = force * dx / dist
                fy = force * dy / dist
                positions[s]["x"] += fx
                positions[s]["y"] += fy
                positions[t]["x"] -= fx
                positions[t]["y"] -= fy

        # Center gravity
        for name in positions:
            positions[name]["x"] += (width / 2 - positions[name]["x"]) * 0.005
            positions[name]["y"] += (height / 2 - positions[name]["y"]) * 0.005

    return positions


def generate_canvas(wiki_dir: str, output: str = None):
    """Generate Obsidian Canvas from wiki."""
    base = Path(wiki_dir)
    wiki = base / "wiki"

    if not wiki.exists():
        print(f"❌ wiki/ not found in {wiki_dir}")
        return

    graph = build_graph(wiki)
    nodes = graph["nodes"]
    edges = graph["edges"]

    if not nodes:
        print("❌ No notes found")
        return

    # Layout
    positions = force_layout(nodes, edges)

    # Build Canvas elements
    canvas_nodes = []
    canvas_edges = []
    node_id_map = {}
    id_counter = 0

    for name, info in nodes.items():
        if name not in positions:
            continue

        nid = f"node-{id_counter}"
        id_counter += 1
        node_id_map[name] = nid

        pos = positions[name]
        color = CANVAS_COLORS.get(info["type"], "0")

        canvas_nodes.append({
            "id": nid,
            "type": "file",
            "file": f"wiki/{info['subdir']}/{name}.md",
            "color": color,
            "x": int(pos["x"]),
            "y": int(pos["y"]),
            "width": CANVAS_NODE_WIDTH,
            "height": CANVAS_NODE_HEIGHT,
        })

    # Create edges with proper binding
    for edge in edges:
        s, t = edge["source"], edge["target"]
        if s in node_id_map and t in node_id_map:
            eid = f"edge-{id_counter}"
            id_counter += 1
            canvas_edges.append({
                "id": eid,
                "fromNode": node_id_map[s],
                "toNode": node_id_map[t],
                "fromSide": "right",
                "toSide": "left",
            })

    canvas = {
        "nodes": canvas_nodes,
        "edges": canvas_edges,
    }

    output = output or str(base / "wiki" / "meta" / "wiki-canvas.canvas")
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(json.dumps(canvas, indent=2, ensure_ascii=False), encoding='utf-8')

    print(f"✅ Generated: {output}")
    print(f"   Nodes: {len(canvas_nodes)}")
    print(f"   Edges: {len(canvas_edges)}")


def main():
    parser = argparse.ArgumentParser(description="Generate Obsidian Canvas from wiki")
    parser.add_argument("--dir", "-d", default=".", help="Wiki root directory")
    parser.add_argument("--output", "-o", default=None, help="Output .canvas file path")
    args = parser.parse_args()
    generate_canvas(args.dir, args.output)


if __name__ == "__main__":
    main()
