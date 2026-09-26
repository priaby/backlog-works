# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""HTTP layer: routes, server-rendered pages, JSON endpoints, headers.

Translates requests into commands on backlog, github, auth, local and
results into responses; renders the board. No backlog parsing, no GitHub
calls, no auth decisions, no mail: those live in their blocks and talk back
through return values and events.
"""
