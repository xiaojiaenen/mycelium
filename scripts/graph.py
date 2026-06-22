#!/usr/bin/env python3
"""
Generate interactive knowledge graph as standalone HTML.
Uses Cytoscape.js for visualization. No dependencies needed.
"""
import json
import argparse
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
from utils import TYPE_COLORS, build_graph, title_from_slug


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
    position: fixed; top: 20px; left: 20px; background: rgba(30,30,50,0.95);
    padding: 18px 22px; border-radius: 12px; color: #fff; font-size: 13px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4); backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.1);
}
#legend h3 { margin-bottom: 12px; font-size: 16px; }
.legend-item { display: flex; align-items: center; margin: 6px 0; }
.legend-dot { width: 14px; height: 14px; border-radius: 50%; margin-right: 10px; border: 1px solid rgba(255,255,255,0.2); }
#info {
    position: fixed; bottom: 20px; left: 20px; background: rgba(30,30,50,0.95);
    padding: 12px 18px; border-radius: 10px; color: #aaa; font-size: 12px;
    backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1);
}
#search {
    position: fixed; top: 20px; right: 20px; padding: 12px 18px;
    border-radius: 10px; border: 1px solid rgba(255,255,255,0.2);
    background: rgba(30,30,50,0.95); color: #fff; font-size: 14px;
    width: 280px; outline: none; backdrop-filter: blur(10px);
}
#search:focus { border-color: #7aa2f7; box-shadow: 0 0 0 2px rgba(122,162,247,0.3); }
#search::placeholder { color: #666; }
.ghost-node { border-style: dashed; }
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
    <div class="legend-item"><div class="legend-dot" style="background:#555; border-style:dashed"></div>Unresolved</div>
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
                'width': 'data(width)',
                'height': 'data(height)',
                'shape': 'round-rectangle',
                'text-wrap': 'wrap',
                'text-max-width': '100px',
                'border-width': 2,
                'border-color': 'data(borderColor)',
            }
        },
        {
            selector: 'node[?ghost]',
            style: {
                'border-style': 'dashed',
                'background-color': '#333',
                'opacity': 0.6,
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
                'target-arrow-color': '#7aa2f7',
                'border-color': '#7aa2f7',
                'width': 3,
            }
        },
        {
            selector: '.search-match',
            style: {
                'background-color': '#f7768e',
                'border-color': '#f7768e',
                'border-width': 3,
            }
        },
        {
            selector: '.faded',
            style: { 'opacity': 0.15 }
        }
    ],
    layout: {
        name: 'cose-bilkent',
        animate: true,
        animationDuration: 1200,
        fit: true,
        padding: 60,
        randomize: false,
        nodeRepulsion: 5000,
        idealEdgeLength: 180,
        edgeElasticity: 0.1,
        nestingFactor: 0.1,
        gravity: 0.25,
    },
    minZoom: 0.2,
    maxZoom: 4,
});

// Click to highlight neighborhood
cy.on('tap', 'node', function(evt) {
    const node = evt.target;
    const neighborhood = node.neighborhood().add(node);
    cy.elements().removeClass('highlighted faded search-match');
    neighborhood.addClass('highlighted');
    cy.elements().not(neighborhood).addClass('faded');

    // Update info panel
    const edges = neighborhood.edges().length;
    document.getElementById('info').textContent =
        `Selected: ${node.data('label')} | Connections: ${edges}`;
});

cy.on('tap', function(evt) {
    if (evt.target === cy) {
        cy.elements().removeClass('highlighted faded search-match');
        document.getElementById('info').textContent =
            `Nodes: ${cy.nodes().length} | Edges: ${cy.edges().length}`;
    }
});

// Search - keep connected edges visible
let searchTimeout;
document.getElementById('search').addEventListener('input', function(e) {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        const query = e.target.value.toLowerCase().trim();
        if (!query) {
            cy.elements().removeClass('highlighted faded search-match');
            return;
        }

        const matchedNodes = cy.nodes().filter(node => {
            const label = node.data('label').toLowerCase();
            return label.includes(query);
        });

        if (matchedNodes.length === 0) {
            cy.elements().addClass('faded');
            return;
        }

        // Get all connected edges and neighbor nodes
        const connectedEdges = matchedNodes.connectedEdges();
        const neighborNodes = connectedEdges.connectedNodes().union(matchedNodes);

        cy.elements().removeClass('highlighted faded search-match');
        cy.elements().not(neighborNodes).not(connectedEdges).addClass('faded');
        matchedNodes.addClass('search-match');

        document.getElementById('info').textContent =
            `Found: ${matchedNodes.length} node(s)`;
    }, 150);
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
    nodes = graph["nodes"]
    edges = graph["edges"]

    if not nodes:
        print("❌ No notes found")
        return

    # Build Cytoscape elements
    cy_nodes = []
    cy_edges = []
    node_ids = set()

    # Determine node sizes based on connection count
    connection_count = {}
    for edge in edges:
        connection_count[edge["source"]] = connection_count.get(edge["source"], 0) + 1
        connection_count[edge["target"]] = connection_count.get(edge["target"], 0) + 1

    max_connections = max(connection_count.values()) if connection_count else 1

    def get_node_size(name):
        count = connection_count.get(name, 0)
        scale = 0.5 + (count / max_connections) * 0.5
        return int(60 * scale), int(30 * scale)

    # Add real nodes
    for name, info in nodes.items():
        w, h = get_node_size(name)
        cy_nodes.append({
            "data": {
                "id": name,
                "label": info["name"],
                "type": info["type"],
                "color": TYPE_COLORS.get(info["type"], "#e9ecef"),
                "borderColor": TYPE_COLORS.get(info["type"], "#e9ecef"),
                "width": w,
                "height": h,
                "ghost": False,
            }
        })
        node_ids.add(name)

    # Add ghost nodes for unresolved links
    ghost_count = 0
    for edge in edges:
        target = edge["target"]
        if target not in node_ids:
            ghost_count += 1
            cy_nodes.append({
                "data": {
                    "id": target,
                    "label": title_from_slug(target),
                    "type": "unknown",
                    "color": "#333",
                    "borderColor": "#666",
                    "width": 50,
                    "height": 25,
                    "ghost": True,
                }
            })
            node_ids.add(target)

    # Add edges
    for edge in edges:
        cy_edges.append({
            "data": {
                "source": edge["source"],
                "target": edge["target"],
            }
        })

    cy_graph = {"nodes": cy_nodes, "edges": cy_edges}
    graph_json = json.dumps(cy_graph, ensure_ascii=False)

    # Safe JSON injection: escape for HTML context
    import html
    graph_json_escaped = html.escape(graph_json, quote=True)

    html_content = HTML_TEMPLATE.replace("GRAPH_DATA", graph_json_escaped)
    html_content = html_content.replace("NODE_COUNT", str(len(cy_nodes)))
    html_content = html_content.replace("EDGE_COUNT", str(len(cy_edges)))

    output = output or str(base / "wiki" / "meta" / "knowledge-graph.html")
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(html_content, encoding='utf-8')

    print(f"✅ Generated: {output}")
    print(f"   Nodes: {len(cy_nodes)} ({ghost_count} unresolved)")
    print(f"   Edges: {len(cy_edges)}")
    print(f"   Open in browser to view")


def main():
    parser = argparse.ArgumentParser(description="Generate knowledge graph HTML")
    parser.add_argument("--dir", "-d", default=".", help="Wiki root directory")
    parser.add_argument("--output", "-o", default=None, help="Output HTML file path")
    args = parser.parse_args()
    generate_graph(args.dir, args.output)


if __name__ == "__main__":
    main()
