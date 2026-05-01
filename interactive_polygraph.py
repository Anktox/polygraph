"""Interactive launcher for PolyGraph."""

from __future__ import annotations

import json
from pathlib import Path

from extractor import scan_project
from graph_builder import build_graph
from renderer import render_html


def main() -> int:
    target_folder = _prompt_for_folder()
    selected_folders = [target_folder]

    print("\nFolders that will be scanned:")
    for folder in selected_folders:
        print(f"- {folder}")

    if not _ask_yes_no("\nDo you want to start generating the graph now?", default=True):
        print("Cancelled. No graph was generated.")
        return 0

    graph = _build_graph_from_folders(selected_folders)
    output_html, output_json = _default_output_paths(target_folder)
    output_html.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    output_html.write_text(render_html(graph, title=f"PolyGraph - {target_folder.name}"), encoding="utf-8")

    print("\nGraph generation complete.")
    print(f"Wrote {output_json.resolve()}")
    print(f"Wrote {output_html.resolve()}")
    print("Run this command in terminal to open the graph:")
    print(f'start "" "{output_html.resolve()}"')
    return 0


def _prompt_for_folder() -> Path:
    while True:
        user_input = input("Which folder would you like to graph? ").strip()
        if not user_input:
            print("Please enter a folder path.")
            continue

        folder = Path(user_input).expanduser().resolve()
        if folder.exists() and folder.is_dir():
            return folder
        print(f'Folder not found: "{folder}"')


def _ask_yes_no(prompt: str, default: bool) -> bool:
    default_text = "Y/n" if default else "y/N"
    while True:
        answer = input(f"{prompt} [{default_text}] ").strip().lower()
        if not answer:
            return default
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        print("Please answer yes or no.")


def _build_graph_from_folders(folders: list[Path]) -> dict:
    scans = []
    used_prefixes: dict[str, int] = {}

    for folder in folders:
        prefix = _unique_prefix(folder.name, used_prefixes)
        folder_scans = scan_project(folder)
        for scan in folder_scans:
            scan.path = f"{prefix}/{scan.path}"
            scan.folder = f"{prefix}/{scan.folder}"
        scans.extend(folder_scans)

    return build_graph(scans, depth="function")


def _unique_prefix(name: str, used_prefixes: dict[str, int]) -> str:
    safe = name.strip() or "folder"
    if safe not in used_prefixes:
        used_prefixes[safe] = 1
        return safe
    used_prefixes[safe] += 1
    return f"{safe}_{used_prefixes[safe]}"


def _default_output_paths(target_folder: Path) -> tuple[Path, Path]:
    graphs_dir = Path("graphs")
    html = graphs_dir / f"{target_folder.name}_graph.html"
    data = graphs_dir / f"{target_folder.name}_graph_data.json"
    return html, data


if __name__ == "__main__":
    raise SystemExit(main())
