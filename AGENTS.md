# Repository Guidelines

## Project Structure & Module Organization

This Python 3.10+ project uses top-level modules:

- `poems.py` defines categories, poem metadata, rights status, and slugs.
- `poembook_cli.py` provides audit, build, practice, progress, and verification commands.
- `fetch_texts.py` retrieves public-domain texts and provenance metadata.
- `build_epub.py` and `make_markdown.py` render the two book formats.
- `texts/` contains poem text (`<slug>.txt`) and source/status metadata (`<slug>.json`).
- `tests/` contains the pytest suite. Generated outputs are `poems-to-memorize.epub` and `poems-to-memorize.md`.

Keep catalog changes in `poems.py`; do not duplicate metadata in renderers. Preserve editorial verification records under `texts/`.

## Build, Test, and Development Commands

Set up a virtual environment, then run `pip install -e '.[dev]'`.

- `poembook build --format all` rebuilds EPUB and Markdown editions.
- `python3 -m pytest -q` runs all automated tests.
- `poembook audit` reports metadata, source, and text-quality issues.
- `poembook verify --all --structural-only` performs noninteractive structural checks.
- `python3 -m zipfile -t poems-to-memorize.epub` checks the EPUB archive; use `epubcheck` when installed for full validation.
- `git config core.hooksPath .githooks` enables the shared commit gates for this clone.

## Coding Style & Naming Conventions

Use four-space indentation, UTF-8, descriptive `snake_case` names, small functions, and PEP 8 conventions. No formatter or linter is configured. Poem slugs combine a category and display number (`a1`, `cs0`). Prefer `pathlib` in new code.

## Testing Guidelines

Tests use pytest in `tests/test_*.py`; functions begin with `test_`. Add focused regression tests for affected behavior. There is no coverage threshold. Run the full suite and rebuild affected formats before submitting.

## Commit & Pull Request Guidelines

Recent commits use short, imperative summaries such as `Add batch structural and editorial verification`. Keep each commit focused. Pull requests should explain the user-visible effect, list validation commands, and call out copyright, source, or edition decisions. Include screenshots only for material rendering changes.

### Required Pre-Commit Review

Every commit requires review of the complete staged diff. Inspect `git diff --cached` for correctness, regressions, tests, artifacts, and source or copyright implications; resolve all actionable findings and rerun validation. Add a `Reviewed-by: NAME` commit trailer to attest completion. The shared hooks reject missing trailers, whitespace errors, and failing tests. This applies to documentation and generated files too.

## Copyright & Configuration

Set `WIKI_CONTACT` before Wikimedia requests. Include full text only when the work and translation are public domain in the United States; otherwise retain commentary and authorized links. Never mark a text editorially verified without a human word-for-word source comparison.
