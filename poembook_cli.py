#!/usr/bin/env python3
"""Command-line tools for auditing, building, and memorizing the collection."""

import argparse
import datetime
import json
import os
import re
import sys
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
    build_parser = commands.add_parser("build", help="build EPUB, Markdown, or both")
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
        errors, warnings = audit()
        for item in errors:
            print(f"ERROR {item}")
        for item in warnings:
            print(f"WARN  {item}")
        print(f"\n{len(errors)} errors, {len(warnings)} warnings")
        return 1 if errors or (args.strict and warnings) else 0
    if args.command == "build":
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
