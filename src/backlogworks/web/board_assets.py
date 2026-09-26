# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""Self-contained board styles and progressive, read-only interactions."""

CSS = """
:root { color-scheme:light; --ink:#20252b; --muted:#616973; --line:#dce0e5;
  --bg:#f6f7f8; --accent:#2458a6; }
* { box-sizing:border-box; }
[hidden] { display:none !important; }
body { margin:0; background:var(--bg); color:var(--ink);
  font:15px/1.5 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
main { max-width:960px; margin:auto; padding:24px 16px; }
a { color:var(--accent); text-underline-offset:3px; }
button,input,select { font:inherit; }
button,summary,select { cursor:pointer; }
button:focus-visible,summary:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible {
  outline:3px solid var(--accent); outline-offset:3px; }
.masthead { margin:28px 0 22px; overflow-wrap:anywhere; }
.eyebrow { color:var(--muted); font-size:12px; font-weight:650; letter-spacing:.08em; margin:0 0 8px; }
h1 { font-size:clamp(26px,4vw,36px); line-height:1.15; letter-spacing:-.025em; margin:0 0 12px; }
.description { color:var(--muted); margin:0 0 14px; }
.source-line { display:flex; flex-wrap:wrap; gap:6px 20px; font-size:13px; color:var(--muted); }
.subtitle { color:var(--muted); font-size:12px; margin:10px 0 0; }
.subtitle:empty,.description:empty { display:none; }
.view-switch { display:grid; grid-template-columns:repeat(6,minmax(0,1fr));
  border:1px solid var(--line); border-radius:9px; padding:3px; background:#e9ecf0; gap:2px; }
.view-switch button { border:0; border-radius:6px; background:transparent; color:var(--muted);
  min-height:44px; padding:7px 2px; font-size:13px; font-weight:600; }
.view-switch button[aria-pressed="true"] { color:var(--accent); background:#fff; box-shadow:0 1px 3px #20252b18; }
.count { color:var(--muted); font-size:13px; margin:10px 0; }
.filters { border-bottom:1px solid var(--line); padding:0 0 12px; margin:0 0 20px; }
.filters summary { width:fit-content; min-height:44px; padding:10px 4px; font-weight:600; }
.filter-fields { display:grid; gap:12px; padding:8px 0; }
.filter-fields label { display:grid; gap:5px; min-width:0; color:var(--muted); font-size:13px; }
input,select { width:100%; min-width:0; min-height:44px; border:1px solid #b9c0c9;
  border-radius:6px; padding:8px 10px; color:var(--ink); background:#fff; }
.card-row { display:grid; grid-template-columns:28px minmax(0,1fr); gap:9px; margin:0 0 12px; }
.rank { display:flex; align-items:center; justify-content:center; width:28px; height:28px;
  border:1px solid var(--line); border-radius:50%; color:var(--muted); background:#fff;
  font-size:12px; font-variant-numeric:tabular-nums; margin-top:15px; }
.card { background:#fff; border:1px solid var(--line); border-radius:9px; padding:16px; min-width:0;
  overflow-wrap:anywhere; }
.item-title { font-size:16px; line-height:1.4; font-weight:650; margin:0 0 10px; }
.item-id { color:var(--accent); }
.meta { display:flex; align-items:center; flex-wrap:wrap; gap:6px; margin-bottom:10px; }
.pill,.chip { font-size:12px; padding:3px 8px; border-radius:5px; }
.pill { font-weight:650; background:#eef0f2; }
.chip { background:#f4f5f6; border:1px solid #e4e7ea; color:#525b66; }
.s-ready { background:#eaf0fb; color:var(--accent); }
.s-progress { background:#e7f3eb; color:#22663b; }
.s-done { background:#eef0f2; color:var(--muted); }
.s-unknown { border:1px dashed var(--muted); }
.sprint { font-variant-numeric:tabular-nums; }
.waiting { margin:0 0 10px; font-size:13px; color:var(--muted); }
.context { color:var(--muted); font-size:14px; margin:0; }
.bug-row { grid-template-columns:minmax(0,1fr); margin-left:37px; }
code { background:#eef0f2; border-radius:3px; padding:0 3px; font-size:.92em; overflow-wrap:anywhere; }
.problems,.empty { padding:16px; border:1px solid var(--line); border-radius:8px; background:#fff; }
.intro { border-bottom:1px solid var(--line); padding:0 0 20px; font-size:13px; color:var(--muted); }
.intro h2 { color:var(--ink); font-size:16px; margin:0 0 6px; }
.intro p { margin:6px 0; }
.intro ul { padding-left:20px; margin:6px 0; }
footer { max-width:960px; margin:auto; padding:0 16px 28px; font-size:12px; color:var(--muted); }
@media (min-width:640px) {
  main { padding:36px; }
  .filter-fields { grid-template-columns:1fr 1fr; }
  .view-switch { width:fit-content; min-width:500px; }
  .card-row { grid-template-columns:36px minmax(0,1fr); gap:14px; }
  .rank { width:36px; height:36px; }
  .bug-row { grid-template-columns:minmax(0,1fr); margin-left:50px; }
}
@media (prefers-reduced-motion:reduce) {
  *,*::before,*::after { animation:none !important; transition:none !important; scroll-behavior:auto !important; }
}
"""

SCRIPT = """
(() => {
  'use strict';
  const board = document.getElementById('board');
  const buttons = [...board.querySelectorAll('[data-view]')];
  const rows = [...board.querySelectorAll('[data-views]')];
  const job = board.querySelector('#job-filter');
  const search = board.querySelector('#search');
  const count = board.querySelector('#view-count');
  const empty = board.querySelector('#empty-state');
  let view = 'open';

  function render() {
    const query = search.value.trim().toLowerCase();
    const selectedJob = job.value === 'all' ? null : job.selectedOptions[0].textContent;
    let eligible = 0;
    let visible = 0;
    rows.forEach(row => {
      const inView = row.dataset.views.split(' ').includes(view);
      if (inView) eligible++;
      const title = row.querySelector('.item-title').textContent.toLowerCase();
      const matchesJob = selectedJob === null ||
        (!row.classList.contains('bug-row') && row.dataset.job === selectedJob);
      const matches = inView && matchesJob && title.includes(query);
      row.hidden = !matches;
      if (matches) visible++;
    });
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.view === view)));
    const label = buttons.find(button => button.dataset.view === view).textContent;
    count.textContent = `${label} · ${visible} of ${eligible} ${eligible === 1 ? 'entry' : 'entries'}`;
    empty.hidden = visible !== 0;
  }

  buttons.forEach(button => {
    button.disabled = false;
    button.addEventListener('click', () => { view = button.dataset.view; render(); });
  });
  job.disabled = false;
  search.disabled = false;
  job.addEventListener('change', render);
  search.addEventListener('input', render);
  render();
})();
"""
