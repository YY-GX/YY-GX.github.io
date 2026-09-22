#!/usr/bin/env python3
"""
Generate a multi-page personal site laid out like shikun.io.

Base CSS is Clarity (CC0, unmodified) for reset/typography/buttons/tables;
assets/site.css adds the nav, split hero, paper rows and news rows that the
Clarity template does not have. Content comes from the live Astro site, so
nothing is retyped by hand.

Run:  python3 build.py
"""
import os
import re
import hashlib as _hashlib
import html

OUT = os.path.dirname(os.path.abspath(__file__))
# Content lives one level up (site.config.yml, src/content/...). Derived from
# this file's location so the build works in CI as well as locally.
SRC = os.path.dirname(OUT)
PREVIEW_DIR = os.path.join(OUT, "images", "publications")


def read(p):
    with open(os.path.join(SRC, p), encoding="utf-8") as f:
        return f.read()


def yaml_get(text, key, section=None):
    lines = text.splitlines()
    if section:
        try:
            start = next(i for i, l in enumerate(lines) if l.startswith(section + ":"))
        except StopIteration:
            return ""
        lines = lines[start + 1:]
        end = next((i for i, l in enumerate(lines)
                    if l and not l.startswith((" ", "\t", "#"))), len(lines))
        lines = lines[:end]
    for l in lines:
        m = re.match(r'\s*' + re.escape(key) + r':\s*"?(.*?)"?\s*$', l)
        if m:
            return m.group(1)
    return ""


CONFIG = read("site.config.yml")
P = lambda k: yaml_get(CONFIG, k, "profile")
S = lambda k: yaml_get(CONFIG, k, "social")

SITE_URL = yaml_get(CONFIG, "url", "site").rstrip("/")
GA_ID = yaml_get(CONFIG, "google_analytics", "analytics")

NAME, POSITION = P("name"), P("position")
UNIVERSITY, EMAIL, BIO = P("university"), P("email"), P("bio")

SOCIAL = [(S("google_scholar"), "fa-solid fa-graduation-cap", "Google Scholar"),
          (S("github"), "fa-brands fa-github", "GitHub"),
          (S("twitter"), "fa-brands fa-x-twitter", "Twitter"),
          (S("linkedin"), "fa-brands fa-linkedin-in", "LinkedIn"),
          ("mailto:" + EMAIL if EMAIL else "", "fa-regular fa-envelope", "Email")]
SOCIAL = [s for s in SOCIAL if s[0]]

# ---------------------------------------------------------------------------
# Home page copy. Edit these four strings to change the hero; they are kept
# here rather than in site.config.yml because they are specific to this
# layout, and the live Astro site would only carry them as dead config keys.
# ---------------------------------------------------------------------------
NAME_ZH = "杨越"
# The word "pronounced" is what does the work here. Setting a respelling beside
# the Chinese name invites the reader to pair them character by character, and
# a Chinese name is surname first, so the respelling then looks reversed.
# Naming it as a pronunciation points it back at "Yue Yang" instead.
NAME_PHONETIC = "yweh yahng"
IDENTITY = "A CS PhD student at UNC Chapel Hill, with an M.S. in CS from Georgia Tech."

# The research sentence, split into its three strands so each can be coloured
# and, once the publications page is grouped by topic, linked. To turn a strand
# into a link later, just fill in its `href`: the renderer already handles it.
# The lead names the research area and links to the Research Focus section,
# which is where that area is actually laid out. The three strands after the
# colon keep pointing at the publications filter.
RESEARCH_LEAD_PRE = "I work on"
RESEARCH_LEAD_KEY = "robot learning for reliable long-horizon manipulation"
RESEARCH_LEAD_HREF = "/about/#research-focus"
RESEARCH_PARTS = [
    ("skills", "learning skills and the way to chain them",
     "/publications/#skills"),
    ("data", "generating the data to train them",
     "/publications/#data"),
    ("hri", "what people and robots need to tell each other to work together",
     "/publications/#hri"),
]

# Publication topics. The first three share their keys, labels and colours with
# RESEARCH_PARTS above, so a strand on the home page lands on this page with the
# matching tag already selected. A paper may carry more than one.
TOPICS = [("skills", "Skill learning &amp; chaining"),
          ("data", "Data generation"),
          ("hri", "Human-robot interaction"),
          ("earlier", "Earlier work")]
# Reverse chronological: Meta (Jun-Aug 2026) then MERL (Jan-Apr 2026).
PREVIOUSLY = ["Meta Reality Labs Research",
              "Mitsubishi Electric Research Laboratories (MERL)"]

# Blog and Résumé are hidden for now. blog.html / post-*.html are still
# generated and reachable by URL; add the tuples back to show them again.
# Directory-style, root-relative. These are the URLs the old Astro site
# published and Google indexed; the .html scheme the first static build used
# turned every one of them into a 404.
NAV = [("Home", "/"), ("About", "/about/"),
       ("Publications", "/publications/")]


# --- content ---------------------------------------------------------------

# Any link leaving the site opens in a new tab. rel=noopener is required with
# target=_blank: without it the opened page gets a handle on window.opener and
# can navigate this tab elsewhere (tabnabbing); noreferrer also stops the
# Referer header leaking.
EXTERNAL_ATTRS = ' target="_blank" rel="noopener noreferrer"'


def ext(url):
    """Attributes for a link: new tab for absolute URLs, nothing for internal."""
    return EXTERNAL_ATTRS if re.match(r'https?://', url or '') else ''


def md_inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
               lambda m: '<a href="%s"%s>%s</a>' % (m.group(2), ext(m.group(2)), m.group(1)),
               t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<i>\1</i>', t)
    return t


def split_frontmatter(raw):
    if raw.startswith("---"):
        p = raw.split("---", 2)
        return p[1], p[2].strip()
    return "", raw.strip()


# Rendered small in the footer corner instead of as a body paragraph.
FOOTER_TAGLINE_MATCH = "Slow Science"


def about_paragraphs():
    """About body, minus the tagline that now lives in the footer."""
    _, body = split_frontmatter(read("src/content/about.md"))
    return [md_inline(p.strip().replace("\n", " "))
            for p in re.split(r'\n\s*\n', body)
            if p.strip() and FOOTER_TAGLINE_MATCH not in p]


def footer_tagline():
    """The Slow Science line, taken from about.md so it stays in one place."""
    _, body = split_frontmatter(read("src/content/about.md"))
    for para in re.split(r'\n\s*\n', body):
        if FOOTER_TAGLINE_MATCH in para:
            return md_inline(para.strip().replace("\n", " ").rstrip("."))
    return ""


MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


# A small Font Awesome mark per kind of news, so the column scans by type.
# Font Awesome is already loaded for the social row, so this costs nothing.
NEWS_ICONS = {"paper": "fa-solid fa-file-lines",
              "talk": "fa-solid fa-microphone-lines",
              "position": "fa-solid fa-briefcase",
              "milestone": "fa-solid fa-graduation-cap",
              "event": "fa-regular fa-calendar-check"}


def news_items():
    d = os.path.join(SRC, "src/content/news")
    out = []
    for fn in sorted(os.listdir(d)):
        if not fn.endswith((".md", ".mdx")):
            continue
        fm, body = split_frontmatter(open(os.path.join(d, fn), encoding="utf-8").read())
        date = yaml_get(fm, "date")
        y, m = (date.split("-") + ["1"])[:2]
        kind = yaml_get(fm, "type") or "paper"
        out.append({"sort": date, "when": f"{MONTHS[int(m) - 1]} {y}",
                    "kind": kind,
                    "icon": NEWS_ICONS.get(kind, NEWS_ICONS["paper"]),
                    "title": yaml_get(fm, "title"),
                    "body": md_inline(body.replace("\n", " ").strip())})
    return sorted(out, key=lambda n: n["sort"], reverse=True)


def blog_posts():
    d = os.path.join(SRC, "src/content/blog")
    out = []
    for fn in sorted(os.listdir(d)):
        if not fn.endswith((".md", ".mdx")):
            continue
        fm, body = split_frontmatter(open(os.path.join(d, fn), encoding="utf-8").read())
        if yaml_get(fm, "draft").lower() == "true":
            continue          # the 4 drafts stay unpublished, as on the live site
        date = yaml_get(fm, "date")
        y, m = (date.split("-") + ["1"])[:2]
        out.append({"slug": os.path.splitext(fn)[0], "sort": date,
                    "when": f"{MONTHS[int(m) - 1]} {y}",
                    "title": yaml_get(fm, "title"),
                    "desc": yaml_get(fm, "description"),
                    "body": [md_inline(p.strip().replace("\n", " "))
                             for p in re.split(r'\n\s*\n', body) if p.strip()]})
    return sorted(out, key=lambda p: p["sort"], reverse=True)


def bibtex_string(kind, key, e):
    """A clean citation for display: real bib fields only, no site-internal
    keys (preview/selected/bibtex_show/pdf/website/code)."""
    venue_key = "booktitle" if kind == "inproceedings" else "journal"
    lines = ["@%s{%s," % (kind, key),
             "  title   = {%s}," % e["title"],
             "  author  = {%s}," % " and ".join(e["authors_raw"]),
             "  %-7s = {%s}," % (venue_key, e["venue"]),
             "  year    = {%s}" % e["year"], "}"]
    return "\n".join(lines)


def bib_entries():
    raw = read("src/content/publications/papers.bib")
    entries = []
    for kind, key, block in re.findall(r'@(\w+)\{([^,]+),(.*?)\n\}', raw, re.S):
        fields = dict(re.findall(
            r'(\w+)\s*=\s*\{(.*?)\}\s*,?\s*(?=\n\s*\w+\s*=|\Z)', block, re.S))
        fields = {k.lower(): " ".join(v.split()) for k, v in fields.items()}
        authors = []
        for a in re.split(r'\s+and\s+', fields.get("author", "")):
            a = a.strip()
            if "," in a:
                last, first = [x.strip() for x in a.split(",", 1)]
                a = f"{first} {last}"
            authors.append(a)
        preview = fields.get("preview", "")
        if preview and not os.path.exists(os.path.join(PREVIEW_DIR, preview)):
            preview = ""      # figure not on disk -> row renders without one
        e = {"key": key.strip(), "kind": kind,
             "title": fields.get("title", ""), "authors": authors,
             "authors_raw": [a.strip() for a in
                             re.split(r'\s+and\s+', fields.get("author", ""))],
             "venue": fields.get("journal") or fields.get("booktitle", ""),
             "year": fields.get("year", ""), "pdf": fields.get("pdf", ""),
             "website": fields.get("website", ""), "code": fields.get("code", ""),
             "dataset": fields.get("dataset", ""),
             "equal": [n.strip() for n in fields.get("equal", "").split(",") if n.strip()],
             "blurb": fields.get("blurb", ""),
             "topics": [t.strip() for t in fields.get("topics", "").split(",") if t.strip()],
             "doi": fields.get("doi", ""), "date": fields.get("date", ""),
             "preview": preview,
             "selected": fields.get("selected", "").lower() == "true"}
        e["bibtex"] = bibtex_string(kind, key.strip(), e)
        entries.append(e)
    return entries


def author_line(authors, equal=()):
    """Render the author list, bolding the site owner and starring any
    equal-contribution authors. The star is appended AFTER the name is matched,
    so marking someone co-first never silently breaks the bolding."""
    out = []
    for a in authors:
        star = "*" if a in equal else ""
        name = html.escape(a) + star
        out.append(f"<b>{name}</b>" if a == NAME else name)
    return ", ".join(out)


def venue_label(v, year):
    v = re.sub(r'arXiv preprint arXiv:([\d.]+)', r'arXiv:\1', v)
    if not v:
        return str(year)
    # A work still under review has no publication year, so never append one:
    # a conference carries its own edition ("ICRA 2027") and a journal has no
    # year at all until it appears.
    if v.lower().startswith("in submission"):
        return html.escape(v)
    # Don't append the year when the venue string already carries one, or you
    # get "...presented at ICRA 2026, 2025". Strip arXiv identifiers before
    # testing: "arXiv:2010.03468" starts with digits that look like a year.
    probe = re.sub(r'arXiv:\s*[\d.]+(v\d+)?', '', v)
    if re.search(r'\b(19|20)\d{2}\b', probe):
        return html.escape(v)
    return f"{html.escape(v)}, {year}"


# --- markup ----------------------------------------------------------------

# Cache-buster for the stylesheet. python -m http.server and GitHub Pages both
# let a browser hold on to an old site.css, which silently drops new rules.
CSS_VERSION = _hashlib.md5(
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "assets", "site.css"), "rb").read()).hexdigest()[:8]


def nav(current):
    def link(label, href):
        # kept out of the f-string: py3.9 rejects backslashes in f-string exprs
        cls = ' class="active"' if href == current else ''
        return f'                        <a href="{href}"{cls}>{label}</a>\n'

    links = "".join(link(label, href) for label, href in NAV)
    socials = "".join(
        f'                        <a href="{html.escape(url)}" class="{icon}"'
        f' aria-label="{title}"{ext(url)}></a>\n' for url, icon, title in SOCIAL)
    mobile = "".join(f'                <a href="{href}">{label}</a>\n'
                     for label, href in NAV)
    return f"""    <div class="nav-bar" id="nav-bar">
        <div class="container">
            <div class="nav-container">
                <div class="menu">
{links}                    <div class="menu-dot"></div>
                </div>
                <div class="social">
{socials}                </div>
            </div>
            <div class="nav-container-small">
                <div class="menu-bar">
                    <button class="menu-default" aria-label="Menu" aria-expanded="false"
                            onclick="document.getElementById('nav-bar').classList.toggle('open');
                                     this.setAttribute('aria-expanded', document.getElementById('nav-bar').classList.contains('open'));">
                        <span></span><span></span><span></span>
                    </button>
                </div>
                <div class="mobile-menu">
{mobile}                    <div class="social-row">
{socials}                    </div>
                </div>
            </div>
        </div>
    </div>
"""


HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{desc}">
    <meta name="robots" content="all">
    <meta property="og:type" content="website">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:image" content="{site}/favicon-512.png">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{desc}">
    <meta name="twitter:image" content="{site}/favicon-512.png">
    <link rel="stylesheet" href="/assets/stylesheets/main_free.css">
    <link rel="stylesheet" href="/clarity/clarity.css">
    <link rel="stylesheet" href="/assets/fontawesome-free-7.2.0-web/css/all.min.css">
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/favicon-180.png">
    <link rel="canonical" href="{canonical}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/assets/site.css?v={cssv}">
{analytics}{jsonld}</head>
<body{body_class}>
"""

FOOT = """    <footer>
        <div class="container">
            <div class="footer-row">
                <p class="footer-main">{name} &middot; Chapel Hill, NC</p>
                <div class="footer-fine">
                    <span class="footer-motto">{tagline}</span>
                    <span class="footer-credit">Layout adapted from <a href="https://shikun.io/projects/clarity" target="_blank" rel="noopener noreferrer">Clarity</a> by <a href="https://shikun.io/" target="_blank" rel="noopener noreferrer">Shikun Liu</a></span>
                </div>
            </div>
        </div>
    </footer>
    <div class="lightbox" id="lightbox" hidden tabindex="-1" role="dialog" aria-modal="true" aria-label="Enlarged figure">
        <button class="lightbox-close" aria-label="Close">&times;</button>
        <figure>
            <img src="" alt="">
            <figcaption>
                <span class="lightbox-title"></span>
                <span class="lightbox-blurb"></span>
            </figcaption>
        </figure>
    </div>
    <script>
    // Topic filter. The URL hash selects a tag, so a research strand on the
    // home page can link straight into a filtered view.
    (function () {{
      var bar = document.querySelector('.tag-bar');
      if (!bar) return;
      var chips = [].slice.call(bar.querySelectorAll('.tag-chip'));
      var rows = [].slice.call(document.querySelectorAll('.paper-row'));
      var years = [].slice.call(document.querySelectorAll('.pub-year'));

      function apply(topic) {{
        rows.forEach(function (r) {{
          var t = (r.getAttribute('data-topics') || '').split(' ');
          r.hidden = !(topic === 'all' || t.indexOf(topic) !== -1);
        }});
        // A year heading with nothing under it should go too.
        years.forEach(function (y) {{
          var any = false, n = y.nextElementSibling;
          while (n && !n.classList.contains('pub-year')) {{
            if (n.classList.contains('paper-row') && !n.hidden) {{ any = true; break; }}
            n = n.nextElementSibling;
          }}
          y.hidden = !any;
        }});
        chips.forEach(function (c) {{
          var on = c.getAttribute('data-topic') === topic;
          c.classList.toggle('is-on', on);
          c.setAttribute('aria-pressed', on ? 'true' : 'false');
        }});
        if (history.replaceState) {{
          history.replaceState(null, '', topic === 'all' ? location.pathname : '#' + topic);
        }}
      }}

      chips.forEach(function (c) {{
        c.addEventListener('click', function () {{
          var t = c.getAttribute('data-topic');
          // Clicking the active tag clears it, so the filter is never a trap.
          apply(c.classList.contains('is-on') && t !== 'all' ? 'all' : t);
        }});
      }});

      function fromHash() {{
        var h = (location.hash || '').replace('#', '');
        apply(chips.some(function (c) {{ return c.getAttribute('data-topic') === h; }}) ? h : 'all');
      }}
      window.addEventListener('hashchange', fromHash);
      fromHash();
    }})();

    // Figure lightbox.
    (function () {{
      var box = document.getElementById('lightbox');
      if (!box) return;
      var img = box.querySelector('img');
      var cap = box.querySelector('.lightbox-title');
      var blurb = box.querySelector('.lightbox-blurb');
      var closeBtn = box.querySelector('.lightbox-close');
      var opener = null;

      function open(btn) {{
        opener = btn;
        img.src = btn.getAttribute('data-full');
        img.alt = 'Figure from ' + btn.getAttribute('data-caption');
        cap.textContent = btn.getAttribute('data-caption');
        var b = btn.getAttribute('data-blurb') || '';
        blurb.textContent = b;
        blurb.hidden = !b;
        box.hidden = false;
        document.body.style.overflow = 'hidden';
        box.focus();
      }}

      function close() {{
        box.hidden = true;
        img.src = '';
        document.body.style.overflow = '';
        if (opener) {{ opener.focus(); opener = null; }}
      }}

      document.querySelectorAll('.thumb-zoom').forEach(function (btn) {{
        btn.addEventListener('click', function () {{ open(btn); }});
      }});
      closeBtn.addEventListener('click', close);
      // Click anywhere outside the figure closes; clicks on the image do not.
      box.addEventListener('click', function (e) {{
        if (e.target === box) close();
      }});
      document.addEventListener('keydown', function (e) {{
        if (e.key === 'Escape' && !box.hidden) close();
      }});
    }})();

    // Slide the dot under the active link, and follow the pointer on hover.
    (function () {{
      var menu = document.querySelector('.nav-bar .menu');
      if (!menu) return;
      var dot = menu.querySelector('.menu-dot');
      var active = menu.querySelector('a.active');
      function place(el) {{
        if (!el) {{ dot.style.opacity = 0; return; }}
        dot.style.left = (el.offsetLeft + el.offsetWidth / 2 - 4) + 'px';
        dot.style.opacity = 1;
      }}
      menu.querySelectorAll('a').forEach(function (a) {{
        a.addEventListener('mouseenter', function () {{ place(a); }});
      }});
      menu.addEventListener('mouseleave', function () {{ place(active); }});
      window.addEventListener('load', function () {{ place(active); }});
      window.addEventListener('resize', function () {{ place(active); }});
    }})();

    // BibTeX disclosure: reveal the citation, and copy it on a second click.
    (function () {{
      document.querySelectorAll('.cite-toggle').forEach(function (btn) {{
        var pre = document.getElementById(btn.getAttribute('aria-controls'));
        if (!pre) return;
        btn.addEventListener('click', function () {{
          var open = pre.hidden === false;
          if (!open) {{
            pre.hidden = false;
            btn.setAttribute('aria-expanded', 'true');
            return;
          }}
          if (navigator.clipboard) {{
            navigator.clipboard.writeText(pre.innerText).then(function () {{
              var label = btn.firstChild;
              var was = label.nodeValue;
              label.nodeValue = 'Copied ';
              setTimeout(function () {{ label.nodeValue = was; }}, 1200);
            }});
          }}
          pre.hidden = true;
          btn.setAttribute('aria-expanded', 'false');
        }});
      }});
    }})();


    // Research Focus figure. Hovering the pill previews that column's work and
    // it closes again on the way out; clicking pins it open. The preview is
    // what tells a first-time reader the pill does anything at all.
    (function () {{
      var hoverable = window.matchMedia('(hover: hover)').matches;
      document.querySelectorAll('.rf-more').forEach(function (btn) {{
        var box = document.getElementById(btn.getAttribute('data-target'));
        if (!box) return;
        var pinned = false, peek = false, timer = null;
        function sync() {{
          var open = pinned || peek;
          box.classList.toggle('is-open', open);
          btn.classList.toggle('is-open', open);
          btn.classList.toggle('is-pinned', pinned);
          btn.setAttribute('aria-expanded', String(open));
        }}
        btn.addEventListener('click', function () {{
          // A click is authoritative. Without resetting the preview too, a
          // click that unpins leaves peek true - the pointer is still on the
          // pill - and the column stays open, so it looks stuck.
          pinned = !pinned;
          peek = pinned;
          sync();
        }});
        if (!hoverable) return;
        function enter() {{ clearTimeout(timer); peek = true; sync(); }}
        function leave() {{
          clearTimeout(timer);
          // The connector sits between the pill and the list, so leaving one to
          // reach the other must not count as leaving.
          timer = setTimeout(function () {{ peek = false; sync(); }}, 140);
        }}
        btn.addEventListener('mouseenter', enter);
        btn.addEventListener('mouseleave', leave);
        // The list keeps an open column open, but hovering it never opens one:
        // otherwise drifting across the lower half of the figure pops columns.
        box.addEventListener('mouseenter', function () {{
          if (box.classList.contains('is-open')) enter();
        }});
        box.addEventListener('mouseleave', leave);
        btn.addEventListener('focus', enter);
        btn.addEventListener('blur', leave);
      }});
    }})();
    </script>
</body>
</html>
"""


ANALYTICS_TPL = """    <script async src="https://www.googletagmanager.com/gtag/js?id={gid}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{gid}');
    </script>
"""


def json_ld():
    """Person markup. sameAs is what lets a machine decide this Yue Yang is the
    same entity across sites, which matters because the name is shared by many
    active researchers; only identifiers verified against his own DOIs go in."""
    import json as _json
    same = [u for u, _, _ in SOCIAL if u.startswith("http")]
    for key in ("orcid", "semantic_scholar", "dblp"):
        v = S(key)
        if v and v not in same:
            same.append(v)
    data = {"@context": "https://schema.org", "@type": "Person",
            "name": NAME, "jobTitle": POSITION,
            "affiliation": {"@type": "CollegeOrUniversity", "name": UNIVERSITY},
            "alumniOf": [{"@type": "CollegeOrUniversity",
                          "name": "Georgia Institute of Technology"}],
            "knowsAbout": ["Robot learning", "Long-horizon manipulation",
                           "Skill chaining", "Vision-Language-Action models",
                           "Robot data generation", "Imitation learning",
                           "Human-robot interaction", "Augmented reality"],
            "url": SITE_URL, "email": EMAIL, "sameAs": same}
    if S("orcid"):
        data["identifier"] = {"@type": "PropertyValue", "propertyID": "ORCID",
                              "value": S("orcid")}
    return ('    <script type="application/ld+json">'
            + _json.dumps(data) + "</script>\n")


def scholarly_ld(papers):
    """One ScholarlyArticle per paper. Without this the publication list is just
    styled text: nothing tells a crawler these are papers, who wrote them, or
    where they appeared."""
    import json as _json
    items = []
    for i, q in enumerate(papers, 1):
        art = {"@type": "ScholarlyArticle", "name": q["title"],
               "author": [{"@type": "Person", "name": a} for a in q["authors"]]}
        if q["date"]:
            art["datePublished"] = q["date"]
        elif q["year"]:
            art["datePublished"] = q["year"]
        if q["doi"]:
            art["identifier"] = {"@type": "PropertyValue", "propertyID": "DOI",
                                 "value": q["doi"]}
            art["sameAs"] = "https://doi.org/" + q["doi"]
        # Only claim a publication venue for work that actually appeared in one.
        if q["venue"] and not q["venue"].lower().startswith("in submission"):
            art["publication"] = q["venue"]
        else:
            art["creativeWorkStatus"] = "Under review"
        url = q["website"] or q["pdf"]
        if url:
            art["url"] = url
        if q["blurb"]:
            art["abstract"] = q["blurb"]
        items.append({"@type": "ListItem", "position": i, "item": art})
    data = {"@context": "https://schema.org", "@type": "ItemList",
            "name": f"Publications by {NAME}", "numberOfItems": len(items),
            "itemListElement": items}
    return ('    <script type="application/ld+json">'
            + _json.dumps(data) + "</script>\n")


def page(title, desc, current, body, hero=False, body_class="", slug="", extra_ld=""):
    cls = ' class="hero-band"' if hero else ""
    tag = footer_tagline()
    tag_html = ('I believe in ' + tag.split('I believe in ')[-1]) if tag else ''
    return (HEAD.format(title=html.escape(title), desc=html.escape(desc),
                        cssv=CSS_VERSION,
                        body_class=(' class="%s"' % body_class) if body_class else "",
                        canonical=SITE_URL + "/" + slug, site=SITE_URL,
                        analytics=ANALYTICS_TPL.format(gid=GA_ID) if GA_ID else "",
                        jsonld=(json_ld() if slug == "" else "") + extra_ld)
            + f'    <div{cls}>\n' + nav(current) + body + '    </div>\n'
            + FOOT.format(name=html.escape(NAME), tagline=tag_html))


def paper_row(p):
    # A <button> rather than a div: keyboard-focusable and Enter/Space work.
    # The hint is always in the DOM (opacity 0) so revealing it on hover cannot
    # shift the row.
    thumb = (f'        <div class="paper-thumb">\n'
             f'            <button class="thumb-zoom" data-full="/images/publications/full/{p["preview"]}"'
             f' data-caption="{html.escape(p["title"], quote=True)}"'
             f' data-blurb="{html.escape(p["blurb"], quote=True)}"'
             f' aria-label="Enlarge figure from {html.escape(p["title"], quote=True)}">\n'
             f'                <img src="/images/publications/{p["preview"]}"'
             f' alt="Figure from {html.escape(p["title"], quote=True)}" loading="lazy">\n'
             f'            </button>\n'
             f'            <span class="thumb-hint" aria-hidden="true">Click to enlarge</span>\n'
             f'        </div>\n'
             if p["preview"] else "")

    def btn(url, label, icon):
        return (f'<a href="{html.escape(url)}" class="button icon"{ext(url)}>{label} '
                f'<i class="{icon}"></i></a>') if url else ""

    # Project page first: it is the richest and the author controls it.
    links = [btn(p["website"], "Website", "fa-solid fa-arrow-up-right-from-square"),
             btn(p["pdf"], "PDF", "fa-regular fa-file-lines"),
             btn(p["code"], "Code", "fa-brands fa-github"),
             # a dataset-release repo is labelled honestly rather than as "Code"
             btn(p["dataset"], "Dataset", "fa-solid fa-database")]
    equal_note = ('<span class="equal-note">* equal contribution</span>'
                  if p["equal"] else "")
    cite_id = "cite-" + p["key"]
    links.append(f'<button class="button icon cite-toggle" aria-expanded="false"'
                 f' aria-controls="{cite_id}">BibTeX '
                 f'<i class="fa-regular fa-copy"></i></button>')
    row = "\n                ".join(x for x in links if x)

    return (f'    <div class="paper-row{"" if p["preview"] else " no-thumb"}"'
            f' data-topics="{" ".join(p["topics"])}">\n'
            f'{thumb}'
            '        <div class="paper-info">\n'
            f'            <p class="paper-title">{html.escape(p["title"])}</p>\n'
            f'            <p class="paper-authors">{author_line(p["authors"], p["equal"])}{equal_note}</p>\n'
            f'            <p class="paper-venue">{venue_label(p["venue"], p["year"])}</p>\n'
            f'            <div class="paper-links">\n                {row}\n            </div>\n'
            f'            <pre class="paper-cite" id="{cite_id}" hidden>'
            f'<code>{html.escape(p["bibtex"])}</code></pre>\n'
            '        </div>\n    </div>\n')


# --- pages -----------------------------------------------------------------

def name_mark():
    """Chinese name plus the pronunciation of the romanised name."""
    return (f'<span class="name-alt">({html.escape(NAME_ZH)}'
            f'<span class="name-phon">, pronounced &ldquo;{html.escape(NAME_PHONETIC)}&rdquo;</span>'
            f')</span>')


def research_html():
    """The research sentence with each strand wrapped in its own colour class,
    and optionally linked once `href` is set in RESEARCH_PARTS."""
    out = []
    for i, (key, text, href) in enumerate(RESEARCH_PARTS):
        if i == len(RESEARCH_PARTS) - 1:
            out.append("and ")
        inner = html.escape(text)
        tag = (f'<a class="ra ra-{key}" href="{html.escape(href)}">{inner}</a>'
               if href else f'<span class="ra ra-{key}">{inner}</span>')
        out.append(tag)
        if i < len(RESEARCH_PARTS) - 1:
            out.append(", ")
    lead = (f'{html.escape(RESEARCH_LEAD_PRE)} '
            f'<a class="ra-lead" href="{RESEARCH_LEAD_HREF}">'
            f'{html.escape(RESEARCH_LEAD_KEY)}</a>:')
    return lead + " " + "".join(out) + "."


# ---------------------------------------------------------------------------
# The research statement above the figure. Written for two readers at once: the
# prose carries the argument for peers, the keyword band underneath carries the
# terms a recruiter or a search scans for, so neither job spoils the other.
# ---------------------------------------------------------------------------
RESEARCH_STATEMENT = [
    "My research focuses on robot learning for reliable long-horizon "
    "manipulation. I investigate how learned skills can remain robust as task "
    "contexts change and be composed to accomplish extended tasks. This goal "
    "connects my work on skill learning, robot data generation, and "
    "human-robot interaction.",

    "I develop methods for learning and composing reusable skills, collecting "
    "and synthesizing training data, and enabling people to teach and guide "
    "robots. These efforts span task-relevant policy learning, intent "
    "communication, and learning safety constraints from demonstrations. "
    "Through benchmarks and evaluation systems, I study the capabilities and "
    "failure modes of learned policies.",
]

# Five, not ten. Platforms and tools (humanoid, bimanual, vision-tactile,
# AR/VR) belong to the individual projects, not beside the research areas.
RESEARCH_KEYWORDS = [
    "Long-horizon manipulation", "Compositional robot learning",
    "Multimodal robustness", "Robot data synthesis",
    "Human-robot interaction",
]


def research_statement_html():
    """Prose left, keywords right. The prose needs a short measure to stay
    readable, which leaves the rest of the container empty, and the keywords
    are exactly the thing that belongs beside it rather than under it."""
    out = '        <div class="rf-intro">\n            <div class="rf-statement">\n'
    # Both paragraphs in one voice: the opening one used to be set larger as a
    # lede, which read as two different pieces of text rather than one statement.
    for para in RESEARCH_STATEMENT:
        out += f'                <p>{html.escape(para)}</p>\n'
    out += ('            </div>\n'
            '            <aside class="rf-keys">\n'
            '                <span class="rf-keys-label">Keywords</span>\n'
            '                <ul>\n')
    for k in RESEARCH_KEYWORDS:
        out += f'                    <li>{k}</li>\n'
    out += ('                </ul>\n'
            '            </aside>\n'
            '        </div>\n')
    return out


# ---------------------------------------------------------------------------
# Research Focus figure. Three research areas side by side and one evaluation
# band across the bottom. No arrows between the areas: an earlier version drew
# a closed loop (failures choosing the next data collection, interaction
# flowing back into training data) that the papers do not demonstrate.
#   (key, heading, publications tag, scope line,
#    [(sub-area, [(paper label, url, contribution), ...]), ...])
# ---------------------------------------------------------------------------
LILO = "https://yy-gx.github.io/LiLo-VLA/"
ARCADE = "https://yy-gx.github.io/ARCADE/"
ARDEMO = "https://arxiv.org/pdf/2403.13910"

RESEARCH_FOCUS = [
    ("skills", "Learning and Composing Robot Skills", "skills",
     "Developing reusable manipulation skills and robust policies for "
     "long-horizon execution.",
     [("Skill Composition and Long-Horizon Execution",
       [("LiLo-VLA", LILO,
         "Object-centric skill composition with failure recovery"),
        ("FurnitureVLA", "https://dannymcy.github.io/furniturevla/",
         "Progress-aware VLA policies for long-horizon bimanual assembly")]),
      ("Multimodal Robustness and Language Grounding",
       [("EGR", "https://yy-gx.github.io/EGR/",
         "Evidence-guided regularization for multimodal policy robustness"),
        ("Counterfactual VLA", "https://vla-cf.github.io/",
         "Counterfactual evaluation and action guidance for language "
         "following")])]),

    ("data", "Robot Data Collection and Synthesis", "data",
     "Scaling robot learning through demonstration interfaces and synthetic "
     "training data.",
     [("Demonstration Interfaces",
       [("ARCADE", ARCADE,
         "AR-assisted demonstration collection and synthetic expansion"),
        ("AR Demonstrations", ARDEMO,
         "Hand-based demonstration collection through augmented reality")]),
      ("Synthetic Data and Reward Learning",
       [("ReBot", "https://yuffish.github.io/rebot/",
         "Real-to-sim-to-real video synthesis for VLA adaptation"),
        ("DenseReward", "https://dense-reward.github.io/",
         "Dense reward learning from synthesized failure trajectories")])]),

    ("hri", "Human-Robot Interaction and Safe Learning", "hri",
     "Supporting robot teaching, intent communication, and learning from "
     "human safety demonstrations.",
     [("Intent Alignment and Competency Communication",
       [("AR Intent",
         "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10973947",
         "AR-mediated intention alignment in collaborative tasks"),
        ("Competency-Aware",
         "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=11154044",
         "Robot competency communication for collaborative exploration")]),
      ("Safety Learning from Demonstrations",
       [("SECURE", "https://dl.acm.org/doi/pdf/10.1145/3610977.3635002",
         "Learning safety constraints from demonstrations for CBF shielding"),
        ("Safe IRL via CBF", "https://arxiv.org/pdf/2212.02753",
         "CBF-informed optimization for safer inverse reinforcement "
         "learning")])]),
]

# Cuts across all three areas, so it gets its own band rather than a column.
RESEARCH_EVAL = (
    "eval", "Benchmarking and Evaluation", "",
    "Diagnosing policy failures and developing systematic evaluation for "
    "robot manipulation.",
    [("Benchmarks and Evaluation Systems",
      [("BOSS", "https://boss-benchmark.github.io/",
        "Benchmarking observation shifts induced by skill chaining"),
       ("HALTER", "https://yy-gx.github.io/HALTER/",
        "Scene-graph-based scoring and autonomous reset for long-horizon "
        "evaluation"),
       ("WatchAct", "https://baiqi-li.github.io/watchact_page/",
        "Benchmarking manipulation grounded in human behavior videos")])],
)


def _rf_card(key, heading, tag, scope, groups, index=None):
    head = f'            <div class="col-head {key}">\n'
    if index:
        head += f'                <span class="idx">{index}</span>\n'
    title = html.escape(heading)
    if tag:
        title = f'<a href="/publications/#{tag}">{title}</a>'
    head += (f'                <h3>{title}</h3>\n'
             f'                <p class="q">{html.escape(scope)}</p>\n'
             f'                <button class="rf-more" data-target="rf-{key}"'
             f' aria-controls="rf-{key}" aria-expanded="false">'
             '<span class="lbl">Papers</span>'
             '<span class="chev"></span></button>\n'
             '            </div>\n'
             f'            <div class="tick {key}"></div>\n'
             f'            <div class="rf-body {key}" id="rf-{key}">\n')
    for title, rows in groups:
        head += ('                <div class="sub">\n'
                 f'                    <h4>{html.escape(title)}</h4>\n'
                 '                    <ul class="items">\n')
        for label, url, what in rows:
            head += ('                        <li>'
                     f'<a href="{html.escape(url)}" target="_blank" '
                     f'rel="noopener noreferrer">{html.escape(label)}</a>'
                     f'<span class="what">{html.escape(what)}</span></li>\n')
        head += ('                    </ul>\n'
                 '                </div>\n')
    return head + '            </div>\n'


def research_focus_html():
    out = '        <div class="rf">\n'
    for i, (key, heading, tag, scope, groups) in enumerate(RESEARCH_FOCUS):
        out += _rf_card(key, heading, tag, scope, groups, index="0%d" % (i + 1))
    key, heading, tag, scope, groups = RESEARCH_EVAL
    out += _rf_card(key, heading, tag, scope, groups)
    return out + '        </div>\n'


def build_404():
    body = ('    <div class="container">\n'
            '        <div class="page-head"><h1>Page not found</h1>\n'
            '        <p class="text">That address does not exist here. It may be from an '
            'older version of this site.</p></div>\n'
            '        <p class="text"><a href="/" class="button icon">Home '
            '<i class="fa-solid fa-arrow-right"></i></a></p>\n'
            '    </div>\n')
    return page(f"Page not found | {NAME}", "Page not found", "/", body, slug="404")


def redirect_stub(target):
    """Client-side redirect: GitHub Pages cannot issue a 301."""
    t = html.escape(target)
    return ('<!DOCTYPE html><html><head><meta charset="UTF-8">'
            f'<link rel="canonical" href="{SITE_URL}{t}">'
            f'<meta http-equiv="refresh" content="0; url={t}">'
            '<meta name="robots" content="noindex">'
            f'<title>Moved</title></head><body>'
            f'<p>This page has moved to <a href="{t}">{t}</a>.</p>'
            '</body></html>\n')


def build_home():
    # &nbsp; before the separator so it can never start a wrapped line, and a
    # normal space after it so the break happens between the two entries.
    prev = "&nbsp;<span class=\"sep\">&middot;</span> ".join(
        html.escape(x) for x in PREVIOUSLY)
    body = ('    <div class="container">\n'
            '        <div class="home-container">\n'
            '            <div class="home-intro">\n'
            '                <h1 class="title">Hello 👋</h1>\n'
            # Phonetic sits directly after the romanised name, which is what
            # it describes; the Chinese name keeps its own parentheses. Pairing
            # them inside one bracket invited the reader to match them element
            # by element, and a Chinese name is surname first, so the order
            # looked wrong.
            f'                <p>I am {html.escape(NAME)} {name_mark()},<br>\n'
            f'                   {html.escape(IDENTITY)}</p>\n'
            f'                <p class="home-research">{research_html()}</p>\n'
            f'                <p class="home-previously">Previously: {prev}</p>\n'
            '                <div>\n'
            '                    <a href="/about/" class="button icon">Read More '
            '<i class="fa-solid fa-arrow-right"></i></a>\n'
            '                </div>\n'
            '            </div>\n'
            '            <div class="home-profile">\n'
            '                <img src="images/avatar.jpg" alt="Portrait">\n'
            '            </div>\n'
            '        </div>\n    </div>\n')
    return page(NAME, BIO, "/", body, hero=True, body_class="home", slug="")


def build_about(news):
    # About first, then News. News was hoisted above the bio back when About
    # was the last nav item and the home page carried nothing, so it got
    # buried; now About sits second in the nav and the hero states who he is,
    # so a reader arriving here wants the story before the recency.
    body = ('    <div class="container">\n'
            '        <div class="page-head"><h1>About</h1></div>\n')
    for p in about_paragraphs():
        body += f'        <p class="text">{p}</p>\n'
    # id only, no tabindex: making the target focusable meant a hash jump
    # drew the global :focus-visible ring around the whole heading block.
    body += '        <div class="page-head" id="research-focus">'\
           '<h1>Research Focus</h1></div>\n'
    body += research_statement_html()
    body += research_focus_html()
    body += '        <div class="page-head"><h1>News</h1></div>\n'
    for n in news:
        body += (f'        <div class="news-row" data-kind="{n["kind"]}">\n'
                 f'            <div class="news-when">{n["when"]}</div>\n'
                 f'            <div class="news-mark"><i class="{n["icon"]}"'
                 ' aria-hidden="true"></i></div>\n'
                 f'            <div class="news-body"><b>{html.escape(n["title"])}</b> {n["body"]}</div>\n'
                 '        </div>\n')
    body += '    </div>\n'
    return page(f"About | {NAME}",
                f"{NAME} is a CS PhD student at UNC Chapel Hill working on "
                "long-horizon robot manipulation. Advisors, background, and news.",
                "/about/", body, slug="about/")


def build_publications(papers):
    chips = ('            <button class="tag-chip is-on" data-topic="all"'
             ' aria-pressed="true">All</button>\n')
    for key, label in TOPICS:
        n = sum(1 for p in papers if key in p["topics"])
        chips += (f'            <button class="tag-chip tag-{key}" data-topic="{key}"'
                  f' aria-pressed="false">{label} <span class="tag-n">{n}</span></button>\n')

    body = ('    <div class="container">\n'
            '        <div class="page-head"><h1>Publications</h1></div>\n'
            '        <div class="tag-bar" role="group" aria-label="Filter by topic">\n'
            f'{chips}'
            '        </div>\n')
    for year in sorted({p["year"] for p in papers}, reverse=True):
        body += f'        <div class="pub-year" data-year="{year}">{year}</div>\n'
        for p in [q for q in papers if q["year"] == year]:
            body += paper_row(p)
    body += '    </div>\n'
    return page(
        f"Publications | {NAME}",
        "Peer-reviewed papers and preprints on long-horizon robot manipulation, "
        "skill learning and chaining, robot data generation, and human-robot "
        f"interaction, by {NAME} (UNC Chapel Hill).",
        "/publications/", body, slug="publications/",
        extra_ld=scholarly_ld(papers))


def build_blog(posts):
    body = ('    <div class="container">\n'
            '        <div class="page-head"><h1>Blog</h1></div>\n')
    for p in posts:
        body += ('        <div class="news-row">\n'
                 f'            <div class="news-when">{p["when"]}</div>\n'
                 f'            <div class="news-body"><a href="/blog/{p["slug"]}/">'
                 f'<b>{html.escape(p["title"])}</b></a><br>{html.escape(p["desc"])}</div>\n'
                 '        </div>\n')
    body += '    </div>\n'
    return page(f"Blog | {NAME}", "Blog", "/blog/", body, slug="blog/")


def build_post(p):
    body = ('    <div class="container">\n'
            f'        <div class="page-head"><h1>{html.escape(p["title"])}</h1>\n'
            f'        <p class="text"><em>{p["when"]}</em></p></div>\n')
    for para in p["body"]:
        body += f'        <p class="text">{para}</p>\n'
    body += '    </div>\n'
    return page(f'{p["title"]} | {NAME}', p["desc"], "/blog/", body, slug=f'blog/{p["slug"]}/')


if __name__ == "__main__":
    papers, news, posts = bib_entries(), news_items(), blog_posts()

    # Directory-style paths, restoring the URLs the Astro site published.
    pages = {"index.html":              build_home(),
             "about/index.html":        build_about(news),
             "publications/index.html": build_publications(papers),
             "blog/index.html":         build_blog(posts)}
    for q in posts:
        pages["blog/%s/index.html" % q["slug"]] = build_post(q)

    # GitHub Pages serves this for any unmatched path. It carries the analytics
    # snippet, so a broken inbound link is visible rather than silent.
    pages["404.html"] = build_404()

    # The .html scheme was live briefly; keep those paths pointing at the real
    # page so nothing that was shared in between breaks.
    # Only /cv/, which was live and indexed until the page was hidden, so people
    # still arrive there from bookmarks and search.
    #
    # There are deliberately NO foo.html stubs beside foo/index.html. Having
    # both makes the path ambiguous: GitHub Pages answers /publications with
    # publications.html, and a crawler that normalises the trailing slash then
    # bounces between the stub and the real page and reports a redirect loop.
    # The .html paths were only live for a day, so nothing depends on them.
    pages["cv/index.html"] = redirect_stub("/")

    # Written by hand and kept in the repo; copied through so it ships.
    llms = os.path.join(SRC, "src/content/llms.txt")
    if os.path.exists(llms):
        with open(llms, encoding="utf-8") as f:
            pages["llms.txt"] = f.read()

    pages["robots.txt"] = ("User-agent: *\nAllow: /\n\n"
                           f"Sitemap: {SITE_URL}/sitemap.xml\n")
    urls = "".join(f"  <url><loc>{SITE_URL}/{u}</loc></url>\n"
                   for u in ["", "about/", "publications/", "blog/"]
                   + ["blog/%s/" % q["slug"] for q in posts])
    pages["sitemap.xml"] = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                            + urls + "</urlset>\n")

    for fn, content in pages.items():
        path = os.path.join(OUT, fn)
        os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(fn) else None
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    missing = sum(1 for q in papers if not q["preview"])
    print(f"wrote {len(pages)} files: {len(papers)} publications "
          f"({missing} without a figure), {len(news)} news, {len(posts)} post(s)")
