#!/usr/bin/env python3

import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Colors
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"  # No Color

VERSION_RE = re.compile(
    r"^##\s+\[(?P<ver>\d+\.\d+\.\d+)\](?:\s*-\s*(?P<date>\d{4}-\d{2}-\d{2}))?\s*$"
)
UNRELEASED_RE = re.compile(r"^##\s+\[Unreleased\]\s*$", re.IGNORECASE)
CATEGORY_RE = re.compile(
    r"^###\s+(Added|Changed|Fixed|Removed|Security)\s*$", re.IGNORECASE
)
BULLET_RE = re.compile(r"^\s*[-*]\s+\S+")


@dataclass(frozen=True)
class Section:
    kind: str  # "unreleased" or "version"
    version: str | None
    date: str | None
    start_line: int
    lines: list[str]


def parse_sections(lines: list[str]) -> list[Section]:
    sections: list[Section] = []
    current: Section | None = None

    def flush() -> None:
        nonlocal current
        if current is not None:
            sections.append(current)
            current = None

    for idx, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")

        if UNRELEASED_RE.match(line):
            flush()
            current = Section(
                kind="unreleased", version=None, date=None, start_line=idx, lines=[]
            )
            continue

        m = VERSION_RE.match(line)
        if m:
            flush()
            current = Section(
                kind="version",
                version=m.group("ver"),
                date=m.group("date"),
                start_line=idx,
                lines=[],
            )
            continue

        if current is not None:
            current.lines.append(line)

    flush()
    return sections


type SemVerKey = tuple[int, int, int]


def semver_key(v: str) -> SemVerKey:
    a, b, c = v.split(".")
    return int(a), int(b), int(c)


def fail(msg: str) -> int:
    print(f"{RED}❌ ERROR: {msg}{NC}", file=sys.stderr)
    return 1


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        msg = (
            f"{RED}❌ Usage: check_changelog.py <CHANGELOG.md> "
            f"[--require-unreleased] [--require-dates]{NC}"
        )
        print(msg, file=sys.stderr)
        return 2

    path = Path(argv[1])
    require_unreleased = "--require-unreleased" in argv[2:]
    require_dates = "--require-dates" in argv[2:]

    if not path.exists():
        return fail(f"changelog not found: {path}")

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines(True)

    # Basic header sanity
    if not any(line.strip().startswith("#") for line in lines[:20]):
        return fail(
            "changelog parece não ter cabeçalho "
            "(nenhum '# ...' nas primeiras 20 linhas)"
        )

    sections = parse_sections(lines)

    if require_unreleased and not any(s.kind == "unreleased" for s in sections):
        return fail(
            "faltando seção '## [Unreleased]' (exigida por --require-unreleased)"
        )

    # Collect version sections
    versions = [s for s in sections if s.kind == "version"]
    if not versions:
        return fail("nenhuma seção de versão encontrada (esperado: '## [x.y.z]')")

    # No duplicates
    seen: set[str] = set()
    for s in versions:
        assert s.version is not None
        if s.version in seen:
            return fail(
                f"versão duplicada no changelog: [{s.version}] (linha {s.start_line})"
            )
        seen.add(s.version)

    # Descending order (top to bottom) check
    sorted_desc = sorted(
        (s.version for s in versions if s.version), key=semver_key, reverse=True
    )
    in_file = [s.version for s in versions if s.version]
    if in_file != sorted_desc:
        return fail(
            "seções de versão não estão em ordem decrescente. "
            f"Encontrado: {in_file}. Esperado: {sorted_desc}."
        )

    # Require dates (optional)
    if require_dates:
        missing = [s for s in versions if s.date is None]
        if missing:
            ex = missing[0]
            return fail(
                f"data ausente em [{ex.version}] (linha {ex.start_line}). "
                f"Use: '## [{ex.version}] - YYYY-MM-DD'"
            )

    # Content sanity: each version must have at least one bullet item somewhere
    for s in versions:
        body = s.lines
        has_bullet = any(BULLET_RE.match(line) for line in body)
        if not has_bullet:
            return fail(
                f"seção [{s.version}] (linha {s.start_line}) "
                "não contém nenhum item em lista (- ...)."
            )

        # If categories exist, ensure bullets appear under some category,
        # not only “floating” text
        # (Soft rule: if there are categories, require at least one bullet
        # after a category header)
        categories = [i for i, line in enumerate(body) if CATEGORY_RE.match(line)]
        if categories:
            ok = False
            for ci in categories:
                for line in body[ci + 1 :]:
                    if line.strip().startswith("### "):
                        break
                    if BULLET_RE.match(line):
                        ok = True
                        break
                if ok:
                    break
            if not ok:
                return fail(
                    f"seção [{s.version}] tem categorias mas "
                    f"nenhum bullet sob elas (linha {s.start_line})."
                )

    print(f"{GREEN}✅ Changelog validation passed!{NC}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
