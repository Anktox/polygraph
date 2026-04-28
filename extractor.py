"""AST-based project scanner for PolyGraph."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ImportRef:
    module: str
    name: str | None
    alias: str
    level: int = 0


@dataclass
class FileScan:
    path: str
    absolute_path: Path
    folder: str
    lines: int
    functions: list[str] = field(default_factory=list)
    classes: list[str] = field(default_factory=list)
    imports: list[ImportRef] = field(default_factory=list)
    calls: list[ast.Call] = field(default_factory=list)
    parse_error: str | None = None


class _ScanVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.functions: list[str] = []
        self.classes: list[str] = []
        self.imports: list[ImportRef] = []
        self.calls: list[ast.Call] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.functions.append(node.name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.functions.append(node.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.classes.append(node.name)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append(
                ImportRef(
                    module=alias.name,
                    name=None,
                    alias=alias.asname or alias.name.split(".", 1)[0],
                )
            )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        for alias in node.names:
            self.imports.append(
                ImportRef(
                    module=module,
                    name=alias.name,
                    alias=alias.asname or alias.name,
                    level=node.level,
                )
            )

    def visit_Call(self, node: ast.Call) -> None:
        self.calls.append(node)
        self.generic_visit(node)


def scan_project(project_path: Path, max_depth: int | None = None) -> list[FileScan]:
    """Scan Python files below project_path and return AST facts per file."""

    project_path = project_path.resolve()
    scans: list[FileScan] = []

    for file_path in sorted(project_path.rglob("*.py")):
        if _is_ignored(file_path, project_path):
            continue
        relative = file_path.relative_to(project_path)
        if max_depth is not None and len(relative.parts) > max_depth:
            continue

        text = file_path.read_text(encoding="utf-8", errors="replace")
        rel_posix = relative.as_posix()
        folder = relative.parent.as_posix() if relative.parent.as_posix() != "." else "root"
        scan = FileScan(
            path=rel_posix,
            absolute_path=file_path,
            folder=folder,
            lines=text.count("\n") + (1 if text else 0),
        )

        try:
            tree = ast.parse(text, filename=str(file_path))
        except SyntaxError as exc:
            scan.parse_error = f"{exc.msg} at line {exc.lineno}"
            scans.append(scan)
            continue

        visitor = _ScanVisitor()
        visitor.visit(tree)
        scan.functions = sorted(set(visitor.functions))
        scan.classes = sorted(set(visitor.classes))
        scan.imports = visitor.imports
        scan.calls = visitor.calls
        scans.append(scan)

    return scans


def _is_ignored(path: Path, root: Path) -> bool:
    ignored_parts = {
        ".git",
        ".hg",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "node_modules",
        "venv",
    }
    relative_parts = set(path.relative_to(root).parts)
    return bool(relative_parts & ignored_parts)
