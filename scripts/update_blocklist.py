#!/usr/bin/env python3
"""
eBlocker RUSSIAN-PROPAGANDA-MAX -- merge & update script.

Reads:
  - domains-base.txt   canonical, manually curated list (one domain per line)
  - sources.txt         optional extra raw list URLs, one per line ('#' = comment)

Writes:
  - eBlocker_Russian_Propaganda_MAX.txt   final eBlocker-ready domain list

Run manually:
    python3 update_blocklist.py

Runs automatically via .github/workflows/update.yml (daily + on push).
"""
from __future__ import annotations

import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent
BASE_FILE = ROOT / "domains-base.txt"
SOURCES_FILE = ROOT / "sources.txt"
OUTPUT_FILE = ROOT / "eBlocker_Russian_Propaganda_MAX.txt"

DOMAIN_RE = re.compile(
    r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)+$"
)


def clean_line(line: str) -> Optional[str]:
    """Normalize a raw line into a bare domain, or None if it isn't one."""
    line = line.strip().lower()
    if not line or line.startswith("#") or line.startswith("!"):
        return None

    parts = line.split()
    # hosts-file style: "0.0.0.0 domain.com" / "127.0.0.1 domain.com"
    if len(parts) == 2 and parts[0] in ("0.0.0.0", "127.0.0.1", "::1", "::"):
        line = parts[1]
    elif len(parts) > 1:
        return None  # AdBlock/easylist-style pattern line -> not a plain domain, skip

    line = line.strip(".").lstrip("*").lstrip(".")
    if not line or not DOMAIN_RE.match(line):
        return None
    return line


def load_local(path: Path) -> set[str]:
    if not path.exists():
        return set()
    domains: set[str] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        d = clean_line(raw)
        if d:
            domains.add(d)
    return domains


def load_remote(url: str) -> set[str]:
    domains: set[str] = set()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "eblocker-list-updater/1.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            text = resp.read().decode("utf-8", errors="ignore")
    except Exception as exc:  # noqa: BLE001 - we want to keep going on any fetch failure
        print(f"  [!] skipped {url}: {exc}", file=sys.stderr)
        return domains
    for raw in text.splitlines():
        d = clean_line(raw)
        if d:
            domains.add(d)
    return domains


def load_sources() -> list[str]:
    if not SOURCES_FILE.exists():
        return []
    urls = []
    for raw in SOURCES_FILE.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if raw and not raw.startswith("#"):
            urls.append(raw)
    return urls


def main() -> None:
    print("== eBlocker RUSSIAN-PROPAGANDA-MAX -- update ==")

    base = load_local(BASE_FILE)
    print(f"Base list (domains-base.txt): {len(base)} domains")

    merged = set(base)
    sources = load_sources()
    if not sources:
        print("No external sources configured in sources.txt (base list only).")
    for url in sources:
        print(f"Fetching: {url}")
        remote = load_remote(url)
        print(f"  -> {len(remote)} valid domains")
        merged |= remote

    added = len(merged) - len(base)
    print(f"Total after merge: {len(merged)} domains (+{added} from external sources)")

    header = (
        "# eBlocker RUSSIAN-PROPAGANDA-MAX\n"
        f"# Auto-generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n"
        f"# Total domains: {len(merged)}\n"
        "#\n"
        "# Format: eBlocker \"Domain list\" (one domain per line, '#' = comment)\n"
        "# Built from: domains-base.txt (curated) + sources.txt (optional external feeds)\n"
        "#\n"
        "# Important: this is NOT a list of every Russian-language website.\n"
        "# Russian-language content also exists on legitimate independent media,\n"
        "# educational, technical and cultural sites, so blanket *.ru blocking\n"
        "# would cause substantial collateral damage.\n"
        "#\n"
        "# Review before deploying in a business/production network.\n"
        "#\n"
    )
    OUTPUT_FILE.write_text(header + "\n".join(sorted(merged)) + "\n", encoding="utf-8")
    print(f"Written: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
