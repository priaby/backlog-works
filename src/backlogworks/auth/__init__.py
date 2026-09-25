# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""Identity: Product Owner sessions and per-repo agent API keys.

Owns magic-link sign-in (PBI-003), session cookies, CSRF token derivation,
and API-key issue/verify (PBI-004), plus its own SQLite tables. Publishes
`auth.*` events; never sends mail itself (notify subscribes). May import
events and config; never web, github, or backlog.
"""
