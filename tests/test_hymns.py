import zipfile
from xml.etree import ElementTree

from build_hymns import audit_hymns, build_epub, build_markdown, included_text
from hymns import CHAPTERS, HYMNS


def test_catalog_has_stable_unique_ids_and_clearance():
    assert len(HYMNS) == 69
    assert len({hymn["id"] for hymn in HYMNS}) == len(HYMNS)
    assert audit_hymns() == []
    assert sum(bool(hymn.get("related_to")) for hymn in HYMNS) == 25
    assert sum(hymn["section"] == "advent_christmas" for hymn in HYMNS) == 30
    assert [(title, sum(h["chapter"] == chapter_id for h in HYMNS))
            for chapter_id, title, _intro in CHAPTERS] == [
                ("The original fourteen", 14),
                ("Related hymns", 25),
                ("Advent and Christmas", 30),
            ]
    assert [hymn["id"] for hymn in HYMNS if included_text(hymn)] == [
        "h001", "h002", "h003", "h007", "h008", "h009", "h010", "h011", "h012", "h014"
    ]
    assert next(h for h in HYMNS if h["id"] == "h004")["text_rights"] == "permission_required"
    candidates = [h for h in HYMNS if h.get("candidate_edition")]
    assert len(candidates) == 58
    assert all(h["text_rights"] == "pending" for h in candidates)
    assert all(h["candidate_year"] < 1931 for h in candidates)
    assert next(h for h in candidates if h["id"] == "h015")["candidate_edition"] == (
        "New Baptist Hymnal (1926), no. 181"
    )
    assert "later stanzas" in next(h for h in candidates if h["id"] == "h044")["candidate_note"]
    assert "differs" in next(h for h in candidates if h["id"] == "h054")["candidate_note"]


def test_hymn_epub_contains_all_entries_and_only_cleared_words(tmp_path):
    output = tmp_path / "hymns.epub"
    counts = build_epub(output)
    assert counts == {"total": 69, "with_text": 10}
    with zipfile.ZipFile(output) as epub:
        assert epub.infolist()[0].filename == "mimetype"
        assert epub.read("mimetype") == b"application/epub+zip"
        for name in ("content.opf", "nav.xhtml", "title.xhtml", "h001.xhtml", "h004.xhtml",
                     "h015.xhtml", "h040.xhtml", "chapter-requested.xhtml",
                     "chapter-related.xhtml", "chapter-advent_christmas.xhtml"):
            ElementTree.fromstring(epub.read(f"OEBPS/{name}"))
        assert "Praise God, from whom all blessings flow" in epub.read("OEBPS/h001.xhtml").decode()
        assert "O Lord my God, when I in awesome wonder" in epub.read("OEBPS/h004.xhtml").decode()
        assert "require permission for reproduction" in epub.read("OEBPS/h004.xhtml").decode()
        assert "Related to" in epub.read("OEBPS/h015.xhtml").decode()
        assert "Historical edition to inspect" in epub.read("OEBPS/h015.xhtml").decode()
        assert "Advent and Christmas" in epub.read("OEBPS/chapter-advent_christmas.xhtml").decode()
        nav = epub.read("OEBPS/nav.xhtml").decode()
        assert nav.index("The original fourteen") < nav.index("Related hymns")
        assert nav.index("Related hymns") < nav.index("Advent and Christmas")


def test_hymn_markdown_lists_all_hymns_and_available_text(tmp_path):
    output = tmp_path / "hymns.md"
    counts = build_markdown(output)
    content = output.read_text(encoding="utf-8")
    assert counts == {"total": 69, "with_text": 10}
    assert content.count("### ") == 69
    assert [line for line in content.splitlines() if line.startswith("## ")] == [
        "## The original fourteen", "## Related hymns", "## Advent and Christmas"
    ]
    assert content.index("### Holy, Holy, Holy! Lord God Almighty!") < content.index(
        "## Related hymns"
    )
    assert "Praise Father, Son, and Holy Ghost." in content
    assert "No text edition is included" in content
    assert "Historical edition to inspect" in content
    assert "New Baptist Hymnal (1926), no. 181" in content
