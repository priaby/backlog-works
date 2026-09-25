# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""HTTP layer: routes, the board page, JSON endpoints, response headers.

Translates requests into calls on backlog, github, and auth, and results
into responses. No parsing of the backlog format here, no GitHub calls
outside the github package, no auth decisions outside auth.
"""
