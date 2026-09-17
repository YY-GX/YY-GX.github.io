# Yue Yang — Personal Website

Static site published at https://yy-gx.github.io

## Structure

```
site.config.yml        profile, social links, analytics id
src/content/           the content: about.md, news/, publications/papers.bib, blog/
site/                  the published site
  build.py             generator: reads the content above, writes the HTML
  assets/ clarity/     Clarity template (CC0), unmodified
  assets/site.css      the parts Clarity does not ship (nav, hero, paper rows)
  images/              figures, with high-resolution copies under images/full/
```

## Editing

Change content in `src/content/` or `site.config.yml`, then:

```bash
cd site
python3 build.py
python3 -m http.server 8000   # http://localhost:8000/
```

Adding a paper is five lines of BibTeX in `src/content/publications/papers.bib`
plus one `build.py` run. Optional fields per entry: `pdf`, `website`, `code`,
`dataset`, `preview` (figure filename), `blurb` (shown under the enlarged
figure), `equal` (comma-separated co-first authors), `selected`.

Home page copy (name, pronunciation, research line) lives in a marked block at
the top of `site/build.py`.

## Deploying

Pushing to `main` runs `site/build.py` in CI and publishes `site/`. Nothing to
install; the generator is plain Python with no dependencies.

## History

The previous Astro version is not in this tree. It is preserved in git history
and tagged locally as `astro-site-final`:

```bash
git checkout astro-site-final
```
