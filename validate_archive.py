#!/usr/bin/env python3
"""Read-only, offline consistency checks for the TurkAnimeTV static archive."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


INDEX_START = "/*INDEX_START*/"
INDEX_END = "/*INDEX_END*/"
VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}
JSONP_PATTERN = re.compile(
    r'^window\.__TKA__=window\.__TKA__\|\|\{\};'
    r'window\.__TKA__\[("(?:[^"\\]|\\.)*")\]=(\[.*\]);?\s*$',
    re.DOTALL,
)


def read_text(path: Path, errors: list[str], label: str | None = None) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"{label or path.as_posix()}: cannot read UTF-8 file ({exc})")
        return None


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def check_javascript(source: str, label: str, errors: list[str], node: str | None) -> None:
    if node is None:
        errors.append(f"{label}: Node.js is required to syntax-check JavaScript")
        return
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as temp:
        temp.write(source)
        temp_path = Path(temp.name)
    try:
        result = subprocess.run(
            [node, "--check", str(temp_path)], capture_output=True, text=True, check=False
        )
        if result.returncode:
            detail = (result.stderr or result.stdout).strip().splitlines()
            errors.append(
                f"{label}: JavaScript syntax error" + (f" ({detail[-1]})" if detail else "")
            )
    finally:
        temp_path.unlink(missing_ok=True)


def parse_jsonp(path: Path, errors: list[str]) -> tuple[str, list[dict[str, Any]]] | None:
    label = path.as_posix()
    source = read_text(path, errors, label)
    if source is None:
        return None
    match = JSONP_PATTERN.fullmatch(source)
    if not match:
        errors.append(f"{label}: expected window.__TKA__[slug]=JSON-array JSONP format")
        return None
    try:
        anime_slug = json.loads(match.group(1))
        episodes = json.loads(match.group(2))
    except json.JSONDecodeError as exc:
        errors.append(f"{label}: invalid JSON payload at line {exc.lineno}, column {exc.colno}")
        return None
    if not is_nonempty_string(anime_slug):
        errors.append(f"{label}: anime slug must be a non-empty string")
        return None
    if not isinstance(episodes, list):
        errors.append(f"{label}: anime payload must be an array")
        return None

    episode_slugs: set[str] = set()
    for episode_number, episode in enumerate(episodes, start=1):
        where = f"{label}: episode {episode_number}"
        if not isinstance(episode, dict):
            errors.append(f"{where} must be an object")
            continue
        if episode.get("no") is not None and (
            isinstance(episode.get("no"), bool)
            or not isinstance(episode.get("no"), (int, float))
        ):
            errors.append(f"{where} field 'no' must be a number or null")
        if not is_nonempty_string(episode.get("ad")):
            errors.append(f"{where} field 'ad' must be a non-empty string")
        slug = episode.get("slug")
        if not is_nonempty_string(slug):
            errors.append(f"{where} field 'slug' must be a non-empty string")
        elif slug in episode_slugs:
            errors.append(f"{where} duplicates episode slug {slug!r}")
        else:
            episode_slugs.add(slug)
        links = episode.get("links")
        if not isinstance(links, list):
            errors.append(f"{where} field 'links' must be an array")
            continue
        for link_number, link in enumerate(links, start=1):
            link_where = f"{where}, link {link_number}"
            if not isinstance(link, dict):
                errors.append(f"{link_where} must be an object")
                continue
            if not is_nonempty_string(link.get("tip")):
                errors.append(f"{link_where} field 'tip' must be a non-empty string")
            if link.get("tip") == "url" and not is_nonempty_string(link.get("url")):
                errors.append(f"{link_where} URL must be a non-empty string")
            for key in ("player", "fansub"):
                if key in link and not isinstance(link[key], str):
                    errors.append(f"{link_where} field '{key}' must be a string when present")
    return anime_slug, episodes


class SiteStructureParser(HTMLParser):
    """Check critical document/script/style closure and collect inline JS."""

    def __init__(self, label: str, errors: list[str], require_document_shell: bool = True) -> None:
        super().__init__(convert_charrefs=False)
        self.label = label
        self.errors = errors
        self.require_document_shell = require_document_shell
        self.open_count: dict[str, int] = {}
        self.close_count: dict[str, int] = {}
        self.doctypes = 0
        self.active_script: tuple[dict[str, str | None], list[str]] | None = None
        self.inline_scripts: list[str] = []

    def handle_decl(self, decl: str) -> None:
        if decl.lower().startswith("doctype html"):
            self.doctypes += 1

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.open_count[tag] = self.open_count.get(tag, 0) + 1
        if tag == "script":
            if self.active_script is not None:
                self.errors.append(f"{self.label}: nested <script> element")
            self.active_script = (dict(attrs), [])
        elif tag == "style" and getattr(self, "active_style", False):
            self.errors.append(f"{self.label}: nested <style> element")
        elif tag == "style":
            self.active_style = True

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        self.close_count[tag] = self.close_count.get(tag, 0) + 1
        if tag == "script":
            if self.active_script is None:
                self.errors.append(f"{self.label}: closing </script> has no opening <script>")
            else:
                attrs, chunks = self.active_script
                self.active_script = None
                script_type = (attrs.get("type") or "").lower()
                if not attrs.get("src") and script_type not in {
                    "application/json", "application/ld+json", "importmap"
                }:
                    self.inline_scripts.append("".join(chunks))
        elif tag == "style":
            if not getattr(self, "active_style", False):
                self.errors.append(f"{self.label}: closing </style> has no opening <style>")
            self.active_style = False

    def handle_data(self, data: str) -> None:
        if self.active_script is not None:
            self.active_script[1].append(data)

    def validate(self) -> None:
        if self.active_script is not None:
            self.errors.append(f"{self.label}: unclosed <script> element")
        if getattr(self, "active_style", False):
            self.errors.append(f"{self.label}: unclosed <style> element")
        if self.require_document_shell and self.doctypes != 1:
            self.errors.append(f"{self.label}: expected exactly one <!doctype html>")
        if self.require_document_shell:
            for tag in ("html", "head", "body"):
                if self.open_count.get(tag, 0) != 1 or self.close_count.get(tag, 0) != 1:
                    self.errors.append(f"{self.label}: expected one properly closed <{tag}> element")
        for tag in ("script", "style"):
            if self.open_count.get(tag, 0) != self.close_count.get(tag, 0):
                self.errors.append(f"{self.label}: <{tag}> opening/closing tag counts differ")


def validate_html(
    path: Path, errors: list[str], node: str | None, *, require_document_shell: bool = True
) -> str | None:
    label = path.as_posix()
    source = read_text(path, errors, label)
    if source is None:
        return None
    parser = SiteStructureParser(label, errors, require_document_shell)
    try:
        parser.feed(source)
        parser.close()
    except Exception as exc:  # HTMLParser usually recovers, but fail clearly if it cannot.
        errors.append(f"{label}: HTML parsing failed ({exc})")
        return source
    parser.validate()
    for number, script in enumerate(parser.inline_scripts, start=1):
        before = len(errors)
        check_javascript(script, f"{label}: inline script {number}", errors, node)
        if len(errors) > before and "JavaScript syntax error" in errors[-1]:
            errors[-1] = errors[-1].replace("JavaScript syntax error", "inline JavaScript syntax error")
    return source


def validate_override(path: Path, variable: str, errors: list[str]) -> list[Any] | None:
    label = path.as_posix()
    source = read_text(path, errors, label)
    if source is None:
        return None
    without_comments = re.sub(r"/\*[\s\S]*?\*/", "", source)
    assignment = re.match(r"\s*window\.([A-Z]+)\s*=\s*", without_comments)
    if not assignment or assignment.group(1) != variable:
        errors.append(f"{label}: expected window.{variable} = JSON-array format")
        return None
    try:
        entries, end = json.JSONDecoder().raw_decode(without_comments, assignment.end())
    except json.JSONDecodeError as exc:
        errors.append(f"{label}: invalid JSON array at line {exc.lineno}, column {exc.colno}")
        return None
    tail = without_comments[end:].strip()
    if tail not in {"", ";"}:
        errors.append(f"{label}: unexpected code after the {variable} data array")
        return None
    if not isinstance(entries, list):
        errors.append(f"{label}: {variable} value must be an array")
        return None
    if variable == "KALDIRILAN":
        seen: set[str] = set()
        for number, url in enumerate(entries, start=1):
            if not is_nonempty_string(url):
                errors.append(f"{label}: entry {number} must be a non-empty URL string")
                continue
            parsed = urlsplit(url)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                errors.append(f"{label}: entry {number} is not an HTTP(S) URL")
            if url in seen:
                errors.append(f"{label}: duplicate URL at entry {number}")
            seen.add(url)
    else:
        for number, entry in enumerate(entries, start=1):
            where = f"{label}: entry {number}"
            if not isinstance(entry, dict):
                errors.append(f"{where} must be an object")
                continue
            for key in ("slug", "url"):
                if not is_nonempty_string(entry.get(key)):
                    errors.append(f"{where} field '{key}' must be a non-empty string")
            url = entry.get("url")
            if is_nonempty_string(url):
                parsed = urlsplit(url)
                if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                    errors.append(f"{where} URL must use HTTP or HTTPS")
            bolum = entry.get("bolum")
            if (
                bolum is None
                or isinstance(bolum, bool)
                or not isinstance(bolum, (str, int, float))
                or (isinstance(bolum, str) and not bolum.strip())
            ):
                errors.append(f"{where} field 'bolum' must be a string or number")
            for key in ("player", "fansub"):
                if key in entry and not isinstance(entry[key], str):
                    errors.append(f"{where} field '{key}' must be a string when present")
    return entries


def validate_archive(root: Path | str) -> list[str]:
    """Return all discovered errors without modifying files or contacting the network."""
    root = Path(root)
    errors: list[str] = []
    node = shutil.which("node")

    anime_files = sorted((root / "b").glob("*.js")) if (root / "b").is_dir() else []
    if not anime_files:
        errors.append("b/: no anime .js files found")
    anime_data: dict[str, list[dict[str, Any]]] = {}
    for path in anime_files:
        parsed = parse_jsonp(path, errors)
        if parsed is None:
            continue
        slug, episodes = parsed
        if path.stem != slug:
            errors.append(f"{path.as_posix()}: filename slug {path.stem!r} does not match payload slug {slug!r}")
        if slug in anime_data:
            errors.append(f"{path.as_posix()}: duplicate anime slug {slug!r}")
        anime_data[slug] = episodes

    search_path = root / "search.html"
    search_html = validate_html(search_path, errors, node)
    index_rows: list[Any] | None = None
    if search_html is not None:
        assignment_pattern = re.compile(
            r"window\.INDEX\s*=\s*" + re.escape(INDEX_START)
            + r"([\s\S]*?)" + re.escape(INDEX_END) + r"\s*;"
        )
        assignment = assignment_pattern.search(search_html)
        index_assignments = re.findall(r"\bwindow\.INDEX\s*=", search_html)
        if (
            search_html.count(INDEX_START) != 1
            or search_html.count(INDEX_END) != 1
            or assignment is None
            or len(index_assignments) != 1
        ):
            errors.append("search.html: expected exactly one window.INDEX assignment enclosing the marker pair")
        else:
            try:
                index_rows = json.loads(assignment.group(1))
            except json.JSONDecodeError as exc:
                errors.append(f"search.html: window.INDEX is invalid JSON at line {exc.lineno}, column {exc.colno}")
            if index_rows is not None and not isinstance(index_rows, list):
                errors.append("search.html: window.INDEX must be an array")
                index_rows = None

    if index_rows is not None:
        index_by_slug: dict[str, list[Any]] = {}
        for number, row in enumerate(index_rows, start=1):
            where = f"search.html: INDEX row {number}"
            if not isinstance(row, list) or len(row) != 6:
                errors.append(f"{where} must contain the six expected fields")
                continue
            slug, title, episodes, urls, masks, providers = row
            if not is_nonempty_string(slug) or not is_nonempty_string(title):
                errors.append(f"{where} slug and title must be non-empty strings")
                continue
            if slug in index_by_slug:
                errors.append(f"{where} duplicates anime slug {slug!r}")
            index_by_slug[slug] = row
            for field, value in (("episodes", episodes), ("URLs", urls), ("masks", masks)):
                if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                    errors.append(f"{where} {field} count must be a non-negative integer")
            if not isinstance(providers, list) or any(not is_nonempty_string(item) for item in providers):
                errors.append(f"{where} provider list must contain only non-empty strings")
            data = anime_data.get(slug)
            if data is not None:
                actual_links = sum(len(item.get("links", [])) for item in data if isinstance(item, dict) and isinstance(item.get("links"), list))
                if episodes != len(data):
                    errors.append(f"{where} episode count {episodes} does not match b/{slug}.js ({len(data)})")
                if urls != actual_links:
                    errors.append(f"{where} URL count {urls} does not match b/{slug}.js ({actual_links})")
        for slug in sorted(set(anime_data) - set(index_by_slug)):
            errors.append(f"b/{slug}.js: anime slug is missing from search.html INDEX")
        for slug in sorted(set(index_by_slug) - set(anime_data)):
            errors.append(f"search.html: INDEX anime {slug!r} has no matching b/{slug}.js file")

    landing_html = validate_html(root / "index.html", errors, node, require_document_shell=False)
    if landing_html is not None and not re.search(
        r'<meta\b(?=[^>]*\bhttp-equiv\s*=\s*["\']?refresh)'
        r'(?=[^>]*\bcontent\s*=\s*["\'][^"\']*url=search\.html[^"\']*["\'])[^>]*>',
        landing_html,
        re.IGNORECASE,
    ):
        errors.append("index.html: expected the existing meta refresh redirect to search.html")
    for filename, variable in (("kaldirilan.js", "KALDIRILAN"), ("eklenen.js", "EKLENEN")):
        path = root / filename
        source = read_text(path, errors, path.as_posix())
        if source is not None:
            check_javascript(source, path.as_posix(), errors, node)
            validate_override(path, variable, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent,
                        help="archive root (defaults to the directory containing this script)")
    args = parser.parse_args()
    errors = validate_archive(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Archive validation failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print(f"Archive validation passed: {len(list((args.root / 'b').glob('*.js')))} anime files; offline checks only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
