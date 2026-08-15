#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_texts.py -- retrieve public-domain poem texts from recorded source editions.

Only poems marked pd=True in poems.py are fetched. Copyrighted poems, including
the entire "Kindness" thread, are never touched.

This is deliberately slow and polite. Wikimedia rate-limits anonymous API
clients hard and returns 429 if you hammer it. So:

  * two requests per poem, not six
  * a real User-Agent with contact info (their policy asks for this)
  * maxlag=5, so the API defers when their servers are busy
  * exponential backoff that honours the Retry-After header
  * progress saved after every poem, so interrupting and resuming is free
  * search results cached, so a re-run after a 429 costs nothing

Set a contact address so you aren't lumped in with anonymous traffic:

    export WIKI_CONTACT="you@example.com"

Usage:
    python3 fetch_texts.py             # fetch whatever is missing
    python3 fetch_texts.py --list      # status only, no network
    python3 fetch_texts.py --force     # refetch everything
    python3 fetch_texts.py --slow      # 5s between poems, for a bad day
    python3 fetch_texts.py --only c6   # just one poem, by slug

Requires: requests, beautifulsoup4, lxml
"""

import os
import sys
import time
import json
import random
import re

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("Need: pip install requests beautifulsoup4 lxml")

from poems import public_domain_poems, slug
from poembook_cli import expected_lines, text_issues

API = "https://en.wikisource.org/w/api.php"
HERE = os.path.dirname(os.path.abspath(__file__))
TEXTDIR = os.path.join(HERE, "texts")
CACHE = os.path.join(TEXTDIR, "_searchcache.json")

CONTACT = os.environ.get("WIKI_CONTACT", "").strip()
UA = ("poembook/2.0 (personal poetry anthology; "
      + (CONTACT if CONTACT else "no contact set - see WIKI_CONTACT")
      + ") python-requests")

BASE_DELAY = 1.5
SLOW_DELAY = 5.0
MAX_RETRIES = 5

session = requests.Session()
session.headers.update({"User-Agent": UA, "Accept-Encoding": "gzip"})

_consecutive_429 = 0


def api_get(params, label=""):
    """One API call, with backoff. Returns parsed JSON or raises."""
    global _consecutive_429
    params = dict(params)
    params.setdefault("format", "json")
    params.setdefault("formatversion", 2)
    params.setdefault("maxlag", 5)

    delay = 2.0
    for attempt in range(1, MAX_RETRIES + 1):
        r = session.get(API, params=params, timeout=45)

        if r.status_code == 200:
            data = r.json()
            # maxlag comes back as HTTP 200 with an error body
            if isinstance(data, dict) and data.get("error", {}).get("code") == "maxlag":
                wait = float(r.headers.get("Retry-After", delay))
                print(f"        servers lagging, waiting {wait:.0f}s", flush=True)
                time.sleep(wait)
                delay = min(delay * 2, 60)
                continue
            _consecutive_429 = 0
            return data

        if r.status_code in (429, 503):
            _consecutive_429 += 1
            wait = float(r.headers.get("Retry-After", delay)) + random.uniform(0, 1.5)
            print(f"        {r.status_code} rate-limited, backing off {wait:.0f}s "
                  f"(attempt {attempt}/{MAX_RETRIES})", flush=True)
            time.sleep(wait)
            delay = min(delay * 2, 120)
            continue

        r.raise_for_status()

    raise RuntimeError(f"gave up after {MAX_RETRIES} retries ({label})")


def load_cache():
    if os.path.exists(CACHE):
        try:
            return json.load(open(CACHE, encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_cache(c):
    os.makedirs(TEXTDIR, exist_ok=True)
    json.dump(c, open(CACHE, "w", encoding="utf-8"), indent=2, ensure_ascii=False)


def search_titles(query, cache):
    if query in cache:
        return cache[query]
    data = api_get({"action": "query", "list": "search", "srsearch": query,
                    "srlimit": 5, "srnamespace": 0}, label=query)
    titles = [h["title"] for h in data.get("query", {}).get("search", [])]
    cache[query] = titles
    save_cache(cache)
    return titles


def get_page_html(title):
    data = api_get({"action": "parse", "page": title, "prop": "text",
                    "redirects": 1}, label=title)
    if "error" in data:
        return None
    return data.get("parse", {}).get("text")


def extract_poem(html_text):
    soup = BeautifulSoup(html_text, "lxml")
    for junk in soup.select(
        ".mw-editsection, .reference, .noprint, table, .navbox, #toc, "
        ".mw-references-wrap, sup.reference, .ws-noexport, .licensetpl, "
        ".header_notes, #headertemplate, .wst-header, style, script"
    ):
        junk.decompose()

    blocks = soup.select("div.poem")
    if blocks:
        chunks = []
        for b in blocks:
            for br in b.find_all("br"):
                br.replace_with("\n")
            chunks.append(b.get_text())
        text = "\n\n".join(chunks)
    else:
        body = soup.select_one(".mw-parser-output") or soup
        for br in body.find_all("br"):
            br.replace_with("\n")
        text = body.get_text()

    text = text.replace("\xa0", " ")
    lines = [ln.rstrip() for ln in text.split("\n")]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    out, blank = [], 0
    for ln in lines:
        if ln.strip():
            out.append(ln)
            blank = 0
        else:
            blank += 1
            if blank <= 1:
                out.append("")
    return "\n".join(out).strip()


def normalize_candidate(cat, poem, text):
    """Remove short title/folio preambles commonly emitted by Wikisource."""
    expected = expected_lines(poem)
    if not expected:
        return text
    lines = text.splitlines()
    marker = poem.get("extract_after")
    if marker:
        for i, line in enumerate(lines):
            if marker in line:
                remainder = line.split(marker, 1)[1].strip()
                lines = ([remainder] if remainder else []) + lines[i + 1:]
                chosen, count = [], 0
                for candidate in lines:
                    if candidate.strip():
                        count += 1
                    chosen.append(candidate)
                    if count == expected:
                        break
                return "\n".join(chosen).strip()
    nonblank = [i for i, line in enumerate(lines) if line.strip()]
    excess = len(nonblank) - expected
    if 0 < excess <= 4:
        remove = set(nonblank[:excess])
        text = "\n".join(line for i, line in enumerate(lines) if i not in remove).strip()
    return text


_gutenberg_text = None


def get_gutenberg_poem(poem):
    """Extract a named poem from Jessie Lemont's public-domain 1918 Rilke volume."""
    global _gutenberg_text
    if _gutenberg_text is None:
        response = session.get("https://www.gutenberg.org/files/38594/38594-8.txt", timeout=45)
        response.raise_for_status()
        _gutenberg_text = response.text.replace("\r\n", "\n")
    heading = poem["gutenberg_section"]
    matches = list(re.finditer(rf"(?im)^\s*{re.escape(heading)}\s*$", _gutenberg_text))
    if not matches:
        return ""
    boundary = matches[-1].start() if poem.get("gutenberg_marker_is_line") else matches[-1].end()
    tail = _gutenberg_text[boundary:].strip()
    expected = expected_lines(poem)
    chosen = []
    for line in tail.splitlines():
        if line.strip():
            chosen.append(line.rstrip())
            if expected and len([x for x in chosen if x.strip()]) == expected:
                break
        elif chosen:
            chosen.append("")
    return "\n".join(chosen).strip() if expected else ""


def problems_with(text):
    if not text:
        return ["empty"]
    p = []
    lines = [l for l in text.split("\n") if l.strip()]
    if len(lines) < 4:
        p.append(f"only {len(lines)} lines")
    if len(text) > 40000:
        p.append("very long - may be a whole collection, not one poem")
    low = text.lower()
    for marker in ("jump to navigation", "this page has been proofread",
                   "sister projects", "download as pdf"):
        if marker in low:
            p.append(f"boilerplate present: {marker!r}")
            break
    return p


def main():
    force = "--force" in sys.argv
    listonly = "--list" in sys.argv
    delay = SLOW_DELAY if "--slow" in sys.argv else BASE_DELAY
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None

    os.makedirs(TEXTDIR, exist_ok=True)
    cache = load_cache()

    targets = public_domain_poems()
    if only:
        targets = [(c, p) for c, p in targets if slug(c["id"], p) == only]
        if not targets:
            sys.exit(f"no public-domain poem with slug {only!r}")

    if not CONTACT and not listonly:
        print("NOTE: WIKI_CONTACT is not set. Wikimedia throttles unidentified")
        print("      clients hardest. Set it and you'll get through faster:")
        print('        export WIKI_CONTACT="you@example.com"\n')

    have = sum(1 for c, p in targets
               if os.path.exists(os.path.join(TEXTDIR, slug(c["id"], p) + ".txt")))
    print(f"{len(targets)} public-domain poems - {have} already cached, "
          f"{len(targets) - have} to go.\n")

    flagged, fetched = [], 0

    for cat, poem in targets:
        sl = slug(cat["id"], poem)
        path = os.path.join(TEXTDIR, sl + ".txt")
        label = f'{poem["title"]} - {poem["author"]}'

        if os.path.exists(path) and not force:
            n = len([l for l in open(path, encoding="utf-8") if l.strip()])
            print(f"  [cached {n:>4} ll] {sl:<5} {label}")
            continue
        if listonly:
            print(f"  [MISSING      ] {sl:<5} {label}")
            continue

        print(f"  [fetching     ] {sl:<5} {label}", flush=True)
        try:
            if poem.get("gutenberg_section"):
                titles = []
                text = get_gutenberg_poem(poem)
                used = f"Project Gutenberg #38594: {poem['gutenberg_section']}"
            else:
                titles = search_titles(poem["ws"], cache)
                if not titles:
                    flagged.append((sl, label, f"no Wikisource hit for {poem['ws']!r}"))
                    print("        no search hit")
                    continue
                text, used = "", None

            # Try the top hit first. Only fall through on genuine failure, so
            # the common case costs exactly two requests.
            for i, title in enumerate(titles[:3]):
                html_text = get_page_html(title)
                if html_text:
                    cand = normalize_candidate(cat, poem, extract_poem(html_text))
                    if cand and not text_issues(cat, poem, cand):
                        text, used = cand, title
                        break
                if i < 2:
                    time.sleep(delay)

            if not text:
                flagged.append((sl, label, f"nothing usable in {titles[:3]}"))
                print(f"        nothing usable; tried {titles[:3]}")
                continue

            with open(path, "w", encoding="utf-8") as f:
                f.write(text + "\n")
            with open(path.replace(".txt", ".json"), "w", encoding="utf-8") as f:
                json.dump({"source": used,
                           "search": poem["ws"],
                           "url": ("https://www.gutenberg.org/ebooks/38594"
                                   if poem.get("gutenberg_section") else
                                   "https://en.wikisource.org/wiki/" + used.replace(" ", "_")),
                           "status": "fetched"},
                          f, indent=2, ensure_ascii=False)

            fetched += 1
            issues = problems_with(text)
            n = len([l for l in text.split("\n") if l.strip()])
            if issues:
                flagged.append((sl, label, "; ".join(issues)))
                print(f"        saved {n} ll from {used!r} - CHECK: {'; '.join(issues)}")
            else:
                print(f"        saved {n} ll from {used!r}")

            time.sleep(delay + random.uniform(0, 0.8))

        except KeyboardInterrupt:
            print("\n\nInterrupted. Progress is saved - just run it again.")
            break
        except Exception as e:
            flagged.append((sl, label, f"{type(e).__name__}: {e}"))
            print(f"        error: {e}")
            if _consecutive_429 >= 3:
                print("\n  Rate-limited repeatedly. Stopping here so we don't make it worse.")
                print("  Everything fetched so far is saved. Wait a few minutes, then:")
                print("      python3 fetch_texts.py --slow")
                break
            time.sleep(delay * 2)

    still = [(c, p) for c, p in targets
             if not os.path.exists(os.path.join(TEXTDIR, slug(c["id"], p) + ".txt"))]

    print(f"\n{fetched} fetched this run. "
          f"{len(targets) - len(still)}/{len(targets)} now present.")

    if flagged:
        print("\n" + "=" * 64)
        print("NEEDS A LOOK")
        print("=" * 64)
        for sl, label, why in flagged:
            print(f"  {sl:<5} {label}\n        {why}")

    if still:
        print("\nStill missing:")
        for c, p in still:
            print(f"  {slug(c['id'], p):<5} {p['title']} - {p['author']}")
        print("\nRun again to pick up where it left off (cached poems are skipped),")
        print("or fetch one at a time:  python3 fetch_texts.py --only <slug>")
        print("\nOr paste it in yourself - every one is a click away at the link in")
        print("the book, and a hand-checked text beats a scraped one:")
        print("  texts/<slug>.txt")

    print("\nBefore you memorize anything: spot-check Dickinson (dashes, capitals)")
    print("and Hopkins (stress marks) against the linked editions. The builder uses")
    print("whatever is in texts/, so corrections stick across rebuilds.")


if __name__ == "__main__":
    main()
