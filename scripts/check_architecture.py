#!/usr/bin/env python3
"""Architecture gate for backlog.works (docs/architecture.md, "Rules").

Fails closed on:
  1. an import between backlogworks modules that the dependency matrix forbids
  2. os.environ used outside backlogworks/config.py
  3. urllib/http.client/socket network use outside backlogworks/github/
  4. a Python source file over the size cap (Crest's debt was 1,800- and
     5,500-line root files)
  5. a tracked file at the repo root that is not in the root allowlist
  6. a top-level package other than the declared building blocks

Stdlib only. Exit 0 clean, 1 violations.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "backlogworks"

# module -> set of backlogworks modules it may import
ALLOWED = {
    "config": set(),
    "events": {"config"},
    "backlog": set(),
    "github": {"backlog", "events", "config"},
    "auth": {"events", "config"},
    "notify": {"events", "config"},
    "demo": {"backlog", "events", "config"},
    "landing": {"config"},
    "docs": {"config"},
    "web": {"backlog", "github", "auth", "demo", "landing", "docs", "events", "config"},
    "__main__": {"config", "events", "web", "notify", "auth", "github"},  # composition root
    "__init__": set(),
}
NETWORK_MODULES = {"urllib", "http.client", "socket", "smtplib", "ssl"}
NETWORK_ALLOWED_IN = {"github", "notify", "web"}  # web: only the stdlib server binding
SIZE_CAP_LINES = 600
SIZE_CAP_EXEMPT: dict[str, int] = {}  # relative path -> justified cap

ROOT_ALLOWLIST = {
    ".gitignore", "AGENTS.md", "CLAUDE.md", "Dockerfile", "LICENSE",
    "README.md", "railway.json",
}
ROOT_DIR_ALLOWLIST = {".agents", ".claude", "docs", "scripts", "src", "tests"}


def top_module(path: Path) -> str:
    rel = path.relative_to(SRC)
    return rel.parts[0].removesuffix(".py")


def check_imports(path: Path, tree: ast.AST) -> list[str]:
    mod = top_module(path)
    allowed = ALLOWED.get(mod)
    out = []
    if allowed is None:
        return [f"{path}: unknown building block {mod!r}; declare it in docs/architecture.md and this checker"]
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            names = [node.module]
        for name in names:
            if name.startswith("backlogworks."):
                target = name.split(".")[1]
                if target != mod and target not in allowed:
                    out.append(f"{path}:{node.lineno}: {mod} may not import backlogworks.{target}")
            root = name.split(".")[0]
            full2 = ".".join(name.split(".")[:2])
            if (root in NETWORK_MODULES or full2 in NETWORK_MODULES) and mod not in NETWORK_ALLOWED_IN:
                out.append(f"{path}:{node.lineno}: network module {name} outside github/web")
    return out


def check_environ(path: Path, tree: ast.AST) -> list[str]:
    if path.name == "config.py":
        return []
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr in {"environ", "getenv"}:
            if isinstance(node.value, ast.Name) and node.value.id == "os":
                out.append(f"{path}:{node.lineno}: os.{node.attr} outside config.py")
    return out


def check_sizes(files: list[Path]) -> list[str]:
    out = []
    for f in files:
        n = len(f.read_text(encoding="utf-8").splitlines())
        cap = SIZE_CAP_EXEMPT.get(str(f.relative_to(ROOT)), SIZE_CAP_LINES)
        if n > cap:
            out.append(f"{f.relative_to(ROOT)}: {n} lines > cap {cap}; split by responsibility")
    return out


def check_root() -> list[str]:
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    out = []
    for t in tracked:
        first = t.split("/", 1)[0]
        if "/" in t:
            if first not in ROOT_DIR_ALLOWLIST:
                out.append(f"{t}: top-level dir {first!r} not in root allowlist")
        elif first not in ROOT_ALLOWLIST:
            out.append(f"{t}: root file not in root allowlist")
    return out


def check_packages() -> list[str]:
    out = []
    for p in SRC.iterdir():
        name = p.name.removesuffix(".py")
        if p.name.startswith("__pycache__"):
            continue
        if name not in ALLOWED:
            out.append(f"src/backlogworks/{p.name}: not a declared building block")
    return out


def main() -> int:
    problems: list[str] = []
    py_files = sorted(p for p in SRC.rglob("*.py"))
    for f in py_files:
        tree = ast.parse(f.read_text(encoding="utf-8"), filename=str(f))
        problems += check_imports(f, tree)
        problems += check_environ(f, tree)
    problems += check_sizes(py_files + sorted((ROOT / "scripts").glob("*.py")))
    problems += check_root()
    problems += check_packages()
    for p in problems:
        print(f"FAIL {p}")
    if problems:
        return 1
    print(f"ok architecture: {len(py_files)} source files, boundaries hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
