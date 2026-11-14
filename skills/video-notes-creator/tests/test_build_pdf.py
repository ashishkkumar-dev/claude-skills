import pymupdf
from PIL import Image

import build_pdf as bp


def test_citation_becomes_internal_link():
    out = bp.inl("Tiktokenizer [[3]](#ref-3) shows tokens")
    assert '<a href="#ref-3"' in out and ">[3]</a>" in out


def test_markdown_web_link_is_not_linked_twice():
    out = bp.inl("[arxiv.org/abs/1](https://arxiv.org/abs/1)")
    assert out.count("<link") == 1 and 'href="https://arxiv.org/abs/1"' in out


def test_bare_url_is_linked():
    assert 'href="https://example.com/x"' in bp.inl("See https://example.com/x for more")


def test_row_anchor_and_escaping():
    out = bp.inl('<a id="ref-2"></a>2 & more <b>')
    assert out.startswith('<a name="ref-2"/>2 &amp; more &lt;b&gt;')


def test_heading_anchor():
    assert bp.anchor("2.4 Supervised finetuning") == '<a name="sec-2.4"/>'
    assert bp.anchor("8. Resources") == '<a name="sec-8"/>'
    assert bp.anchor("Summary") == ""


def test_build_makes_working_links(tmp_path):
    Image.new("RGB", (800, 400), (230, 240, 250)).save(tmp_path / "fig.png")
    (tmp_path / "notes.md").write_text(
        "# Test notes\n\n"
        "## 1. Intro\n\n"
        "![Figure 1: A test figure.](fig.png)\n\n"
        "Tiktokenizer [[1]](#ref-1) shows tokens.\n\n"
        "## 8. Resources\n\n"
        "| # | Resource | Link | Cited in |\n|---|---|---|---|\n"
        '| <a id="ref-1"></a>1 | Tiktokenizer | [tiktokenizer.vercel.app](https://tiktokenizer.vercel.app/) | [1](#sec-1) |\n'
    )
    pages = bp.build(str(tmp_path / "notes.md"), str(tmp_path / "notes.pdf"))
    doc = pymupdf.open(tmp_path / "notes.pdf")
    assert pages == len(doc) >= 1
    links = [l for p in doc for l in p.get_links()]
    assert any(l.get("uri") == "https://tiktokenizer.vercel.app/" for l in links)
    assert sum(1 for l in links if l["kind"] in (pymupdf.LINK_GOTO, pymupdf.LINK_NAMED)) == 2
    text = "".join(p.get_text() for p in doc)
    assert "Figure 1: A test figure." in text and "[1]" in text
