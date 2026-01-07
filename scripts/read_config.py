#!/usr/bin/env python3
import sys
from pathlib import Path

import yaml  # type: ignore

# Config Reader
# usage: ./read_config.py <key>
# example: ./read_config.py author.name


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: read_config.py <key.path>", file=sys.stderr)
        sys.exit(1)

    key_path = sys.argv[1].split(".")
    config_path = Path(".project-config.yaml")

    if not config_path.exists():
        print(f"Error: {config_path} not found", file=sys.stderr)
        sys.exit(1)

    try:
        with open(config_path) as f:
            data = yaml.safe_load(f)

        value = data
        for key in key_path:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                print(f"Error: Key '{sys.argv[1]}' not found", file=sys.stderr)
                sys.exit(1)

        print(value)

    except Exception as e:
        print(f"Error reading config: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
