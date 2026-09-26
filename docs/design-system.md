---
title: "backlog.works Design System"
doc_type: design-system
status: active
updated: 2026-09-26
related: ["architecture.md", "../src/backlogworks/web/board_assets.py"]
---

# backlog.works design system

Foundations for the one board (`web.board`). Every class, token and state
the board uses is listed here. If it is not listed, it does not exist yet:
add it here first, then build it (see "Rules").

Version 1, 2026-09-26 (Product Owner instruction: robust foundations so no
component or primitive is invented twice; structure from the sibling
product's board, finish materially more vibrant, hover behaviour inspired
by Fizzy, which is under the O'Saasy licence and is therefore inspiration
only: no CSS, token values or class names copied). Authority: this page
for names and values; `src/backlogworks/web/board_assets.py` (or
`board_css.py`) for the shipped CSS. Parity is test-enforced (every
`--bw-*` token named here must exist in the CSS).

## 1. Principles

1. Phone first. Design at 390x844, then widen. Nothing needs a hover or
   a wide screen to be usable.
2. 44px hit targets for everything interactive, including icon buttons.
3. One accent (violet) for action and focus; three status hues
   (tangerine In Progress, lagoon Ready, fern Done); a small hue list
   for custom statuses. Nothing else carries colour.
4. Vibrant but legible: saturated mid-steps are for rails, dots and
   fills; text always uses the dark step of a ramp on its light step.
5. WCAG 2.2 AA: body text >= 4.5:1, large text and UI boundaries >= 3:1.
   Every text/background pair is listed in `contrast.md` receipts.
6. Motion is short (100/150ms) and optional: `prefers-reduced-motion`
   removes all transitions and animations.
7. Light first, dark ready: colours exist only as tokens, so a later dark
   block overrides tokens and nothing else. No dark block ships yet.
8. No external assets: system font stack, no web fonts, no images, icons
   as inline SVG or a text glyph. The strict CSP (inline style/script only)
   stays.
9. Works without JS: every primitive renders a usable resting state from
   server HTML; JS only adds state (pressed, moved, hidden).

## 2. Tokens

All colours are OKLCH with the sRGB hex fallback in a comment (for
review and contrast checks; browsers use the OKLCH value). Ramps use
steps 1-2 (tints), 5 (vivid), 7 (text). The CSS token block is delimited
by `/* tokens:start */` and `/* tokens:end */`; colour literals appear
only inside it.

```css
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
```

Tones. A tone class sets three local variables; `bw-pill` and `bw-card`
read only these, never a ramp directly:

| Class | `--bw-tone-2` / `-5` / `-7` from |
|---|---|
| `bw-tone-progress` | `--bw-progress-*` |
| `bw-tone-ready` | `--bw-ready-*` |
| `bw-tone-done` | `--bw-done-*` |
| `bw-tone-neutral` | `--bw-neutral-*` (default when no tone class) |
| `bw-tone-h1` .. `bw-tone-h4` | `--bw-h1-*` .. `--bw-h4-*` |
| `bw-tone-waiting` | `--bw-h2-*` (mustard) |

Custom statuses (any status other than `In Progress`, `Ready`, `Done`,
empty) get `bw-tone-h{n}` with `n = zlib.crc32(status.encode()) % 4 + 1`
(stable across renders and processes) plus `bw-pill--custom`.

Dark mode (not shipped): a later `@media (prefers-color-scheme: dark)`
block overrides only the colour tokens above (canvas/surface become dark
steps, ink and ramp step 7 become light steps, step 2 becomes a low
lightness tint). Primitives must not change for it.

## 3. Primitives

States apply in this order: default, hover (inside
`@media (any-hover: hover)` only), active, focus-visible (`outline:
var(--bw-focus-ring); outline-offset: var(--bw-focus-offset)`), disabled
(`[disabled]` or `aria-disabled="true"`: opacity .4, `cursor:
not-allowed`, no hover). State comes from ARIA or native attributes
(`aria-pressed`, `disabled`, `hidden`); the only state classes are
listed modifiers (`bw-card--moved`).

### bw-button
Pill-shaped action. `<button type="button">` or `<a>`.
- Base: `min-height: var(--bw-hit)`, padding 0 `--bw-space-4`, radius
  pill, `--bw-text-sm`, weight strong, inline-flex centered, gap
  `--bw-space-2`, transition background/filter/transform fast ease-out.
- `bw-button--primary`: bg accent-6, text on-accent (5.62:1). Hover
  `filter: brightness(.92)`. Active `transform: scale(.97)`.
- `bw-button--quiet`: bg transparent, text accent-7, 1px border line.
  Hover bg accent-1, border accent-2. Active bg accent-2.
- `bw-button--icon`: 44x44 square, padding 0, radius control, quiet
  colours; content is one inline SVG (20px, `stroke: currentColor`,
  `aria-hidden="true"`) or one text glyph; the button MUST carry
  `aria-label`. Hover bg accent-1, text accent-6.
- Size `bw-button--sm`: visual height 32px, `--bw-text-xs`; a `::after`
  at `inset: -6px` keeps the 44px hit area. Neighbours need >= 12px gap.
- May contain: a text label, optionally one icon. May not contain:
  pills, chips, links, more than one icon, block elements.

### bw-segmented
The view switch. `<div class="bw-segmented" role="group" aria-label>`
of `<button class="bw-segmented__option" aria-pressed>`.
- Container: grid `repeat(N,minmax(0,1fr))` (N = option count, 4 today),
  bg sunken, radius pill, padding 4px, gap 2px. On phones it is sticky:
  `position: sticky; top: calc(var(--bw-inset-top) + var(--bw-space-2));
  z-index: var(--bw-z-sticky)`, with `--bw-shadow-1`. Implemented as
  `grid-auto-flow: column` so the option count never has to reach the CSS.
- Option: min-height 44px, radius pill, `--bw-text-xs` strong, text
  ink-2 (8.1:1 on sunken). Hover (not pressed): text ink, bg
  `color-mix(in oklch, var(--bw-accent-2) 60%, var(--bw-sunken))`.
  Pressed (`aria-pressed="true"`): bg surface, text accent-7,
  `--bw-shadow-1`. Disabled (server render before JS): full opacity for the
  pressed option, others .6.
- May contain: 2-5 short text options. May not contain: icons alone,
  counts, links, nested groups.

### bw-pill
Status label. `<span class="bw-pill bw-tone-*">`.
- Radius pill, padding 2px 10px 2px 8px, `--bw-text-xs` strong, bg
  tone-2, text tone-7 (>= 5.8:1 for every tone). `::before` is an 8px dot
  in tone-5 (decorative, the vivid accent of the pill).
- `bw-pill--custom`: 1px dashed border in tone-7 (marks a non-standard
  status).
- No hover, not interactive. May contain: the status word only. May
  not contain: icons, buttons, notes.

### bw-chip
Neutral metadata (core job, sprint). `<span class="bw-chip">`.
- Radius pill, padding 2px 10px, `--bw-text-xs`, bg sunken, text ink-2.
- `bw-chip--sprint`: `font-variant-numeric: tabular-nums`, text
  accent-7, bg accent-1.
- Not interactive, never coloured by status. Wraps with
  `overflow-wrap: anywhere`.

### bw-card
One backlog item. `<div class="bw-card-row">` (grid: rank column 32px
phone / 40px from 640px, gap 12px) holding `bw-rank` and
`<article class="bw-card bw-tone-*">`.
- Rest: bg surface, radius card, padding `--bw-space-4`, border 1px
  transparent, `--bw-shadow-1`, plus a 4px status rail:
  `box-shadow: inset 4px 0 0 var(--bw-tone-5), var(--bw-shadow-1)`.
- Hover / `:focus-within`: bg `color-mix(in oklch, var(--bw-accent-6) 6%,
  var(--bw-surface))` (#f5f5ff), border accent-2, rail stays,
  `--bw-shadow-2`, `transform: translateY(-2px)`, `z-index: raised`.
  Transition transform/shadow base with ease-spring, colours fast.
  `:focus-within` has the same tint without the lift.
- `bw-card--moved` (added by JS after a reorder, removed on
  `animationend`): keyframes `bw-moved` from bg flash plus
  `0 0 0 2px var(--bw-accent-6)` to rest, over `--bw-flash-duration`
  ease-out.
- Parts: `bw-card__title` (h2, `--bw-text-md`, strong, leading tight),
  `bw-card__id` (accent-7, tabular nums), `bw-card__meta` (flex wrap,
  gap 6px: pill, chips), `bw-card__waiting` (`--bw-text-xs`, ink-2, a
  `bw-pill bw-tone-waiting` then text), `bw-card__context` (sm, ink-3),
  then optional `bw-controls` last.
- May contain: exactly those parts in that order. May not contain: a
  second heading, links other than inside context text, primary buttons.
- The list container is `bw-card-list` (`#cards`): block, no padding; it
  carries no visual style of its own.

### bw-rank
Priority number. `<span class="bw-rank" aria-label="Priority N">`.
- 32px circle (40px from 640px), radius pill, bg accent-1, 1px border
  accent-2, text accent-7 (7.3:1), `--bw-text-xs` strong, tabular nums,
  aligned to the card title (margin-top 12px). Not interactive.

### bw-controls
Reorder tools inside a card: `<div class="bw-controls" role="group"
aria-label="...">` of `bw-button bw-button--icon` (Move up, Move down,
Move to top), in that order.
- Flex, gap `--bw-space-2`, margin-top `--bw-space-3`, top border 1px
  line with padding-top `--bw-space-3`, justify end.
- Disabled buttons (first item cannot move up) use the disabled state;
  they stay in place so the layout does not shift.
- May contain: 1-4 icon buttons. May not contain: text buttons, selects,
  pills.

### bw-notice
One status line with an optional action (e.g. "Order changed locally"
plus Reset; also the no-JS message and format notes).
`<div class="bw-notice" role="status">`.
- Flex, align center, gap `--bw-space-3`, padding `--bw-space-3`
  `--bw-space-4`, radius card, bg accent-1, 1px border accent-2, text
  ink, `--bw-text-sm`. The action is `bw-button bw-button--quiet
  bw-button--sm`, pushed right (`margin-left: auto`).
- `bw-notice--warn`: bg h2-2, border h2-5, strong label text h2-7.
- May contain: one sentence or one strong label plus one list (format
  notes only), and at most one action button. May not contain: links
  and a button together, headings, more than one action.

### bw-empty
"Nothing in this view." `<p class="bw-empty">`.
- Padding `--bw-space-8` `--bw-space-4`, text centered ink-3, bg
  surface, 1px dashed line-strong, radius card.
- May contain: one sentence, optionally one quiet button. No
  illustrations.

### bw-masthead
Board header. `<header class="bw-masthead">`.
- Parts in order: `bw-masthead__eyebrow` (repo, `--bw-text-xs` strong,
  letter-spacing .08em, accent-7), `h1` (no class; `--bw-text-xl`,
  leading tight, ink, letter-spacing -.02em), `bw-masthead__description`
  (sm, ink-2), `bw-masthead__source` (xs, ink-3, flex wrap; its link is
  accent-7 with underline offset 3px, hover accent-6),
  `bw-masthead__subtitle` (xs, ink-3). Empty parts are `display:none`.
- May not contain: buttons, pills, the view switch.

### bw-prose
Trusted chrome prose above the board (landing pitch). Headings
`--bw-text-lg`, text xs-sm ink-2, lists indented 20px, bottom border 1px
line. May not contain: controls.

Base layer (element selectors, no classes): `*` box-sizing, `[hidden]`,
`body` (canvas, ink, `--bw-font`, sm, leading), `main` (max page width,
padding with safe-area insets), `a`, `button` font inherit, `code`
(sunken, radius control/2, mono .92em), `footer` (xs, ink-3),
`:focus-visible`.

## 4. Rules

1. Add a component here first (name, parts, states, may / may not
   contain), then in the CSS, in the same commit. Reuse beats variants;
   variants beat new components.
2. No one-off colours: outside the token block the CSS has no hex, `rgb(`,
   `hsl(` or `oklch(` literal; only `var(--bw-*)` and `color-mix()` over
   tokens. A test enforces this.
3. No inline `style` attributes and no `<style>` other than the one
   board stylesheet. Colour is never set from Python except by choosing a
   `bw-tone-*` class.
4. Naming: `bw-<block>`, `bw-<block>__<part>`, `bw-<block>--<variant>`,
   `bw-tone-<name>`. Tokens `--bw-<group>-<step>`. No id selectors in
   CSS; ids and `data-*` belong to tests and JS.
5. Every interactive element: 44px hit area, visible focus ring, hover
   only under `any-hover`, a disabled state, an accessible name.
6. CSS lives in `src/backlogworks/web/board_assets.py` (`CSS`) until a
   single file would pass 400 lines, then `web/board_css.py`; a
   `web/assets/` split waits until a second page needs it.
7. Verify every visual change with:
   - screenshots at 390x844 (phone) and 1280x800, no horizontal overflow;
   - a hover capture of one card at 1280;
   - a `contrast.md` table computed from the shipped tokens: every text
     pair >= 4.5, focus ring and control borders >= 3 against the
     background they sit on;
   - `scripts/check.sh` green, with JS disabled still showing the All view.

## 5. Deviation from the reference structure

The structure the Product Owner knows is kept: masthead, segmented view
switch, rank badge, card, pills, chips. The finish changes:
- Grey on grey became a faintly violet canvas with white cards and one
  vivid violet accent; status pills went from pale, near-identical tints
  to three clearly different hues (tangerine, lagoon, fern), each with a
  vivid dot.
- Cards gained a 4px status rail, so status reads from colour at a
  glance while scrolling on a phone; the pill still carries the word.
- Hover is now visible: cards lift 2px, take a 6% accent tint and a
  violet shadow; buttons shift brightness. Touch devices never see a
  stuck hover.
- Rank badges, sprint chips and ids use the accent, so priority reads
  first. Reorders flash the moved card instead of jumping silently.
- Controls are pill-shaped and at least 44px; the view switch stays
  visible (sticky) on phones.
