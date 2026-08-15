import json
import zipfile
from pathlib import Path

from build_epub import build
from poems import CATEGORIES, POEMS, all_poems, slug
from poembook_cli import audit, expected_lines, practice_text, record_verification, text_issues, verification_level
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


def test_line_count_parser():
    assert expected_lines({"form": "14 lines, sonnet"}) == 14
    assert expected_lines({"form": "~20 lines"}) is None


def test_practice_modes_preserve_line_structure():
    poem = "Hope is a thing\nWith feathers"
    assert practice_text(poem, "first-words") == "Hope\nWith"
    assert practice_text(poem, "initials") == "H i a t\nW f"
    assert practice_text(poem, "blanks") == "_____ _____ _____ _____\n_____ _____"


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
