You are designing a **dark-first, high-data-intensity developer frontage** for `fair-value` — a valuation MCP server + REST API for Ascent Partners Group (Hong Kong). It is NOT the corporate marketing site; it is a technical documentation + API product surface. Think "Bloomberg terminal meets a modern API docs site".

## Design tokens (CANONICAL — never invent values outside this list)

Sourced from ascent-partners.com. Dark surfaces use the neutral ramp; brand accents use the primary (teal) and secondary (gold) ramps.

```
Primary (teal) ramp:
  primary-50 #caffff  100 #baf4ff  200 #a2e5ff  300 #80cdea  400 #53adcd
  primary-500 #2a8eaf 600 #007a9a  700 #00607b  800 #004f67  900 #004055  950 #002432
Secondary (gold) ramp:
  50 #fff4b6  100 #ffe8a4  200 #f3d78a  300 #dfb947  400 #bf9b2a  500 #a17d00
  600 #896700 700 #705200  800 #5d4200  900 #4c3500  950 #2c1c00
Neutral ramp:
  50 #f5f5f5  100 #eaeaea  200 #d9d9d9  300 #c0c0c0  400 #9f9f9f  500 #828282
  600 #6c6c6c 700 #575757  800 #464646  900 #373737  950 #1f1f1f
Brand anchors: teal #007a9a (primary-600), tealDark #006987, gold #dfb947
```

Dark theme mapping (default):
```
page background     neutral-950 (#1f1f1f)          deep, near-black
raised surface      neutral-900 (#373737)
borders/dividers    neutral-800 (#464646)
default text        neutral-50  (#f5f5f5)
secondary text      neutral-400 (#9f9f9f)
accent text/links   primary-300 (#80cdea) / primary-400 (#53adcd)
accent fills        primary-600 (#007a9a)
highlight / badge   secondary-300 (#dfb947)
```
Light theme is a mirror (bg #ffffff, text #1f1f1f, borders #eaeaea, accents unchanged). Dark is the DEFAULT; include a sun/moon toggle.

## Typography
- Body: **Open Sans** 300/400/600
- Headings: **Titillium Web** 400/600/700
- Accent/eyebrow: **Raleway**
- Data / code: a monospace (JetBrains Mono / ui-monospace), tabular numerals for all figures
- Scale: h1 30–44px, h2 22–26px, body 14px, micro 12–12.5px, mono 12–12.5px

## High data intensity (the point of this surface)
- Dense tables: compact row height, hairline dividers, tabular numbers, right-aligned numerics, sticky headers, hover row highlight.
- Code panels with a labelled header bar (language/filename) and a copy button.
- Badges/chips for standards clauses (`IVS.103.A20` teal, `IFRS.13.62` gold), approach, solution_type.
- Inline monospace JSON data viewers (scrollable, thin dark scrollbars).
- Stat strips: big tabular numbers with small uppercase labels.
- Search + filter controls (by tool, approach, clause) on the catalogue.
- A split "request / response" playground: generated input form on the left, envelope + citations on the right.

## Layout & components
- Site max-width ~1180px; generous but efficient spacing; sticky top nav (48–56px) with a mono wordmark chip.
- Docs layout: left sidebar (≈220px) with grouped links + active state, content column max ~760px.
- Rectangular corners (radius 4–6px max). No pill buttons. No gradients. 1px hairline borders define structure.
- Every container uses flex/grid (never bare block flow); do not use space-y-* — use flex flex-col gap-*.
- Cards: neutral-900 surface, 1px neutral-800 border, no heavy shadow.
- Links: primary-300 on dark, underline on hover. Focus ring: 2px primary-500.

## Banned
- No shadcn/ui component library — custom Tailwind only.
- No invented colours outside the ramps above.
- No gradients, no heavy drop shadows, no rounded-pill buttons.
- No emoji in the UI.

## What to design (this task)
A single responsive page set, cohesive:
1. **Landing** — compact hero ("Valuation, as a governed API"), one-line value prop, four stat figures (138 methods · 16 tools · 120 cited · 27 clauses), a live status chip, endpoint list (/mcp, /v1/calculate/{tool}, /v1/methods, /v1/standards), a capability grid (6 cards), a two-column quickstart (curl + Python code panels), and a 16-tool coverage grid.
2. **Methods catalogue** — dense searchable table: method (mono link) · tool · approach · solution_type · clause badges; filters above.
3. **Docs shell** — sidebar + content with code blocks and clause cards.

Target: 1440px desktop reference; also correct at 390px mobile. This is a technical product surface for developers/financial analysts — restrained, precise, dense, trustworthy.
