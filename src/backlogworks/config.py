# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""Runtime configuration, read once from the environment at startup.

Every setting the service reads is declared here with its env var name and
default; no other module calls os.environ. Adding a setting means adding a
field here and, if it is a secret, a Railway project variable (see
.agents/skills/backlog-works-secrets/SKILL.md).

Env vars: `PORT`, `BACKLOG_FILE`.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BACKLOG_FILE = "docs/product/backlog.md"


@dataclass(frozen=True)
class Config:
    port: int = 8080
    bind_host: str = "0.0.0.0"
    backlog_file: Path = APP_ROOT / DEFAULT_BACKLOG_FILE

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "Config":
        e = os.environ if env is None else env
        raw = e.get("BACKLOG_FILE", "") or DEFAULT_BACKLOG_FILE
        path = Path(raw)
        return cls(port=int(e.get("PORT", "8080")),
                    backlog_file=path if path.is_absolute() else APP_ROOT / path)
