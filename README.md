# Poembook

Poembook builds a curated, copyright-aware anthology for reading and
memorization. It currently contains 78 poems in four thematic threads:

- pursuit, flight, and wrestling with God;
- sorrow turning toward kindness;
- compact poems built around one sustaining image;
- Rilke on solitude, attention, terror, and transformation.

Public-domain texts may be included in the generated book. Copyrighted poems
remain commentary plus links to authorized sources.

## Install

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

Set a contact address before using Wikimedia, as its API policy requests:

```bash
export WIKI_CONTACT="you@example.com"
```

## Commands

```bash
poembook audit                 # metadata, line counts, source/review status
python3 fetch_texts.py         # download missing public-domain texts
poembook clean-cache           # remove provable title/folio preambles
poembook build --format all    # EPUB and Markdown
poembook practice a1 --mode first-words
poembook practice a1 --mode initials
poembook practice a1 --mode blanks
poembook status a1 learning
poembook verify a1             # after comparing the text with its cited edition
```

`audit --strict` exits unsuccessfully while any text is missing, structurally
suspect, or unverified. The builders exclude structurally suspect downloads.
Verification is intentionally manual: punctuation, capitalization, stress
marks, and editorial variants matter when a text will be memorized.

Personal memorization state is stored in `.poembook-progress.json` and is not
committed.

## Adding a poem

Add an ordinary record to the appropriate list in `poems.py`. Use `pd=True`
only when the text and the particular translation are public domain in the
United States. Give Wikisource searches a `ws` value; copyrighted records use
`pd=False, ws=None` and authorized links only.

Rilke's included English texts come from Jessie Lemont's 1918 translation,
available as public-domain Project Gutenberg ebook 38594. Modern translations
often differ substantially and remain copyrighted.

## Files

- `poems.py` — catalog, themes, commentary, and rights metadata
- `poembook_cli.py` — audit, build, practice, progress, and verification commands
- `fetch_texts.py` — resumable Wikisource/Project Gutenberg downloader
- `build_epub.py` and `make_markdown.py` — output renderers
- `texts/` — source text plus provenance/status JSON
- `tests/` — catalog and practice-mode checks

Run `epubcheck poems-to-memorize.epub` for independent EPUB validation when
`epubcheck` is installed.
