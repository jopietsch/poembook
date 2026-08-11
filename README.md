# Poem book builder

Builds *Poems to Cherish and Memorize* as an EPUB (and markdown), with the
public-domain poem texts filled in.

## Quick start

```bash
pip install requests beautifulsoup4 lxml

export WIKI_CONTACT="you@example.com"   # do this — see below
python3 fetch_texts.py                  # 26 public-domain texts from Wikisource
python3 build_epub.py                   # -> poems-to-memorize.epub
python3 make_markdown.py                # -> poems-to-memorize.md
```

The EPUB in this bundle was already built, but **without** the poem texts,
because the machine it was built on has no network access to Wikisource. Run
`fetch_texts.py` and rebuild and the 26 texts drop in.

## If you get `429 Too Many Requests`

Wikimedia rate-limits anonymous API clients hard. Three things help, in order of
how much difference they make:

1. **Set `WIKI_CONTACT`.** Wikimedia's User-Agent policy asks clients to
   identify themselves, and unidentified traffic is throttled first and worst.
   One `export` gets you through much faster.
2. **Re-run it.** Every fetched poem is written to disk immediately and skipped
   on the next run, and search results are cached separately — so re-running
   after a pause costs nothing and picks up exactly where it stopped. Repeat
   until the "still missing" list is empty.
3. **`python3 fetch_texts.py --slow`** puts five seconds between poems. Slower,
   but it tends to get through in one pass.

The fetcher backs off exponentially, honours the `Retry-After` header, and stops
on its own after repeated 429s rather than making things worse. Nothing is lost
when it stops.

For a single stubborn poem: `python3 fetch_texts.py --only a5`

**Or just paste it in.** All 26 are one click away at the links already in the
book. Drop the text into `texts/<slug>.txt` and rebuild — the builder uses
whatever is in that file, and a hand-checked text is better than a scraped one
anyway. `python3 fetch_texts.py --list` prints the slugs.

## What gets fetched, and what doesn't

| | count | text included |
|---|---|---|
| Category A — Hound of Heaven line | 13 | yes, all public domain |
| Category B — Kindness line | 13 | **no** — all under active copyright |
| Category C — Hope is the thing with feathers line | 13 | yes, all public domain |

Category B is Nye, Walcott, Bass, Gilbert, Clifton, Berry, Oliver, Howe,
Zagajewski, Kinnell, and Laméris — all living or recently dead, all with active
estates and publishers. `fetch_texts.py` will not touch them; they stay as
commentary plus links to poets.org, the Poetry Foundation, the Poetry Society of
America, and On Being, which are the authorized sources.

Two of those thirteen have no authorized free text online at all — Oliver's
"In Blackwater Woods" and Zagajewski's "Try to Praise the Mutilated World." Each
is flagged in the book with the volume to buy.

## Check the texts before you memorize them

`fetch_texts.py` searches Wikisource rather than guessing URLs, so it fails
loudly rather than silently — anything questionable gets printed at the end
under `NEEDS A LOOK`. But Wikisource transcriptions vary in quality, and the
places they go wrong are exactly the places that matter here:

- **Dickinson** — dashes and capitalization. Many transcriptions still follow
  the 1890s editors who regularized both. You want Franklin's readings.
- **Hopkins** — stress marks. `shéer plód`, `unpertherbèd`, `all félled`. Strip
  those and the sprung rhythm is unrecoverable from the page.
- **Herbert, Donne, Vaughan, Milton** — 17th-century spelling and elision.
  `lack'd` vs `lacked` changes the syllable count and therefore the line.

Anything in `texts/<slug>.txt` wins over what the fetcher would pull, so to fix
a poem just edit that file and re-run the builder. Hand-corrected always beats
scraped.

## Files

- `poems.py` — all the metadata and commentary. Edit here to add poems.
- `fetch_texts.py` — Wikisource fetcher. `--list` to see status, `--force` to refetch.
- `build_epub.py` — assembles a valid EPUB 3 with a nested TOC (category → poem)
  plus an EPUB 2 `toc.ncx` so older readers get navigation too.
- `make_markdown.py` — same content as markdown, with a linked TOC.
- `texts/` — fetched poem texts, one `.txt` per poem, plus a `.json` recording
  which Wikisource page it came from.

## Adding poems

Append a dict to the right list in `poems.py`. The fields are documented at the
top of that file. Set `pd=True` and give a `ws` search string if the poem is
public domain and you want its text fetched; set `pd=False` and it stays
link-only. Then re-run the two build scripts.

## Validating the EPUB

If you want to be sure before sideloading:

```bash
pip install epubcheck   # or: brew install epubcheck
epubcheck poems-to-memorize.epub
```

The build already guarantees the two things most readers choke on: `mimetype` is
the first entry in the zip and is stored uncompressed, and every XHTML file is
well-formed XML.
