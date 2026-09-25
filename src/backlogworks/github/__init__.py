# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""GitHub adapter: read and commit the backlog file via the Contents API, and
accept the `push` webhook.

The only module with GitHub egress. Read with ETag cache; write with the
blob sha as optimistic-concurrency guard, committing straight to the
configured branch. Publishes `backlog.file_changed` (webhook),
`backlog.committed`, `backlog.commit_conflicted`. May import backlog,
events, config; never web or auth.
"""
