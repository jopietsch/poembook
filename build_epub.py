#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_epub.py -- assemble a browse or memorize EPUB

Reads the metadata in poems.py and any poem texts sitting in texts/, and writes
a valid EPUB 3 with a nested table of contents (category -> poem).

Run fetch_texts.py first if you want all public-domain texts included.
Without it the browse edition still contains the complete commentary catalog.

Usage:
    python3 build_epub.py [--edition browse|memorize] [-o output.epub]
"""

import os
import sys
import html
import zipfile
import datetime
import uuid
import json
from pathlib import Path

from poems import CATEGORIES, POEMS, FURTHER, DICKINSON_NOTE, slug

HERE = os.path.dirname(os.path.abspath(__file__))
TEXTDIR = os.path.join(HERE, "texts")
PROGRESS_PATH = Path(HERE) / ".poembook-progress.json"
ASSETDIR = Path(HERE) / "assets"

TITLE = "Poems to Cherish and Memorize"
SUBTITLE = "A curated collection in six thematic threads"
BOOK_ID = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_DNS, "poems-to-memorize.local"))

CSS = """\
@page { margin: 5%; }
body { font-family: Georgia, "Iowan Old Style", serif; line-height: 1.5;
       margin: 0 1em; hyphens: auto; }
h1 { font-size: 1.5em; line-height: 1.25; margin: 1.2em 0 0.2em; font-weight: normal; }
h2 { font-size: 1.2em; margin: 1.5em 0 0.3em; font-weight: normal; }
h1.booktitle { font-size: 2em; margin-top: 3em; text-align: center; }
p.subtitle { text-align: center; font-style: italic; color: #555; margin-top: 0; }
p.byline { text-align: center; color: #777; font-size: 0.85em; margin-top: 3em; }
p.updated { text-align: center; color: #666; font-size: 0.8em; margin-top: 1em; }
.cat-label { font-size: 0.8em; letter-spacing: 0.12em; text-transform: uppercase;
             color: #888; margin-bottom: 0; }
.poemhead { margin-bottom: 1em; }
.author { font-style: italic; color: #444; margin: 0.1em 0 0.6em; }
dl.meta { font-size: 0.85em; color: #444; margin: 0.8em 0 1.2em;
          border-left: 3px solid #ddd; padding-left: 0.9em; }
dl.meta dt { font-weight: bold; float: left; clear: left; width: 7.5em; }
dl.meta dd { margin: 0 0 0.35em 8em; }
.verse { margin: 1.6em 0; hyphens: none; text-align: left; }
.verse p { margin: 0 0 0.9em; text-indent: 0; }
.line { display: block; text-indent: -0.8em; padding-left: 0.8em; }
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
.practice-label { font-size: 0.8em; letter-spacing: 0.1em; text-transform: uppercase;
                  margin: 1.2em 0 0.5em; }
.memory-aid { line-height: 1.35; }
.memory-aid p { margin: 0 0 0.8em; }
"""

MEMORIZE_CSS = CSS + """\
@page { margin: 2%; }
body { line-height: 1.4; margin: 0 0.35em; }
h1 { margin-top: 0.35em; }
.poemhead { margin-bottom: 0.7em; }
.verse { margin-top: 0.8em; }
.reference { border-top: 1px solid #999; margin-top: 1.6em; padding-top: 0.7em;
             font-size: 0.85em; }
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
        # Never publish a structurally suspect scrape merely because it exists.
        from poembook_cli import text_issues
        cat = next(c for c in CATEGORIES if c["id"] == cat_id)
        if t and not text_issues(cat, poem, t):
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


def memorize_poem_page(cat, poem, text):
    """Render a distraction-free, text-first poem page for pocket practice."""
    sid = slug(cat["id"], poem)
    sidecar = Path(TEXTDIR) / f"{sid}.json"
    verification = "not editorially verified"
    if sidecar.exists():
        from poembook_cli import verification_level
        level = verification_level(json.loads(sidecar.read_text(encoding="utf-8")))
        verification = ("editorially verified" if level == "editorial" else
                        "source-compared; final editorial review pending" if level == "source" else
                        "structurally checked; source comparison pending")
    parts = [f'<div class="poemhead"><h1>{html.escape(poem["title"])}</h1>',
             f'<p class="author">{html.escape(poem["author"])}</p></div>',
             verse_html(text),
             '<div class="reference">',
             f'<p>{html.escape(cat["title"])} &#183; {poem["num"]}<br/>'
             f'<strong>Published:</strong> {poem["dates"]}<br/>'
             f'<strong>Form:</strong> {html.escape(poem["form"])}<br/>'
             f'<strong>To memorize:</strong> {poem["difficulty"]}<br/>'
             f'<strong>Text:</strong> {verification}</p>',
             '</div>']
    return page(f'{poem["title"]} \u2014 {poem["author"]}', "\n".join(parts))


def memory_aid_html(text):
    from poembook_cli import practice_text

    def aid_lines(mode):
        rendered = practice_text(text, mode)
        return verse_html(rendered).replace('class="verse"', 'class="verse memory-aid"')

    return (f'<p class="practice-label">Stanza openings</p>{aid_lines("stanza-starts")}'
            f'<hr/><p class="practice-label">First words</p>{aid_lines("first-words")}'
            f'<hr/><p class="practice-label">Blank structure</p>{aid_lines("structure")}')


def memory_map_html(poem, text):
    cues = poem.get("memory_map")
    if not cues:
        stanzas = [stanza for stanza in text.replace("\r", "").split("\n\n")
                   if stanza.strip()]
        cues = [stanza.splitlines()[0].strip() for stanza in stanzas]
    items = "".join(f"<li>{html.escape(cue)}</li>" for cue in cues)
    return f'<p class="practice-label">Memory map</p><ol>{items}</ol>'


def memorize_aid_page(poem, text):
    body = (f'<h1>{html.escape(poem["title"])}: Recall</h1>'
            f'<p class="author">{html.escape(poem["author"])}</p>'
            f'{memory_map_html(poem, text)}<hr/>'
            f'{memory_aid_html(text)}'
            '<hr/><p class="practice-label">Could I recite it?</p>'
            '<p><strong>Easy</strong> — move on · <strong>Hesitant</strong> — bookmark this page · '
            '<strong>Failed</strong> — return to the full text</p>')
    return page(f'{poem["title"]}: Recall', body)


def movement_pages(poem, text):
    lines = [line for line in text.splitlines() if line.strip()]
    if len(lines) < 80:
        return []
    stanzas = [stanza for stanza in text.replace("\r", "").split("\n\n") if stanza.strip()]
    labels = poem.get("memory_map") or [f"Movement {index}" for index in range(1, len(stanzas) + 1)]
    return [(labels[index] if index < len(labels) else f"Movement {index + 1}", stanza)
            for index, stanza in enumerate(stanzas)]


def rotation_page(progress):
    groups = (("Learning now", "learning"), ("Review", "memorized"),
              ("Next", "want-to-learn"))
    found = []
    for heading, state in groups:
        entries = []
        for cat in CATEGORIES:
            for poem in POEMS[cat["id"]]:
                sid = slug(cat["id"], poem)
                entry = progress.get(sid, {})
                due = entry.get("next_review", "") <= datetime.date.today().isoformat()
                if (entry.get("state") == state and load_text(cat["id"], poem)
                        and (state != "memorized" or due)):
                    entries.append(f'<li><a href="{sid}.xhtml">{html.escape(poem["title"])}</a> '
                                   f'<span class="small">— {html.escape(poem["author"])}</span></li>')
        if entries:
            found.extend([f"<h2>{heading}</h2>", "<ol>", *entries, "</ol>"])
    if not found:
        found.append("<p>No active rotation yet. Use <code>poembook status SLUG learning</code> "
                     "and rebuild this edition.</p>")
    return page("Current rotation", "<h1>Current rotation</h1>" + "\n".join(found))


def index_pages():
    records = [(cat, poem, slug(cat["id"], poem)) for cat in CATEGORIES for poem in POEMS[cat["id"]]]

    def links(items):
        return "<ol>" + "".join(
            f'<li><a href="{sid}.xhtml">{html.escape(poem["title"])}</a> '
            f'<span class="small">— {html.escape(poem["author"])}</span></li>'
            for _cat, poem, sid in items) + "</ol>"

    by_author = sorted(records, key=lambda item: (item[1]["author"], item[1]["title"]))
    first_lines = [(cat, poem, sid, load_text(cat["id"], poem)) for cat, poem, sid in records]
    first_lines = [item for item in first_lines if item[3]]
    first_body = "<ol>" + "".join(
        f'<li>“<a href="{sid}.xhtml">{html.escape(text.splitlines()[0].strip())}</a>” '
        f'<span class="small">— {html.escape(poem["author"])}</span></li>'
        for cat, poem, sid, text in sorted(first_lines, key=lambda item: item[3].lower())) + "</ol>"

    difficulty = sorted(records, key=lambda item: (item[1]["difficulty"], item[1]["title"]))
    difficulty_body = "<ol>" + "".join(
        f'<li><a href="{sid}.xhtml">{html.escape(poem["title"])}</a><br/>'
        f'<span class="small">{html.escape(poem["difficulty"])} · '
        f'{html.escape(poem["form"])}</span></li>'
        for cat, poem, sid in difficulty) + "</ol>"
    included = [item for item in records if load_text(item[0]["id"], item[1])]
    link_only = [item for item in records if not load_text(item[0]["id"], item[1])]
    availability_body = (f'<h2>Full text included ({len(included)})</h2>{links(included)}'
                         f'<h2>Commentary and links only ({len(link_only)})</h2>{links(link_only)}')
    def line_count(item):
        cat, poem, _sid = item
        text = load_text(cat["id"], poem)
        return len([line for line in text.splitlines() if line.strip()]) if text else 10000

    length = sorted(records, key=lambda item: (line_count(item), item[1]["title"]))
    length_body = "<ol>" + "".join(
        f'<li><a href="{sid}.xhtml">{html.escape(poem["title"])}</a> '
        f'<span class="small">— {html.escape(poem["form"])}</span></li>'
        for cat, poem, sid in length) + "</ol>"
    themes = []
    for cat in CATEGORIES:
        items = [item for item in records if item[0]["id"] == cat["id"]]
        themes.append(f'<h2>{html.escape(cat["title"])}</h2>{links(items)}')
    return {
        "index-authors.xhtml": page("Index by author", "<h1>Authors</h1>" + links(by_author)),
        "index-first-lines.xhtml": page("Index by first line", "<h1>First lines</h1>" + first_body),
        "index-difficulty.xhtml": page("Index by difficulty", "<h1>Difficulty and form</h1>" + difficulty_body),
        "index-length.xhtml": page("Index by length", "<h1>Length</h1>" + length_body),
        "index-themes.xhtml": page("Index by theme", "<h1>Themes</h1>" + "".join(themes)),
        "index-availability.xhtml": page("Index by availability", "<h1>Text availability</h1>" + availability_body),
    }


def category_page(cat, poems=None, compact=False):
    poems = POEMS[cat["id"]] if poems is None else poems
    body = [f'<h1>{cat["title"]}</h1>',
            f'<p class="subtitle">{html.escape(cat["subtitle"])}</p>']
    if not compact:
        body.append(f"<p>{cat['intro']}</p>")
    if cat["id"] == "c" and not compact:
        body.append(DICKINSON_NOTE)
    body.append("<hr/>")
    body.append("<h2>In this section</h2><ol>")
    for p in poems:
        body.append(f'<li><a href="{slug(cat["id"], p)}.xhtml">'
                    f'{html.escape(p["title"])}</a> '
                    f'<span class="small">\u2014 {html.escape(p["author"])}</span></li>')
    body.append("</ol>")
    if FURTHER.get(cat["id"]) and not compact:
        body.append("<h2>Also worth your time in this vein</h2><ul class=\"further\">")
        for name, note in FURTHER[cat["id"]]:
            body.append(f"<li><strong>{name}</strong>{(' \u2014 ' + note) if note else ''}</li>")
        body.append("</ul>")
    return page(cat["title"], "\n".join(body))


HOWTO = """
<h1>How to use this book</h1>
<p>A growing collection organized into six thematic threads: five seed works,
plus a path through Rilke. Each entry gives the poem's date
and source, form, commentary, memorization difficulty, and authoritative links.</p>

<p><strong>Which texts are here.</strong> Public-domain texts are included when available;
works under active copyright appear as commentary and authorized links only.</p>

<p><strong>Check the texts before you commit them.</strong> These were extracted by script
from recorded Wikisource or Project Gutenberg editions. That is more reliable than most of what floats around the web, but it
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
<h1>Recommended poems to start with</h1>
<p><strong>Start with Emily Dickinson's <a href="cs0.xhtml">\u201cHope\u201d is the thing with feathers</a>.</strong>
It is short, musical, and built on one image, so its meter and rhyme give you
plenty of cues. If you already know it, begin with George Herbert's
<a href="a1.xhtml">\u201cLove (III).\u201d</a></p>

<p>The sequence below favors early wins, then gradually adds length and
resistance while keeping the book's different threads of feeling in rotation.
You do not need to follow it rigidly: a poem you urgently want to know is often
easier to learn than a technically simpler poem you merely admire.</p>

<p><strong>Where the original three seeds fit.</strong> Dickinson's
<a href="cs0.xhtml">\u201cHope\u201d</a> belongs in the first
group \u2014 it is as easy as anything here, and if you don't already have it, get it
first. Nye's <a href="bs0.xhtml">\u201cKindness\u201d</a> sits with the harder free verse
around 12\u201315. Thompson's <a href="as0.xhtml">\u201cHound of Heaven\u201d</a> is in a
category of its own: 182 irregular lines, more than four
times the length of anything else. Don't start with it, and consider learning it in
movements \u2014 the flight, the failed refuges, the surrender \u2014 rather than whole.</p>

<h2>Your first five after \u201cHope\u201d</h2>
<ol>
<li><strong><a href="a1.xhtml">Herbert, \u201cLove (III)\u201d</a></strong> \u2014 eighteen lines, gentle dialogue, and a clear emotional turn.</li>
<li><strong><a href="b4.xhtml">Clifton, \u201cblessing the boats\u201d</a></strong> \u2014 thirteen spare lines that move like a spoken blessing.</li>
<li><strong><a href="c9.xhtml">Yeats, \u201cThe Lake Isle of Innisfree\u201d</a></strong> \u2014 three musical quatrains with strong sensory landmarks.</li>
<li><strong><a href="c4.xhtml">Dickinson, \u201cI'm Nobody! Who are you?\u201d</a></strong> \u2014 brief, playful, and rhythmically adhesive.</li>
<li><strong><a href="b6.xhtml">Berry, \u201cThe Peace of Wild Things\u201d</a></strong> \u2014 plainspoken free verse with a simple movement from fear to rest.</li>
</ol>

<h2>Next five (still short, slightly more resistance)</h2>
<ol start="6">
<li><a href="c8.xhtml">Rossetti, \u201cRemember\u201d</a></li>
<li><a href="b1.xhtml">Walcott, \u201cLove After Love\u201d</a></li>
<li><a href="c7.xhtml">Hopkins, \u201cSpring and Fall\u201d</a></li>
<li><a href="c10.xhtml">Housman, \u201cLoveliest of trees\u201d</a></li>
<li><a href="b5.xhtml">Clifton, \u201cwon't you celebrate with me\u201d</a></li>
</ol>

<h2>Then the ones worth the work</h2>
<ol start="11">
<li><a href="a4.xhtml">Donne, \u201cBatter my heart\u201d</a></li>
<li><a href="c2.xhtml">Dickinson, \u201cThere's a certain Slant of light\u201d</a></li>
<li><a href="a5.xhtml">Hopkins, \u201cGod's Grandeur\u201d</a></li>
<li><a href="c6.xhtml">Hardy, \u201cThe Darkling Thrush\u201d</a></li>
<li><a href="b2.xhtml">Bass, \u201cThe Thing Is\u201d</a></li>
</ol>

<h2>Choose a short path</h2>
<p><strong>Five easy wins:</strong> <a href="cs0.xhtml">“Hope”</a>,
<a href="a1.xhtml">“Love (III)”</a>, <a href="c4.xhtml">“I'm Nobody!”</a>,
<a href="c9.xhtml">“The Lake Isle of Innisfree”</a>, and
<a href="c11.xhtml">“Nothing Gold Can Stay.”</a></p>
<p><strong>Grief toward consolation:</strong> <a href="c7.xhtml">“Spring and Fall”</a>,
<a href="c8.xhtml">“Remember”</a>, <a href="b6.xhtml">“The Peace of Wild Things”</a>,
and <a href="b1.xhtml">“Love After Love.”</a></p>
<p><strong>Prayer and struggle:</strong> <a href="a1.xhtml">“Love (III)”</a>,
<a href="a2.xhtml">“The Collar”</a>, <a href="a4.xhtml">“Batter my heart”</a>,
and <a href="a7.xhtml">“Carrion Comfort.”</a></p>
<p><strong>Attention and transformation:</strong> <a href="c9.xhtml">“Innisfree”</a>,
<a href="d1.xhtml">“Archaic Torso of Apollo”</a>, and the Rilke sequence that follows it.</p>
<p><strong>A one-month sequence:</strong> week 1 — <a href="cs0.xhtml">“Hope”</a>;
week 2 — <a href="a1.xhtml">“Love (III)”</a>; week 3 —
<a href="c9.xhtml">“Innisfree”</a>; week 4 — review all three, then choose the next
poem from whichever thread still feels alive.</p>

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


def colophon(counts, compiled_date):
    return f"""
<h1>Colophon</h1>
<p>Compiled {compiled_date}.</p>
<p>{counts['total']} poems: {counts['with_text']} with full text included
({counts['pd']} are public domain in the United States),
{counts['copyright']} under copyright and given as commentary and links only.</p>
<p>Public-domain status noted throughout is for the United States and may differ
where you are. The UK and EU generally use life-of-author-plus-70, which affects
Hopkins, Hardy, Yeats, Teasdale, Frost, and Eliot differently than US law does \u2014
Frost's \u201cNothing Gold Can Stay\u201d is public domain in the US but not in the EU until
2034, and Eliot's \u201cJourney of the Magi\u201d not until 2036.</p>
<p class="small">Texts extracted from the source editions recorded in their
sidecars. Commentary written for this collection. Built with a script you have
a copy of, so you can add to it.</p>
"""


def build(outpath, edition="browse", progress=None):
    if edition not in ("browse", "memorize"):
        raise ValueError(f"unknown EPUB edition: {edition}")

    files = {}
    spine = []
    nav_entries = []
    is_memorize = edition == "memorize"
    included_poems = [p for c in CATEGORIES for p in POEMS[c["id"]]
                      if not is_memorize or (p.get("pd") and load_text(c["id"], p))]
    total_poems = len(included_poems)
    book_id = (BOOK_ID if not is_memorize else
               "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_DNS,
                                             "poems-to-memorize.local.memorize")))

    book_title = f"{TITLE} \u2014 {'Memorize' if is_memorize else 'Browse'}"
    book_subtitle = ("A pocket practice edition with recall cues" if is_memorize
                     else SUBTITLE)
    files["style.css"] = MEMORIZE_CSS if is_memorize else CSS
    cover_path = ASSETDIR / f"cover-{edition}.png"
    if cover_path.exists():
        files["cover.png"] = cover_path.read_bytes()
    source_paths = [Path(__file__), Path(HERE) / "poems.py"]
    source_paths.extend(Path(TEXTDIR).glob("*"))
    if cover_path.exists():
        source_paths.append(cover_path)
    latest_mtime = max(path.stat().st_mtime for path in source_paths if path.is_file())
    modified_dt = datetime.datetime.fromtimestamp(latest_mtime, datetime.timezone.utc)
    local_modified = datetime.datetime.fromtimestamp(latest_mtime).astimezone()
    compiled_date = local_modified.date().isoformat()
    updated_label = local_modified.strftime("%Y-%m-%d %I:%M %p %Z").replace(" 0", " ", 1)
    modified_stamp = modified_dt.replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
    byline = (f'<p class="byline">{total_poems} poems for pocket practice</p>'
              if is_memorize else
              f'<p class="byline">{total_poems} poems in {len(CATEGORIES)} thematic threads</p>')

    files["title.xhtml"] = page(book_title,
        f'<h1 class="booktitle">{book_title}</h1>'
        f'<p class="subtitle">{book_subtitle}</p>'
        f'{byline}'
        f'<p class="updated">Last updated {updated_label}</p>')
    spine.append("title.xhtml")

    memorize_howto = """
<h1>How to use this edition</h1>
<p>This pocket edition contains poems whose full texts are available locally.
Each poem is followed by a recall chapter: first read or recite the poem, then
advance one chapter to test yourself from its first words and initials.</p>
<p>Long-press a page-turn button to move by chapter. Bookmark poems in your
current rotation. For fidelity, texts awaiting final human word-for-word review
should be checked against the source named in the Browse edition before you
commit them to memory.</p>
"""
    files["howto.xhtml"] = page("How to use this book",
                                memorize_howto if is_memorize else HOWTO)
    spine.append("howto.xhtml")
    nav_entries.append(("How to use this book", "howto.xhtml", []))

    if is_memorize:
        if progress is None:
            progress = (json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
                        if PROGRESS_PATH.exists() else {})
        files["rotation.xhtml"] = rotation_page(progress)
        spine.append("rotation.xhtml")
        nav_entries.append(("Current rotation", "rotation.xhtml", []))

    counts = dict(total=0, with_text=0, pd=0, copyright=0)

    for cat in CATEGORIES:
        cid = cat["id"]
        catfile = f"cat-{cid}.xhtml"
        category_poems = POEMS[cid]
        if is_memorize:
            category_poems = [p for p in category_poems
                              if p.get("pd") and load_text(cid, p)]
            if not category_poems:
                continue
        files[catfile] = category_page(cat, category_poems, compact=is_memorize)
        spine.append(catfile)

        children = []
        for poem in POEMS[cid]:
            sl = slug(cid, poem)
            text = load_text(cid, poem) if poem.get("pd") else None
            if is_memorize and not text:
                continue
            fn = f"{sl}.xhtml"
            files[fn] = (memorize_poem_page(cat, poem, text) if is_memorize
                         else poem_page(cat, poem))
            spine.append(fn)
            children.append((f'{poem["title"]} \u2014 {poem["author"]}', fn, []))

            if is_memorize:
                for movement_number, (label, movement_text) in enumerate(
                        movement_pages(poem, text), 1):
                    movement_fn = f"{sl}-movement-{movement_number}.xhtml"
                    movement_body = (f'<h1>{html.escape(poem["title"])}: '
                                     f'{html.escape(label)}</h1>'
                                     f'<p class="author">{html.escape(poem["author"])}</p>'
                                     f'{verse_html(movement_text)}')
                    files[movement_fn] = page(f'{poem["title"]}: {label}', movement_body)
                    spine.append(movement_fn)
                aid_fn = f"{sl}-recall.xhtml"
                files[aid_fn] = memorize_aid_page(poem, text)
                spine.append(aid_fn)

            counts["total"] += 1
            if poem.get("pd"):
                counts["pd"] += 1
                if load_text(cid, poem):
                    counts["with_text"] += 1
            else:
                counts["copyright"] += 1

        if children:
            nav_entries.append((cat["title"], catfile, children))

    if not is_memorize:
        indexes = index_pages()
        files.update(indexes)
        index_entries = [
            ("Authors", "index-authors.xhtml", []),
            ("First lines", "index-first-lines.xhtml", []),
            ("Difficulty and form", "index-difficulty.xhtml", []),
            ("Length", "index-length.xhtml", []),
            ("Themes", "index-themes.xhtml", []),
            ("Text availability", "index-availability.xhtml", []),
        ]
        for _label, filename, _children in index_entries:
            spine.append(filename)
        nav_entries.append(("Indexes", "index-authors.xhtml", index_entries))

        files["order.xhtml"] = page("Recommended poems to start with", ORDER)
        spine.append("order.xhtml")
        nav_entries.append(("Recommended poems to start with", "order.xhtml", []))

    files["colophon.xhtml"] = page("Colophon", colophon(counts, compiled_date))
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

    # A section summary up top, so the first thing you see is the thematic lines
    # of feeling rather than a wall of titles.
    seeds = {"a": "Francis Thompson, \u201cThe Hound of Heaven\u201d",
             "b": "Naomi Shihab Nye, \u201cKindness\u201d",
             "c": "Emily Dickinson, \u201c\u2018Hope\u2019 is the thing with feathers\u201d",
             "d": "Rilke's poems of solitude and transformation",
             "e": "\u201cSaint Patrick's Breastplate\u201d",
             "f": "Saint Francis, \u201cThe Canticle of the Sun\u201d"}
    summary = [('<p class="lede">Practice by theme.</p>' if is_memorize else
                f'<p class="lede">{len(CATEGORIES)} sections, each growing out of a seed work.</p>'),
               '<div class="sections">']
    for n, cat in enumerate(CATEGORIES, 1):
        cid = cat["id"]
        poems = POEMS[cid]
        if is_memorize:
            poems = [p for p in poems if p.get("pd") and load_text(cid, p)]
            if not poems:
                continue
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
    summary.append('<hr/><p class="lede">Poems</p>' if is_memorize else
                   '<hr/><p class="lede">Everything, in order</p>')

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
<meta name="dtb:uid" content="{book_id}"/>
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
    if "cover.png" in files:
        manifest.append('<item id="cover" href="cover.png" media-type="image/png" properties="cover-image"/>')
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
<dc:identifier id="bookid">{book_id}</dc:identifier>
<dc:title>{book_title}</dc:title>
<dc:language>en</dc:language>
<dc:creator>Various</dc:creator>
<dc:description>{book_subtitle}</dc:description>
<dc:date>{compiled_date}</dc:date>
{'<meta name="cover" content="cover"/>' if "cover.png" in files else ''}
<meta property="dcterms:modified">{modified_stamp}</meta>
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
        zip_time = max((1980, 1, 1, 0, 0, 0), modified_dt.timetuple()[:6])

        def write_entry(name, content, compression=zipfile.ZIP_DEFLATED):
            entry = zipfile.ZipInfo(name, date_time=zip_time)
            entry.compress_type = compression
            z.writestr(entry, content)

        # mimetype must be first and stored uncompressed
        write_entry("mimetype", "application/epub+zip", zipfile.ZIP_STORED)
        write_entry("META-INF/container.xml",
                   '<?xml version="1.0" encoding="utf-8"?>\n'
                   '<container version="1.0" '
                   'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
                   '<rootfiles><rootfile full-path="OEBPS/content.opf" '
                   'media-type="application/oebps-package+xml"/></rootfiles>\n'
                   '</container>\n')
        for name, content in files.items():
            write_entry("OEBPS/" + name, content)

    return counts


if __name__ == "__main__":
    edition = "browse"
    if "--edition" in sys.argv:
        edition = sys.argv[sys.argv.index("--edition") + 1]
    out = f"poembook-{edition}.epub"
    if "-o" in sys.argv:
        out = sys.argv[sys.argv.index("-o") + 1]
    c = build(out, edition=edition)
    print(f"wrote {out}")
    print(f"  {c['total']} poems")
    print(f"  {c['with_text']} with full text ({c['pd']} public domain)")
    print(f"  {c['copyright']} copyright, links only")
    if c["with_text"] < c["pd"]:
        print(f"\n  {c['pd'] - c['with_text']} public-domain texts still missing.")
        print("  Run:  python3 fetch_texts.py")
