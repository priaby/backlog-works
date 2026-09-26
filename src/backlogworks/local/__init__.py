# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""Local backlog source: this product's own backlog file read from disk
(path from `Config.backlog_file`, env `BACKLOG_FILE`). The first tenant is
this repository (dogfood). `BacklogSource`-shaped read; no write until
J709 (Persist backlog changes to the repo). May import backlog, events,
config.
"""

from backlogworks.local.source import LOCAL_REPO, load_backlog

__all__ = ["LOCAL_REPO", "load_backlog"]
