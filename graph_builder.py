"""Build PolyGraph nodes and edges from extracted AST facts."""

from __future__ import annotations

import ast
import sys
from collections import defaultdict
from pathlib import PurePosixPath
from typing import Any

from categorizer import CATEGORY_COLORS, categorize_file
from extractor import FileScan, ImportRef


STDLIB_MODULES = set(getattr(sys, "stdlib_module_names", ()))


def build_graph(scans: list[FileScan], depth: str = "function") -> dict[str, Any]:
    """Convert file scans into a serializable graph model."""

    module_to_path = _module_index(scans)
    path_to_scan = {scan.path: scan for scan in scans}
    function_to_paths = _function_index(scans)

    import_targets: dict[str, set[str]] = defaultdict(set)
    import_external: dict[str, set[str]] = defaultdict(set)
    alias_targets: dict[str, dict[str, str]] = defaultdict(dict)
    direct_function_targets: dict[str, dict[str, tuple[str, str]]] = defaultdict(dict)

    for scan in scans:
        for import_ref in scan.imports:
            target_path = _resolve_import(scan, import_ref, module_to_path)
            display_name = _display_import(import_ref)
            if target_path and target_path != scan.path:
                import_targets[scan.path].add(target_path)
                alias_targets[scan.path][import_ref.alias] = target_path
                if import_ref.name and import_ref.name in path_to_scan[target_path].functions:
                    direct_function_targets[scan.path][import_ref.alias] = (target_path, import_ref.name)
            elif target_path == scan.path:
                continue
            else:
                root_name = _external_root(import_ref)
                if root_name:
                    import_external[scan.path].add(root_name)

    nodes: list[dict[str, Any]] = []
    for scan in scans:
        imports_all = [_display_import(import_ref) for import_ref in scan.imports]
        category = categorize_file(scan.path, imports_all)
        nodes.append(
            {
                "id": scan.path,
                "path": scan.path,
                "folder": scan.folder,
                "category": category,
                "lines": scan.lines,
                "functions": scan.functions,
                "classes": scan.classes,
                "imports_local": sorted(import_targets[scan.path]),
                "imports_external": sorted(import_external[scan.path]),
                "parse_error": scan.parse_error,
            }
        )

    edge_map: dict[tuple[str, str, str], dict[str, Any]] = {}
    for source, targets in import_targets.items():
        for target in targets:
            edge_map[(source, target, "import")] = {
                "source": source,
                "target": target,
                "type": "import",
            }

    if depth == "function":
        for scan in scans:
            calls_by_target: dict[str, set[str]] = defaultdict(set)
            local_functions = set(scan.functions)
            for call in scan.calls:
                target = _resolve_call(
                    call=call,
                    source=scan.path,
                    alias_targets=alias_targets[scan.path],
                    direct_function_targets=direct_function_targets[scan.path],
                    function_to_paths=function_to_paths,
                    local_functions=local_functions,
                )
                if target and target[0] != scan.path:
                    calls_by_target[target[0]].add(target[1])

            for target_path, calls in calls_by_target.items():
                edge_map[(scan.path, target_path, "function_call")] = {
                    "source": scan.path,
                    "target": target_path,
                    "type": "function_call",
                    "calls": sorted(calls),
                }

    return {
        "meta": {
            "node_count": len(nodes),
            "edge_count": len(edge_map),
            "depth": depth,
            "categories": CATEGORY_COLORS,
        },
        "nodes": sorted(nodes, key=lambda item: item["path"]),
        "edges": sorted(edge_map.values(), key=lambda item: (item["source"], item["target"], item["type"])),
    }


def _module_index(scans: list[FileScan]) -> dict[str, str]:
    index: dict[str, str] = {}
    for scan in scans:
        pure = PurePosixPath(scan.path)
        parts = list(pure.with_suffix("").parts)
        if parts[-1] == "__init__":
            package = ".".join(parts[:-1])
            if package:
                index[package] = scan.path
        module = ".".join(parts)
        index[module] = scan.path
        index.setdefault(parts[-1], scan.path)
    return index


def _function_index(scans: list[FileScan]) -> dict[str, list[str]]:
    found: dict[str, list[str]] = defaultdict(list)
    for scan in scans:
        for function in scan.functions:
            found[function].append(scan.path)
    return found


def _resolve_import(scan: FileScan, import_ref: ImportRef, module_to_path: dict[str, str]) -> str | None:
    candidates: list[str] = []
    if import_ref.level:
        package = list(PurePosixPath(scan.path).parent.parts)
        if package == ["."]:
            package = []
        base = package[: max(0, len(package) - import_ref.level + 1)]
        if import_ref.module:
            candidates.append(".".join([*base, *import_ref.module.split(".")]).strip("."))
        if import_ref.name:
            candidates.append(".".join([*base, *import_ref.module.split("."), import_ref.name]).strip("."))
    else:
        if import_ref.module:
            candidates.append(import_ref.module)
            if import_ref.name:
                candidates.append(f"{import_ref.module}.{import_ref.name}")
        elif import_ref.name:
            candidates.append(import_ref.name)

    for candidate in candidates:
        if candidate in module_to_path:
            return module_to_path[candidate]

    if not import_ref.level and import_ref.module:
        top_level = import_ref.module.split(".", 1)[0]
        return module_to_path.get(top_level)

    return None


def _resolve_call(
    call: ast.Call,
    source: str,
    alias_targets: dict[str, str],
    direct_function_targets: dict[str, tuple[str, str]],
    function_to_paths: dict[str, list[str]],
    local_functions: set[str],
) -> tuple[str, str] | None:
    func = call.func
    if isinstance(func, ast.Name):
        if func.id in direct_function_targets:
            return direct_function_targets[func.id]
        paths = function_to_paths.get(func.id, [])
        if func.id not in local_functions and len(paths) == 1:
            return paths[0], func.id
        return None

    if isinstance(func, ast.Attribute):
        root = _root_name(func.value)
        if root and root in alias_targets:
            return alias_targets[root], func.attr

    return None


def _root_name(node: ast.AST) -> str | None:
    current = node
    while isinstance(current, ast.Attribute):
        current = current.value
    if isinstance(current, ast.Name):
        return current.id
    return None


def _display_import(import_ref: ImportRef) -> str:
    if import_ref.name:
        prefix = "." * import_ref.level + import_ref.module
        return f"{prefix}.{import_ref.name}".strip(".")
    return import_ref.module


def _external_root(import_ref: ImportRef) -> str:
    name = import_ref.module or import_ref.name or ""
    root = name.lstrip(".").split(".", 1)[0]
    if root in STDLIB_MODULES:
        return f"stdlib:{root}"
    return root
