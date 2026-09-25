# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""Runtime configuration, read once from the environment at startup.

Every setting the service reads is declared here with its env var name and
default; no other module calls os.environ. Adding a setting means adding a
field here and, if it is a secret, a Railway project variable (see
.agents/skills/backlog-works-secrets/SKILL.md).
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    port: int = 8080
    bind_host: str = "0.0.0.0"

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "Config":
        e = os.environ if env is None else env
        return cls(port=int(e.get("PORT", "8080")))
