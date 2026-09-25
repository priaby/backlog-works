# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""GitHub adapter: read and commit the backlog file via the Contents API.

The only module that talks to GitHub. Read with ETag cache; write with the
blob sha as optimistic-concurrency guard, committing straight to the
configured branch. May import backlogworks.backlog for types; never web or
auth.
"""
