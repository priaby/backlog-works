# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""Self-contained board styles and progressive, read-only interactions.

CSS moved to board_css.py (docs/design-system.md rule 4.6: a single file
stays under 400 lines before the split); re-exported here so callers keep
importing CSS and SCRIPT from this module.
"""

from backlogworks.web.board_css import CSS

__all__ = ["CSS", "SCRIPT"]

SCRIPT = """
(() => {
  'use strict';
  const board = document.getElementById('board');
  const list = document.getElementById('cards');
  const viewButtons = [...board.querySelectorAll('.bw-segmented [data-view]')];
  const empty = document.getElementById('empty-state');
  const status = document.getElementById('order-status');
  const reset = document.getElementById('order-reset');
  const rows = () => [...list.children];
  const original = rows();
  const currentIds = () => rows().map(r => r.dataset.id);
  let view = viewButtons.find(b => b.getAttribute('aria-pressed') === 'true') || viewButtons[0];
  const matches = r => {
    const v = view.dataset.view;
    return v === 'all'
      || (v === 'open' && r.dataset.state === 'open')
      || (v === 'done' && r.dataset.state === 'done')
      || (v === 'progress' && r.dataset.stage === 'In Progress');
  };

  function step(r, dir) {
    let n = dir < 0 ? r.previousElementSibling : r.nextElementSibling;
    while (n && n.hidden) n = dir < 0 ? n.previousElementSibling : n.nextElementSibling;
    return n;
  }

  function syncControls() {
    rows().forEach(r => {
      const edge = {up: !step(r, -1), down: !step(r, 1), top: r === list.firstElementChild};
      r.querySelectorAll('[data-move]').forEach(b => {
        b.disabled = edge[b.dataset.move];
        b.toggleAttribute('data-edge', edge[b.dataset.move]);
      });
    });
  }

  function renumber() {
    rows().forEach((r, i) => {
      const b = r.querySelector('.bw-rank');
      b.textContent = String(i + 1);
      b.setAttribute('aria-label', 'Priority ' + (i + 1));
    });
  }

  function applyView() {
    let visible = 0;
    rows().forEach(r => {
      r.hidden = !matches(r);
      if (!r.hidden) visible++;
    });
    empty.hidden = visible !== 0;
    viewButtons.forEach(b => b.setAttribute('aria-pressed', String(b === view)));
    syncControls();
  }

  // J709 (Persist backlog changes to the repo) replaces this body with
  // POST /api/backlog/reorder {ids, base_sha}. Until then: local preview only.
  function persistOrder(ids) { return [...ids]; }

  function afterReorder() {
    renumber();
    syncControls();
    status.hidden = rows().every((r, i) => r === original[i]);
    persistOrder(currentIds());
  }

  function flash(row) {
    const card = row.querySelector('.bw-card');
    if (!card) return;
    card.classList.remove('bw-card--moved');
    void card.offsetWidth; // restart the animation if it is already running
    card.classList.add('bw-card--moved');
  }

  function move(r, kind) {
    if (kind === 'top') list.prepend(r);
    else if (kind === 'up') { const n = step(r, -1); if (n) n.before(r); }
    else { const n = step(r, 1); if (n) n.after(r); }
    afterReorder();
    flash(r);
  }

  list.addEventListener('animationend', e => {
    if (e.animationName === 'bw-moved') e.target.classList.remove('bw-card--moved');
  });

  viewButtons.forEach(button => {
    button.disabled = false;
    button.addEventListener('click', () => { view = button; applyView(); });
  });
  list.querySelectorAll('[data-move]').forEach(b => { b.disabled = false; });

  list.addEventListener('click', e => {
    const button = e.target.closest('[data-move]');
    if (!button || button.disabled) return;
    const row = button.closest('.bw-card-row');
    const kind = button.dataset.move;
    move(row, kind);
    let toFocus = row.querySelector('[data-move="' + kind + '"]');
    if (toFocus.disabled) toFocus = row.querySelector('[data-move]:not(:disabled)') || row;
    toFocus.focus();
    row.scrollIntoView({block: 'nearest'});
  });

  reset.addEventListener('click', () => {
    original.forEach(r => list.append(r));
    afterReorder();
    applyView();
    view.focus();
  });

  applyView();
})();
"""
