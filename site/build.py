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
NAME_PHONETIC = "/yweh yahng/"
IDENTITY = "A CS PhD student at UNC Chapel Hill, with an M.S. in CS from Georgia Tech."

# The research sentence, split into its three strands so each can be coloured
# and, once the publications page is grouped by topic, linked. To turn a strand
# into a link later, just fill in its `href`: the renderer already handles it.
RESEARCH_LEAD = "I work on long-horizon robot manipulation:"
RESEARCH_PARTS = [
    ("skills", "learning skills and the way to chain them", ""),
    ("data", "generating the data to train them", ""),
    ("hri", "what people and robots need to tell each other to work together", ""),
]
# Reverse chronological: Meta (Jun-Aug 2026) then MERL (Jan-Apr 2026).
PREVIOUSLY = ["Meta Reality Labs Research",
              "Mitsubishi Electric Research Laboratories (MERL)"]

# Blog and Résumé are hidden for now. blog.html / post-*.html are still
# generated and reachable by URL; add the tuples back to show them again.
NAV = [("Home", "index.html"), ("About", "about.html"),
       ("Publications", "publications.html")]


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


def news_items():
    d = os.path.join(SRC, "src/content/news")
    out = []
    for fn in sorted(os.listdir(d)):
        if not fn.endswith((".md", ".mdx")):
            continue
        fm, body = split_frontmatter(open(os.path.join(d, fn), encoding="utf-8").read())
        date = yaml_get(fm, "date")
        y, m = (date.split("-") + ["1"])[:2]
        out.append({"sort": date, "when": f"{MONTHS[int(m) - 1]} {y}",
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
    <link rel="stylesheet" href="assets/stylesheets/main_free.css">
    <link rel="stylesheet" href="clarity/clarity.css">
    <link rel="stylesheet" href="assets/fontawesome-free-7.2.0-web/css/all.min.css">
    <link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="favicon-16.png">
    <link rel="apple-touch-icon" sizes="180x180" href="favicon-180.png">
    <link rel="canonical" href="{canonical}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="assets/site.css">
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
    """Person markup, same shape the previous Astro site emitted."""
    import json as _json
    data = {"@context": "https://schema.org", "@type": "Person",
            "name": NAME, "jobTitle": POSITION,
            "affiliation": {"@type": "Organization", "name": UNIVERSITY},
            "url": SITE_URL, "email": EMAIL,
            "sameAs": [u for u, _, _ in SOCIAL if u.startswith("http")]}
    return ('    <script type="application/ld+json">'
            + _json.dumps(data) + "</script>\n")


def page(title, desc, current, body, hero=False, body_class="", slug=""):
    cls = ' class="hero-band"' if hero else ""
    tag = footer_tagline()
    tag_html = ('I believe in ' + tag.split('I believe in ')[-1]) if tag else ''
    return (HEAD.format(title=html.escape(title), desc=html.escape(desc),
                        body_class=(' class="%s"' % body_class) if body_class else "",
                        canonical=SITE_URL + "/" + slug, site=SITE_URL,
                        analytics=ANALYTICS_TPL.format(gid=GA_ID) if GA_ID else "",
                        jsonld=json_ld() if slug == "" else "")
            + f'    <div{cls}>\n' + nav(current) + body + '    </div>\n'
            + FOOT.format(name=html.escape(NAME), tagline=tag_html))


def paper_row(p):
    # A <button> rather than a div: keyboard-focusable and Enter/Space work.
    # The hint is always in the DOM (opacity 0) so revealing it on hover cannot
    # shift the row.
    thumb = (f'        <div class="paper-thumb">\n'
             f'            <button class="thumb-zoom" data-full="images/publications/full/{p["preview"]}"'
             f' data-caption="{html.escape(p["title"], quote=True)}"'
             f' data-blurb="{html.escape(p["blurb"], quote=True)}"'
             f' aria-label="Enlarge figure from {html.escape(p["title"], quote=True)}">\n'
             f'                <img src="images/publications/{p["preview"]}"'
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

    return (f'    <div class="paper-row{"" if p["preview"] else " no-thumb"}">\n'
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
    return html.escape(RESEARCH_LEAD) + " " + "".join(out) + "."


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
            f'                <p>I am {html.escape(NAME)} '
            f'<span class="name-phon">{html.escape(NAME_PHONETIC)}</span> '
            f'<span class="name-alt">({html.escape(NAME_ZH)})</span>,<br>\n'
            f'                   {html.escape(IDENTITY)}</p>\n'
            f'                <p class="home-research">{research_html()}</p>\n'
            f'                <p class="home-previously">Previously: {prev}</p>\n'
            '                <div>\n'
            '                    <a href="about.html" class="button icon">Read More '
            '<i class="fa-solid fa-arrow-right"></i></a>\n'
            '                </div>\n'
            '            </div>\n'
            '            <div class="home-profile">\n'
            '                <img src="images/avatar.jpg" alt="Portrait">\n'
            '            </div>\n'
            '        </div>\n    </div>\n')
    return page(NAME, BIO, "index.html", body, hero=True, body_class="home", slug="")


def build_about(news):
    # About first, then News. News was hoisted above the bio back when About
    # was the last nav item and the home page carried nothing, so it got
    # buried; now About sits second in the nav and the hero states who he is,
    # so a reader arriving here wants the story before the recency.
    body = ('    <div class="container">\n'
            '        <div class="page-head"><h1>About</h1></div>\n')
    for p in about_paragraphs():
        body += f'        <p class="text">{p}</p>\n'
    body += '        <div class="page-head"><h1>News</h1></div>\n'
    for n in news:
        body += ('        <div class="news-row">\n'
                 f'            <div class="news-when">{n["when"]}</div>\n'
                 f'            <div class="news-body"><b>{html.escape(n["title"])}</b> {n["body"]}</div>\n'
                 '        </div>\n')
    body += '    </div>\n'
    return page(f"About | {NAME}", "About " + NAME, "about.html", body, slug="about.html")


def build_publications(papers):
    body = ('    <div class="container">\n'
            '        <div class="page-head"><h1>Publications</h1>\n'
            f'        <p class="text">{len(papers)} publications.</p></div>\n')
    for year in sorted({p["year"] for p in papers}, reverse=True):
        body += f'        <div class="pub-year">{year}</div>\n'
        for p in [q for q in papers if q["year"] == year]:
            body += paper_row(p)
    body += '    </div>\n'
    return page(f"Publications | {NAME}", f"Publications by {NAME}",
                "publications.html", body, slug="publications.html")


def build_blog(posts):
    body = ('    <div class="container">\n'
            '        <div class="page-head"><h1>Blog</h1></div>\n')
    for p in posts:
        body += ('        <div class="news-row">\n'
                 f'            <div class="news-when">{p["when"]}</div>\n'
                 f'            <div class="news-body"><a href="post-{p["slug"]}.html">'
                 f'<b>{html.escape(p["title"])}</b></a><br>{html.escape(p["desc"])}</div>\n'
                 '        </div>\n')
    body += '    </div>\n'
    return page(f"Blog | {NAME}", "Blog", "blog.html", body, slug="blog.html")


def build_post(p):
    body = ('    <div class="container">\n'
            f'        <div class="page-head"><h1>{html.escape(p["title"])}</h1>\n'
            f'        <p class="text"><em>{p["when"]}</em></p></div>\n')
    for para in p["body"]:
        body += f'        <p class="text">{para}</p>\n'
    body += '    </div>\n'
    return page(f'{p["title"]} | {NAME}', p["desc"], "blog.html", body, slug=f'post-{p["slug"]}.html')


if __name__ == "__main__":
    papers, news, posts = bib_entries(), news_items(), blog_posts()
    pages = {"index.html": build_home(),
             "about.html": build_about(news),
             "publications.html": build_publications(papers),
             "blog.html": build_blog(posts)}
    for p in posts:
        pages[f'post-{p["slug"]}.html'] = build_post(p)
    # robots + sitemap, matching what the previous Astro site published
    pages["robots.txt"] = ("User-agent: *\nAllow: /\n\n"
                           f"Sitemap: {SITE_URL}/sitemap.xml\n")
    urls = "".join(
        f"  <url><loc>{SITE_URL}/{'' if fn == 'index.html' else fn}</loc></url>\n"
        for fn in ["index.html", "about.html", "publications.html", "blog.html"]
        + [f'post-{q["slug"]}.html' for q in posts])
    pages["sitemap.xml"] = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                            + urls + "</urlset>\n")

    for fn, content in pages.items():
        with open(os.path.join(OUT, fn), "w", encoding="utf-8") as f:
            f.write(content)
    missing = sum(1 for p in papers if not p["preview"])
    print(f"wrote {len(pages)} pages: {len(papers)} publications "
          f"({missing} without a figure), {len(news)} news, {len(posts)} post(s)")
