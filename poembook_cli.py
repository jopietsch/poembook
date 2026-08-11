#!/usr/bin/env python3
"""Command-line tools for auditing, building, and memorizing the collection."""

import argparse
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
    suspicious = ("versions of ", "was born", "dictionary of national biography",
                  "courtesy of", "table of contents")
    if any(term in text.lower() for term in suspicious):
        issues.append("likely page boilerplate or unrelated prose")
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
            meta_path = path.with_suffix(".json")
            meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
            if meta.get("status") != "verified":
                warnings.append(f"{sid}: text is not marked verified")
    return errors, warnings


def find_poem(sid):
    for cat, poem in all_poems():
        if slug(cat["id"], poem) == sid:
            return cat, poem
    raise SystemExit(f"unknown poem slug: {sid}")


def practice_text(text, mode):
    if mode == "full":
        return text
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
    practice_parser = commands.add_parser("practice", help="print a memorization aid")
    practice_parser.add_argument("slug")
    practice_parser.add_argument("--mode", choices=("full", "first-words", "initials", "blanks"), default="first-words")
    status_parser = commands.add_parser("status", help="show or update memorization status")
    status_parser.add_argument("slug", nargs="?")
    status_parser.add_argument("state", nargs="?", choices=("want-to-learn", "learning", "memorized"))
    verify_parser = commands.add_parser("verify", help="mark a reviewed local text verified")
    verify_parser.add_argument("slug")
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
            counts = build(str(ROOT / "poems-to-memorize.epub"))
            print(f"wrote poems-to-memorize.epub ({counts['total']} poems)")
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
            data[args.slug] = {"state": args.state}
            save_progress(data)
        for sid, value in sorted(data.items()):
            print(f"{sid:<6} {value['state']}")
        return 0
    if args.command == "verify":
        cat, poem = find_poem(args.slug)
        path = TEXTS / f"{args.slug}.txt"
        if not path.exists():
            raise SystemExit("text file does not exist")
        issues = text_issues(cat, poem, path.read_text(encoding="utf-8"))
        if issues:
            raise SystemExit("cannot verify: " + "; ".join(issues))
        meta_path = path.with_suffix(".json")
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        meta["status"] = "verified"
        meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"marked {args.slug} verified")
        return 0
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
