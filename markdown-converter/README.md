# Markdown Converter


A small Markdown to HTML converter written from scratch (no libraries). It supports the parts of Markdown used most often and is built to be safe against HTML injection.

## Supported syntax
- Headings `#` to `######`
- Paragraphs, **bold**, *italic*, `inline code`
- Bulleted and numbered lists
- Fenced code blocks
- Links (only `http(s)`, `mailto:`, and relative or anchor URLs; `javascript:` links are stripped)

## Usage
```bash
python md2html.py notes.md -o notes.html
echo "# Hello **world**" | python md2html.py
```

## Run the tests
```bash
pip install pytest
pytest
```

## What I practiced
Regular expressions, a line-by-line block parser, escaping untrusted input (XSS prevention), and protecting code spans from further formatting.

## Limitations
This is a learning project, not a full CommonMark implementation: no nested lists, tables, images or blockquotes. For production use a library such as `markdown-it` or `mistune`.
