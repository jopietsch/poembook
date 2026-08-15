# Repository Guidelines

## Project Structure & Module Organization

This is a small Python 3.10+ project built from top-level modules:

- `poems.py` defines categories, poem metadata, rights status, and slugs.
- `poembook_cli.py` provides audit, build, practice, progress, and verification commands.
- `fetch_texts.py` retrieves public-domain texts and provenance metadata.
- `build_epub.py` and `make_markdown.py` render the two book formats.
- `texts/` contains poem text (`<slug>.txt`) and source/status metadata (`<slug>.json`).
- `tests/` contains the pytest suite. Generated outputs are `poems-to-memorize.epub` and `poems-to-memorize.md`.

Keep catalog changes in `poems.py`; do not duplicate poem metadata in a renderer. Preserve unrelated local changes, especially editorial verification records under `texts/`.

## Build, Test, and Development Commands

Create an environment with `python3 -m venv .venv`, activate it, and run `pip install -e '.[dev]'`.

- `poembook build --format all` rebuilds EPUB and Markdown editions.
- `python3 -m pytest -q` runs all automated tests.
- `poembook audit` reports metadata, source, and text-quality issues.
- `poembook verify --all --structural-only` performs noninteractive structural checks.
- `python3 -m zipfile -t poems-to-memorize.epub` checks the EPUB archive; use `epubcheck` when installed for full validation.

## Coding Style & Naming Conventions

Use four-space indentation, UTF-8, descriptive `snake_case` names, and small functions. Follow existing Python and PEP 8 conventions; no formatter or linter is currently configured. Poem slugs combine a category ID and display number (`a1`, `cs0`). Use `pathlib` in new code where practical, while matching nearby style when editing existing modules.

## Testing Guidelines

Tests use pytest and live in `tests/test_*.py`; test functions begin with `test_`. Add focused tests for catalog invariants, parsing, practice modes, or renderer behavior affected by a change. There is no formal coverage threshold. Always run the full suite and rebuild affected formats before submitting.

## Commit & Pull Request Guidelines

Recent commits use short, imperative summaries such as `Add batch structural and editorial verification`. Keep each commit focused. Pull requests should explain the user-visible effect, list validation commands, and call out copyright, source, or edition decisions. Include screenshots only for material rendering changes.

## Copyright & Configuration

Set `WIKI_CONTACT` before Wikimedia requests. Include full text only when the work and translation are public domain in the United States; otherwise retain commentary and authorized links. Never mark a text editorially verified without a human word-for-word source comparison.
