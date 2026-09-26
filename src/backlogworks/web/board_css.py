# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""Board stylesheet: tokens (docs/design-system.md section 2) plus every
primitive (section 3), in doc order. Split out of board_assets.py once the
sheet passed 400 lines (docs/design-system.md rule 4.6). No colour literal
appears outside the tokens:start/tokens:end block; every other rule reads a
--bw-* variable or color-mix() over one."""

CSS = """
/* tokens:start */
:root {
  color-scheme: light;
  /* Surfaces and ink (hue 285, faint violet cast) */
  --bw-canvas:      oklch(98.5% 0.005 285); /* #fafafd */
  --bw-surface:     oklch(100% 0 0);        /* #ffffff */
  --bw-sunken:      oklch(95.5% 0.012 285); /* #efeff8 */
  --bw-ink:         oklch(23% 0.035 285);   /* #1b1a2d */
  --bw-ink-2:       oklch(40% 0.03 285);    /* #464658 */
  --bw-ink-3:       oklch(51% 0.025 285);   /* #646474 */
  --bw-line:        oklch(90.5% 0.014 285); /* #dedfe9 */
  --bw-line-strong: oklch(64% 0.02 285);    /* #8a8b98 */

  /* Accent: violet */
  --bw-accent-1: oklch(97.5% 0.012 285); /* #f6f6ff */
  --bw-accent-2: oklch(94% 0.028 285);   /* #e9e9fe */
  --bw-accent-6: oklch(54% 0.235 285);   /* #6a47ee */
  --bw-accent-7: oklch(46% 0.215 285);   /* #5532c7 */
  --bw-on-accent: var(--bw-surface);

  /* Status: In Progress = tangerine */
  --bw-progress-2: oklch(93.5% 0.045 70); /* #fee5ca */
  --bw-progress-5: oklch(72% 0.17 55);    /* #f3821d */
  --bw-progress-7: oklch(47% 0.13 45);    /* #933d08 */
  /* Status: Ready = lagoon */
  --bw-ready-2: oklch(93.5% 0.04 215);    /* #ccf1fa */
  --bw-ready-5: oklch(70% 0.12 215);      /* #18b1cd */
  --bw-ready-7: oklch(46% 0.085 225);     /* #07617c */
  /* Status: Done = fern */
  --bw-done-2: oklch(94% 0.05 150);       /* #d5f5da */
  --bw-done-5: oklch(70% 0.15 150);       /* #4cb86a */
  --bw-done-7: oklch(45% 0.12 150);       /* #09672e */
  /* Neutral: ordinary items (empty status) */
  --bw-neutral-2: oklch(94% 0.008 285);   /* #eaeaf0 */
  --bw-neutral-5: oklch(64% 0.02 285);    /* #8a8b98 */
  --bw-neutral-7: oklch(45% 0.02 285);    /* #545460 */
  /* Custom-status hue list (index = crc32(status) % 4 + 1) */
  --bw-h1-2: oklch(94% 0.035 350);  /* #ffe2ee  berry   */
  --bw-h1-5: oklch(68% 0.19 350);   /* #ea5da9 */
  --bw-h1-7: oklch(47% 0.17 350);   /* #9a2068 */
  --bw-h2-2: oklch(94% 0.06 100);   /* #f4edbf  mustard */
  --bw-h2-5: oklch(78% 0.15 95);    /* #d6b529 */
  --bw-h2-7: oklch(46% 0.095 95);   /* #695700 */
  --bw-h3-2: oklch(94% 0.027 255);  /* #dfedfe  cobalt  */
  --bw-h3-5: oklch(64% 0.16 255);   /* #408dea */
  --bw-h3-7: oklch(46% 0.14 255);   /* #1157a4 */
  --bw-h4-2: oklch(94% 0.03 20);    /* #ffe4e3  brick   */
  --bw-h4-5: oklch(66% 0.19 25);    /* #f05653 */
  --bw-h4-7: oklch(47% 0.16 20);    /* #a12433 */
  /* Moved-flash highlight */
  --bw-flash: oklch(96% 0.05 100);  /* #f9f3cd */

  /* Type: system stack only */
  --bw-font: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --bw-font-mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  --bw-text-xs: 13px;   /* meta, pills, chips, segmented, footer */
  --bw-text-sm: 15px;   /* body, context, buttons */
  --bw-text-md: 17px;   /* card title */
  --bw-text-lg: 20px;   /* section/prose heading */
  --bw-text-xl: 28px;   /* masthead h1 */
  --bw-leading: 1.5;
  --bw-leading-tight: 1.25;
  --bw-weight-strong: 650;

  /* Spacing: 4px base */
  --bw-space-1: 4px;  --bw-space-2: 8px;  --bw-space-3: 12px;
  --bw-space-4: 16px; --bw-space-6: 24px; --bw-space-8: 32px;
  --bw-space-10: 40px;

  /* Radius */
  --bw-radius-control: 8px;   /* icon buttons, inputs, code (half) */
  --bw-radius-card: 12px;     /* card, notice, empty */
  --bw-radius-pill: 999px;    /* buttons, segmented, pills, chips, rank */

  /* Shadow: layered, low */
  --bw-shadow-1: 0 0 0 1px oklch(23% 0.035 285 / 7%),  /* #1b1a2d12 */
                 0 1px 2px oklch(23% 0.035 285 / 6%);  /* #1b1a2d0f */
  --bw-shadow-2: 0 0 0 1px oklch(54% 0.235 285 / 22%), /* #6a47ee38 */
                 0 2px 4px oklch(23% 0.035 285 / 6%),  /* #1b1a2d0f */
                 0 10px 20px -6px oklch(54% 0.235 285 / 22%); /* #6a47ee38 */

  /* Motion */
  --bw-duration-fast: 100ms;  /* colour, brightness */
  --bw-duration-base: 150ms;  /* lift, shadow, pressed */
  --bw-ease-out: cubic-bezier(0.2, 0.8, 0.2, 1);
  --bw-ease-spring: cubic-bezier(0.3, 1.4, 0.6, 1); /* small overshoot, lift only */
  --bw-flash-duration: calc(var(--bw-duration-base) * 6); /* 900ms */

  /* Focus */
  --bw-focus-width: 3px;
  --bw-focus-offset: 2px;
  --bw-focus-color: var(--bw-accent-6);
  --bw-focus-ring: var(--bw-focus-width) solid var(--bw-focus-color);

  /* Layout and safe areas */
  --bw-hit: 44px;
  --bw-page-max: 960px;
  --bw-inset-top: env(safe-area-inset-top, 0px);
  --bw-inset-right: env(safe-area-inset-right, 0px);
  --bw-inset-bottom: env(safe-area-inset-bottom, 0px);
  --bw-inset-left: env(safe-area-inset-left, 0px);

  /* Z-index (only these values) */
  --bw-z-base: 0;
  --bw-z-raised: 1;    /* hovered / flashing card */
  --bw-z-sticky: 10;   /* sticky segmented view switch */
  --bw-z-notice: 20;   /* notice pinned above cards */
  --bw-z-toast: 30;    /* reserved */
}
/* tokens:end */

/* Tones: bw-card and bw-pill read only --bw-tone-*, never a ramp directly. */
.bw-tone-progress { --bw-tone-2: var(--bw-progress-2); --bw-tone-5: var(--bw-progress-5); --bw-tone-7: var(--bw-progress-7); }
.bw-tone-ready    { --bw-tone-2: var(--bw-ready-2);    --bw-tone-5: var(--bw-ready-5);    --bw-tone-7: var(--bw-ready-7); }
.bw-tone-done     { --bw-tone-2: var(--bw-done-2);     --bw-tone-5: var(--bw-done-5);     --bw-tone-7: var(--bw-done-7); }
.bw-tone-neutral  { --bw-tone-2: var(--bw-neutral-2);  --bw-tone-5: var(--bw-neutral-5);  --bw-tone-7: var(--bw-neutral-7); }
.bw-tone-h1       { --bw-tone-2: var(--bw-h1-2);       --bw-tone-5: var(--bw-h1-5);       --bw-tone-7: var(--bw-h1-7); }
.bw-tone-h2       { --bw-tone-2: var(--bw-h2-2);       --bw-tone-5: var(--bw-h2-5);       --bw-tone-7: var(--bw-h2-7); }
.bw-tone-h3       { --bw-tone-2: var(--bw-h3-2);       --bw-tone-5: var(--bw-h3-5);       --bw-tone-7: var(--bw-h3-7); }
.bw-tone-h4       { --bw-tone-2: var(--bw-h4-2);       --bw-tone-5: var(--bw-h4-5);       --bw-tone-7: var(--bw-h4-7); }
.bw-tone-waiting  { --bw-tone-2: var(--bw-h2-2);       --bw-tone-5: var(--bw-h2-5);       --bw-tone-7: var(--bw-h2-7); }

/* Base layer: element selectors, no classes. */
* { box-sizing: border-box; }
[hidden] { display: none !important; }
body {
  margin: 0; background: var(--bw-canvas); color: var(--bw-ink);
  font-family: var(--bw-font); font-size: var(--bw-text-sm); line-height: var(--bw-leading);
}
main {
  max-width: var(--bw-page-max); margin: 0 auto;
  padding: calc(var(--bw-space-6) + var(--bw-inset-top)) calc(var(--bw-space-4) + var(--bw-inset-right))
           calc(var(--bw-space-6) + var(--bw-inset-bottom)) calc(var(--bw-space-4) + var(--bw-inset-left));
}
a, button { font: inherit; }
code {
  background: var(--bw-sunken); border-radius: calc(var(--bw-radius-control) / 2);
  padding: 0 3px; font-family: var(--bw-font-mono); font-size: .92em; overflow-wrap: anywhere;
}
footer {
  max-width: var(--bw-page-max); margin: 0 auto;
  padding: 0 calc(var(--bw-space-4) + var(--bw-inset-right)) calc(var(--bw-space-8) + var(--bw-inset-bottom))
           calc(var(--bw-space-4) + var(--bw-inset-left));
  font-size: var(--bw-text-xs); color: var(--bw-ink-3);
}
:focus-visible { outline: var(--bw-focus-ring); outline-offset: var(--bw-focus-offset); }

/* bw-button */
.bw-button {
  display: inline-flex; align-items: center; justify-content: center; gap: var(--bw-space-2);
  min-height: var(--bw-hit); padding: 0 var(--bw-space-4); border-radius: var(--bw-radius-pill);
  font-size: var(--bw-text-sm); font-weight: var(--bw-weight-strong); border: 0; background: none; color: inherit;
  transition: background-color var(--bw-duration-fast) var(--bw-ease-out),
              filter var(--bw-duration-fast) var(--bw-ease-out),
              transform var(--bw-duration-base) var(--bw-ease-out);
}
.bw-button--primary { background: var(--bw-accent-6); color: var(--bw-on-accent); }
@media (any-hover: hover) {
  .bw-button--primary:hover:not([disabled]):not([aria-disabled="true"]) { filter: brightness(.92); }
}
.bw-button--primary:active:not([disabled]):not([aria-disabled="true"]) { transform: scale(.97); }
.bw-button--quiet { background: transparent; color: var(--bw-accent-7); border: 1px solid var(--bw-line); }
@media (any-hover: hover) {
  .bw-button--quiet:hover:not([disabled]):not([aria-disabled="true"]) { background: var(--bw-accent-1); border-color: var(--bw-accent-2); }
}
.bw-button--quiet:active:not([disabled]):not([aria-disabled="true"]) { background: var(--bw-accent-2); }
.bw-button--icon {
  width: var(--bw-hit); height: var(--bw-hit); padding: 0; border-radius: var(--bw-radius-control);
  background: transparent; color: var(--bw-accent-7); border: 1px solid var(--bw-line);
}
@media (any-hover: hover) {
  .bw-button--icon:hover:not([disabled]):not([aria-disabled="true"]) { background: var(--bw-accent-1); color: var(--bw-accent-6); }
}
.bw-button--sm { position: relative; min-height: 32px; height: 32px; padding: 0 var(--bw-space-3); font-size: var(--bw-text-xs); }
.bw-button--sm::after { content: ""; position: absolute; inset: -6px; }
.bw-button[disabled], .bw-button[aria-disabled="true"] { opacity: .4; cursor: not-allowed; }

/* bw-segmented: grid-auto-flow keeps every option in one row regardless of
   count, with no Python-supplied option count and no inline style (CSP);
   past 5 options (< 72px/track) the container scrolls horizontally instead
   of shrinking tracks further. */
.bw-segmented {
  display: grid; grid-auto-flow: column; grid-auto-columns: minmax(72px, 1fr); gap: 2px;
  background: var(--bw-sunken); border-radius: var(--bw-radius-pill); padding: 4px;
  overflow-x: auto;
}
@media (max-width: 639px) {
  .bw-segmented {
    position: sticky; top: calc(var(--bw-inset-top) + var(--bw-space-2));
    z-index: var(--bw-z-sticky); box-shadow: var(--bw-shadow-1);
  }
}
.bw-segmented__option {
  min-height: var(--bw-hit); min-width: 0; border-radius: var(--bw-radius-pill); font-size: var(--bw-text-xs);
  font-weight: var(--bw-weight-strong); color: var(--bw-ink-2); background: transparent;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 0 var(--bw-space-1);
  transition: background-color var(--bw-duration-fast) var(--bw-ease-out), color var(--bw-duration-fast) var(--bw-ease-out);
}
.bw-segmented__option[disabled]:not([aria-pressed="true"]),
.bw-segmented__option[aria-disabled="true"]:not([aria-pressed="true"]) { opacity: .6; }
.bw-segmented__option[aria-pressed="true"] {
  background: var(--bw-surface); color: var(--bw-accent-7); box-shadow: var(--bw-shadow-1); opacity: 1;
}
@media (any-hover: hover) {
  .bw-segmented__option:not([aria-pressed="true"]):not([disabled]):not([aria-disabled="true"]):hover {
    color: var(--bw-ink); background: color-mix(in oklch, var(--bw-accent-2) 60%, var(--bw-sunken));
  }
}

/* bw-pill */
.bw-pill {
  display: inline-flex; align-items: center; gap: 4px; padding: 2px 10px 2px 8px;
  border-radius: var(--bw-radius-pill); font-size: var(--bw-text-xs); font-weight: var(--bw-weight-strong);
  background: var(--bw-tone-2); color: var(--bw-tone-7);
}
.bw-pill::before { content: ""; width: 8px; height: 8px; border-radius: 50%; background: var(--bw-tone-5); }
.bw-pill--custom { border: 1px dashed var(--bw-tone-7); }

/* bw-chip */
.bw-chip {
  display: inline-flex; align-items: center; padding: 2px 10px; border-radius: var(--bw-radius-pill);
  font-size: var(--bw-text-xs); background: var(--bw-sunken); color: var(--bw-ink-2); overflow-wrap: anywhere;
}
.bw-chip--sprint { font-variant-numeric: tabular-nums; color: var(--bw-accent-7); background: var(--bw-accent-1); }

/* bw-card, bw-rank, bw-controls */
.bw-card-list { margin-top: var(--bw-space-6); }
.bw-card-row { display: grid; grid-template-columns: 32px minmax(0, 1fr); gap: var(--bw-space-3); margin: 0 0 var(--bw-space-3); }
@media (min-width: 640px) { .bw-card-row { grid-template-columns: 40px minmax(0, 1fr); } }
.bw-rank {
  display: flex; align-items: center; justify-content: center; width: 32px; height: 32px; margin-top: 12px;
  border-radius: var(--bw-radius-pill); background: var(--bw-accent-1); border: 1px solid var(--bw-accent-2);
  color: var(--bw-accent-7); font-size: var(--bw-text-xs); font-weight: var(--bw-weight-strong); font-variant-numeric: tabular-nums;
}
@media (min-width: 640px) { .bw-rank { width: 40px; height: 40px; } }
.bw-card {
  position: relative; background: var(--bw-surface); border-radius: var(--bw-radius-card); padding: var(--bw-space-4);
  border: 1px solid transparent; min-width: 0; overflow-wrap: anywhere;
  box-shadow: inset 4px 0 0 var(--bw-tone-5), var(--bw-shadow-1);
  transition: background-color var(--bw-duration-fast) var(--bw-ease-out),
              border-color var(--bw-duration-fast) var(--bw-ease-out),
              box-shadow var(--bw-duration-base) var(--bw-ease-spring),
              transform var(--bw-duration-base) var(--bw-ease-spring);
}
@media (any-hover: hover) {
  .bw-card:hover {
    background: color-mix(in oklch, var(--bw-accent-6) 6%, var(--bw-surface));
    border-color: var(--bw-accent-2); box-shadow: inset 4px 0 0 var(--bw-tone-5), var(--bw-shadow-2);
    transform: translateY(-2px); z-index: var(--bw-z-raised);
  }
}
.bw-card:focus-within {
  background: color-mix(in oklch, var(--bw-accent-6) 6%, var(--bw-surface));
  border-color: var(--bw-accent-2); box-shadow: inset 4px 0 0 var(--bw-tone-5), var(--bw-shadow-2);
  z-index: var(--bw-z-raised);
}
.bw-card--moved { animation: bw-moved var(--bw-flash-duration) var(--bw-ease-out); }
@keyframes bw-moved {
  from { background: var(--bw-flash); box-shadow: 0 0 0 2px var(--bw-accent-6); }
  to { background: var(--bw-surface); box-shadow: inset 4px 0 0 var(--bw-tone-5), var(--bw-shadow-1); }
}
.bw-card__title { margin: 0 0 var(--bw-space-2); font-size: var(--bw-text-md); font-weight: var(--bw-weight-strong); line-height: var(--bw-leading-tight); }
.bw-card__id { color: var(--bw-accent-7); font-variant-numeric: tabular-nums; }
.bw-card__meta { display: flex; align-items: center; flex-wrap: wrap; gap: 6px; margin-bottom: var(--bw-space-2); }
.bw-card__waiting { margin: 0 0 var(--bw-space-2); font-size: var(--bw-text-xs); color: var(--bw-ink-2); }
.bw-card__context { margin: 0; font-size: var(--bw-text-sm); color: var(--bw-ink-3); }
.bw-controls {
  display: flex; justify-content: flex-end; gap: var(--bw-space-2); margin-top: var(--bw-space-3);
  padding-top: var(--bw-space-3); border-top: 1px solid var(--bw-line);
}

/* bw-notice */
.bw-notice {
  display: flex; align-items: center; gap: var(--bw-space-3); padding: var(--bw-space-3) var(--bw-space-4);
  border-radius: var(--bw-radius-card); background: var(--bw-accent-1); border: 1px solid var(--bw-accent-2);
  color: var(--bw-ink); font-size: var(--bw-text-sm);
}
.bw-notice p { margin: 0; }
.bw-notice .bw-button { margin-left: auto; }
.bw-notice--warn { background: var(--bw-h2-2); border-color: var(--bw-h2-5); }
.bw-notice--warn strong { color: var(--bw-h2-7); }
.bw-notice--warn ul { margin: var(--bw-space-2) 0 0; padding-left: 20px; }
@media (max-width: 639px) {
  .bw-notice--warn { flex-direction: column; align-items: flex-start; }
}

/* bw-empty */
.bw-empty {
  margin: var(--bw-space-4) 0 0; padding: var(--bw-space-8) var(--bw-space-4); text-align: center;
  color: var(--bw-ink-3); background: var(--bw-surface); border: 1px dashed var(--bw-line-strong);
  border-radius: var(--bw-radius-card);
}

/* bw-masthead */
.bw-masthead { margin: var(--bw-space-6) 0; overflow-wrap: anywhere; }
.bw-masthead__eyebrow {
  margin: 0 0 var(--bw-space-2); font-size: var(--bw-text-xs); font-weight: var(--bw-weight-strong);
  letter-spacing: .08em; color: var(--bw-accent-7);
}
.bw-masthead h1 { margin: 0 0 var(--bw-space-3); font-size: var(--bw-text-xl); line-height: var(--bw-leading-tight); letter-spacing: -.02em; color: var(--bw-ink); }
.bw-masthead__description { margin: 0 0 var(--bw-space-3); font-size: var(--bw-text-sm); color: var(--bw-ink-2); }
.bw-masthead__description:empty { display: none; }
.bw-masthead__source { display: flex; flex-wrap: wrap; gap: 6px 20px; font-size: var(--bw-text-xs); color: var(--bw-ink-3); }
.bw-masthead__source a {
  display: inline-flex; align-items: center; min-height: var(--bw-hit);
  color: var(--bw-accent-7); text-decoration: underline; text-underline-offset: 3px;
}
@media (any-hover: hover) { .bw-masthead__source a:hover { color: var(--bw-accent-6); } }
.bw-masthead__subtitle { margin: var(--bw-space-2) 0 0; font-size: var(--bw-text-xs); color: var(--bw-ink-3); }
.bw-masthead__subtitle:empty { display: none; }

/* bw-prose */
.bw-prose { padding-bottom: var(--bw-space-6); border-bottom: 1px solid var(--bw-line); font-size: var(--bw-text-sm); color: var(--bw-ink-2); }
.bw-prose h2 { font-size: var(--bw-text-lg); color: var(--bw-ink); margin: 0 0 var(--bw-space-2); }
.bw-prose p { margin: var(--bw-space-2) 0; }
.bw-prose ul { margin: var(--bw-space-2) 0; padding-left: 20px; }

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; scroll-behavior: auto !important; }
}
"""
