#!/usr/bin/env python3
"""
Knowledge Graph Builder for MeKB
Builds a persistent, typed knowledge graph from vault wiki-links and relationships.

Usage:
    python3 scripts/build-graph.py                    # Build/update graph
    python3 scripts/build-graph.py --stats             # Show graph statistics
    python3 scripts/build-graph.py --orphans           # List unlinked notes
    python3 scripts/build-graph.py --hubs              # List most connected notes
    python3 scripts/build-graph.py --traverse "Note.md" --depth 2  # BFS traversal
    python3 scripts/build-graph.py --path "A.md" "B.md"  # Shortest path
    python3 scripts/build-graph.py --json              # Output as JSON

Dependencies: Python 3.9+ (stdlib only)
"""

import argparse
import json
import os
import re
import sys
import time
from collections import deque
from pathlib import Path

# Folders to skip
SKIP_DIRS = {
    ".git", ".obsidian", ".claude", ".mekb", ".graph",
    "node_modules", "__pycache__", ".venv", "venv",
}

SKIP_FILES = {".DS_Store", "Thumbs.db"}

# Wiki-link pattern: [[Note Title]] or [[Note Title|Display Text]]
WIKILINK_PATTERN = re.compile(r"\[\[([^\]|]+?)(?:\|[^\]]+?)?\]\]")

# Frontmatter regex
FM_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# Typed relationship types
RELATIONSHIP_TYPES = {
    "references", "depends-on", "supersedes", "contradicts",
    "supports", "implements", "extends", "inspired-by",
}


def extract_field(yaml_text, field):
    """Extract a simple scalar field from YAML text."""
    match = re.search(rf"^{field}\s*:\s*(.+)$", yaml_text, re.MULTILINE)
    if match:
        value = match.group(1).strip().strip("'\"")
        if value in ("null", "~", ""):
            return None
        return value
    return None


def extract_list(yaml_text, field):
    """Extract a YAML list field (inline or block)."""
    # Inline: field: [a, b, c]
    match = re.search(rf"^{field}\s*:\s*\[([^\]]*)\]", yaml_text, re.MULTILINE)
    if match:
        items = [item.strip().strip("'\"") for item in match.group(1).split(",")]
        return [i for i in items if i and i not in ("null", "~")]

    # Block: field:\n  - a\n  - b
    match = re.search(rf"^{field}\s*:\s*$", yaml_text, re.MULTILINE)
    if match:
        pos = match.end()
        items = []
        for line in yaml_text[pos:].split("\n"):
            stripped = line.strip()
            if stripped.startswith("- "):
                items.append(stripped[2:].strip().strip("'\""))
            elif stripped and not stripped.startswith("#"):
                break
        return items

    return []


def extract_relationships(yaml_text):
    """Extract typed relationships from frontmatter.

    Expected format:
        relationships:
          - type: depends-on
            target: "[[Decision - Cloud Provider Selection]]"
          - type: references
            target: "[[Concept - Event Sourcing]]"

    Or simpler block format:
        relationships:
          depends-on: ["[[Decision - Cloud Provider Selection]]"]
          references: ["[[Concept - Event Sourcing]]"]
    """
    relationships = []

    # Try block format first: relationships:\n  type: [targets]
    match = re.search(r"^relationships\s*:\s*$", yaml_text, re.MULTILINE)
    if match:
        pos = match.end()
        remaining = yaml_text[pos:]

        for rel_type in RELATIONSHIP_TYPES:
            # Match the line for this relationship type with an inline list
            # Use greedy match up to the last ] on the line
            type_match = re.search(
                rf"^\s+{rel_type}\s*:\s*\[(.+)\]\s*$",
                remaining, re.MULTILINE
            )
            if type_match:
                targets = type_match.group(1)
                for link_match in WIKILINK_PATTERN.finditer(targets):
                    relationships.append({
                        "type": rel_type,
                        "target": link_match.group(1),
                    })

            # Block list format
            type_match = re.search(
                rf"^\s+{rel_type}\s*:\s*$",
                remaining, re.MULTILINE
            )
            if type_match:
                list_pos = type_match.end()
                for line in remaining[list_pos:].split("\n"):
                    stripped = line.strip()
                    if stripped.startswith("- "):
                        link_match = WIKILINK_PATTERN.search(stripped)
                        if link_match:
                            relationships.append({
                                "type": rel_type,
                                "target": link_match.group(1),
                            })
                    elif stripped and not stripped.startswith("#") and not stripped.startswith("-"):
                        break

    return relationships


def parse_note(path, vault_root, all_paths_by_stem):
    """Parse a note for graph data."""
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except (IOError, OSError):
        return None

    rel_path = str(path.relative_to(vault_root))
    stem = path.stem

    # Parse frontmatter
    fm_match = FM_PATTERN.match(content)
    yaml_text = fm_match.group(1) if fm_match else ""
    body = content[fm_match.end():] if fm_match else content

    title = extract_field(yaml_text, "title") or stem
    note_type = extract_field(yaml_text, "type")
    classification = extract_field(yaml_text, "classification") or "personal"
    tags = extract_list(yaml_text, "tags")

    # Extract wiki-links from body
    links = set()
    for match in WIKILINK_PATTERN.finditer(body):
        link_target = match.group(1).strip()
        links.add(link_target)

    # Also extract wiki-links from frontmatter (e.g. project: "[[Project - X]]")
    if yaml_text:
        for match in WIKILINK_PATTERN.finditer(yaml_text):
            link_target = match.group(1).strip()
            links.add(link_target)

    # Extract typed relationships
    typed_rels = extract_relationships(yaml_text) if yaml_text else []

    # Resolve link targets to actual paths
    resolved_links = []
    for link_text in links:
        resolved = resolve_link(link_text, all_paths_by_stem)
        if resolved:
            resolved_links.append(resolved)

    resolved_rels = []
    for rel in typed_rels:
        resolved = resolve_link(rel["target"], all_paths_by_stem)
        if resolved:
            resolved_rels.append({
                "type": rel["type"],
                "target": resolved,
            })

    return {
        "path": rel_path,
        "title": title,
        "type": note_type,
        "classification": classification,
        "tags": tags,
        "links": resolved_links,
        "relationships": resolved_rels,
    }


def resolve_link(link_text, paths_by_stem):
    """Resolve a wiki-link target to a relative path."""
    # Direct match by stem
    if link_text in paths_by_stem:
        return paths_by_stem[link_text]

    # Try with common type prefixes stripped
    for prefix in ("Person - ", "System - ", "Concept - ", "Note - ",
                    "Decision - ", "Meeting - ", "Task - ", "Project - ",
                    "Resource - ", "Interaction - ", "ActionItem - ",
                    "Daily - ", "Weblink - "):
        full = prefix + link_text
        if full in paths_by_stem:
            return paths_by_stem[full]

    return None


def find_vault_root():
    """Find the vault root."""
    path = Path.cwd()
    while path != path.parent:
        if (path / ".mekb").is_dir() or (path / "CLAUDE.md").is_file():
            return path
        path = path.parent
    return Path.cwd()


def should_skip(path, vault_root):
    """Check if a path should be skipped."""
    rel = path.relative_to(vault_root)
    for part in rel.parts[:-1]:
        if part in SKIP_DIRS:
            return True
    if path.suffix != ".md":
        return True
    if path.name in SKIP_FILES:
        return True
    return False


def collect_notes(vault_root):
    """Collect all markdown files."""
    notes = []
    for path in vault_root.rglob("*.md"):
        if not should_skip(path, vault_root):
            notes.append(path)
    return sorted(notes)


def build_graph(vault_root, verbose=False):
    """Build the full knowledge graph."""
    notes = collect_notes(vault_root)

    # Build stem -> relative path mapping for link resolution
    paths_by_stem = {}
    for path in notes:
        rel = str(path.relative_to(vault_root))
        paths_by_stem[path.stem] = rel

    # Parse all notes
    nodes = {}
    edges = []
    typed_edges = []

    for path in notes:
        data = parse_note(path, vault_root, paths_by_stem)
        if not data:
            continue

        rel_path = data["path"]
        nodes[rel_path] = {
            "title": data["title"],
            "type": data["type"],
            "classification": data["classification"],
            "tags": data["tags"],
            "out_degree": len(data["links"]),
            "in_degree": 0,  # Computed below
        }

        # Add edges (untyped wiki-links)
        for target in data["links"]:
            if target != rel_path:  # No self-links
                edges.append({"source": rel_path, "target": target})

        # Add typed relationship edges
        for rel in data["relationships"]:
            if rel["target"] != rel_path:
                typed_edges.append({
                    "source": rel_path,
                    "target": rel["target"],
                    "type": rel["type"],
                })

        if verbose:
            link_count = len(data["links"]) + len(data["relationships"])
            if link_count > 0:
                print(f"  {rel_path}: {link_count} link(s)")

    # Compute in-degree
    for edge in edges:
        target = edge["target"]
        if target in nodes:
            nodes[target]["in_degree"] += 1

    for edge in typed_edges:
        target = edge["target"]
        if target in nodes:
            nodes[target]["in_degree"] += 1

    # Compute total degree
    for path, node in nodes.items():
        node["degree"] = node["in_degree"] + node["out_degree"]

    return {
        "nodes": nodes,
        "edges": edges,
        "typed_edges": typed_edges,
        "built": time.strftime("%Y-%m-%d %H:%M:%S"),
        "stats": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "total_typed_edges": len(typed_edges),
            "avg_degree": sum(n["degree"] for n in nodes.values()) / max(len(nodes), 1),
        },
    }


def save_graph(graph, graph_path):
    """Save graph to JSON."""
    graph_path.parent.mkdir(exist_ok=True)
    with open(graph_path, "w") as f:
        json.dump(graph, f, indent=2)


def find_orphans(graph):
    """Find notes with no connections (degree 0)."""
    orphans = []
    for path, node in graph["nodes"].items():
        if node["degree"] == 0:
            orphans.append({
                "path": path,
                "title": node["title"],
                "type": node["type"],
            })
    return sorted(orphans, key=lambda x: x["path"])


def find_hubs(graph, limit=15):
    """Find most connected notes."""
    hubs = []
    for path, node in graph["nodes"].items():
        hubs.append({
            "path": path,
            "title": node["title"],
            "type": node["type"],
            "degree": node["degree"],
            "in_degree": node["in_degree"],
            "out_degree": node["out_degree"],
        })
    hubs.sort(key=lambda x: x["degree"], reverse=True)
    return hubs[:limit]


def build_adjacency(graph):
    """Build adjacency list from graph edges."""
    adj = {}
    for node_path in graph["nodes"]:
        adj[node_path] = set()

    for edge in graph["edges"]:
        src, tgt = edge["source"], edge["target"]
        if src in adj and tgt in adj:
            adj[src].add(tgt)
            adj[tgt].add(src)  # Undirected for traversal

    for edge in graph["typed_edges"]:
        src, tgt = edge["source"], edge["target"]
        if src in adj and tgt in adj:
            adj[src].add(tgt)
            adj[tgt].add(src)

    return adj


def bfs_traverse(graph, start, depth=2):
    """BFS traversal from a starting node."""
    adj = build_adjacency(graph)

    if start not in adj:
        return {"error": f"Node not found: {start}"}

    visited = {start: 0}
    queue = deque([(start, 0)])
    layers = {}

    while queue:
        current, d = queue.popleft()
        if d > depth:
            break

        if d not in layers:
            layers[d] = []
        layers[d].append({
            "path": current,
            "title": graph["nodes"][current]["title"],
            "type": graph["nodes"][current]["type"],
        })

        if d < depth:
            for neighbour in adj[current]:
                if neighbour not in visited:
                    visited[neighbour] = d + 1
                    queue.append((neighbour, d + 1))

    return {
        "start": start,
        "depth": depth,
        "layers": layers,
        "total_reachable": len(visited) - 1,  # Exclude start
    }


def shortest_path(graph, start, end):
    """Find shortest path between two nodes using BFS."""
    adj = build_adjacency(graph)

    if start not in adj:
        return {"error": f"Node not found: {start}"}
    if end not in adj:
        return {"error": f"Node not found: {end}"}

    visited = {start: None}
    queue = deque([start])

    while queue:
        current = queue.popleft()
        if current == end:
            # Reconstruct path
            path = []
            node = end
            while node is not None:
                path.append(node)
                node = visited[node]
            path.reverse()
            return {
                "start": start,
                "end": end,
                "path": path,
                "length": len(path) - 1,
                "nodes": [{
                    "path": p,
                    "title": graph["nodes"][p]["title"],
                    "type": graph["nodes"][p]["type"],
                } for p in path],
            }

        for neighbour in adj[current]:
            if neighbour not in visited:
                visited[neighbour] = current
                queue.append(neighbour)

    return {"start": start, "end": end, "path": None, "length": -1, "error": "No path found"}


def show_stats(graph):
    """Display graph statistics."""
    stats = graph["stats"]
    nodes = graph["nodes"]

    print(f"\nKnowledge Graph")
    print(f"Built: {graph['built']}")
    print(f"Total nodes: {stats['total_nodes']}")
    print(f"Total edges: {stats['total_edges']} (untyped) + {stats['total_typed_edges']} (typed)")
    print(f"Average degree: {stats['avg_degree']:.1f}")

    # By type
    by_type = {}
    for node in nodes.values():
        t = node.get("type") or "unknown"
        by_type[t] = by_type.get(t, 0) + 1

    if by_type:
        print("\nNodes by type:")
        for note_type, count in sorted(by_type.items(), key=lambda x: -x[1]):
            print(f"  {note_type:<20} {count:>4}")

    # Orphans count
    orphan_count = sum(1 for n in nodes.values() if n["degree"] == 0)
    connected = len(nodes) - orphan_count
    print(f"\nConnected: {connected} ({connected * 100 // max(len(nodes), 1)}%)")
    print(f"Orphans: {orphan_count}")

    # Typed relationship counts
    typed_counts = {}
    for edge in graph.get("typed_edges", []):
        t = edge["type"]
        typed_counts[t] = typed_counts.get(t, 0) + 1

    if typed_counts:
        print("\nTyped relationships:")
        for rel_type, count in sorted(typed_counts.items(), key=lambda x: -x[1]):
            print(f"  {rel_type:<20} {count:>4}")


def resolve_note_arg(arg, graph):
    """Resolve a CLI argument to a graph node path."""
    # Direct match
    if arg in graph["nodes"]:
        return arg

    # Try matching by stem/title
    arg_lower = arg.lower()
    for path in graph["nodes"]:
        stem = Path(path).stem.lower()
        if stem == arg_lower or arg_lower in stem:
            return path

    return None


def main():
    parser = argparse.ArgumentParser(description="Build MeKB knowledge graph")
    parser.add_argument("--stats", action="store_true", help="Show graph statistics")
    parser.add_argument("--orphans", action="store_true", help="List orphan notes")
    parser.add_argument("--hubs", action="store_true", help="List hub notes (most connected)")
    parser.add_argument("--traverse", metavar="NOTE", help="BFS traverse from a note")
    parser.add_argument("--depth", type=int, default=2, help="Traversal depth (default: 2)")
    parser.add_argument("--path", nargs=2, metavar="NOTE", help="Find shortest path between two notes")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show progress")
    parser.add_argument("--vault", help="Vault root directory")
    args = parser.parse_args()

    vault_root = Path(args.vault) if args.vault else find_vault_root()
    graph_path = vault_root / ".mekb" / "graph.json"

    # Operations that need the graph file
    needs_graph = args.stats or args.orphans or args.hubs or args.traverse or args.path

    if needs_graph and graph_path.exists():
        with open(graph_path, "r") as f:
            graph = json.load(f)
    elif needs_graph:
        # Build first if no graph exists
        print("Building graph...")
        graph = build_graph(vault_root, verbose=args.verbose)
        save_graph(graph, graph_path)
    else:
        # Default: build/rebuild
        start = time.time()
        graph = build_graph(vault_root, verbose=args.verbose)
        save_graph(graph, graph_path)
        elapsed = time.time() - start
        stats = graph["stats"]
        print(f"Graph built in {elapsed:.2f}s")
        print(f"  Nodes: {stats['total_nodes']}")
        print(f"  Edges: {stats['total_edges']} (untyped) + {stats['total_typed_edges']} (typed)")
        orphan_count = sum(1 for n in graph["nodes"].values() if n["degree"] == 0)
        print(f"  Orphans: {orphan_count}")
        return

    # Execute requested operation
    if args.stats:
        show_stats(graph)
        return

    if args.orphans:
        orphans = find_orphans(graph)
        if args.json:
            print(json.dumps(orphans, indent=2))
        else:
            if orphans:
                print(f"\n{len(orphans)} orphan note(s) (no connections):\n")
                for o in orphans:
                    note_type = o["type"] or "unknown"
                    print(f"  [{note_type}] {o['path']}")
            else:
                print("No orphan notes found - all notes are connected!")
        return

    if args.hubs:
        hubs = find_hubs(graph)
        if args.json:
            print(json.dumps(hubs, indent=2))
        else:
            print(f"\nTop {len(hubs)} most connected notes:\n")
            for i, h in enumerate(hubs, 1):
                note_type = h["type"] or "unknown"
                print(f"  {i:>2}. [{note_type}] {h['title']}")
                print(f"      {h['path']} (degree: {h['degree']}, in: {h['in_degree']}, out: {h['out_degree']})")
        return

    if args.traverse:
        start_node = resolve_note_arg(args.traverse, graph)
        if not start_node:
            print(f"Note not found: {args.traverse}", file=sys.stderr)
            sys.exit(1)

        result = bfs_traverse(graph, start_node, depth=args.depth)
        if "error" in result:
            print(result["error"], file=sys.stderr)
            sys.exit(1)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\nTraversal from: {start_node} (depth {args.depth})")
            print(f"Reachable notes: {result['total_reachable']}\n")
            for d, layer_nodes in sorted(result["layers"].items(), key=lambda x: int(x[0])):
                label = "Start" if int(d) == 0 else f"Depth {d}"
                print(f"  {label}:")
                for n in layer_nodes:
                    note_type = n["type"] or "unknown"
                    print(f"    [{note_type}] {n['title']} ({n['path']})")
        return

    if args.path:
        start_node = resolve_note_arg(args.path[0], graph)
        end_node = resolve_note_arg(args.path[1], graph)

        if not start_node:
            print(f"Note not found: {args.path[0]}", file=sys.stderr)
            sys.exit(1)
        if not end_node:
            print(f"Note not found: {args.path[1]}", file=sys.stderr)
            sys.exit(1)

        result = shortest_path(graph, start_node, end_node)

        if args.json:
            print(json.dumps(result, indent=2))
        elif result.get("path"):
            print(f"\nShortest path ({result['length']} hop(s)):\n")
            for i, n in enumerate(result["nodes"]):
                note_type = n["type"] or "unknown"
                connector = "  -> " if i > 0 else "     "
                print(f"  {connector}[{note_type}] {n['title']} ({n['path']})")
        else:
            print(f"No path found between {args.path[0]} and {args.path[1]}")


if __name__ == "__main__":
    main()
