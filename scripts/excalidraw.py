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
    EXCALIDRAW_EDGE_ELASTICITY, TYPE_COLORS,
    parse_frontmatter, extract_wikilinks,
)


def build_graph(wiki_dir: Path) -> dict:
    """Build node/edge graph from wiki."""
    nodes = {}
    edges = []

    for subdir in ['sources', 'concepts', 'entities', 'comparisons', 'questions', 'contradictions']:
        dir_path = wiki_dir / subdir
        if not dir_path.exists():
            continue
        for md_file in dir_path.glob('*.md'):
            content = md_file.read_text(encoding='utf-8')
            fm = parse_frontmatter(content)
            name = fm.get('title', md_file.stem)
            note_type = fm.get('type', subdir.rstrip('s'))
            links = extract_wikilinks(content)

            nodes[md_file.stem] = {
                "name": name,
                "type": note_type,
                "links": links,
            }

            for link in links:
                edges.append({"source": md_file.stem, "target": link})

    return {"nodes": nodes, "edges": edges}


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

    # Color map for note types
    colors = {
        "source": "#a5d8ff",
        "concept": "#b2f2bb",
        "entity": "#ffec99",
        "comparison": "#ffc9c9",
        "question": "#d0bfff",
        "contradiction": "#ffd8a8",
    }

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
        color = colors.get(info["type"], "#e9ecef")

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

    # Create edges (arrows)
    for edge in edges:
        s, t = edge["source"], edge["target"]
        if s not in node_ids or t not in node_ids:
            continue
        eid = f"edge_{id_counter}"
        id_counter += 1
        s_pos = positions[s]
        t_pos = positions[t]

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
            "startBinding": None,
            "endBinding": None,
            "startArrowhead": None,
            "endArrowhead": "arrow",
        })

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
