#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_epub.py -- assemble poems-to-memorize.epub

Reads the metadata in poems.py and any poem texts sitting in texts/, and writes
a valid EPUB 3 with a nested table of contents (category -> poem).

Run fetch_texts.py first if you want the 26 public-domain texts included.
Without it you still get a complete, working book of commentary and links.

Usage:
    python3 build_epub.py [-o output.epub]
"""

import os
import sys
import html
import zipfile
import datetime
import uuid

from poems import CATEGORIES, POEMS, FURTHER, DICKINSON_NOTE, slug

HERE = os.path.dirname(os.path.abspath(__file__))
TEXTDIR = os.path.join(HERE, "texts")

TITLE = "Poems to Cherish and Memorize"
SUBTITLE = "A curated expansion from three seed poems"
BOOK_ID = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_DNS, "poems-to-memorize.local"))
TODAY = datetime.date.today().isoformat()

CSS = """\
@page { margin: 5%; }
body { font-family: Georgia, "Iowan Old Style", serif; line-height: 1.5;
       margin: 0 1em; hyphens: auto; }
h1 { font-size: 1.5em; line-height: 1.25; margin: 1.2em 0 0.2em; font-weight: normal; }
h2 { font-size: 1.2em; margin: 1.5em 0 0.3em; font-weight: normal; }
h1.booktitle { font-size: 2em; margin-top: 3em; text-align: center; }
p.subtitle { text-align: center; font-style: italic; color: #555; margin-top: 0; }
p.byline { text-align: center; color: #777; font-size: 0.85em; margin-top: 3em; }
.cat-label { font-size: 0.8em; letter-spacing: 0.12em; text-transform: uppercase;
             color: #888; margin-bottom: 0; }
.poemhead { margin-bottom: 1em; }
.author { font-style: italic; color: #444; margin: 0.1em 0 0.6em; }
dl.meta { font-size: 0.85em; color: #444; margin: 0.8em 0 1.2em;
          border-left: 3px solid #ddd; padding-left: 0.9em; }
dl.meta dt { font-weight: bold; float: left; clear: left; width: 7.5em; }
dl.meta dd { margin: 0 0 0.35em 8em; }
.verse { margin: 1.6em 0 1.6em 0.5em; }
.verse p { margin: 0 0 0.9em; text-indent: 0; }
.line { display: block; text-indent: -1.4em; padding-left: 1.4em; }
.commentary { margin: 1em 0; }
.flag { background: #fff8e5; border: 1px solid #e8d9a8; padding: 0.7em 0.9em;
        font-size: 0.9em; margin: 1.2em 0; }
.nofetch { color: #666; font-size: 0.9em; font-style: italic;
           border-left: 3px solid #eee; padding-left: 0.9em; margin: 1.4em 0; }
ul.links { list-style: none; padding-left: 0; font-size: 0.9em; margin: 1em 0; }
ul.links li { margin-bottom: 0.35em; }
ul.links li:before { content: "\\2192\\00a0"; color: #999; }
a { color: #29527a; text-decoration: none; }
nav ol { list-style: none; padding-left: 1em; }
nav > ol { padding-left: 0; }
nav ol li { margin: 0.3em 0; }
.seed { background: #eef4ee; border: 1px solid #cfe0cf; padding: 0.4em 0.7em;
        font-size: 0.8em; letter-spacing: 0.08em; text-transform: uppercase;
        color: #3d5c3d; display: inline-block; margin-bottom: 0.8em; }
hr { border: 0; border-top: 1px solid #ddd; margin: 2em 0; }
.small { font-size: 0.85em; color: #666; }
ul.further li { margin-bottom: 0.6em; }
p.lede { font-size: 0.8em; letter-spacing: 0.1em; text-transform: uppercase;
         color: #888; margin: 1.8em 0 0.8em; }
.sections { margin: 0 0 1.5em; }
p.sec { margin: 0 0 1.1em; padding-left: 2.1em; text-indent: -2.1em;
        line-height: 1.45; }
.secnum { display: inline-block; width: 1.5em; color: #b08d57;
          font-size: 0.95em; text-indent: 0; }
p.sec a { font-size: 1.05em; }
p.sec .small { color: #666; }
"""


def page(title, body, is_nav=False):
    ns = ' xmlns:epub="http://www.idpf.org/2007/ops"' if is_nav else ""
    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"{ns} lang="en" xml:lang="en">
<head>
<meta charset="utf-8"/>
<title>{html.escape(title)}</title>
<link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body>
{body}
</body>
</html>
"""


def verse_html(text):
    """Render fetched plain text as stanzas, preserving line breaks."""
    stanzas = [s for s in text.replace("\r", "").split("\n\n") if s.strip()]
    out = ['<div class="verse">']
    for st in stanzas:
        lines = [l for l in st.split("\n") if l.strip() != ""]
        if not lines:
            continue
        out.append("<p>")
        for l in lines:
            lead = len(l) - len(l.lstrip())
            style = f' style="padding-left:{lead * 0.5:.1f}em"' if lead > 1 else ""
            out.append(f'<span class="line"{style}>{html.escape(l.strip())}</span>')
        out.append("</p>")
    out.append("</div>")
    return "\n".join(out)


def load_text(cat_id, poem):
    p = os.path.join(TEXTDIR, slug(cat_id, poem) + ".txt")
    if os.path.exists(p):
        t = open(p, encoding="utf-8").read().strip()
        if t:
            return t
    return None


def poem_page(cat, poem):
    sl = slug(cat["id"], poem)
    parts = [f'<p class="cat-label">{html.escape(cat["title"])} &#183; {poem["num"]}</p>']
    if poem.get("seed"):
        parts.append('<p class="seed">Your seed poem</p>')
    parts.append(f'<div class="poemhead"><h1>{html.escape(poem["title"])}</h1>'
                 f'<p class="author">{html.escape(poem["author"])}</p></div>')

    parts.append("<dl class=\"meta\">")
    parts.append(f"<dt>Published</dt><dd>{poem['dates']}</dd>")
    parts.append(f"<dt>Form</dt><dd>{html.escape(poem['form'])}</dd>")
    parts.append(f"<dt>To memorize</dt><dd>{poem['difficulty']}</dd>")
    parts.append("</dl>")

    text = load_text(cat["id"], poem) if poem.get("pd") else None
    if text:
        parts.append(verse_html(text))
    elif poem.get("pd"):
        parts.append('<p class="nofetch">Text not fetched. Run <code>fetch_texts.py</code>, '
                     'or drop the poem into <code>texts/%s.txt</code> yourself.</p>' % sl)
    else:
        parts.append('<p class="nofetch">Still in copyright \u2014 text not included. '
                     'Follow the link below.</p>')

    parts.append(f'<div class="commentary"><p>{poem["why"]}</p></div>')

    if poem.get("flag"):
        parts.append(f'<p class="flag"><strong>Note.</strong> {poem["flag"]}</p>')

    if poem.get("links"):
        parts.append('<ul class="links">')
        for label, url in poem["links"]:
            parts.append(f'<li><a href="{html.escape(url)}">{html.escape(label)}</a></li>')
        parts.append("</ul>")

    return page(f'{poem["title"]} \u2014 {poem["author"]}', "\n".join(parts))


def category_page(cat):
    body = [f'<h1>{cat["title"]}</h1>',
            f'<p class="subtitle">{html.escape(cat["subtitle"])}</p>',
            f"<p>{cat['intro']}</p>"]
    if cat["id"] == "c":
        body.append(DICKINSON_NOTE)
    body.append("<hr/>")
    body.append("<h2>In this section</h2><ol>")
    for p in POEMS[cat["id"]]:
        body.append(f'<li><a href="{slug(cat["id"], p)}.xhtml">'
                    f'{html.escape(p["title"])}</a> '
                    f'<span class="small">\u2014 {html.escape(p["author"])}</span></li>')
    body.append("</ol>")
    if FURTHER.get(cat["id"]):
        body.append("<h2>Also worth your time in this vein</h2><ul class=\"further\">")
        for name, note in FURTHER[cat["id"]]:
            body.append(f"<li><strong>{name}</strong>{(' \u2014 ' + note) if note else ''}</li>")
        body.append("</ul>")
    return page(cat["title"], "\n".join(body))


HOWTO = """
<h1>How to use this book</h1>
<p>Thirty-nine poems \u2014 three seeds plus twelve more in each of their three
categories \u2014 with a further twenty or so named at the end of each section.
Each entry gives the poem's date and source, its form, why it belongs beside
your three, how hard it is to memorize, and a link to an authoritative text.</p>

<p><strong>Which texts are here.</strong> Twenty-six of the thirty-nine are in the public
domain in the United States and their full texts are included. The thirteen in
the Kindness section are under active copyright \u2014 Nye, Walcott, Bass, Gilbert,
Clifton, Berry, Oliver, Howe, Zagajewski, Kinnell, Lam&#233;ris \u2014 and appear here as
commentary and links only. Two of those thirteen have no authorized free text
online at all; they are flagged individually with what to buy instead.</p>

<p><strong>Check the texts before you commit them.</strong> These were pulled from Wikisource
by script. That is more reliable than most of what floats around the web, but it
is not infallible, and the places it fails are exactly the places that matter for
memorization: Dickinson's dashes and capitals, Hopkins's stress accents
(<em>sh&#233;er pl&#243;d</em>, <em>unpertherb&#232;d</em>), Herbert's 1633 spelling. Where a reading
matters to you, check it against the linked edition. A memorized poem inherits
every error in the copy you learned it from.</p>

<p><strong>Difficulty ratings</strong> describe memorization, not comprehension.
<em>Easy</em> means metrical, rhymed, under twenty lines \u2014 it goes in over a few days
and stays. <em>Moderate</em> means longer, or free verse with a strong logical spine.
<em>Hard</em> means long, syntactically knotty, or free verse without much scaffolding.</p>
"""

ORDER = """
<h1>A suggested memorization order</h1>
<p>Early wins first, gradually increasing difficulty, keeping all three lines of
feeling in rotation.</p>

<p><strong>Where your three seeds fit.</strong> Dickinson's \u201cHope\u201d belongs in the first
group \u2014 it is as easy as anything here, and if you don't already have it, get it
first. Nye's \u201cKindness\u201d sits with the harder free verse around 12\u201315. Thompson's
\u201cHound of Heaven\u201d is in a category of its own: 182 irregular lines, more than four
times the length of anything else. Don't start with it, and consider learning it in
movements \u2014 the flight, the failed refuges, the surrender \u2014 rather than whole.</p>

<h2>First five (all under twenty lines, all easy)</h2>
<ol>
<li>Clifton, \u201cblessing the boats\u201d</li>
<li>Herbert, \u201cLove (III)\u201d</li>
<li>Yeats, \u201cThe Lake Isle of Innisfree\u201d</li>
<li>Dickinson, \u201cI'm Nobody! Who are you?\u201d</li>
<li>Berry, \u201cThe Peace of Wild Things\u201d</li>
</ol>

<h2>Next five (still short, slightly more resistance)</h2>
<ol start="6">
<li>Rossetti, \u201cRemember\u201d</li>
<li>Walcott, \u201cLove After Love\u201d</li>
<li>Hopkins, \u201cSpring and Fall\u201d</li>
<li>Housman, \u201cLoveliest of trees\u201d</li>
<li>Clifton, \u201cwon't you celebrate with me\u201d</li>
</ol>

<h2>Then the ones worth the work</h2>
<ol start="11">
<li>Donne, \u201cBatter my heart\u201d</li>
<li>Dickinson, \u201cThere's a certain Slant of light\u201d</li>
<li>Hopkins, \u201cGod's Grandeur\u201d</li>
<li>Hardy, \u201cThe Darkling Thrush\u201d</li>
<li>Bass, \u201cThe Thing Is\u201d</li>
</ol>

<hr/>
<p><strong>Method note.</strong> The metrical poems \u2014 Herbert, Hopkins, Dickinson, Rossetti,
Yeats, Housman, Hardy, Frost, Teasdale \u2014 go in fast and stay, because meter and
rhyme are error-correcting codes: misremember a word and the line stops scanning,
so you know. <strong>Say them aloud.</strong> They were built for the ear, and silent reading
loses the mechanism entirely.</p>

<p>Free verse \u2014 Nye, Walcott, Bass, Gilbert, Berry, Howe, Oliver, Kinnell,
Lam&#233;ris \u2014 has no such safety net. Learn those by <strong>the turns of thought rather
than the line breaks</strong>. Walcott is arrival \u2192 recognition \u2192 feast; Zagajewski is an
escalating imperative; Gilbert is a legal brief with a thesis and evidence. Get
the argument's skeleton first and the words hang on it.</p>
"""


def colophon(counts):
    return f"""
<h1>Colophon</h1>
<p>Compiled {TODAY}. All links checked at time of writing.</p>
<p>{counts['total']} poems: {counts['with_text']} with full text included
({counts['pd']} are public domain in the United States),
{counts['copyright']} under copyright and given as commentary and links only.</p>
<p>Public-domain status noted throughout is for the United States and may differ
where you are. The UK and EU generally use life-of-author-plus-70, which affects
Hopkins, Hardy, Yeats, Teasdale, Frost, and Eliot differently than US law does \u2014
Frost's \u201cNothing Gold Can Stay\u201d is public domain in the US but not in the EU until
2034, and Eliot's \u201cJourney of the Magi\u201d not until 2036.</p>
<p class="small">Texts fetched from Wikisource. Commentary written for this
collection. Built with a script you have a copy of, so you can add to it.</p>
"""


def build(outpath):
    files = {}
    spine = []
    nav_entries = []

    files["style.css"] = CSS

    files["title.xhtml"] = page(TITLE,
        f'<h1 class="booktitle">{TITLE}</h1>'
        f'<p class="subtitle">{SUBTITLE}</p>'
        f'<p class="byline">Francis Thompson &#183; Naomi Shihab Nye &#183; Emily Dickinson<br/>'
        f'and thirty-six others</p>')
    spine.append("title.xhtml")

    files["howto.xhtml"] = page("How to use this book", HOWTO)
    spine.append("howto.xhtml")
    nav_entries.append(("How to use this book", "howto.xhtml", []))

    counts = dict(total=0, with_text=0, pd=0, copyright=0)

    for cat in CATEGORIES:
        cid = cat["id"]
        catfile = f"cat-{cid}.xhtml"
        files[catfile] = category_page(cat)
        spine.append(catfile)

        children = []
        for poem in POEMS[cid]:
            sl = slug(cid, poem)
            fn = f"{sl}.xhtml"
            files[fn] = poem_page(cat, poem)
            spine.append(fn)
            children.append((f'{poem["title"]} \u2014 {poem["author"]}', fn, []))

            counts["total"] += 1
            if poem.get("pd"):
                counts["pd"] += 1
                if load_text(cid, poem):
                    counts["with_text"] += 1
            else:
                counts["copyright"] += 1

        nav_entries.append((cat["title"], catfile, children))

    files["order.xhtml"] = page("A suggested memorization order", ORDER)
    spine.append("order.xhtml")
    nav_entries.append(("A suggested memorization order", "order.xhtml", []))

    files["colophon.xhtml"] = page("Colophon", colophon(counts))
    spine.append("colophon.xhtml")
    nav_entries.append(("Colophon", "colophon.xhtml", []))

    # ---- nav.xhtml (EPUB 3 TOC, and a visible contents page in the spine) ----
    def nav_ol(entries, depth=0):
        pad = "  " * depth
        out = [f"{pad}<ol>"]
        for label, href, kids in entries:
            out.append(f'{pad}  <li><a href="{href}">{html.escape(label)}</a>')
            if kids:
                out.append(nav_ol(kids, depth + 2))
            out.append(f"{pad}  </li>")
        out.append(f"{pad}</ol>")
        return "\n".join(out)

    # A section summary up top, so the first thing you see is the three lines
    # of feeling rather than a wall of thirty-nine titles.
    seeds = {"a": "Francis Thompson, \u201cThe Hound of Heaven\u201d",
             "b": "Naomi Shihab Nye, \u201cKindness\u201d",
             "c": "Emily Dickinson, \u201c\u2018Hope\u2019 is the thing with feathers\u201d"}
    summary = ['<p class="lede">Three sections, one growing out of each poem '
               'you started with.</p>', '<div class="sections">']
    for n, cat in enumerate(CATEGORIES, 1):
        cid = cat["id"]
        poems = POEMS[cid]
        npd = sum(1 for p in poems if p.get("pd"))
        ntx = sum(1 for p in poems if p.get("pd") and load_text(cid, p))
        if npd == 0:
            texts_note = "all still in copyright \u2014 commentary and links only"
        elif ntx == npd:
            texts_note = f"all {npd} public domain, full texts included"
        elif ntx:
            texts_note = f"{ntx} of {npd} public-domain texts included"
        else:
            texts_note = f"{npd} public domain \u2014 run fetch_texts.py for the texts"
        summary.append(
            f'<p class="sec"><span class="secnum">{n}</span>'
            f'<a href="cat-{cid}.xhtml"><strong>{html.escape(cat["title"])}</strong></a><br/>'
            f'<span class="small">{html.escape(cat["subtitle"])}</span><br/>'
            f'<span class="small">Grows out of {seeds[cid]} \u00b7 '
            f'{len(poems)} poems \u00b7 {texts_note}</span></p>')
    summary.append("</div>")
    summary.append('<hr/><p class="lede">Everything, in order</p>')

    nav_body = ('<nav epub:type="toc" id="toc">\n<h1>Contents</h1>\n'
                + "\n".join(summary) + "\n"
                + nav_ol(nav_entries) + "\n</nav>")
    files["nav.xhtml"] = page("Contents", nav_body, is_nav=True)

    # Put it in the reading order too, so paging forward from the title page
    # lands on Contents rather than skipping straight to the first section.
    spine.insert(1, "nav.xhtml")

    # ---- toc.ncx (EPUB 2 fallback, for older readers) ----
    navpoints, counter = [], [0]

    def ncx(entries, depth=1):
        out = []
        for label, href, kids in entries:
            counter[0] += 1
            i = counter[0]
            out.append(f'<navPoint id="np{i}" playOrder="{i}">'
                       f'<navLabel><text>{html.escape(label)}</text></navLabel>'
                       f'<content src="{href}"/>')
            if kids:
                out.append(ncx(kids, depth + 1))
            out.append("</navPoint>")
        return "\n".join(out)

    navpoints = ncx(nav_entries)
    files["toc.ncx"] = f"""<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
<head>
<meta name="dtb:uid" content="{BOOK_ID}"/>
<meta name="dtb:depth" content="2"/>
<meta name="dtb:totalPageCount" content="0"/>
<meta name="dtb:maxPageNumber" content="0"/>
</head>
<docTitle><text>{TITLE}</text></docTitle>
<navMap>
{navpoints}
</navMap>
</ncx>
"""

    # ---- content.opf ----
    manifest, spine_items = [], []
    manifest.append('<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>')
    manifest.append('<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>')
    manifest.append('<item id="css" href="style.css" media-type="text/css"/>')
    for i, fn in enumerate(spine):
        if fn == "nav.xhtml":
            # already in the manifest above, with properties="nav"
            spine_items.append('<itemref idref="nav"/>')
            continue
        iid = f"x{i}"
        manifest.append(f'<item id="{iid}" href="{fn}" media-type="application/xhtml+xml"/>')
        spine_items.append(f'<itemref idref="{iid}"/>')

    files["content.opf"] = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:identifier id="bookid">{BOOK_ID}</dc:identifier>
<dc:title>{TITLE}</dc:title>
<dc:language>en</dc:language>
<dc:creator>Various</dc:creator>
<dc:description>{SUBTITLE}</dc:description>
<dc:date>{TODAY}</dc:date>
<meta property="dcterms:modified">{datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}</meta>
</metadata>
<manifest>
{chr(10).join(manifest)}
</manifest>
<spine toc="ncx">
{chr(10).join(spine_items)}
</spine>
</package>
"""

    # ---- zip it ----
    with zipfile.ZipFile(outpath, "w") as z:
        # mimetype must be first and stored uncompressed
        zi = zipfile.ZipInfo("mimetype")
        zi.compress_type = zipfile.ZIP_STORED
        z.writestr(zi, "application/epub+zip")
        z.writestr("META-INF/container.xml",
                   '<?xml version="1.0" encoding="utf-8"?>\n'
                   '<container version="1.0" '
                   'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
                   '<rootfiles><rootfile full-path="OEBPS/content.opf" '
                   'media-type="application/oebps-package+xml"/></rootfiles>\n'
                   '</container>\n', zipfile.ZIP_DEFLATED)
        for name, content in files.items():
            z.writestr("OEBPS/" + name, content, zipfile.ZIP_DEFLATED)

    return counts


if __name__ == "__main__":
    out = "poems-to-memorize.epub"
    if "-o" in sys.argv:
        out = sys.argv[sys.argv.index("-o") + 1]
    c = build(out)
    print(f"wrote {out}")
    print(f"  {c['total']} poems")
    print(f"  {c['with_text']} with full text ({c['pd']} public domain)")
    print(f"  {c['copyright']} copyright, links only")
    if c["with_text"] < c["pd"]:
        print(f"\n  {c['pd'] - c['with_text']} public-domain texts still missing.")
        print("  Run:  python3 fetch_texts.py")
