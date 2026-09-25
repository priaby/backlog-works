# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""Identity: Product Owner sessions and per-repo agent API keys.

Owns sign-in (magic-link email, PBI-003), session cookies, CSRF token
derivation, and API-key issue/verify (PBI-004). Storage lives behind this
package's own interface. May import config; never web, github, or backlog.
"""
