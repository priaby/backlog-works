# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""Event core: typed domain events, the in-process bus, and the audit sink.

Modules never call sideways; they publish an Event after their primary
effect succeeded and other modules subscribe. Dispatch is synchronous in
the publishing thread; a failing subscriber is logged and isolated, it
never fails the command that produced the event. The persisted event log
(timeline) and the outbox for external effects land with N835 and are
specified in docs/architecture.md section 4.
"""

from backlogworks.events.bus import Event, EventBus, audit_to_stderr

__all__ = ["Event", "EventBus", "audit_to_stderr"]
