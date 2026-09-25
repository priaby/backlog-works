# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""Outbound notifications, driven only by events.

Subscribes to `auth.signin_requested` (magic-link mail) and
`backlog.item_status_changed` (Product Owner digest when an agent moves an
item to review). Writes to the outbox table; a dispatcher drains it with
retries. Provider chosen in PBI-003 (Standalone sign-in). May import events
and config; never called directly by another module.
"""
