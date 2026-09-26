# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""Demo tenant: a fictitious product backlog packaged with the image.

Exists so the board can be shown before the GitHub source (J709) and
sign-in (N835) exist. Reads its own packaged markdown file; it is the
only place a packaged backlog is read. Removed or hidden once a real tenant
is configured. May import backlog, events, config.
"""

from backlogworks.demo.source import DEMO_REPO, load_demo

__all__ = ["DEMO_REPO", "load_demo"]
