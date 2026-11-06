#!/usr/bin/env python3
"""Markdown Converter: turn a practical subset of Markdown into safe HTML."""

import argparse
import html
import re
import sys
from pathlib import Path

SAFE_URL = re.compile(r"^(https?://|mailto:|/|#|\.{1,2}/)", re.IGNORECASE)


def inline(text: str) -> str:
    """Convert inline Markdown (code, bold, italic, links). HTML in the input is escaped."""
    text = html.escape(text, quote=False)
    codes = []

    def stash(match):
        codes.append(match.group(1))
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", stash, text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)

    def link(match):
        label, url = match.group(1), match.group(2)
        if not SAFE_URL.match(url):
            return label  # drop unsafe schemes such as javascript:
        return f'<a href="{url.replace(chr(34), "&quot;")}">{label}</a>'

    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)
    return re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{codes[int(m.group(1))]}</code>", text)


def convert(text: str) -> str:
    out, para, code = [], [], []
    list_tag = None
    in_code = False

    def flush_para():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    def close_list():
        nonlocal list_tag
        if list_tag:
            out.append(f"</{list_tag}>")
            list_tag = None

    def flush_code():
        out.append("<pre><code>" + "\n".join(code) + "</code></pre>")
        code.clear()

    for line in text.splitlines():
        if in_code:
            if line.strip().startswith("```"):
                flush_code()
                in_code = False
            else:
                code.append(html.escape(line, quote=False))
            continue
        if line.strip().startswith("```"):
            flush_para()
            close_list()
            in_code = True
            continue
        if not line.strip():
            flush_para()
            close_list()
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            flush_para()
            close_list()
            level = len(heading.group(1))
            out.append(f"<h{level}>{inline(heading.group(2).strip())}</h{level}>")
            continue
        bullet = re.match(r"^\s*[-*]\s+(.*)$", line)
        numbered = re.match(r"^\s*\d+\.\s+(.*)$", line)
        if bullet or numbered:
            flush_para()
            tag = "ul" if bullet else "ol"
            if list_tag != tag:
                close_list()
                out.append(f"<{tag}>")
                list_tag = tag
            out.append(f"<li>{inline((bullet or numbered).group(1))}</li>")
            continue
        close_list()
        para.append(line.strip())

    if in_code:
        flush_code()
    flush_para()
    close_list()
    return "\n".join(out)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Convert Markdown to HTML.")
    parser.add_argument("file", nargs="?", type=Path, help="Markdown file; reads stdin if omitted")
    parser.add_argument("-o", "--output", type=Path, help="write HTML here instead of stdout")
    args = parser.parse_args(argv)

    source = args.file.read_text(encoding="utf-8") if args.file else sys.stdin.read()
    result = convert(source)
    if args.output:
        args.output.write_text(result + "\n", encoding="utf-8")
    else:
        print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
