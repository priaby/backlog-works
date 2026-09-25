# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""Public marketing surface: `/` and static pitch pages.

Server-rendered HTML with the README "Why"/"How it works" copy until PBI-006
(Brand and landing page) gives it a real identity. Knows nothing about
backlogs or sessions; may import config only.
"""

from backlogworks.landing.pages import index_html

__all__ = ["index_html"]
