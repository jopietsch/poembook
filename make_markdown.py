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

    L = []
    L.append("# Poems to Cherish and Memorize")
    L.append("### A curated expansion from three seed poems\n")
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
    L.append("- [A suggested memorization order](#a-suggested-memorization-order)")
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
             f"{n_txt} currently have their full text included. The {n_c} in the Kindness "
             "category are under active copyright and appear as commentary and authorized "
             "links only.\n")
    L.append("**Check the texts before you commit them.** These were pulled from Wikisource "
             "by script \u2014 more reliable than most of what floats around the web, but not "
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
    L.append("# A suggested memorization order\n")
    L.append("Early wins first, gradually increasing difficulty, keeping all three lines of "
             "feeling in rotation.\n")
    L.append("**Where your three seeds fit.** Dickinson's \u201cHope\u201d belongs in the first group "
             "\u2014 it's as easy as anything here, and if you don't already have it, get it "
             "first. Nye's \u201cKindness\u201d sits with the harder free verse around 12\u201315. "
             "Thompson's \u201cHound of Heaven\u201d is in a category of its own: 182 irregular lines, "
             "more than four times the length of anything else. Don't start with it, and "
             "consider learning it in movements \u2014 the flight, the failed refuges, the "
             "surrender \u2014 rather than whole.\n")
    L.append("**First five** (all under 20 lines, all easy)\n")
    for i, s in enumerate([
        "Clifton, \u201cblessing the boats\u201d", "Herbert, \u201cLove (III)\u201d",
        "Yeats, \u201cThe Lake Isle of Innisfree\u201d", "Dickinson, \u201cI'm Nobody! Who are you?\u201d",
        "Berry, \u201cThe Peace of Wild Things\u201d"], 1):
        L.append(f"{i}. {s}")
    L.append("\n**Next five** (still short, slightly more resistance)\n")
    for i, s in enumerate([
        "Rossetti, \u201cRemember\u201d", "Walcott, \u201cLove After Love\u201d",
        "Hopkins, \u201cSpring and Fall\u201d", "Housman, \u201cLoveliest of trees\u201d",
        "Clifton, \u201cwon't you celebrate with me\u201d"], 6):
        L.append(f"{i}. {s}")
    L.append("\n**Then the ones worth the work**\n")
    for i, s in enumerate([
        "Donne, \u201cBatter my heart\u201d", "Dickinson, \u201cThere's a certain Slant of light\u201d",
        "Hopkins, \u201cGod's Grandeur\u201d", "Hardy, \u201cThe Darkling Thrush\u201d",
        "Bass, \u201cThe Thing Is\u201d"], 11):
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
             f"United States), {n_c} under copyright and given as commentary and links only. "
             "All links checked at time of writing.\n")
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
