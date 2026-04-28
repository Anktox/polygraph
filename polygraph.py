"""PolyGraph CLI entrypoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from extractor import scan_project
from graph_builder import build_graph
from renderer import render_html


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="polygraph",
        description="Scan a Python project and generate a self-contained 3D code graph.",
    )
    parser.add_argument("--path", default=".", help="Python project folder to scan.")
    parser.add_argument("--output", default="graph.html", help="HTML file to write.")
    parser.add_argument(
        "--data-output",
        default=None,
        help="JSON graph data file to write. Defaults next to the HTML output.",
    )
    parser.add_argument(
        "--graphs-dir",
        default="graphs",
        help="Folder used for bare output filenames, keeping the project root uncluttered.",
    )
    parser.add_argument(
        "--depth",
        choices=("import", "function"),
        default="function",
        help="Use fast import-only mode or include best-effort cross-file calls.",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        help="Optional maximum path depth below --path.",
    )
    args = parser.parse_args()

    project_path = Path(args.path).expanduser().resolve()
    if not project_path.exists() or not project_path.is_dir():
        parser.error(f"--path must be an existing directory: {project_path}")

    scans = scan_project(project_path, max_depth=args.max_depth)
    graph = build_graph(scans, depth=args.depth)

    graphs_dir = Path(args.graphs_dir).expanduser()
    output = _resolve_output_path(args.output, graphs_dir)
    data_output = (
        _resolve_output_path(args.data_output, graphs_dir)
        if args.data_output
        else output.with_name(f"{output.stem}_data.json")
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    data_output.parent.mkdir(parents=True, exist_ok=True)
    data_output.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    output.write_text(render_html(graph, title=f"PolyGraph - {project_path.name}"), encoding="utf-8")

    print(f"Scanned {len(scans)} Python files")
    print(f"Wrote {data_output.resolve()}")
    print(f"Wrote {output.resolve()}")
    return 0


def _resolve_output_path(value: str, graphs_dir: Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute() and path.parent == Path("."):
        return graphs_dir / path
    return path


if __name__ == "__main__":
    raise SystemExit(main())
