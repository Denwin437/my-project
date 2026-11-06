import md2html


def test_headings():
    assert md2html.convert("# Title") == "<h1>Title</h1>"
    assert md2html.convert("### Sub") == "<h3>Sub</h3>"


def test_paragraph_joins_lines():
    assert md2html.convert("one\ntwo") == "<p>one two</p>"


def test_bold_italic_code():
    html = md2html.convert("**bold** and *it* and `code`")
    assert html == "<p><strong>bold</strong> and <em>it</em> and <code>code</code></p>"


def test_lists():
    assert md2html.convert("- a\n- b") == "<ul>\n<li>a</li>\n<li>b</li>\n</ul>"
    assert md2html.convert("1. a\n2. b") == "<ol>\n<li>a</li>\n<li>b</li>\n</ol>"


def test_list_then_paragraph():
    out = md2html.convert("- a\n\ntext")
    assert out == "<ul>\n<li>a</li>\n</ul>\n<p>text</p>"


def test_code_block_is_escaped_and_not_formatted():
    out = md2html.convert("```\n<b>**x**</b>\n```")
    assert out == "<pre><code>&lt;b&gt;**x**&lt;/b&gt;</code></pre>"


def test_inline_code_not_formatted():
    assert md2html.convert("`**no**`") == "<p><code>**no**</code></p>"


def test_html_is_escaped():
    out = md2html.convert("<script>alert(1)</script>")
    assert "<script>" not in out and "&lt;script&gt;" in out


def test_safe_and_unsafe_links():
    assert '<a href="https://example.com">site</a>' in md2html.convert("[site](https://example.com)")
    out = md2html.convert("[bad](javascript:alert(1))")
    assert "href" not in out and "bad" in out


def test_cli_writes_file(tmp_path):
    src, dst = tmp_path / "a.md", tmp_path / "a.html"
    src.write_text("# Hi", encoding="utf-8")
    assert md2html.main([str(src), "-o", str(dst)]) == 0
    assert dst.read_text(encoding="utf-8").strip() == "<h1>Hi</h1>"
