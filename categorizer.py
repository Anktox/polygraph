"""File categorization helpers for PolyGraph."""

from __future__ import annotations

from pathlib import PurePosixPath


CATEGORY_COLORS = {
    "entry": "#f5c542",
    "bot": "#ff7a45",
    "market": "#2dd4bf",
    "config": "#a78bfa",
    "data": "#60a5fa",
    "test": "#f472b6",
    "utils": "#94a3b8",
    "core": "#34d399",
}


def categorize_file(path: str, imports: list[str] | None = None) -> str:
    """Return a broad category for a Python source file."""

    posix = path.replace("\\", "/").lower()
    pure = PurePosixPath(posix)
    stem = pure.stem
    imports_text = " ".join(imports or []).lower()
    haystack = f"{posix} {stem} {imports_text}"

    if stem in {"main", "__main__", "app", "run", "cli", "manage"}:
        return "entry"
    if any(part in haystack for part in ("test", "spec", "pytest")):
        return "test"
    if any(part in haystack for part in ("config", "settings", "constant", "env", "secret")):
        return "config"
    if any(part in haystack for part in ("bot", "trade", "trading", "strategy", "signal", "order")):
        return "bot"
    if any(part in haystack for part in ("market", "exchange", "binance", "ticker", "candle", "ohlc")):
        return "market"
    if any(part in haystack for part in ("data", "dataset", "loader", "storage", "db", "sql", "csv")):
        return "data"
    if any(part in haystack for part in ("util", "helper", "common", "logger", "log_", "tools")):
        return "utils"
    return "core"
