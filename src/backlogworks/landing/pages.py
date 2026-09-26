# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""Landing chrome. The landing page is the demo backlog rendered by the same
board engine as every tenant board (web.board.render_board); this module
only supplies the pitch shown above it. Pre-escaped, trusted HTML."""

PITCH_HTML = """<section class="intro">
<h2>backlog.works</h2>
<p>A Scrum product backlog shared by a human Product Owner and agentic teams.</p>
<ul>
  <li>The backlog is a plain markdown file, in your repo or hosted here, versioned like code.</li>
  <li>Below is a fictitious product's backlog rendered by the same engine that will serve yours.</li>
  <li>Planned: Product Owner sign-in, ordering and acceptance from a phone, API access for agents.</li>
</ul>
<p><small>Pre-alpha.</small></p>
</section>
"""


def pitch_html() -> str:
    return PITCH_HTML
