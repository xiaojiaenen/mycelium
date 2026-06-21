#!/usr/bin/env python3
"""
Generate interactive knowledge graph as standalone HTML.
Uses Cytoscape.js for visualization. No dependencies needed.
"""
import re
import json
import argparse
from pathlib import Path


def parse_frontmatter(content: str) -> dict:
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, _, val = line.partition(':')
            val = val.strip().strip('"').strip("'")
            fm[key.strip()] = val
    return fm


def extract_wikilinks(content: str) -> list:
    return re.findall(r'\[\[([^\]]+)\]\]', content)


def build_graph(wiki_dir: Path) -> dict:
    nodes = []
    edges = []
    node_ids = set()

    type_colors = {
        "source": "#a5d8ff",
        "concept": "#b2f2bb",
        "entity": "#ffec99",
        "comparison": "#ffc9c9",
        "question": "#d0bfff",
        "contradiction": "#ffd8a8",
    }

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

            if md_file.stem not in node_ids:
                nodes.append({
                    "data": {
                        "id": md_file.stem,
                        "label": name,
                        "type": note_type,
                        "color": type_colors.get(note_type, "#e9ecef"),
                    }
                })
                node_ids.add(md_file.stem)

            for link in links:
                edges.append({
                    "data": {
                        "source": md_file.stem,
                        "target": link,
                    }
                })

    return {"nodes": nodes, "edges": edges}


HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Mycelium Knowledge Graph</title>
<script src="https://unpkg.com/cytoscape@3.28.1/dist/cytoscape.min.js"></script>
<script src="https://unpkg.com/cytoscape-cose-bilkent@4.1.0/cytoscape-cose-bilkent.js"></script>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: system-ui, -apple-system, sans-serif; background: #1a1b26; }
#graph { width: 100vw; height: 100vh; }
#legend {
    position: fixed; top: 20px; left: 20px; background: rgba(30,30,50,0.9);
    padding: 15px 20px; border-radius: 10px; color: #fff; font-size: 13px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
#legend h3 { margin-bottom: 10px; font-size: 15px; }
.legend-item { display: flex; align-items: center; margin: 5px 0; }
.legend-dot { width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }
#info {
    position: fixed; bottom: 20px; left: 20px; background: rgba(30,30,50,0.9);
    padding: 10px 15px; border-radius: 8px; color: #aaa; font-size: 12px;
}
#search {
    position: fixed; top: 20px; right: 20px; padding: 10px 15px;
    border-radius: 8px; border: 1px solid #444; background: rgba(30,30,50,0.9);
    color: #fff; font-size: 14px; width: 250px; outline: none;
}
#search:focus { border-color: #7aa2f7; }
</style>
</head>
<body>
<div id="graph"></div>
<div id="legend">
    <h3>🍄 Mycelium Graph</h3>
    <div class="legend-item"><div class="legend-dot" style="background:#a5d8ff"></div>Sources</div>
    <div class="legend-item"><div class="legend-dot" style="background:#b2f2bb"></div>Concepts</div>
    <div class="legend-item"><div class="legend-dot" style="background:#ffec99"></div>Entities</div>
    <div class="legend-item"><div class="legend-dot" style="background:#ffc9c9"></div>Comparisons</div>
    <div class="legend-item"><div class="legend-dot" style="background:#d0bfff"></div>Questions</div>
    <div class="legend-item"><div class="legend-dot" style="background:#ffd8a8"></div>Contradictions</div>
</div>
<input id="search" placeholder="🔍 Search nodes..." />
<div id="info">Nodes: NODE_COUNT | Edges: EDGE_COUNT</div>

<script>
const graphData = GRAPH_DATA;

const cy = cytoscape({
    container: document.getElementById('graph'),
    elements: graphData,
    style: [
        {
            selector: 'node',
            style: {
                'background-color': 'data(color)',
                'label': 'data(label)',
                'color': '#fff',
                'text-valign': 'center',
                'text-halign': 'center',
                'font-size': '12px',
                'width': 60,
                'height': 30,
                'shape': 'round-rectangle',
                'text-wrap': 'wrap',
                'text-max-width': '80px',
            }
        },
        {
            selector: 'edge',
            style: {
                'width': 1.5,
                'line-color': '#555',
                'target-arrow-color': '#555',
                'target-arrow-shape': 'triangle',
                'arrow-scale': 0.8,
                'curve-style': 'bezier',
            }
        },
        {
            selector: '.highlighted',
            style: {
                'background-color': '#7aa2f7',
                'line-color': '#7aa2f7',
                'width': 3,
            }
        },
        {
            selector: '.faded',
            style: { 'opacity': 0.2 }
        }
    ],
    layout: {
        name: 'cose-bilkent',
        animate: true,
        animationDuration: 1000,
        fit: true,
        padding: 50,
        randomize: false,
        nodeRepulsion: 4500,
        idealEdgeLength: 150,
        edgeElasticity: 0.1,
        nestingFactor: 0.1,
        gravity: 0.3,
    },
    minZoom: 0.3,
    maxZoom: 3,
});

// Click to highlight neighborhood
cy.on('tap', 'node', function(evt) {
    const node = evt.target;
    const neighborhood = node.neighborhood().add(node);
    cy.elements().removeClass('highlighted faded');
    neighborhood.addClass('highlighted');
    cy.elements().not(neighborhood).addClass('faded');
});

cy.on('tap', function(evt) {
    if (evt.target === cy) {
        cy.elements().removeClass('highlighted faded');
    }
});

// Search
document.getElementById('search').addEventListener('input', function(e) {
    const query = e.target.value.toLowerCase();
    if (!query) {
        cy.elements().removeClass('highlighted faded');
        return;
    }
    cy.nodes().forEach(node => {
        const label = node.data('label').toLowerCase();
        if (label.includes(query)) {
            node.addClass('highlighted');
            node.removeClass('faded');
        } else {
            node.removeClass('highlighted');
            node.addClass('faded');
        }
    });
    cy.edges().addClass('faded');
});
</script>
</body>
</html>"""


def generate_graph(wiki_dir: str, output: str = None):
    """Generate interactive HTML knowledge graph."""
    base = Path(wiki_dir)
    wiki = base / "wiki"

    if not wiki.exists():
        print(f"❌ wiki/ not found in {wiki_dir}")
        return

    graph = build_graph(wiki)
    graph_json = json.dumps(graph, ensure_ascii=False)

    html = HTML_TEMPLATE.replace("GRAPH_DATA", graph_json)
    html = html.replace("NODE_COUNT", str(len(graph["nodes"])))
    html = html.replace("EDGE_COUNT", str(len(graph["edges"])))

    output = output or str(base / "wiki" / "meta" / "knowledge-graph.html")
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(html, encoding='utf-8')

    print(f"✅ Generated: {output}")
    print(f"   Nodes: {len(graph['nodes'])}")
    print(f"   Edges: {len(graph['edges'])}")
    print(f"   Open in browser to view")


def main():
    parser = argparse.ArgumentParser(description="Generate knowledge graph HTML")
    parser.add_argument("--dir", "-d", default=".", help="Wiki root directory")
    parser.add_argument("--output", "-o", default=None, help="Output HTML file path")
    args = parser.parse_args()
    generate_graph(args.dir, args.output)


if __name__ == "__main__":
    main()
