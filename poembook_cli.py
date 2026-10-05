#!/usr/bin/env python3
"""Command-line tools for auditing, building, and memorizing the collection."""

import argparse
import concurrent.futures
import datetime
import html
import json
import os
import re
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from poems import CATEGORIES, POEMS, all_poems, slug

ROOT = Path(__file__).resolve().parent
TEXTS = ROOT / "texts"
PROGRESS = ROOT / ".poembook-progress.json"
REQUIRED = ("num", "title", "author", "dates", "form", "why", "difficulty", "links", "pd")
VERIFY_VERSION = 1


def nonblank_lines(text):
    return [line for line in text.splitlines() if line.strip()]


def expected_lines(poem):
    """Read an explicit line count from metadata; return None when it is approximate."""
    form = re.sub(r"<[^>]+>", "", poem.get("form", ""))
    if "~" in form or "opening" in form or "verses" in form:
        return None
    match = re.search(r"\b(\d+)\s+lines?\b", form)
    return int(match.group(1)) if match else None


def text_issues(cat, poem, text):
    issues = []
    lines = nonblank_lines(text)
    expected = expected_lines(poem)
    if expected and len(lines) != expected:
        issues.append(f"expected {expected} lines, found {len(lines)}")
    if len(lines) < 4:
        issues.append(f"only {len(lines)} nonblank lines")
    if len(text) > 15000 and (not expected or expected < 100):
        issues.append("implausibly long")
    first = lines[0].strip() if lines else ""
    suspicious = ("versions of ", "dictionary of national biography",
                  "courtesy of", "table of contents")
    if any(term in text.lower() for term in suspicious):
        issues.append("likely page boilerplate or unrelated prose")
    birth_statement = re.search(
        r"\bwas born (?:(?:on|in|at)\b|\d{1,4}\b|"
        r"(?:january|february|march|april|may|june|july|august|"
        r"september|october|november|december)\b)",
        text.lower(),
    )
    if birth_statement:
        issues.append("likely biographical prose")
    if re.fullmatch(r"\d+", first):
        issues.append("starts with a page number")
    return issues


def audit():
    errors, warnings, seen = [], [], set()
    for cat, poem in all_poems():
        sid = slug(cat["id"], poem)
        if sid in seen:
            errors.append(f"{sid}: duplicate slug")
        seen.add(sid)
        missing = [key for key in REQUIRED if key not in poem]
        if missing:
            errors.append(f"{sid}: missing metadata: {', '.join(missing)}")
        for label, url in poem.get("links", []):
            if not re.match(r"https?://", url):
                errors.append(f"{sid}: invalid link for {label!r}")
        path = TEXTS / f"{sid}.txt"
        if poem.get("pd") and not path.exists():
            warnings.append(f"{sid}: public-domain text missing")
        elif path.exists():
            text = path.read_text(encoding="utf-8")
            for issue in text_issues(cat, poem, text):
                warnings.append(f"{sid}: {issue}")
            meta, _ = load_text_meta(path)
            level = verification_level(meta)
            if level == "source":
                warnings.append(f"{sid}: source-compared; human editorial signoff pending")
            elif level != "editorial":
                warnings.append(f"{sid}: text is not editorially verified")
    return errors, warnings


def _match_words(value):
    """Return meaningful words for a deliberately forgiving page-content check."""
    ignored = {"the", "and", "with", "from", "saint", "this", "that"}
    return [word.lower() for word in re.findall(r"[A-Za-zÀ-ÿ]{4,}", value)
            if word.lower() not in ignored]


def _page_text(value):
    """Normalize visible HTML text enough to compare poetry across markup."""
    value = html.unescape(re.sub(r"<[^>]+>", " ", value))
    value = value.replace("’", "'").replace("‘", "'").replace("—", "-")
    return re.sub(r"\s+", " ", value).strip().lower()


def remote_records():
    """Yield every reader-facing link and every source used by a local text."""
    for cat, poem in all_poems():
        sid = slug(cat["id"], poem)
        for label, url in poem["links"]:
            yield {"kind": "link", "slug": sid, "title": poem["title"],
                   "author": poem["author"], "label": label, "url": url}
        text_path = TEXTS / f"{sid}.txt"
        metadata_path = TEXTS / f"{sid}.json"
        if not (text_path.exists() and metadata_path.exists()):
            continue
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        source_url = metadata.get("url")
        if source_url:
            first_line = next((line.strip() for line in text_path.read_text(
                encoding="utf-8").splitlines() if line.strip()), "")
            yield {"kind": "source", "slug": sid, "title": poem["title"],
                   "author": poem["author"], "label": "recorded source", "url": source_url,
                   "first_line": first_line}


def fetch_remote(url, timeout=20):
    """Fetch a bounded page body for an explicit, user-invoked link audit."""
    parts = urllib.parse.urlsplit(url)
    url = urllib.parse.urlunsplit((
        parts.scheme, parts.netloc, urllib.parse.quote(parts.path, safe="/%"),
        urllib.parse.quote(parts.query, safe="=&%"), urllib.parse.quote(parts.fragment, safe="%"),
    ))
    request = urllib.request.Request(
        url, headers={"User-Agent": "poembook/2.0 link audit"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.status, response.url, response.read(500_000).decode("utf-8", "ignore")


def audit_remote(records=None, fetch=fetch_remote, workers=8):
    """Check that remote pages are reachable and carry the expected poem evidence."""
    errors, warnings = [], []
    def inspect(record):
        try:
            _status, final_url, body = fetch(record["url"])
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403, 429) or 500 <= exc.code < 600:
                return (None, [f"{record['slug']}: {record['label']} could not be checked (HTTP {exc.code})"])
            return (f"{record['slug']}: {record['label']} unreachable: {exc}", [])
        except (TimeoutError, socket.timeout) as exc:
            return (None, [f"{record['slug']}: {record['label']} could not be checked ({exc})"])
        except (OSError, UnicodeError, ValueError) as exc:
            return (f"{record['slug']}: {record['label']} unreachable: {exc}", [])
        visible = _page_text(body)
        if record["kind"] == "source":
            expected = _page_text(record.get("first_line", ""))
            if expected and expected not in visible:
                title_matches = any(word in visible for word in _match_words(record["title"]))
                author_matches = any(word in visible for word in _match_words(record["author"]))
                if not (title_matches and author_matches):
                    return (None, [f"{record['slug']}: source reachable but poem evidence was not found ({final_url})"])
            return (None, [])
        record_warnings = []
        title_words = _match_words(record["title"])
        author_words = _match_words(record["author"])
        if not any(word in visible for word in title_words):
            record_warnings.append(f"{record['slug']}: link reachable but title was not found ({final_url})")
        if author_words and not any(word in visible for word in author_words):
            record_warnings.append(f"{record['slug']}: link reachable but author was not found ({final_url})")
        return (None, record_warnings)

    records = list(records or remote_records())
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        for error, record_warnings in executor.map(inspect, records):
            if error:
                errors.append(error)
            warnings.extend(record_warnings)
    return errors, warnings


def find_poem(sid):
    for cat, poem in all_poems():
        if slug(cat["id"], poem) == sid:
            return cat, poem
    raise SystemExit(f"unknown poem slug: {sid}")


def load_text_meta(path):
    meta_path = path.with_suffix(".json")
    if not meta_path.exists():
        return {}, meta_path
    return json.loads(meta_path.read_text(encoding="utf-8")), meta_path


def verification_level(meta):
    """Return the strongest recorded verification level, including legacy metadata."""
    verification = meta.get("verification", {})
    if verification.get("editorial", {}).get("status") == "passed":
        return "editorial"
    if meta.get("status") == "verified":  # v0 metadata migration
        return "editorial"
    if verification.get("source_comparison", {}).get("status") == "passed":
        return "source"
    if verification.get("structural", {}).get("status") == "passed":
        return "structural"
    return None


def record_verification(meta, level, method):
    now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
    verification = meta.setdefault("verification", {})
    verification[level] = {
        "status": "passed", "checked_at": now, "method": method,
        "schema_version": VERIFY_VERSION,
    }
    if level == "editorial":
        meta["status"] = "verified"
    elif meta.get("status") != "verified":
        meta["status"] = "structurally_valid"


def structurally_verify(cat, poem, path):
    if not path.exists():
        return ["text file does not exist"]
    return text_issues(cat, poem, path.read_text(encoding="utf-8"))


def editorial_prompt(sid, poem, path, meta):
    source = meta.get("url") or (poem.get("links") or [("", "no source URL recorded")])[0][1]
    while True:
        print(f"\n{sid}: {poem['title']} — {poem['author']}")
        print(f"Source: {source}")
        answer = input("Compared word-for-word with that edition? [y]es [v]iew [s]kip [q]uit: ").strip().lower()
        if answer in ("y", "yes"):
            return "verified"
        if answer in ("s", "skip", ""):
            return "skipped"
        if answer in ("q", "quit"):
            return "quit"
        if answer in ("v", "view"):
            print("\n" + path.read_text(encoding="utf-8").rstrip() + "\n")
        else:
            print("Please enter y, v, s, or q.")


def practice_text(text, mode):
    if mode == "full":
        return text
    if mode == "stanza-starts":
        stanzas = [stanza for stanza in text.replace("\r", "").split("\n\n")
                   if stanza.strip()]
        return "\n\n".join(stanza.splitlines()[0].strip() for stanza in stanzas)
    if mode == "structure":
        stanzas = [stanza for stanza in text.replace("\r", "").split("\n\n")
                   if stanza.strip()]
        output = []
        for index, stanza in enumerate(stanzas, 1):
            line_count = len(stanza.splitlines())
            unit = "line" if line_count == 1 else "lines"
            output.append(f"Stanza {index} — {line_count} {unit}")
        return "\n".join(output)
    output = []
    for line in text.splitlines():
        if not line.strip():
            output.append("")
            continue
        words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ’']+", line)
        if mode == "first-words":
            output.append(words[0] if words else "")
        elif mode == "initials":
            output.append(" ".join(word[0] for word in words))
        elif mode == "blanks":
            output.append(re.sub(r"[A-Za-zÀ-ÖØ-öø-ÿ’']+", "_____", line))
    return "\n".join(output)


def load_progress():
    if PROGRESS.exists():
        return json.loads(PROGRESS.read_text(encoding="utf-8"))
    return {}


def save_progress(data):
    PROGRESS.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="poembook")
    commands = parser.add_subparsers(dest="command", required=True)
    audit_parser = commands.add_parser("audit", help="check metadata and downloaded texts")
    audit_parser.add_argument("--strict", action="store_true", help="treat warnings as failure")
    audit_parser.add_argument("--book", choices=("poems", "hymns"), default="poems")
    remote_parser = commands.add_parser("audit-links", help="check remote poem links and recorded text sources")
    remote_parser.add_argument("--strict", action="store_true", help="treat ambiguous page matches as failure")
    build_parser = commands.add_parser("build", help="build EPUB, Markdown, or both")
    build_parser.add_argument("--book", choices=("poems", "hymns"), default="poems")
    build_parser.add_argument("--format", choices=("epub", "markdown", "all"), default="all")
    build_parser.add_argument("--edition", choices=("browse", "memorize", "all"), default="all",
                              help="EPUB edition(s) to build; Markdown is always the browse edition")
    practice_parser = commands.add_parser("practice", help="print a memorization aid")
    practice_parser.add_argument("slug")
    practice_parser.add_argument(
        "--mode",
        choices=("full", "stanza-starts", "first-words", "initials", "structure", "blanks"),
        default="first-words",
    )
    status_parser = commands.add_parser("status", help="show or update memorization status")
    status_parser.add_argument("slug", nargs="?")
    status_parser.add_argument("state", nargs="?", choices=("want-to-learn", "learning", "memorized"))
    review_parser = commands.add_parser("review", help="record a recall result and schedule review")
    review_parser.add_argument("slug")
    review_parser.add_argument("rating", choices=("easy", "hesitant", "failed"))
    verify_parser = commands.add_parser("verify", help="structurally check and editorially review texts")
    verify_parser.add_argument("slug", nargs="?")
    verify_parser.add_argument("--all", action="store_true", help="check all texts, then open a resumable review queue")
    verify_parser.add_argument("--structural-only", action="store_true", help="record structural results without editorial review")
    commands.add_parser("clean-cache", help="remove safe title/folio preambles")
    args = parser.parse_args(argv)

    if args.command == "audit":
        if args.book == "hymns":
            from build_hymns import audit_hymns
            errors = audit_hymns()
            for item in errors:
                print(f"ERROR {item}")
            print(f"\n{len(errors)} errors")
            return 1 if errors else 0
        errors, warnings = audit()
        for item in errors:
            print(f"ERROR {item}")
        for item in warnings:
            print(f"WARN  {item}")
        print(f"\n{len(errors)} errors, {len(warnings)} warnings")
        return 1 if errors or (args.strict and warnings) else 0
    if args.command == "audit-links":
        errors, warnings = audit_remote()
        for item in errors:
            print(f"ERROR {item}")
        for item in warnings:
            print(f"WARN  {item}")
        print(f"\n{len(errors)} errors, {len(warnings)} warnings")
        return 1 if errors or (args.strict and warnings) else 0
    if args.command == "build":
        if args.book == "hymns":
            if args.edition == "memorize":
                raise SystemExit("the hymn book currently has a browse edition only")
            from build_hymns import build_epub as build_hymn_epub, build_markdown as build_hymn_markdown
            if args.format in ("epub", "all"):
                output = ROOT / "hymnbook-browse.epub"
                counts = build_hymn_epub(output)
                print(f"wrote {output.name} ({counts['total']} hymns; {counts['with_text']} with words)")
            if args.format in ("markdown", "all"):
                output = ROOT / "hymnbook-browse.md"
                counts = build_hymn_markdown(output)
                print(f"wrote {output.name} ({counts['total']} hymns; {counts['with_text']} with words)")
            return 0
        if args.format in ("epub", "all"):
            from build_epub import build
            editions = ("browse", "memorize") if args.edition == "all" else (args.edition,)
            outputs = {
                "browse": ROOT / "poembook-browse.epub",
                "memorize": ROOT / "poembook-memorize.epub",
            }
            for edition in editions:
                counts = build(str(outputs[edition]), edition=edition)
                print(f"wrote {outputs[edition].name} ({counts['total']} poems)")
        if args.format in ("markdown", "all"):
            from make_markdown import main as markdown_main
            old = sys.argv
            try:
                sys.argv = ["make_markdown.py", "-o", str(ROOT / "poems-to-memorize.md")]
                markdown_main()
            finally:
                sys.argv = old
        return 0
    if args.command == "practice":
        cat, poem = find_poem(args.slug)
        path = TEXTS / f"{args.slug}.txt"
        if not path.exists():
            raise SystemExit("no local text; copyrighted and missing poems cannot be practiced here")
        print(f"{poem['title']} — {poem['author']}\n")
        print(practice_text(path.read_text(encoding="utf-8").strip(), args.mode))
        return 0
    if args.command == "status":
        data = load_progress()
        if args.slug and args.state:
            find_poem(args.slug)
            entry = data.setdefault(args.slug, {})
            entry["state"] = args.state
            entry["updated_at"] = datetime.date.today().isoformat()
            save_progress(data)
        for sid, value in sorted(data.items()):
            print(f"{sid:<6} {value['state']}")
        return 0
    if args.command == "review":
        find_poem(args.slug)
        data = load_progress()
        entry = data.setdefault(args.slug, {"state": "learning"})
        today = datetime.date.today()
        previous = int(entry.get("review_interval_days", 1))
        if args.rating == "easy":
            interval = min(max(previous * 2, 3), 60)
            entry["state"] = "memorized"
        elif args.rating == "hesitant":
            interval = 1
        else:
            interval = 0
            entry["state"] = "learning"
        entry.update({
            "last_review": today.isoformat(),
            "last_rating": args.rating,
            "review_interval_days": interval,
            "next_review": (today + datetime.timedelta(days=interval)).isoformat(),
        })
        save_progress(data)
        print(f"{args.slug}: {args.rating}; next review {entry['next_review']}")
        return 0
    if args.command == "verify":
        if bool(args.slug) == bool(args.all):
            raise SystemExit("provide one slug or --all")
        targets = list(all_poems()) if args.all else [find_poem(args.slug)]
        clean, failed = [], []
        for cat, poem in targets:
            sid = slug(cat["id"], poem)
            path = TEXTS / f"{sid}.txt"
            if not poem.get("pd") and not path.exists():
                continue
            issues = structurally_verify(cat, poem, path)
            if issues:
                failed.append((sid, issues))
                continue
            meta, meta_path = load_text_meta(path)
            record_verification(meta, "structural", "poembook structural checks")
            meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            clean.append((sid, poem, path, meta, meta_path))
        print(f"Structural verification: {len(clean)} passed, {len(failed)} failed")
        for sid, issues in failed:
            print(f"  FAIL {sid}: {'; '.join(issues)}")
        if args.structural_only:
            return 1 if failed else 0
        pending = [item for item in clean if verification_level(item[3]) != "editorial"]
        if not pending:
            print("Editorial verification: nothing pending")
            return 1 if failed else 0
        if not sys.stdin.isatty():
            print(f"Editorial verification: {len(pending)} pending; run in an interactive terminal")
            return 1
        verified = 0
        for sid, poem, path, meta, meta_path in pending:
            result = editorial_prompt(sid, poem, path, meta)
            if result == "quit":
                break
            if result == "verified":
                record_verification(meta, "editorial", "human word-for-word source comparison")
                meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                verified += 1
                print(f"  marked {sid} editorially verified")
        remaining = len(pending) - verified
        print(f"Editorial verification: {verified} newly verified, {remaining} left in this queue")
        return 1 if failed else 0
    if args.command == "clean-cache":
        changed = 0
        for cat, poem in all_poems():
            expected = expected_lines(poem)
            path = TEXTS / f"{slug(cat['id'], poem)}.txt"
            if not expected or not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            lines = text.splitlines()
            positions = [i for i, line in enumerate(lines) if line.strip()]
            excess = len(positions) - expected
            if 0 < excess <= 4:
                remove = set(positions[:excess])
                cleaned = "\n".join(line for i, line in enumerate(lines) if i not in remove).strip() + "\n"
                if not text_issues(cat, poem, cleaned):
                    path.write_text(cleaned, encoding="utf-8")
                    print(f"cleaned {slug(cat['id'], poem)} ({excess} preamble lines)")
                    changed += 1
        print(f"cleaned {changed} texts")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
