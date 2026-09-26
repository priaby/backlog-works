#!/usr/bin/env python3
"""Architecture convention gate for the matrix below and documented rules.

Checks ordinary absolute/relative imports, os environment bindings, known
network and file I/O entry points, declared packages/docstrings, recursive
Python sizes and tracked root paths. Dynamic imports, reflection and arbitrary
runtime effects still require review: this AST gate is not a Python sandbox.
Stdlib only. Exit 0 clean, 1 violations.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from importlib.util import resolve_name
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
    "local": {"backlog", "events", "config"},
    "landing": {"config"},
    "docs": {"config"},
    "web": {"backlog", "github", "auth", "local", "landing", "docs", "events", "config"},
    "__main__": {"config", "events", "web", "notify", "auth", "github"},  # composition root
    "__init__": set(),
}
NETWORK_MODULES = {"urllib", "http.client", "http.server", "socket", "socketserver", "smtplib", "ssl"}
NETWORK_ALLOWED_IN = {"github", "notify"}
SERVER_MODULES = {"http.server", "socketserver"}
MODULE_BLOCKS = {"config", "__main__", "__init__"}
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


def imported_names(path: Path, node: ast.Import | ast.ImportFrom) -> list[str]:
    """Resolve from-import bases and members, including package re-exports."""
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    base = node.module or ""
    if node.level:
        package = ".".join(("backlogworks", *path.relative_to(SRC).parent.parts))
        base = resolve_name("." * node.level + base, package)
    return [base, *(f"{base}.{alias.name}" for alias in node.names if alias.name != "*")]


def is_module(name: str, modules: set[str]) -> bool:
    return any(name == module or name.startswith(module + ".") for module in modules)


def check_imports(path: Path, tree: ast.AST) -> list[str]:
    mod = top_module(path)
    allowed = ALLOWED.get(mod)
    out = []
    if allowed is None:
        return [f"{path}: unknown building block {mod!r}; declare it in docs/architecture.md and this checker"]
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        try:
            names = imported_names(path, node)
        except ImportError:
            out.append(f"{path}:{node.lineno}: relative import escapes backlogworks")
            continue
        for name in names:
            if name.startswith("backlogworks."):
                target = name.split(".")[1]
                if target != mod and target not in allowed:
                    out.append(f"{path}:{node.lineno}: {mod} may not import backlogworks.{target}")
            listener_import = (path == SRC / "web" / "server.py"
                               and is_module(name, SERVER_MODULES))
            if is_module(name, NETWORK_MODULES) and mod not in NETWORK_ALLOWED_IN and not listener_import:
                out.append(f"{path}:{node.lineno}: network module {name} outside permitted adapter/listener")
    return out


def check_environ(path: Path, tree: ast.AST) -> list[str]:
    if path == SRC / "config.py":
        return []
    out = []
    os_names = {"os"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            os_names.update(alias.asname or "os" for alias in node.names if alias.name == "os")
        elif isinstance(node, ast.ImportFrom) and node.module == "os" and not node.level:
            for alias in node.names:
                if alias.name in {"environ", "getenv", "*"}:
                    out.append(f"{path}:{node.lineno}: os.{alias.name} outside config.py")
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr in {"environ", "getenv"}:
            if isinstance(node.value, ast.Name) and node.value.id in os_names:
                out.append(f"{path}:{node.lineno}: os.{node.attr} outside config.py")
    return out


def check_purity(path: Path, tree: ast.AST) -> list[str]:
    """Reject known file reads in backlog, including aliased open and Path reads.

    Attribute checks intentionally also catch Path objects passed as arguments;
    provenance and less direct I/O remain a code-review responsibility.
    """
    if top_module(path) != "backlog":
        return []
    open_names = {"open"}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module in {"builtins", "io"}:
            open_names.update(alias.asname or alias.name for alias in node.names if alias.name == "open")
    out = []
    read_methods = {"open", "read_text", "read_bytes", "iterdir", "glob", "rglob"}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if ((isinstance(func, ast.Name) and func.id in open_names)
                or (isinstance(func, ast.Attribute) and func.attr in read_methods)):
            out.append(f"{path}:{node.lineno}: file I/O in pure backlog block")
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
    tracked = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split("\0")
    out = []
    for t in filter(None, tracked):
        first = t.split("/", 1)[0]
        if "/" in t:
            if first not in ROOT_DIR_ALLOWLIST:
                out.append(f"{t}: top-level dir {first!r} not in root allowlist")
        elif first not in ROOT_ALLOWLIST:
            out.append(f"{t}: root file not in root allowlist")
    return out


def check_packages() -> list[str]:
    out = []
    for p in (ROOT / "src").iterdir():
        if p.name not in {"backlogworks", "__pycache__"}:
            out.append(f"src/{p.name}: not a declared top-level source package")
    if not SRC.is_dir():
        return out + ["src/backlogworks: required source package missing"]
    for p in SRC.iterdir():
        name = p.name.removesuffix(".py")
        if p.name == "__pycache__":
            continue
        if name not in ALLOWED:
            out.append(f"src/backlogworks/{p.name}: not a declared building block")
    for name in ALLOWED:
        contract = SRC / f"{name}.py" if name in MODULE_BLOCKS else SRC / name / "__init__.py"
        if not contract.is_file():
            out.append(f"{contract}: declared block missing module/package contract")
            continue
        tree = ast.parse(contract.read_text(encoding="utf-8"), filename=str(contract))
        if not (ast.get_docstring(tree) or "").strip():
            out.append(f"{contract}: declared block requires a module docstring")
    return out


def python_files() -> list[Path]:
    """The size-checked universe includes untracked source, tests and tooling."""
    return sorted(p for directory in ("src", "tests", "scripts")
                  for p in (ROOT / directory).rglob("*.py"))


def main() -> int:
    problems: list[str] = []
    py_files = sorted(p for p in SRC.rglob("*.py"))
    for f in py_files:
        tree = ast.parse(f.read_text(encoding="utf-8"), filename=str(f))
        problems += check_imports(f, tree)
        problems += check_environ(f, tree)
        problems += check_purity(f, tree)
    problems += check_sizes(python_files())
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
