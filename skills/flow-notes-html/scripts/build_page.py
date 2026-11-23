#!/usr/bin/env python3
"""Build one self-contained HTML page from small source files, or split a built page back.

build: page.html (skeleton with <!-- @STYLE --> and <!-- @SCRIPT -->) + data.js
       + this skill's assets/style.css and assets/engine.js -> one HTML file.
split: a built page -> page.html + data.js, without the style and the engine.
       Use it to revise a published page without reading the style or the engine.

Usage:
  python3 build_page.py build PAGE_HTML DATA_JS OUT_HTML
  python3 build_page.py split BUILT_HTML OUT_DIR
"""
import os, re, sys

ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
STYLE_RE = re.compile(r'<style data-part="style">.*?</style>', re.S)
DATA_RE = re.compile(r'<script data-part="data">\n?(.*?)</script>', re.S)
ENGINE_RE = re.compile(r'<script data-part="engine">.*?</script>', re.S)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def build(page_html, data_js, out_html):
    page, data = read(page_html), read(data_js)
    for marker in ("<!-- @STYLE -->", "<!-- @SCRIPT -->"):
        if page.count(marker) != 1:
            raise SystemExit(f"{page_html}: expected exactly one {marker}")
    style = read(os.path.join(ASSETS, "style.css"))
    engine = read(os.path.join(ASSETS, "engine.js"))
    out = page.replace("<!-- @STYLE -->", f'<style data-part="style">\n{style}</style>')
    out = out.replace("<!-- @SCRIPT -->", f'<script data-part="data">\n{data}</script>\n<script data-part="engine">\n{engine}</script>')
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(out)
    return out_html


def split(built_html, out_dir):
    built = read(built_html)
    m = DATA_RE.search(built)
    if not (STYLE_RE.search(built) and m and ENGINE_RE.search(built)):
        raise SystemExit(f"{built_html}: not a page built by build_page.py")
    page = STYLE_RE.sub("<!-- @STYLE -->", built, count=1)
    page = ENGINE_RE.sub("", page, count=1)
    page = DATA_RE.sub("<!-- @SCRIPT -->", page, count=1)
    page = page.replace("<!-- @SCRIPT -->\n\n", "<!-- @SCRIPT -->\n")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "page.html"), "w", encoding="utf-8") as f:
        f.write(page)
    with open(os.path.join(out_dir, "data.js"), "w", encoding="utf-8") as f:
        f.write(m.group(1))
    return out_dir


if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[1] == "build":
        print(build(*sys.argv[2:]))
    elif len(sys.argv) == 4 and sys.argv[1] == "split":
        print(split(*sys.argv[2:]))
    else:
        print(__doc__)
        sys.exit(2)
