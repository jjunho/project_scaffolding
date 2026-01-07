#!/usr/bin/env python3
import re
import subprocess
import sys

# SemVer Advisor
# Analyzes git history since the last tag to suggest the next version bump.
# Logic:
#   - BREAKING CHANGE or !: -> MAJOR
#   - feat: -> MINOR
#   - fix:, perf:, etc. -> PATCH

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"

type BumpResult = tuple[str, str]
type VersionTuple = tuple[int, int, int]


def get_latest_tag() -> str:
    try:
        # Get the latest reachable tag from HEAD
        tag = (
            subprocess.check_output(
                ["git", "describe", "--tags", "--abbrev=0"], stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
        )
        return tag
    except subprocess.CalledProcessError:
        return "v0.0.0"  # Fallback if no tags exist


def get_commits_since(tag: str) -> list[str]:
    # If tag is v0.0.0 and doesn't exist, log all commits
    rng = "HEAD" if tag == "v0.0.0" else f"{tag}..HEAD"

    try:
        logs = (
            subprocess.check_output(
                ["git", "log", "--pretty=%s|%b", rng], stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
            .split("\n")
        )
        return [line for line in logs if line]
    except subprocess.CalledProcessError:
        return []


def analyze_bump(commits: list[str]) -> BumpResult:
    if not commits:
        return ("NONE", "No changes detected")

    reason = "Default to PATCH for maintenance"

    has_feat = False

    for commit in commits:
        subject, body = commit.split("|", 1) if "|" in commit else (commit, "")
        full_text = f"{subject}\n{body}"

        # 1. Check for BREAKING CHANGE
        if (
            "BREAKING CHANGE" in full_text
            or re.search(r"^[a-z]+\(.*\)!:", subject)
            or re.search(r"^[a-z]+!:", subject)
        ):
            return ("MAJOR", f"Breaking change detected: '{subject}'")

        # 2. Check for feat
        if subject.startswith("feat"):
            has_feat = True
            reason = f"Feature detected: '{subject}'"

    if has_feat:
        return ("MINOR", reason)

    return ("PATCH", "Only fixes/chores detected")


def parse_version(tag: str) -> VersionTuple:
    # Strip 'v' if present
    clean = tag.lstrip("v")
    parts = clean.split(".")
    return (int(parts[0]), int(parts[1]), int(parts[2]))


def main() -> None:
    tag = get_latest_tag()
    print(f"{BLUE}Current Version:{NC} {tag}")

    commits = get_commits_since(tag)
    print(f"{BLUE}Commits since tag:{NC} {len(commits)}")

    bump_type, reason = analyze_bump(commits)

    if bump_type == "NONE":
        print(f"\n{YELLOW}No changes to release.{NC}")
        sys.exit(0)

    major, minor, patch = parse_version(tag)

    if bump_type == "MAJOR":
        next_ver = f"v{major + 1}.0.0"
    elif bump_type == "MINOR":
        next_ver = f"v{major}.{minor + 1}.0"
    else:  # PATCH
        next_ver = f"v{major}.{minor}.{patch + 1}"

    print(f"\n{GREEN}Suggested Bump:{NC} {bump_type}")
    print(f"{GREEN}Next Version:{NC}  {next_ver}")
    print(f"{YELLOW}Reason:{NC}        {reason}")


if __name__ == "__main__":
    main()
