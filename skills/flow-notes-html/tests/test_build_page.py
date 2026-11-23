import os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
SCRIPT = os.path.join(SKILL, "scripts", "build_page.py")
ASSETS = os.path.join(SKILL, "assets")


def run(*args):
    return subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True)


def test_build_inlines_style_data_and_engine(tmp_path):
    out = tmp_path / "out.html"
    r = run("build", os.path.join(ASSETS, "skeleton.html"), os.path.join(ASSETS, "data.example.js"), str(out))
    assert r.returncode == 0, r.stderr
    html = out.read_text(encoding="utf-8")
    assert '<style data-part="style">' in html
    assert '<script data-part="data">' in html and '<script data-part="engine">' in html
    assert "@STYLE" not in html and "@SCRIPT" not in html
    assert html.index('data-part="data"') < html.index('data-part="engine"')


def test_split_gives_back_the_sources(tmp_path):
    built = tmp_path / "built.html"
    run("build", os.path.join(ASSETS, "skeleton.html"), os.path.join(ASSETS, "data.example.js"), str(built))
    r = run("split", str(built), str(tmp_path / "src"))
    assert r.returncode == 0, r.stderr
    page = (tmp_path / "src" / "page.html").read_text(encoding="utf-8")
    data = (tmp_path / "src" / "data.js").read_text(encoding="utf-8")
    assert data == open(os.path.join(ASSETS, "data.example.js"), encoding="utf-8").read()
    assert page.count("<!-- @STYLE -->") == 1 and page.count("<!-- @SCRIPT -->") == 1
    assert "makeStepper(" not in page.split("<!-- @SCRIPT -->")[0]
    rebuilt = tmp_path / "rebuilt.html"
    assert run("build", str(tmp_path / "src" / "page.html"), str(tmp_path / "src" / "data.js"), str(rebuilt)).returncode == 0
    assert rebuilt.read_text(encoding="utf-8") == built.read_text(encoding="utf-8")


def test_build_rejects_a_page_without_markers(tmp_path):
    page = tmp_path / "page.html"
    page.write_text("<html><body></body></html>", encoding="utf-8")
    r = run("build", str(page), os.path.join(ASSETS, "data.example.js"), str(tmp_path / "o.html"))
    assert r.returncode != 0
