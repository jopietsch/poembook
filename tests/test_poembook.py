from poems import CATEGORIES, POEMS, all_poems, slug
from poembook_cli import expected_lines, practice_text


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
