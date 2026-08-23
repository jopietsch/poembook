import json
import urllib.error
import zipfile
from pathlib import Path

import poembook_cli
from build_epub import build
from poems import CATEGORIES, POEMS, all_poems, slug
from poembook_cli import (audit, audit_remote, expected_lines, main, practice_text,
                          record_verification, text_issues, verification_level)
from fetch_texts import normalize_candidate


ROOT = Path(__file__).resolve().parents[1]


def test_catalog_has_unique_slugs_and_required_fields():
    slugs = []
    for cat, poem in all_poems():
        slugs.append(slug(cat["id"], poem))
        for field in ("title", "author", "dates", "form", "why", "difficulty", "links", "pd"):
            assert field in poem
    assert len(slugs) == len(set(slugs))


def test_every_category_has_poems():
    assert {cat["id"] for cat in CATEGORIES} == set(POEMS)
    assert all(POEMS[cat["id"]] for cat in CATEGORIES)


def test_category_rights_summaries_match_catalog():
    categories = {cat["id"]: cat for cat in CATEGORIES}
    assert all(not poem["pd"] for poem in POEMS["b"])
    assert "All poems in this thread are under active copyright" in categories["b"]["intro"]
    assert any(not poem["pd"] for poem in POEMS["a"])
    assert "Every poem in this category is in the public domain" not in categories["a"]["intro"]


def test_line_count_parser():
    assert expected_lines({"form": "14 lines, sonnet"}) == 14
    assert expected_lines({"form": "~20 lines"}) is None


def test_practice_modes_preserve_line_structure():
    poem = "Hope is a thing\nWith feathers"
    assert practice_text(poem, "first-words") == "Hope\nWith"
    assert practice_text(poem, "initials") == "H i a t\nW f"
    assert practice_text(poem, "blanks") == "_____ _____ _____ _____\n_____ _____"


def test_practice_modes_include_gradual_recall_steps():
    poem = "First stanza\nSecond line\n\nNext stanza"
    assert practice_text(poem, "stanza-starts") == "First stanza\n\nNext stanza"
    assert practice_text(poem, "structure") == "Stanza 1 — 2 lines\nStanza 2 — 1 line"


def test_verification_levels_are_distinct():
    meta = {}
    record_verification(meta, "structural", "test")
    assert verification_level(meta) == "structural"
    assert meta["status"] == "structurally_valid"
    record_verification(meta, "editorial", "test review")
    assert verification_level(meta) == "editorial"
    assert meta["status"] == "verified"


def test_source_comparison_sits_between_structural_and_editorial_review():
    meta = {"verification": {"structural": {"status": "passed"},
                             "source_comparison": {"status": "passed"}}}
    assert verification_level(meta) == "source"


def test_verification_uses_strongest_completed_level():
    verification = {
        "structural": {"status": "passed"},
        "source_comparison": {"status": "passed"},
        "editorial": {"status": "passed"},
    }
    assert verification_level({"verification": verification}) == "editorial"


def test_poem_language_is_not_mistaken_for_biographical_boilerplate():
    assert text_issues({}, {"form": "4 lines"}, "It is the blight man was born for,\nOne\nTwo\nThree") == []


def test_prepositionless_birth_date_is_biographical_boilerplate():
    text = "T. S. Eliot was born 26 September 1888\nOne\nTwo\nThree"
    assert "likely biographical prose" in text_issues({}, {"form": "4 lines"}, text)


def test_prepositionless_birth_month_is_biographical_boilerplate():
    text = "T. S. Eliot was born September 1888\nOne\nTwo\nThree"
    assert "likely biographical prose" in text_issues({}, {"form": "4 lines"}, text)


def test_named_anthology_section_is_extracted_to_expected_length():
    poem = {"form": "3 lines", "extract_after": "POEM TITLE"}
    source = "unrelated prose\nPOEM TITLEFirst line\nSecond line\nThird line\ntrailing notes"
    assert normalize_candidate({}, poem, source) == "First line\nSecond line\nThird line"


def test_short_title_preamble_is_removed_to_match_line_count():
    poem = {"form": "3 lines"}
    source = "POEM TITLE\nFirst line\nSecond line\nThird line"
    assert normalize_candidate({}, poem, source) == "First line\nSecond line\nThird line"


def test_missing_anthology_marker_does_not_truncate_source():
    poem = {"form": "3 lines", "extract_after": "MISSING TITLE"}
    source = "First line\nSecond line\nThird line"
    assert normalize_candidate({}, poem, source) == source


def test_repository_text_assets_respect_rights_and_have_provenance():
    for cat, poem in all_poems():
        sid = slug(cat["id"], poem)
        text_path = ROOT / "texts" / f"{sid}.txt"
        meta_path = ROOT / "texts" / f"{sid}.json"
        if poem["pd"]:
            assert text_path.exists(), f"missing public-domain text: {sid}"
            metadata = json.loads(meta_path.read_text(encoding="utf-8"))
            comparison = metadata["verification"]["source_comparison"]
            assert comparison["status"] == "passed"
            sources = comparison.get("compared_sources") or comparison.get("sources")
            assert sources, f"missing comparison sources: {sid}"
            assert comparison.get("chosen_edition"), f"missing chosen edition: {sid}"
        else:
            assert not text_path.exists(), f"copyrighted text must not be bundled: {sid}"


def test_catalog_and_local_texts_have_no_audit_errors():
    errors, _warnings = audit()
    assert errors == []


def test_remote_audit_checks_expected_page_evidence_without_network():
    records = [
        {"kind": "link", "slug": "x1", "title": "A Bright Field", "author": "Ada Poet",
         "label": "publisher", "url": "https://example.test/poem"},
        {"kind": "source", "slug": "x2", "title": "Source Poem", "author": "Ada Poet",
         "label": "recorded source", "url": "https://example.test/source", "first_line": "First line"},
    ]

    def fetch(url):
        if url.endswith("poem"):
            return 200, url, "<title>A Bright Field — Ada Poet</title>"
        return 200, url, "<p>First\nline of the source poem</p>"

    errors, warnings = audit_remote(records, fetch=fetch)
    assert errors == []
    assert warnings == []


def test_remote_audit_reports_unreachable_and_ambiguous_records():
    records = [
        {"kind": "link", "slug": "x1", "title": "A Bright Field", "author": "Ada Poet",
         "label": "publisher", "url": "https://example.test/missing"},
        {"kind": "source", "slug": "x2", "title": "Source Poem", "author": "Ada Poet",
         "label": "recorded source", "url": "https://example.test/source", "first_line": "First line"},
    ]

    def fetch(url):
        if url.endswith("missing"):
            raise OSError("not reachable")
        return 200, url, "<p>A different text</p>"

    errors, warnings = audit_remote(records, fetch=fetch)
    assert errors == ["x1: publisher unreachable: not reachable"]
    assert warnings == ["x2: source reachable but poem evidence was not found (https://example.test/source)"]


def test_remote_audit_reports_malformed_unicode_url_without_crashing():
    records = [{"kind": "link", "slug": "x1", "title": "A Bright Field", "author": "Ada Poet",
                "label": "publisher", "url": "https://example.test/—"}]

    def fetch(_url):
        raise UnicodeEncodeError("ascii", "—", 0, 1, "not encodable")

    errors, warnings = audit_remote(records, fetch=fetch)
    assert errors == ["x1: publisher unreachable: 'ascii' codec can't encode character '\\u2014' in position 0: not encodable"]
    assert warnings == []


def test_remote_audit_distinguishes_access_restrictions_from_dead_links():
    records = [{"kind": "link", "slug": "x1", "title": "A Bright Field", "author": "Ada Poet",
                "label": "publisher", "url": "https://example.test/restricted"}]

    def fetch(_url):
        raise urllib.error.HTTPError("https://example.test/restricted", 403, "Forbidden", {}, None)

    errors, warnings = audit_remote(records, fetch=fetch)
    assert errors == []
    assert warnings == ["x1: publisher could not be checked (HTTP 403)"]


def test_remote_audit_treats_server_errors_as_warnings():
    records = [{"kind": "link", "slug": "x1", "title": "A Bright Field", "author": "Ada Poet",
                "label": "publisher", "url": "https://example.test/unavailable"}]

    def fetch(_url):
        raise urllib.error.HTTPError("https://example.test/unavailable", 504, "Gateway Timeout", {}, None)

    errors, warnings = audit_remote(records, fetch=fetch)
    assert errors == []
    assert warnings == ["x1: publisher could not be checked (HTTP 504)"]


def test_remote_audit_treats_timeouts_as_warnings():
    records = [{"kind": "link", "slug": "x1", "title": "A Bright Field", "author": "Ada Poet",
                "label": "publisher", "url": "https://example.test/slow"}]

    def fetch(_url):
        raise TimeoutError("The read operation timed out")

    errors, warnings = audit_remote(records, fetch=fetch)
    assert errors == []
    assert warnings == ["x1: publisher could not be checked (The read operation timed out)"]


def test_remote_audit_accepts_identified_source_when_edition_first_line_differs():
    records = [{"kind": "source", "slug": "x1", "title": "A Bright Field", "author": "Ada Poet",
                "label": "recorded source", "url": "https://example.test/source", "first_line": "Different edition"}]

    errors, warnings = audit_remote(
        records, fetch=lambda url: (200, url, "<title>A Bright Field — Ada Poet</title>"))
    assert errors == []
    assert warnings == []


def test_epub_build_smoke(tmp_path):
    output = tmp_path / "poembook.epub"
    counts = build(output)

    catalog = [poem for _cat, poem in all_poems()]
    public_domain = sum(poem["pd"] for poem in catalog)
    assert counts == {
        "total": len(catalog),
        "with_text": public_domain,
        "pd": public_domain,
        "copyright": len(catalog) - public_domain,
    }
    with zipfile.ZipFile(output) as epub:
        first = epub.infolist()[0]
        assert first.filename == "mimetype"
        assert first.compress_type == zipfile.ZIP_STORED
        assert epub.read("mimetype") == b"application/epub+zip"
        assert "OEBPS/content.opf" in epub.namelist()
        love = epub.read("OEBPS/a1.xhtml").decode("utf-8")
        assert "Love (III)" in love
        assert "Love bade me welcome" in love
        title = epub.read("OEBPS/title.xhtml").decode("utf-8")
        assert "Last updated" in title


def test_memorize_epub_contains_text_and_recall_aids_only(tmp_path):
    output = tmp_path / "memorize.epub"
    counts = build(output, edition="memorize")

    catalog = [poem for _cat, poem in all_poems()]
    public_domain = sum(poem["pd"] for poem in catalog)
    assert counts == {
        "total": public_domain,
        "with_text": public_domain,
        "pd": public_domain,
        "copyright": 0,
    }
    with zipfile.ZipFile(output) as epub:
        names = epub.namelist()
        assert "OEBPS/a1.xhtml" in names
        assert "OEBPS/a1-recall.xhtml" in names
        assert "OEBPS/b1.xhtml" not in names
        assert "OEBPS/order.xhtml" not in names
        assert "OEBPS/cover.png" in names
        assert "OEBPS/as0-movement-1.xhtml" in names
        love = epub.read("OEBPS/a1.xhtml").decode("utf-8")
        assert love.index("Love bade me welcome") < love.index("Published")
        recall = epub.read("OEBPS/a1-recall.xhtml").decode("utf-8")
        assert "First words" in recall
        assert "Initials" not in recall
        assert "Stanza openings" in recall
        assert "Blank structure" in recall
        assert "Memory map" in recall
        nav = epub.read("OEBPS/nav.xhtml").decode("utf-8")
        assert "Love After Love" not in nav
        assert "Love (III): Recall" not in nav


def test_browse_epub_contains_indexes_and_current_counts(tmp_path):
    output = tmp_path / "browse.epub"
    build(output, edition="browse")
    with zipfile.ZipFile(output) as epub:
        names = epub.namelist()
        assert "OEBPS/cover.png" in names
        assert "OEBPS/index-authors.xhtml" in names
        assert "OEBPS/index-first-lines.xhtml" in names
        assert "OEBPS/index-difficulty.xhtml" in names
        kindness = epub.read("OEBPS/cat-b.xhtml").decode("utf-8")
        assert "All thirteen" not in kindness
        assert "All poems in this thread" in kindness


def test_memorize_rotation_uses_progress(tmp_path):
    output = tmp_path / "memorize.epub"
    build(output, edition="memorize", progress={"a1": {"state": "learning"},
                                                 "cs0": {"state": "memorized"}})
    with zipfile.ZipFile(output) as epub:
        rotation = epub.read("OEBPS/rotation.xhtml").decode("utf-8")
        assert "Learning now" in rotation
        assert "Love (III)" in rotation
        assert "Review" in rotation
        assert "thing with feathers" in rotation


def test_epub_build_is_reproducible_for_unchanged_inputs(tmp_path):
    first = tmp_path / "first.epub"
    second = tmp_path / "second.epub"
    build(first, edition="memorize", progress={})
    build(second, edition="memorize", progress={})
    assert first.read_bytes() == second.read_bytes()


def test_review_command_schedules_next_recall(tmp_path, monkeypatch):
    progress = tmp_path / "progress.json"
    monkeypatch.setattr(poembook_cli, "PROGRESS", progress)
    assert main(["review", "a1", "easy"]) == 0
    entry = json.loads(progress.read_text(encoding="utf-8"))["a1"]
    assert entry["state"] == "memorized"
    assert entry["review_interval_days"] == 3
    assert entry["next_review"] > entry["last_review"]
