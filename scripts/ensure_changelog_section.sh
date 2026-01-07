#!/bin/bash
set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

if [ $# -ne 2 ]; then
    echo -e "${RED}❌ Usage: ensure_changelog_section.sh <CHANGELOG.md> <version>${NC}" >&2
    exit 2
fi

changelog="$1"
version="$2"

if [ ! -f "$changelog" ]; then
    echo -e "${RED}❌ Changelog not found: ${BLUE}$changelog${NC}" >&2
    exit 1
fi

needle="## [$version]"

if ! grep -qF "$needle" "$changelog"; then
    echo -e "${RED}❌ Missing changelog section: ${YELLOW}$needle${NC}" >&2
    exit 1
fi

echo -e "${GREEN}✅ Found changelog section: ${YELLOW}$needle${NC}"
exit 0
