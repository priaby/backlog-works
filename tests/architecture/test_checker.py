# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""AST and filesystem regressions for the architecture gate's ordinary bypasses."""

import ast
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from scripts import check_architecture as checker


class ImportTests(unittest.TestCase):
    def check(self, source, relative="backlog/probe.py"):
        return checker.check_imports(checker.SRC / relative, ast.parse(source))

    def test_forbidden_import_spellings(self):
        for source in (
            "import backlogworks.auth",
            "from backlogworks.auth import anything",
            "from backlogworks import auth",
            "from backlogworks import auth as identity",
            "from ..auth import anything",
            "from .. import auth",
            "from ... import auth",
        ):
            path = "backlog/nested/probe.py" if "..." in source else "backlog/probe.py"
            with self.subTest(source=source):
                self.assertTrue(self.check(source, path))

    def test_package_relative_imports(self):
        self.assertTrue(self.check("from .. import auth", "backlog/__init__.py"))
        self.assertTrue(self.check("from . import auth", "__init__.py"))
        self.assertTrue(self.check("from ...auth import x"))

    def test_positive_allowed_and_intrablock_imports(self):
        for source, path in (
            ("from .model import Item", "backlog/__init__.py"),
            ("from . import model", "backlog/__init__.py"),
            ("from .. import model", "backlog/nested/probe.py"),
            ("from backlogworks import backlog", "demo/source.py"),
            ("from ..events import Event", "demo/source.py"),
            ("import json\nfrom collections import Counter", "backlog/probe.py"),
        ):
            with self.subTest(source=source):
                self.assertEqual(self.check(source, path), [])

    def test_network_forms_are_uniformly_rejected(self):
        for source in (
            "from http import client", "from http.client import HTTPConnection",
            "import http.client", "import socketserver", "from socketserver import TCPServer",
            "import socket as net", "from socket import socket", "import ssl",
            "from ssl import SSLContext", "import smtplib", "from smtplib import SMTP",
            "import urllib.request", "from urllib import request", "from urllib.request import urlopen",
            "from http import server", "from http.server import HTTPServer",
        ):
            with self.subTest(source=source):
                self.assertTrue(self.check(source))
                self.assertTrue(self.check(source, "web/probe.py"))
                self.assertEqual(self.check(source, "github/client.py"), [])
                self.assertEqual(self.check(source, "notify/mail.py"), [])

    def test_listener_exception_is_path_and_module_specific(self):
        for source in ("import socketserver", "from http.server import ThreadingHTTPServer",
                       "from http import server"):
            with self.subTest(source=source):
                self.assertEqual(self.check(source, "web/server.py"), [])
                self.assertTrue(self.check(source, "web/nested/server.py"))
        for source in ("import urllib.request", "from http import client", "import socket",
                       "import ssl", "import smtplib"):
            with self.subTest(source=source):
                self.assertTrue(self.check(source, "web/server.py"))


class EnvironmentTests(unittest.TestCase):
    def test_environment_forms_and_exact_config_exemption(self):
        for source in (
            "import os; value = os.environ",
            "import os as system; value = system.environ",
            "import os as system; value = system.getenv('PORT')",
            "from os import environ; value = environ['PORT']",
            "from os import environ as env; value = env.get('PORT')",
            "from os import getenv; value = getenv('PORT')",
            "from os import getenv as read_env; value = read_env('PORT')",
            "from os import *; value = getenv('PORT')",
        ):
            tree = ast.parse(source)
            with self.subTest(source=source):
                for path in ("backlog/probe.py", "backlog/config.py", "web/config.py"):
                    self.assertTrue(checker.check_environ(checker.SRC / path, tree))
                self.assertEqual(checker.check_environ(checker.SRC / "config.py", tree), [])

    def test_non_environment_os_use_is_allowed(self):
        self.assertEqual(checker.check_environ(checker.SRC / "web/probe.py",
                                              ast.parse("import os as system; value = system.name")), [])


class PurityTests(unittest.TestCase):
    def test_known_file_reads(self):
        for source in (
            "open('backlog.md').read()",
            "import builtins as b; b.open('backlog.md')",
            "from builtins import open as read; read('backlog.md')",
            "from io import open as read; read('backlog.md')",
            "import pathlib; pathlib.Path('backlog.md').read_text()",
            "import pathlib as p; p.Path('backlog.md').read_bytes()",
            "from pathlib import Path as P; P('backlog.md').open()",
            "from pathlib import Path; p = Path('backlog.md'); p.read_text()",
            "def read(path): return path.read_bytes()",
        ):
            tree = ast.parse(source)
            with self.subTest(source=source):
                self.assertTrue(checker.check_purity(checker.SRC / "backlog/probe.py", tree))
                self.assertEqual(checker.check_purity(checker.SRC / "demo/source.py", tree), [])

    def test_pure_parser_operations_are_allowed(self):
        tree = ast.parse("import re\nrows = text.splitlines()\nmatch = re.match('x', rows[0])")
        self.assertEqual(checker.check_purity(checker.SRC / "backlog/probe.py", tree), [])


class FileTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.src = self.root / "src" / "backlogworks"
        self.src.mkdir(parents=True)
        for name in checker.ALLOWED:
            path = (self.src / f"{name}.py" if name in checker.MODULE_BLOCKS
                    else self.src / name / "__init__.py")
            path.parent.mkdir(exist_ok=True)
            path.write_text('"""Block responsibility."""\n', encoding="utf-8")
        root_patch = patch.object(checker, "ROOT", self.root)
        src_patch = patch.object(checker, "SRC", self.src)
        root_patch.start()
        src_patch.start()
        self.addCleanup(root_patch.stop)
        self.addCleanup(src_patch.stop)

    def test_declared_packages_with_docstrings_pass(self):
        self.assertEqual(checker.check_packages(), [])

    def test_missing_package_or_docstring_fails(self):
        contract = self.src / "auth" / "__init__.py"
        contract.unlink()
        self.assertTrue(any("missing" in p for p in checker.check_packages()))
        for source in ("# comment only\n", '"""   """\n'):
            contract.write_text(source, encoding="utf-8")
            self.assertTrue(any("docstring" in p for p in checker.check_packages()))

    def test_undeclared_top_level_source_package_fails(self):
        (self.root / "src" / "other_package").mkdir()
        self.assertTrue(any("other_package" in p for p in checker.check_packages()))

    def test_undeclared_building_block_fails(self):
        (self.src / "other_block").mkdir()
        self.assertTrue(any("other_block" in p for p in checker.check_packages()))

    def test_sizes_cover_nested_source_tests_and_scripts(self):
        for relative in ("src/other_package/deep/large.py", "tests/backlog/deep/large.py",
                         "scripts/nested/deep/large.py"):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# line\n" * 601, encoding="utf-8")
            self.assertIn(path, checker.python_files())
        self.assertEqual(len(checker.check_sizes(checker.python_files())), 3)
        for path in checker.python_files():
            path.write_text("# line\n" * 600, encoding="utf-8")
        self.assertEqual(checker.check_sizes(checker.python_files()), [])

    def test_git_paths_use_nul_delimiters(self):
        output = Mock(stdout="README.md\0tests/space and\nnewline.py\0rogue file.py\0")
        with patch.object(checker.subprocess, "run", return_value=output) as run:
            problems = checker.check_root()
        self.assertEqual(problems, ["rogue file.py: root file not in root allowlist"])
        self.assertEqual(run.call_args.args[0], ["git", "ls-files", "-z"])
