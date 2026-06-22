#!/usr/bin/env python3
"""
Generate Excalidraw diagrams from wiki concept maps.
Creates .excalidraw files that can be opened in Obsidian Excalidraw plugin.
"""
import json
import argparse
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    EXCALIDRAW_SOURCE, EXCALIDRAW_CANVAS_WIDTH, EXCALIDRAW_CANVAS_HEIGHT,
    EXCALIDRAW_LAYOUT_RADIUS, EXCALIDRAW_SIMULATION_ITERATIONS,
    EXCALIDRAW_REPULSION, EXCALIDRAW_FORCE_STEP, EXCALIDRAW_IDEAL_EDGE,
    EXCALIDRAW_EDGE_ELASTICITY, TYPE_COLORS, build_graph,
)


def force_layout(nodes: dict, edges: list, width: int = 1200, height: int = 800) -> dict:
    """Simple force-directed layout (no external deps)."""
    import random
    random.seed(42)

    # Initialize positions
    positions = {}
    node_list = list(nodes.keys())
    for i, name in enumerate(node_list):
        angle = 2 * 3.14159 * i / len(node_list)
        positions[name] = {
            "x": width / 2 + 200 * __import__('math').cos(angle),
            "y": height / 2 + 200 * __import__('math').sin(angle),
        }

    # Simple force simulation
    for _ in range(50):
        # Repulsion between all nodes
        for i, a in enumerate(node_list):
            for b in node_list[i + 1:]:
                dx = positions[a]["x"] - positions[b]["x"]
                dy = positions[a]["y"] - positions[b]["y"]
                dist = max((dx ** 2 + dy ** 2) ** 0.5, 1)
                force = 5000 / dist
                fx = force * dx / dist
                fy = force * dy / dist
                positions[a]["x"] += fx * 0.1
                positions[a]["y"] += fy * 0.1
                positions[b]["x"] -= fx * 0.1
                positions[b]["y"] -= fy * 0.1

        # Attraction along edges
        for edge in edges:
            s, t = edge["source"], edge["target"]
            if s in positions and t in positions:
                dx = positions[t]["x"] - positions[s]["x"]
                dy = positions[t]["y"] - positions[s]["y"]
                dist = max((dx ** 2 + dy ** 2) ** 0.5, 1)
                force = (dist - 150) * 0.01
                fx = force * dx / dist
                fy = force * dy / dist
                positions[s]["x"] += fx
                positions[s]["y"] += fy
                positions[t]["x"] -= fx
                positions[t]["y"] -= fy

        # Center gravity
        for name in positions:
            positions[name]["x"] += (width / 2 - positions[name]["x"]) * 0.01
            positions[name]["y"] += (height / 2 - positions[name]["y"]) * 0.01

    return positions


def generate_excalidraw(wiki_dir: str, output: str = None):
    """Generate Excalidraw file from wiki concept map."""
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

    # Build Excalidraw elements
    elements = []
    id_counter = 0

    # Create nodes (rectangles)
    node_ids = {}
    for name, info in nodes.items():
        if name not in positions:
            continue
        eid = f"node_{id_counter}"
        id_counter += 1
        node_ids[name] = eid
        pos = positions[name]
        color = TYPE_COLORS.get(info["type"], "#e9ecef")

        # Rectangle (the box)
        elements.append({
            "id": eid,
            "type": "rectangle",
            "x": pos["x"] - 60,
            "y": pos["y"] - 20,
            "width": 120,
            "height": 40,
            "strokeColor": "#1e1e1e",
            "backgroundColor": color,
            "fillStyle": "solid",
            "strokeWidth": 2,
            "roughness": 1,
            "opacity": 100,
            "angle": 0,
            "seed": id_counter * 1000,
            "version": 1,
            "versionNonce": id_counter * 1000,
            "isDeleted": False,
            "boundElements": [{"id": f"text_{id_counter}", "type": "text"}],
            "updated": 1,
            "link": None,
            "locked": False,
        })
        # Text element (references the rectangle)
        text_id = f"text_{id_counter}"
        elements.append({
            "id": text_id,
            "type": "text",
            "x": pos["x"] - 55,
            "y": pos["y"] - 15,
            "width": 110,
            "height": 30,
            "strokeColor": "#1e1e1e",
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "roughness": 1,
            "opacity": 100,
            "angle": 0,
            "seed": id_counter * 1000 + 1,
            "version": 1,
            "versionNonce": id_counter * 1000 + 1,
            "isDeleted": False,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False,
            "text": info["name"],
            "fontSize": 14,
            "fontFamily": 1,
            "textAlign": "center",
            "verticalAlign": "middle",
            "containerId": eid,
            "originalText": info["name"],
            "lineHeight": 1.25,
        })

    # Create edges (arrows) and track bindings
    edge_bindings = {}  # node_id -> list of arrow ids
    for edge in edges:
        s, t = edge["source"], edge["target"]
        if s not in node_ids or t not in node_ids:
            continue
        eid = f"edge_{id_counter}"
        id_counter += 1
        s_pos = positions[s]
        t_pos = positions[t]

        # Track bindings for nodes
        edge_bindings.setdefault(s, []).append(eid)
        edge_bindings.setdefault(t, []).append(eid)

        elements.append({
            "id": eid,
            "type": "arrow",
            "x": s_pos["x"],
            "y": s_pos["y"],
            "width": t_pos["x"] - s_pos["x"],
            "height": t_pos["y"] - s_pos["y"],
            "strokeColor": "#868e96",
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "roughness": 1,
            "opacity": 100,
            "angle": 0,
            "seed": id_counter * 1000,
            "version": 1,
            "versionNonce": id_counter * 1000,
            "isDeleted": False,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False,
            "points": [[0, 0], [t_pos["x"] - s_pos["x"], t_pos["y"] - s_pos["y"]]],
            "lastCommittedPoint": None,
            "startBinding": {
                "elementId": node_ids[s],
                "focus": 0,
                "gap": 1,
            },
            "endBinding": {
                "elementId": node_ids[t],
                "focus": 0,
                "gap": 1,
            },
            "startArrowhead": None,
            "endArrowhead": "arrow",
        })

    # Update node boundElements to include connected arrows
    for elem in elements:
        if elem["type"] == "rectangle" and elem["id"] in [node_ids[n] for n in nodes]:
            # Find which node this is
            for node_name, node_eid in node_ids.items():
                if node_eid == elem["id"]:
                    arrow_ids = edge_bindings.get(node_name, [])
                    elem["boundElements"] = [{"id": f"text_{elem['id'].split('_')[1]}", "type": "text"}]
                    elem["boundElements"].extend([{"id": aid, "type": "arrow"} for aid in arrow_ids])
                    break

    # Build Excalidraw file
    excalidraw = {
        "type": "excalidraw",
        "version": 2,
        "source": "mycelium",
        "elements": elements,
        "appState": {
            "gridSize": None,
            "viewBackgroundColor": "#ffffff",
        },
        "files": {},
    }

    output = output or str(base / "wiki" / "meta" / "concept-map.excalidraw")
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(json.dumps(excalidraw, indent=2, ensure_ascii=False), encoding='utf-8')

    print(f"✅ Generated: {output}")
    print(f"   Nodes: {len(node_ids)}")
    print(f"   Edges: {len([e for e in edges if e['source'] in node_ids and e['target'] in node_ids])}")


def main():
    parser = argparse.ArgumentParser(description="Generate Excalidraw diagram from wiki")
    parser.add_argument("--dir", "-d", default=".", help="Wiki root directory")
    parser.add_argument("--output", "-o", default=None, help="Output .excalidraw file path")
    args = parser.parse_args()
    generate_excalidraw(args.dir, args.output)


if __name__ == "__main__":
    main()
