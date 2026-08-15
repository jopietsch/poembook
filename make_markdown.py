#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_markdown.py -- emit the markdown edition, with table of contents.

Same data as the EPUB, so the two never drift apart. Public-domain texts are
included if present in texts/; copyrighted poems stay link-only.

Usage:  python3 make_markdown.py [-o poems-to-memorize.md]
"""

import os
import re
import sys
import datetime
from pathlib import Path

from poems import CATEGORIES, POEMS, FURTHER, slug

HERE = os.path.dirname(os.path.abspath(__file__))
TEXTDIR = os.path.join(HERE, "texts")


def detag(s):
    s = re.sub(r"</?strong>", "**", s)
    s = re.sub(r"</?em>", "*", s)
    s = s.replace("&amp;", "&").replace("&#233;", "\u00e9").replace("&#183;", "\u00b7")
    s = re.sub(r"<[^>]+>", "", s)
    return s


def anchor(text):
    a = text.lower()
    a = re.sub(r"[^\w\s-]", "", a)
    return re.sub(r"\s+", "-", a).strip("-")


def load_text(cid, poem):
    p = os.path.join(TEXTDIR, slug(cid, poem) + ".txt")
    if os.path.exists(p):
        t = open(p, encoding="utf-8").read().strip()
        from poembook_cli import text_issues
        cat = next(c for c in CATEGORIES if c["id"] == cid)
        if t and not text_issues(cat, poem, t):
            return t
    return None


def main():
    out = "poems-to-memorize.md"
    if "-o" in sys.argv:
        out = sys.argv[sys.argv.index("-o") + 1]

    n_pd = sum(1 for c in CATEGORIES for p in POEMS[c["id"]] if p.get("pd"))
    n_txt = sum(1 for c in CATEGORIES for p in POEMS[c["id"]]
                if p.get("pd") and load_text(c["id"], p))
    n_c = sum(1 for c in CATEGORIES for p in POEMS[c["id"]] if not p.get("pd"))
    n_total = n_pd + n_c
    source_paths = [Path(__file__), Path(HERE) / "poems.py"]
    source_paths.extend(Path(TEXTDIR).glob("*"))
    latest_mtime = max(path.stat().st_mtime for path in source_paths if path.is_file())
    updated = datetime.datetime.fromtimestamp(latest_mtime).astimezone().strftime(
        "%Y-%m-%d %I:%M %p %Z").replace(" 0", " ", 1)

    L = []
    L.append("# Poems to Cherish and Memorize")
    L.append("### A curated expansion from three seed poems\n")
    L.append(f"*Last updated {updated}*\n")
    L.append("**Original seeds** \u2014 each heads one of the first three categories as entry **\u00a70**:")
    L.append("- Francis Thompson, \u201cThe Hound of Heaven\u201d (1890/1893) \u2192 Category A")
    L.append("- Naomi Shihab Nye, \u201cKindness\u201d (coll. 1995) \u2192 Category B")
    L.append("- Emily Dickinson, \u201c\u2018Hope\u2019 is the thing with feathers\u201d (Fr314) \u2192 Category C")
    L.append("\n---\n")

    # ---------- table of contents ----------
    L.append("## Contents\n")
    L.append("**Four thematic threads, including a new path through Rilke.**\n")

    seeds = {"a": "Thompson, \u201cThe Hound of Heaven\u201d",
             "b": "Nye, \u201cKindness\u201d",
             "c": "Dickinson, \u201c\u2018Hope\u2019 is the thing with feathers\u201d",
             "d": "Rilke's solitude and transformation poems"}
    L.append("| | Section | Grows out of | Poems | Texts |")
    L.append("|---|---|---|---|---|")
    for i, cat in enumerate(CATEGORIES, 1):
        cid = cat["id"]
        ps = POEMS[cid]
        npd = sum(1 for p in ps if p.get("pd"))
        ntx = sum(1 for p in ps if p.get("pd") and load_text(cid, p))
        if npd == 0:
            note = "in copyright \u2014 links only"
        elif ntx == npd:
            note = f"all {npd} included"
        elif ntx:
            note = f"{ntx} of {npd} included"
        else:
            note = f"{npd} PD \u2014 run `fetch_texts.py`"
        L.append(f"| **{i}** | [{detag(cat['title'])}](#{anchor(detag(cat['title']))}) "
                 f"<br/><sub>{cat['subtitle']}</sub> | {seeds[cid]} | {len(ps)} | {note} |")
    L.append("")
    L.append("<details>\n<summary><strong>Everything, in order</strong> "
             "(click to expand)</summary>\n")
    L.append("- [How to use this file](#how-to-use-this-file)")
    for cat in CATEGORIES:
        L.append(f"- **[{detag(cat['title'])}](#{anchor(detag(cat['title']))})** \u2014 "
                 f"*{cat['subtitle'].lower()}*")
        for p in POEMS[cat["id"]]:
            mark = ""
            if p.get("pd") and load_text(cat["id"], p):
                mark = " \u25aa"
            elif p.get("flag"):
                mark = " \u26a0"
            L.append(f"    - {p['num']}. [{p['title']}](#{anchor(p['num'] + ' ' + p['title'])})"
                     f" \u2014 {p['author']}{mark}")
        if FURTHER.get(cat["id"]):
            L.append(f"    - [Also worth your time in this vein]"
                     f"(#also-worth-your-time--{cat['id']})")
    L.append("- [Recommended poems to start with](#recommended-poems-to-start-with)")
    L.append("- [Colophon](#colophon)")
    L.append("\n</details>\n")
    L.append("\u25aa = full text included \u00b7 \u26a0 = no authorized free text online\n")
    L.append("\n---\n")

    # ---------- how to use ----------
    L.append("## How to use this file\n")
    L.append(f"{n_total} poems organized into {len(CATEGORIES)} thematic threads. Each entry gives "
             "**title, author, date, source, form, why it belongs, memorization difficulty, "
             "and a link**.\n")
    L.append(f"**Which texts are here.** {n_pd} of the {n_total} are public domain in the US and "
             f"{n_txt} currently have their full text included. The remaining {n_c} entries "
             "are under active copyright and appear as commentary and authorized links only.\n")
    L.append("**Check the texts before you commit them.** These were extracted by script "
             "from recorded Wikisource or Project Gutenberg editions \u2014 more reliable than "
             "most of what floats around the web, but not "
             "infallible, and it fails exactly where it matters for memorization: "
             "Dickinson's dashes and capitals, Hopkins's stress accents (*sh\u00e9er pl\u00f3d*, "
             "*unpertherb\u00e8d*), Herbert's 1633 spelling. Where a reading matters, check it "
             "against the linked edition. A memorized poem inherits every error in the copy "
             "you learned it from.\n")
    L.append("**Difficulty ratings** describe memorization, not comprehension. *Easy* = "
             "metrical, rhymed, under 20 lines. *Moderate* = longer, or free verse with a "
             "strong logical spine. *Hard* = long, knotty, or free verse without scaffolding.\n")
    L.append("\n---\n")

    # ---------- categories ----------
    for cat in CATEGORIES:
        cid = cat["id"]
        L.append(f"# {detag(cat['title'])}")
        L.append(f"### {cat['subtitle']}\n")
        L.append(detag(cat["intro"]) + "\n")

        if cid == "c":
            L.append("**A note on Dickinson texts.** Use the **Franklin** numbering (Fr) and "
                     "the R. W. Franklin *Reading Edition* (1999), the Emily Dickinson Archive "
                     "(edickinson.org), or the Poetry Foundation links below \u2014 which use "
                     "Franklin numbers and restore her punctuation. Nineteenth- and early-"
                     "twentieth-century editors \u201ccorrected\u201d her dashes, capitals, and rhymes; "
                     "a complete restored edition didn't appear until Franklin's in 1998, and "
                     "many free sites still carry the bowdlerized texts. Her poems are in "
                     "**hymn meter** (common metre, 8-6-8-6), which is why they're so "
                     "memorizable: nearly every one can be sung to \u201cAmazing Grace.\u201d Use that. "
                     "It's not a gimmick; it's how the poems are built.\n")

        for p in POEMS[cid]:
            L.append(f"## {p['num']}. {p['title']}")
            L.append(f"**{p['author']}** \u2014 {detag(p['dates'])}  ")
            L.append(f"*{detag(p['form'])}* \u00b7 **To memorize:** {detag(p['difficulty'])}\n")

            if p.get("seed"):
                L.append("> **Your seed poem.**\n")

            txt = load_text(cid, p) if p.get("pd") else None
            if txt:
                L.append("```")
                L.append(txt)
                L.append("```\n")
            elif p.get("pd"):
                L.append(f"*(Text not fetched \u2014 run `fetch_texts.py`, or put it in "
                         f"`texts/{slug(cid, p)}.txt` yourself.)*\n")
            else:
                L.append("*(Still in copyright \u2014 text not included. See link below.)*\n")

            L.append(detag(p["why"]) + "\n")

            if p.get("flag"):
                L.append(f"> \u26a0 **Note.** {detag(p['flag'])}\n")

            for label, url in p.get("links", []):
                L.append(f"\u2192 [{label}]({url})")
            L.append("")

        if FURTHER.get(cid):
            L.append(f"### Also worth your time \u2014 {cid}\n")
            for name, note in FURTHER.get(cid, []):
                L.append(f"- **{detag(name)}**" + (f" \u2014 {detag(note)}" if note else ""))
        L.append("\n---\n")

    # ---------- order ----------
    L.append("# Recommended poems to start with\n")
    L.append("**Start with Emily Dickinson's [\u201cHope\u201d is the thing with feathers]"
             "(#0-hope-is-the-thing-with-feathers).** It is short, "
             "musical, and built on one image, so its meter and rhyme give you plenty of "
             "cues. If you already know it, begin with George Herbert's "
             "[\u201cLove (III).\u201d](#1-love-iii)\n")
    L.append("The sequence below favors early wins, then gradually adds length and resistance "
             "while keeping the book's different threads of feeling in rotation. You do not "
             "need to follow it rigidly: a poem you urgently want to know is often easier to "
             "learn than a technically simpler poem you merely admire.\n")
    L.append("**Where your three seeds fit.** Dickinson's [\u201cHope\u201d]"
             "(#0-hope-is-the-thing-with-feathers) belongs in the first group "
             "\u2014 it's as easy as anything here, and if you don't already have it, get it "
             "first. Nye's [\u201cKindness\u201d](#0-kindness) sits with the harder free verse "
             "around 12\u201315. Thompson's [\u201cHound of Heaven\u201d](#0-the-hound-of-heaven) "
             "is in a category of its own: 182 irregular lines, "
             "more than four times the length of anything else. Don't start with it, and "
             "consider learning it in movements \u2014 the flight, the failed refuges, the "
             "surrender \u2014 rather than whole.\n")
    L.append("**Your first five after \u201cHope\u201d**\n")
    for i, s in enumerate([
        "**[Herbert, \u201cLove (III)\u201d](#1-love-iii)** \u2014 eighteen lines, gentle dialogue, and a clear emotional turn",
        "**[Clifton, \u201cblessing the boats\u201d](#4-blessing-the-boats)** \u2014 thirteen spare lines that move like a spoken blessing",
        "**[Yeats, \u201cThe Lake Isle of Innisfree\u201d](#9-the-lake-isle-of-innisfree)** \u2014 three musical quatrains with strong sensory landmarks",
        "**[Dickinson, \u201cI'm Nobody! Who are you?\u201d](#4-im-nobody-who-are-you)** \u2014 brief, playful, and rhythmically adhesive",
        "**[Berry, \u201cThe Peace of Wild Things\u201d](#6-the-peace-of-wild-things)** \u2014 plainspoken free verse with a simple movement from fear to rest"], 1):
        L.append(f"{i}. {s}")
    L.append("\n**Next five** (still short, slightly more resistance)\n")
    for i, s in enumerate([
        "[Rossetti, \u201cRemember\u201d](#8-remember)",
        "[Walcott, \u201cLove After Love\u201d](#1-love-after-love)",
        "[Hopkins, \u201cSpring and Fall\u201d](#7-spring-and-fall-to-a-young-child)",
        "[Housman, \u201cLoveliest of trees\u201d](#10-loveliest-of-trees-the-cherry-now)",
        "[Clifton, \u201cwon't you celebrate with me\u201d](#5-wont-you-celebrate-with-me)"], 6):
        L.append(f"{i}. {s}")
    L.append("\n**Then the ones worth the work**\n")
    for i, s in enumerate([
        "[Donne, \u201cBatter my heart\u201d](#4-batter-my-heart-three-persond-god)",
        "[Dickinson, \u201cThere's a certain Slant of light\u201d](#2-theres-a-certain-slant-of-light)",
        "[Hopkins, \u201cGod's Grandeur\u201d](#5-gods-grandeur)",
        "[Hardy, \u201cThe Darkling Thrush\u201d](#6-the-darkling-thrush)",
        "[Bass, \u201cThe Thing Is\u201d](#2-the-thing-is)"], 11):
        L.append(f"{i}. {s}")
    L.append("\n**Method note.** The metrical poems (Herbert, Hopkins, Dickinson, Rossetti, "
             "Yeats, Housman, Hardy, Frost, Teasdale) go in fast and stay, because meter and "
             "rhyme are error-correcting codes \u2014 misremember a word and the line stops "
             "scanning, so you know. **Say them aloud**; they were built for the ear, and "
             "silent reading loses the mechanism entirely.\n")
    L.append("Free verse (Nye, Walcott, Bass, Gilbert, Berry, Howe, Oliver, Kinnell, "
             "Lam\u00e9ris) has no such safety net. Learn those by **the turns of thought rather "
             "than the line breaks** \u2014 Walcott is arrival \u2192 recognition \u2192 feast; Zagajewski "
             "is an escalating imperative; Gilbert is a legal brief with a thesis and "
             "evidence. Get the argument's skeleton first and the words hang on it.\n")
    L.append("\n---\n")

    L.append("# Colophon\n")
    L.append(f"{n_total} poems: {n_txt} with full text included ({n_pd} are public domain in the "
             f"United States), {n_c} under copyright and given as commentary and links only.\n")
    L.append("Public-domain status noted throughout is for the United States and may differ "
             "where you are. The UK and EU generally use life-of-author-plus-70, which "
             "affects Hopkins, Hardy, Yeats, Teasdale, Frost, and Eliot differently \u2014 "
             "Frost's \u201cNothing Gold Can Stay\u201d is public domain in the US but not in the EU "
             "until 2034, and Eliot's \u201cJourney of the Magi\u201d not until 2036.\n")

    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print(f"wrote {out}  ({n_txt}/{n_pd} public-domain texts present)")


if __name__ == "__main__":
    main()
