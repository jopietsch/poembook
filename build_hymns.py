"""Build the words-focused companion hymnal in EPUB and Markdown."""

import datetime
import html
import json
import uuid
import zipfile
from pathlib import Path

from build_epub import CSS, page, verse_html
from hymns import CHAPTERS, HYMNS, SECTIONS, TUNES

ROOT = Path(__file__).resolve().parent
TEXT_DIR = ROOT / "hymn_texts"
TITLE = "Hymns to Sing and Cherish"
BOOK_ID = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_DNS, "poembook.hymns.browse"))


def included_text(hymn):
    """Return words only for a specifically selected public-domain edition."""
    if hymn["text_rights"] != "public_domain" or not hymn["text_edition"]:
        return None
    path = TEXT_DIR / f"{hymn['id']}.txt"
    sidecar = path.with_suffix(".json")
    if not (path.exists() and sidecar.exists()):
        return None
    metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    if (metadata.get("chosen_edition") != hymn["text_edition"]
            or metadata.get("text_rights") != "public_domain"
            or not metadata.get("url")):
        return None
    text = path.read_text(encoding="utf-8").strip()
    return text if len([line for line in text.splitlines() if line.strip()]) >= 4 else None


def audit_hymns():
    errors = []
    section_ids = {section_id for section_id, _title in SECTIONS}
    chapter_ids = {chapter_id for chapter_id, _title, _intro in CHAPTERS}
    hymn_ids = {hymn["id"] for hymn in HYMNS}
    seen = set()
    for hymn in HYMNS:
        sid = hymn["id"]
        if sid in seen:
            errors.append(f"{sid}: duplicate ID")
        seen.add(sid)
        if hymn["section"] not in section_ids:
            errors.append(f"{sid}: unknown section")
        if hymn["chapter"] not in chapter_ids:
            errors.append(f"{sid}: unknown chapter")
        if hymn.get("related_to") and hymn["related_to"] not in hymn_ids:
            errors.append(f"{sid}: unknown related hymn")
        if hymn.get("related_to") == sid:
            errors.append(f"{sid}: cannot be related to itself")
        if hymn["section"] == "advent_christmas" and not hymn.get("season"):
            errors.append(f"{sid}: missing season")
        if hymn["tune"] and hymn["tune"] not in TUNES:
            errors.append(f"{sid}: unknown tune")
        if hymn["text_rights"] not in {"pending", "public_domain", "permission_required"}:
            errors.append(f"{sid}: unknown text rights status")
        if not hymn["source"].startswith("https://"):
            errors.append(f"{sid}: invalid source link")
        if hymn.get("candidate_edition"):
            if hymn["text_rights"] != "pending":
                errors.append(f"{sid}: historical candidate conflicts with selected text")
            if not hymn.get("candidate_year") or hymn["candidate_year"] >= 1931:
                errors.append(f"{sid}: historical candidate needs a pre-1931 year")
            if not hymn.get("candidate_source", "").startswith("https://"):
                errors.append(f"{sid}: invalid historical candidate link")
        if hymn["text_rights"] == "public_domain" and not included_text(hymn):
            errors.append(f"{sid}: selected text is missing or lacks matching provenance")
        if hymn["text_rights"] != "public_domain" and (TEXT_DIR / f"{sid}.txt").exists():
            errors.append(f"{sid}: text exists without clearance for inclusion")
    return errors


def _modified():
    paths = [Path(__file__), ROOT / "hymns.py", ROOT / "build_epub.py"]
    paths.extend(TEXT_DIR.glob("*"))
    timestamp = max(path.stat().st_mtime for path in paths if path.is_file())
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc)


def _hymn_page(hymn):
    esc = html.escape
    parts = [f'<h1>{esc(hymn["title"])}</h1>',
             f'<p class="author">{esc(hymn["author"])}</p>',
             '<dl class="meta">',
             f'<dt>First line</dt><dd>{esc(hymn["first_line"])}</dd>']
    if hymn["tune"]:
        parts.append(f'<dt>Tune</dt><dd>{esc(TUNES[hymn["tune"]]["name"])}</dd>')
    if hymn["meter"]:
        parts.append(f'<dt>Meter</dt><dd>{esc(hymn["meter"])}</dd>')
    if hymn.get("season"):
        parts.append(f'<dt>Season</dt><dd>{esc(hymn["season"])}</dd>')
    elif hymn["chapter"] != "advent_christmas":
        theme = next(title for section_id, title in SECTIONS
                     if section_id == hymn["section"])
        parts.append(f'<dt>Theme</dt><dd>{esc(theme)}</dd>')
    if hymn.get("related_to"):
        related = next(item for item in HYMNS if item["id"] == hymn["related_to"])
        parts.append(f'<dt>Related to</dt><dd><a href="{related["id"]}.xhtml">'
                     f'{esc(related["title"])}</a></dd>')
    parts.append('</dl>')
    words = included_text(hymn)
    if words:
        parts.append(verse_html(words))
        parts.append(f'<p class="small">Words from {esc(hymn["text_edition"])}. '
                     'Human word-for-word editorial review remains pending.</p>')
    elif hymn["text_rights"] == "permission_required":
        parts.append('<p class="nofetch">These words require permission for reproduction. '
                     'Use the source link below.</p>')
    else:
        parts.append('<p class="nofetch">Words are linked below; no text edition is '
                     'included in this book yet.</p>')
    if hymn.get("candidate_edition"):
        parts.append(f'<p class="small">Historical edition to inspect: '
                     f'<a href="{esc(hymn["candidate_source"], quote=True)}">'
                     f'{esc(hymn["candidate_edition"])}</a>. '
                     'Its wording and rights have not been checked for inclusion.</p>')
        if hymn.get("candidate_note"):
            parts.append(f'<p class="small">{esc(hymn["candidate_note"])}</p>')
    parts.append(f'<p><a href="{esc(hymn["source"], quote=True)}">Source and versions</a></p>')
    return page(hymn["title"], "\n".join(parts))


def build_epub(outpath):
    errors = audit_hymns()
    if errors:
        raise ValueError("; ".join(errors))
    modified = _modified()
    stamp = modified.replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
    date = modified.date().isoformat()
    files = {"style.css": CSS}
    files["title.xhtml"] = page(TITLE, f'<h1 class="booktitle">{TITLE}</h1>'
        '<p class="subtitle">A growing collection of hymn words and sources</p>'
        f'<p class="byline">{len(HYMNS)} hymns</p>')
    nav = ['<nav epub:type="toc" id="toc"><h1>Contents</h1><ol>']
    spine = ["title.xhtml", "nav.xhtml"]
    for chapter_id, chapter_title, intro in CHAPTERS:
        chapter_hymns = [hymn for hymn in HYMNS if hymn["chapter"] == chapter_id]
        chapter_name = f"chapter-{chapter_id}.xhtml"
        files[chapter_name] = page(chapter_title,
                                   f'<h1>{html.escape(chapter_title)}</h1>'
                                   f'<p>{len(chapter_hymns)} hymns</p>'
                                   f'<p>{html.escape(intro)}</p>')
        spine.append(chapter_name)
        nav.append(f'<li><a href="{chapter_name}">{html.escape(chapter_title)}</a><ol>')
        for hymn in chapter_hymns:
            filename = f'{hymn["id"]}.xhtml'
            files[filename] = _hymn_page(hymn)
            spine.append(filename)
            nav.append(f'<li><a href="{filename}">{html.escape(hymn["title"])}</a></li>')
        nav.append('</ol></li>')
    nav.append('</ol></nav>')
    files["nav.xhtml"] = page("Contents", "\n".join(nav), is_nav=True)
    manifest = [
        '<item id="css" href="style.css" media-type="text/css"/>',
        '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
    ]
    refs = []
    for index, filename in enumerate(spine):
        item_id = "nav" if filename == "nav.xhtml" else f"x{index}"
        if filename != "nav.xhtml":
            manifest.append(f'<item id="{item_id}" href="{filename}" media-type="application/xhtml+xml"/>')
        refs.append(f'<itemref idref="{item_id}"/>')
    files["content.opf"] = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid">'
        '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
        f'<dc:identifier id="bookid">{BOOK_ID}</dc:identifier>'
        f'<dc:title>{TITLE}</dc:title><dc:language>en</dc:language>'
        f'<dc:date>{date}</dc:date><meta property="dcterms:modified">{stamp}</meta>'
        '</metadata><manifest>' + "".join(manifest) + '</manifest><spine>'
        + "".join(refs) + '</spine></package>')
    outpath = Path(outpath)
    with zipfile.ZipFile(outpath, "w") as archive:
        zip_time = max((1980, 1, 1, 0, 0, 0), modified.timetuple()[:6])

        def write(name, content, compression=zipfile.ZIP_DEFLATED):
            entry = zipfile.ZipInfo(name, date_time=zip_time)
            entry.compress_type = compression
            archive.writestr(entry, content)

        write("mimetype", "application/epub+zip", zipfile.ZIP_STORED)
        write("META-INF/container.xml", '<?xml version="1.0" encoding="utf-8"?>'
              '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
              '<rootfiles><rootfile full-path="OEBPS/content.opf" '
              'media-type="application/oebps-package+xml"/></rootfiles></container>')
        for name, content in files.items():
            write("OEBPS/" + name, content)
    return {"total": len(HYMNS), "with_text": sum(bool(included_text(h)) for h in HYMNS)}


def build_markdown(outpath):
    errors = audit_hymns()
    if errors:
        raise ValueError("; ".join(errors))
    lines = [f"# {TITLE}", "", "A growing collection of hymn words and sources.", ""]
    for chapter_id, chapter_title, intro in CHAPTERS:
        lines.extend([f"## {chapter_title}", "", intro, ""])
        for hymn in HYMNS:
            if hymn["chapter"] != chapter_id:
                continue
            lines.extend([f"### {hymn['title']}", "", f"*{hymn['author']}*", "",
                          f"First line: {hymn['first_line']}  "])
            if hymn["tune"]:
                lines.append(f"Tune: {TUNES[hymn['tune']]['name']}  ")
            if hymn["meter"]:
                lines.append(f"Meter: {hymn['meter']}  ")
            if hymn.get("season"):
                lines.append(f"Season: {hymn['season']}  ")
            else:
                theme = next(title for section_id, title in SECTIONS
                             if section_id == hymn["section"])
                lines.append(f"Theme: {theme}  ")
            if hymn.get("related_to"):
                related = next(item for item in HYMNS if item["id"] == hymn["related_to"])
                lines.append(f"Related to: {related['title']}  ")
            lines.append("")
            words = included_text(hymn)
            if words:
                for stanza in words.split("\n\n"):
                    lines.extend(line + "  " for line in stanza.splitlines())
                    lines.append("")
                lines.extend([f"Words from {hymn['text_edition']}. Human editorial review remains pending.", ""])
            elif hymn["text_rights"] == "permission_required":
                lines.extend(["These words require permission for reproduction. Use the source link below.", ""])
            else:
                lines.extend(["No text edition is included in this book yet. Use the source link below.", ""])
            if hymn.get("candidate_edition"):
                lines.extend([
                    f"Historical edition to inspect: [{hymn['candidate_edition']}]"
                    f"({hymn['candidate_source']}). Its wording and rights have not "
                    "been checked for inclusion.", ""
                ])
                if hymn.get("candidate_note"):
                    lines.extend([hymn["candidate_note"], ""])
            lines.extend([f"[Source and versions]({hymn['source']})", ""])
    Path(outpath).write_text("\n".join(lines), encoding="utf-8")
    return {"total": len(HYMNS), "with_text": sum(bool(included_text(h)) for h in HYMNS)}
