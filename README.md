# Poembook

Poembook builds a curated, copyright-aware anthology for reading and
memorization. It currently contains 102 poems in six thematic threads:

- pursuit, flight, and wrestling with God;
- sorrow turning toward kindness;
- compact poems built around one sustaining image;
- Rilke on solitude, attention, terror, and transformation.
- Saint Patrick's Breastplate on protection, courage, and prayer in the world.
- Saint Francis's Canticle of the Sun on creaturely kinship, praise, and death.

Public-domain texts may be included in the generated book. Copyrighted poems
remain commentary plus links to authorized sources.

## Install

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
git config core.hooksPath .githooks
```

The shared hooks run the test suite before each commit and require a
`Reviewed-by: NAME` commit-message trailer after review of the staged diff.

Set a contact address before using Wikimedia, as its API policy requests:

```bash
export WIKI_CONTACT="you@example.com"
```

## Commands

```bash
poembook audit                 # metadata, line counts, source/review status
poembook audit-links           # live-check poem links and recorded text sources
python3 fetch_texts.py         # download missing public-domain texts
poembook clean-cache           # remove provable title/folio preambles
poembook build --format all    # browse EPUB, memorize EPUB, and Markdown
poembook build --format epub --edition browse
poembook build --format epub --edition memorize
poembook practice a1 --mode first-words
poembook practice a1 --mode initials
poembook practice a1 --mode blanks
poembook status a1 learning
poembook review a1 easy       # schedule the next recall
poembook verify --all          # all structural checks, then a resumable editorial queue
poembook verify --all --structural-only
poembook verify a1             # check and confirm one poem after source comparison
```

`audit --strict` exits unsuccessfully while any text is missing, structurally
suspect, or editorially unverified. The builders exclude structurally suspect
downloads. `verify --all` records automatic structural results first, then lets
you confirm clean texts against their cited editions with `yes`, `view`, `skip`,
or `quit`; progress is written after every confirmation, so later runs resume.
Editorial verification is intentionally human: punctuation, capitalization,
stress marks, translations, and edition choices matter when a text is memorized.

Text sidecars in `texts/<slug>.json` distinguish three levels: `structural`
checks catch shape and scraper problems; `source_comparison` records the chosen
edition, comparison sources, and machine-assisted findings; `editorial` means a
human completed a word-for-word comparison. Source comparison never implies
editorial approval.

Personal memorization state is stored in `.poembook-progress.json` and is not
committed.

## Editions

The EPUB build produces two complementary books from the same catalog and text
assets:

- `poembook-browse.epub` contains all entries, thematic introductions,
  commentary, links, recommendations, and every available public-domain text.
- `poembook-memorize.epub` contains only entries with local full text. Each
  text-first poem chapter is followed by graduated recall cues: memory map,
  stanza openings, first words, and blank structure. Very long poems
  also receive movement chapters. Its compact navigation and typography are
  designed for small, button-driven readers such as the Xteink X3 running
  CrossPoint.

The memorize edition begins with a Current rotation generated from
`.poembook-progress.json`: `learning`, `memorized`, and `want-to-learn` become
Learning now, Review, and Next. The browse edition includes indexes by author,
first line, difficulty/form, length, theme, and text availability, plus several
short suggested reading paths. Both editions embed distinct monochrome 528×792
cover art under `assets/`.

After a recitation, `poembook review SLUG easy|hesitant|failed` records the
result. Easy recalls receive a growing review interval, hesitant recalls return
tomorrow, and failed recalls return immediately to Learning now. Rebuilding the
memorize edition places due poems in its Review section.

EPUB timestamps are derived from their source assets, so rebuilding unchanged
inputs produces stable files and does not needlessly invalidate CrossPoint's
content-based reading cache. See `screenshots/x3/README.md` for the physical
device visual-regression checklist.

The Markdown output remains the complete browse edition. Texts in the memorize
edition may still be awaiting final human word-for-word editorial signoff; use
`poembook audit` and the recorded source editions before committing them to
memory.

## Adding a poem

Add an ordinary record to the appropriate list in `poems.py`. Use `pd=True`
only when the text and the particular translation are public domain in the
United States. Give Wikisource searches a `ws` value; copyrighted records use
`pd=False, ws=None` and authorized links only.

Rilke's included English texts come from Jessie Lemont's 1918 translation,
available as public-domain Project Gutenberg ebook 38594. Modern translations
often differ substantially and remain copyrighted.

Prefer a stable, named book edition when one is available. Project Gutenberg is
often stronger for whole-volume provenance; Wikisource is useful for individual
poem discovery and extraction. Neither is automatically authoritative. Compare
against at least one additional reputable edition, preserve intentional edition
variants, and record all compared URLs and the chosen edition in the sidecar.

## Files

- `poems.py` — catalog, themes, commentary, and rights metadata
- `poembook_cli.py` — audit, build, practice, progress, and verification commands
- `fetch_texts.py` — resumable Wikisource/Project Gutenberg downloader
- `build_epub.py` and `make_markdown.py` — browse/memorize EPUB and Markdown renderers
- `texts/` — source text plus provenance/status JSON
- `tests/` — catalog and practice-mode checks

Run `epubcheck poembook-browse.epub` and `epubcheck poembook-memorize.epub`
for independent EPUB validation when installed.
