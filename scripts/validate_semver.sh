#!/bin/bash
set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

if [ $# -ne 1 ]; then
    echo -e "${RED}❌ Usage: validate_semver.sh <version>${NC}" >&2
    exit 2
fi

version="$1"

if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "${RED}❌ Invalid semver: ${YELLOW}$version${NC}" >&2
    exit 1
fi

echo -e "${GREEN}✅ Valid semver: ${YELLOW}$version${NC}"
exit 0
