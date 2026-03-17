#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys

PATTERN = re.compile(r"^(feat|fix|refactor|perf|docs|test|build|ci|chore|style|revert)(\([a-z0-9-]+\))?(!)?: [a-z0-9].{0,71}$")


def validate(message: str) -> tuple[bool, str]:
    if message.endswith("."):
        return False, "description must not end with a period"
    if not PATTERN.match(message):
        return False, "message must follow Conventional Commits with optional single scope"
    return True, "valid"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Conventional Commit message.")
    parser.add_argument("--message", required=True, help="Commit message subject line")
    args = parser.parse_args()

    ok, reason = validate(args.message)
    print(reason)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
