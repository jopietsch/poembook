from poems import CATEGORIES, POEMS, all_poems, slug
from poembook_cli import expected_lines, practice_text, record_verification, text_issues, verification_level
from fetch_texts import normalize_candidate


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


def test_poem_language_is_not_mistaken_for_biographical_boilerplate():
    assert text_issues({}, {"form": "4 lines"}, "It is the blight man was born for,\nOne\nTwo\nThree") == []


def test_named_anthology_section_is_extracted_to_expected_length():
    poem = {"form": "3 lines", "extract_after": "POEM TITLE"}
    source = "unrelated prose\nPOEM TITLEFirst line\nSecond line\nThird line\ntrailing notes"
    assert normalize_candidate({}, poem, source) == "First line\nSecond line\nThird line"
