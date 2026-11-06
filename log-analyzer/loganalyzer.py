#!/usr/bin/env python3
"""Log Analyzer: summarize web server access logs in Common Log Format."""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

LINE = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] '
    r'"(?P<method>[A-Z]+) (?P<path>\S+)[^"]*" (?P<status>\d{3}) (?P<size>\d+|-)'
)


def parse_line(line: str):
    """Return a dict for a valid log line, or None if it is malformed."""
    match = LINE.match(line.strip())
    if not match:
        return None
    entry = match.groupdict()
    entry["status"] = int(entry["status"])
    entry["size"] = 0 if entry["size"] == "-" else int(entry["size"])
    return entry


def analyze(lines, top: int = 5) -> dict:
    ips, paths, classes = Counter(), Counter(), Counter()
    total = malformed = bytes_sent = server_errors = 0
    for line in lines:
        if not line.strip():
            continue
        entry = parse_line(line)
        if entry is None:
            malformed += 1
            continue
        total += 1
        ips[entry["ip"]] += 1
        paths[entry["path"]] += 1
        classes[f"{entry['status'] // 100}xx"] += 1
        bytes_sent += entry["size"]
        if entry["status"] >= 500:
            server_errors += 1
    return {
        "requests": total,
        "malformed": malformed,
        "bytes": bytes_sent,
        "status_classes": dict(sorted(classes.items())),
        "error_rate": round(server_errors / total * 100, 1) if total else 0.0,
        "top_ips": ips.most_common(top),
        "top_paths": paths.most_common(top),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Summarize an access log.")
    parser.add_argument("file", nargs="?", type=Path, help="log file; reads stdin if omitted")
    parser.add_argument("--top", type=int, default=5)
    args = parser.parse_args(argv)

    lines = args.file.read_text(encoding="utf-8", errors="replace").splitlines() if args.file else sys.stdin
    result = analyze(lines, args.top)
    print(f"Requests:     {result['requests']} ({result['malformed']} malformed lines skipped)")
    print(f"Data sent:    {result['bytes']} bytes")
    print(f"5xx rate:     {result['error_rate']}%")
    print("Status codes: " + ", ".join(f"{k}={v}" for k, v in result["status_classes"].items()))
    print("Top IPs:")
    for ip, n in result["top_ips"]:
        print(f"  {ip:<18} {n}")
    print("Top paths:")
    for path, n in result["top_paths"]:
        print(f"  {path:<30} {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
