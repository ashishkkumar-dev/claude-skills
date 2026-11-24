import re

from PIL import Image

import build_html as bh


def test_citation_becomes_internal_link():
    out = bh.inl("Tiktokenizer [[3]](#ref-3) shows tokens")
    assert '<a class="cite" href="#ref-3">[3]</a>' in out


def test_markdown_web_link_is_not_linked_twice():
    out = bh.inl("[arxiv.org/abs/1](https://arxiv.org/abs/1)")
    assert out.count("<a ") == 1 and 'href="https://arxiv.org/abs/1"' in out


def test_bare_url_is_linked():
    assert 'href="https://example.com/x"' in bh.inl("See https://example.com/x for more")


def test_row_anchor_escaping_and_code():
    out = bh.inl('<a id="ref-2"></a>2 & more <b> `x*y*z`')
    assert out.startswith('<a id="ref-2"></a>2 &amp; more &lt;b&gt;')
    assert "<code>x*y*z</code>" in out and "<i>" not in out      # stars inside code stay stars


def test_heading_anchor():
    assert bh.anchor("2.4 Supervised finetuning") == "sec-2.4"
    assert bh.anchor("8. Resources") == "sec-8"
    assert bh.anchor("Summary") == ""


def write_notes(tmp_path, md, images=("a.png", "b.png", "c.png")):
    (tmp_path / "figures").mkdir()
    for name in images:
        Image.new("RGB", (160, 90), (230, 240, 250)).save(tmp_path / "figures" / name)
    (tmp_path / "notes.md").write_text(md)
    warn = bh.build(str(tmp_path / "notes.md"), str(tmp_path / "notes.html"))
    return warn, (tmp_path / "notes.html").read_text()


def test_figures_in_a_row_become_one_slider_and_a_lone_figure_stays_single(tmp_path):
    md = ("# T\n\n## 1. Intro\n\n"
          "![Figure 1: First.](figures/a.png)\n\n![Figure 2: Second.](figures/b.png)\n\n"
          "Text between.\n\n![Figure 3: Alone.](figures/c.png)\n")
    warn, page = write_notes(tmp_path, md)
    assert warn == []
    assert page.count('class="slider"') == 1
    slider = page[page.index('class="slider"'):page.index("Text between.")]
    assert slider.count("<figure") == 2 and slider.count('class="thumb"') == 2
    assert page.count("<figure") == 3 and bh.build.stats == dict(sections=1, figures=3, sliders=1)


def test_page_has_contents_links_and_resource_anchors(tmp_path):
    md = ("# T\n\n## 2. Main ideas\n\n### 2.1 One\n\nA tool [[1]](#ref-1).\n\n## 8. Resources\n\n"
          "| # | Resource | Cited in |\n|---|---|---|\n| <a id=\"ref-1\"></a>1 | Tool | [2.1](#sec-2.1) |\n")
    warn, page = write_notes(tmp_path, md, images=())
    assert warn == []
    toc = page[page.index('<nav id="toc">'):page.index("</nav>")]
    assert all(f'href="#{a}"' in toc for a in ("sec-2", "sec-2.1", "sec-8"))
    assert 'id="ref-1"' in page and 'href="#sec-2.1"' in page and "<table>" in page


def test_build_warns_about_missing_images_broken_links_and_long_sentences(tmp_path):
    md = ("# T\n\n## 1. Intro\n\n![Figure 1: Gone.](figures/missing.png)\n\nSee [[4]](#ref-4).\n\n"
          + " ".join(["word"] * 25) + ".\n")
    warn, _ = write_notes(tmp_path, md, images=())
    assert any("missing image: figures/missing.png" in w for w in warn)
    assert any("#ref-4" in w for w in warn)
    assert any("sentence over 20 words" in w for w in warn)


def test_nested_lists_and_code_blocks(tmp_path):
    md = "# T\n\n- one\n  - inner\n- two\n\n1. first\n2. second\n\n```settings.json\n{\"a\": 1}\n```\n"
    warn, page = write_notes(tmp_path, md, images=())
    assert re.search(r"<ul><li>one<ul><li>inner</li></ul></li><li>two</li></ul>", page)
    assert "<ol><li>first</li><li>second</li></ol>" in page
    assert 'class="codelabel">settings.json<' in page and "{&quot;a&quot;: 1}" not in page and '{"a": 1}' in page
