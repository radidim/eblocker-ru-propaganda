#!/usr/bin/env python3
"""
update_blocklist.py

Слива:
  1) sources/base_manual.txt   – ръчно поддържания базов списък
  2) sources/public_feeds.txt  – URL-и на публични анти-пропаганда feed-ове

... в чист, дедупликиран, сортиран plain-domain списък, съвместим с
eBlocker Domain Blocker. Изходен файл: output/blocklist.txt
"""

import re
import sys
import urllib.request
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = ROOT / "sources"
OUTPUT_DIR = ROOT / "output"
BASE_FILE = SOURCES_DIR / "base_manual.txt"
FEEDS_FILE = SOURCES_DIR / "public_feeds.txt"
OUTPUT_FILE = OUTPUT_DIR / "blocklist.txt"
STATS_FILE = OUTPUT_DIR / "STATS.md"

DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)(?!-)[a-z0-9-]{1,63}(?<!-)"
    r"(\.(?!-)[a-z0-9-]{1,63}(?<!-))+$",
    re.IGNORECASE,
)

USER_AGENT = "eblocker-ru-propaganda-updater/1.0 (+https://github.com/)"


def fetch(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def clean_domain(token: str):
    token = token.strip().lower()
    if not token or token.startswith("#") or token.startswith("!"):
        return None
    m = re.match(r"^\|\|([a-z0-9.\-]+)\^", token)
    if m:
        token = m.group(1)
    m = re.match(r"^(?:0\.0\.0\.0|127\.0\.0\.1)\s+([a-z0-9.\-]+)", token)
    if m:
        token = m.group(1)
    token = re.sub(r"^https?://", "", token)
    token = token.split("/")[0]
    token = token.rstrip(".")
    if DOMAIN_RE.match(token):
        return token
    return None


def load_local(path: Path):
    if not path.exists():
        return set()
    domains = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        d = clean_domain(line)
        if d:
            domains.add(d)
    return domains


def load_feed_urls(path: Path):
    if not path.exists():
        return []
    urls = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        urls.append(line)
    return urls


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    base_domains = load_local(BASE_FILE)
    print(f"[base]  {len(base_domains)} домейна от {BASE_FILE.name}")

    all_domains = set(base_domains)
    feed_report = []

    for url in load_feed_urls(FEEDS_FILE):
        try:
            raw = fetch(url)
        except Exception as exc:
            print(f"[WARN] Неуспешно теглене на {url}: {exc}", file=sys.stderr)
            feed_report.append((url, 0, f"error: {exc}"))
            continue

        found = set()
        for line in raw.splitlines():
            d = clean_domain(line)
            if d:
                found.add(d)

        new_ones = found - all_domains
        all_domains |= found
        print(f"[feed]  {len(found):5d} домейна ({len(new_ones)} нови) от {url}")
        feed_report.append((url, len(found), f"{len(new_ones)} нови"))

    sorted_domains = sorted(all_domains)
    OUTPUT_FILE.write_text("\n".join(sorted_domains) + "\n", encoding="utf-8")
    print(f"[done]  общо {len(sorted_domains)} уникални домейна -> {OUTPUT_FILE}")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    stats_lines = [
        "# eBlocker RU-Propaganda-MAX — статистика на последното обновяване",
        "",
        f"Последно обновено: **{now}**",
        "",
        f"- Домейни от ръчния (базов) списък: **{len(base_domains)}**",
        f"- Общо уникални домейни след сливане: **{len(sorted_domains)}**",
        "",
        "## Публични източници",
        "",
        "| URL | Домейни | Резултат |",
        "|---|---|---|",
    ]
    for url, count, note in feed_report:
        stats_lines.append(f"| {url} | {count} | {note} |")
    STATS_FILE.write_text("\n".join(stats_lines) + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
