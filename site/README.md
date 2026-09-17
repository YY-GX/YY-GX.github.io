# new-site — multi-page, laid out like shikun.io

## Run

```bash
cd new-site
python3 -m http.server 8000     # http://localhost:8000/
```

Static HTML. No build step, no npm.

## Regenerate after a content change

```bash
python3 build.py
```

Reads the live site's own content — `site.config.yml`, `about.md`,
`news/*.md`, `papers.bib`, `blog/*.mdx` — and rewrites every page. Adding a
paper stays five lines of BibTeX plus this one command.

## Why this exists

`clarity-direct/` is the Clarity template used verbatim, and it is one page,
because **Clarity is a single-page project-page template** — it ships no
navigation at all. shikun.io is *not* built with it: his site loads his own
`shikun.css`, uses classes (`home-container`, `home-intro`, `home-profile`)
that do not exist in the template, and injects a nav via jQuery. So matching
his site means building the parts he never released.

## What's borrowed vs. written

| | Source |
|---|---|
| Reset, typography, `.button`/`.icon`, tables, `.container` padding ladder, Charter | Clarity template (CC0), **unmodified** |
| Nav bar + sliding dot, split home hero, paper rows, news rows | `assets/site.css` — ours, ~260 lines |

`assets/site.css` was written from *measurements* of the rendered shikun.io
(nav `1.5em` padding, links `24px/500`, the dot `8px` `#ff9800` animated on
`left`, hero `1fr 1fr` at ≥769px with 5–10vw gap). His stylesheet was not
copied: the Clarity template is CC0, his personal site's CSS is not offered
for reuse.

Two deliberate deviations, both documented in `site.css`:
- His nav font is **Athletics** (proprietary). Poppins here — the face Clarity
  itself ships.
- His `.menu` uses `space-between` in a 2fr column with a 25vw gap, which suits
  his four short labels. Our five wider ones ("Publications", "Résumé") exactly
  filled the column and ran together, so the menu uses an explicit `2.4em` gap.

## Pages

| File | Content |
|---|---|
| `index.html` | Split hero — Hello, intro, Read More, portrait. Locked to one viewport |
| `about.html` | Full bio + all 8 news items |
| `publications.html` | All 16, grouped by year, your name bold, thumbnails |
| `blog.html` + `post-*.html` | Published posts only |
| `cv.pdf` | Linked as "Résumé" in the nav, exactly as Shikun does |

## Notes

- **Drafts stay unpublished.** 4 of your 5 posts are `draft: true`; the
  generator skips them, so only `getting_started` builds a page.
- **Missing figures.** 5 of 16 entries have no preview image on disk
  (including `lilo26.png` / `vision26.png`). Those rows keep the empty
  thumbnail track so every title stays on one vertical line. Drop the PNGs into
  `images/publications/` and re-run `build.py`.
- **Blog and Résumé are hidden** from the nav for now. `blog.html` and
  `post-*.html` are still generated and reachable by URL, and `cv.pdf` is still
  in the folder — add the tuples back to the `NAV` list in `build.py` to show
  them again.
- **The home page never scrolls** on desktop (>=769px): it is locked to exactly
  one viewport, with the hero vertically centred and the footer sitting inside
  it. Below 769px it scrolls normally, because a stacked hero plus a portrait
  cannot fit one phone screen without shrinking the photo to nothing.

## Not wired to anything

No deploy, no CI. Your live site is untouched; this folder is git-ignored via
`.git/info/exclude`. `rm -rf new-site` removes it.

## Appearance pass (latest)

- Home locked to one viewport; hero vertically centred; footer inside the fold.
- Nav trimmed to Home / Publications / About; links use a muted ink that goes
  solid on hover and when active; social icons lift slightly on hover.
- Publication rows: year labels are small tracked uppercase over a rule,
  thumbnails are 4:3 `object-fit: cover` with a hairline and 3px radius,
  authors muted with your name in solid ink, venue italic and quieter, PDF
  button reduced to a small chip.
- News rows: fixed 150px date column on desktop, stacked on mobile.
- Prose: paragraph spacing restored (Clarity's `p.text` ships with no margin,
  so paragraphs ran together), measure capped at 46em.
- Links in prose are underlined in a muted rule colour that darkens on hover
  rather than being coloured.
- Focus-visible rings in the accent colour; `::selection` in the accent;
  `prefers-reduced-motion` honoured.
- Mobile menu: solid panel (it was transparent, so page text showed through the
  links), animated X, and the icon font fixed — the panel's Poppins rule was
  outranking FontAwesome and rendering every icon as a tofu box.
