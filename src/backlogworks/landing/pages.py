# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>backlog.works</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 40em; margin: 3em auto; padding: 0 1.2em; color: #1d1d1f; line-height: 1.5; }
  h1 { font-size: 1.6em; margin-bottom: .2em; }
  p.lead { font-size: 1.1em; color: #444; }
  a.btn { display: inline-block; padding: .7em 1.2em; border-radius: .6em; background: #1d1d1f; color: #fff; text-decoration: none; }
  ul { padding-left: 1.2em; }
</style>
</head>
<body>
<h1>backlog.works</h1>
<p class="lead">A Scrum product backlog shared by a human Product Owner and agentic teams.</p>
<ul>
  <li>The backlog is a markdown file in your repo, versioned like code.</li>
  <li>Planned: Product Owner sign-in, ordering and acceptance from a phone.</li>
  <li>Agents can work on the file through git. API access is planned.</li>
</ul>
<p><a class="btn" href="/demo">See a demo backlog</a></p>
<p><small>Pre-alpha. Coming soon.</small></p>
</body>
</html>
"""


def index_html() -> str:
    return INDEX_HTML
