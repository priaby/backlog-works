# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""Public marketing surface: the pitch chrome shown on `/`.

The landing page itself is this product's own backlog rendered by the
single board engine (PO decision 2026-09-26: no separate backlog
implementation for the landing). This block supplies only the pitch block
above the board, until G761 (Brand and landing page) gives it a real
identity. Knows nothing about backlogs or sessions; may import config
only.
"""

from backlogworks.landing.pages import pitch_html

__all__ = ["pitch_html"]
