import io

from PIL import Image

import slide_tools as st


def solid(rgb, size=(64, 36)):
    return Image.new("RGB", size, rgb)


def run(start, end, rgb):
    im = solid(rgb)
    return dict(start=start, end=end, im=im, sig=st.sig(im))


def test_fmt_and_parse_round_trip():
    assert st.fmt(75) == "01:15"
    assert st.fmt(3725, long=True) == "1:02:05"
    assert st.parse("01:15") == 75
    assert st.parse("1:02:05") == 3725
    for t in (0, 59, 61, 3599, 3600, 12683):
        assert st.parse(st.fmt(t, long=True)) == t


def test_same_picture_has_zero_distance_and_different_pictures_do_not():
    a, b = st.sig(solid((200, 50, 50))), st.sig(solid((50, 50, 200)))
    assert st.dist(a, a) == 0
    assert st.dist(a, b) > st.VIEW


def test_paper_detects_pages():
    assert st.paper(solid((255, 255, 255))) == 1.0
    assert st.paper(solid((10, 10, 10))) == 1.0
    assert st.paper(solid((120, 90, 60))) == 0.0


def test_runs_merge_same_picture_and_keep_the_last_frame():
    r = st.Runs()
    first, build_step, last = solid((200, 50, 50)), solid((202, 52, 52)), solid((204, 54, 54))
    for t, im in ((0, first), (2, build_step), (4, last), (6, solid((50, 50, 200)))):
        r.feed(t, im)
    assert len(r.runs) == 2
    assert (r.runs[0]["start"], r.runs[0]["end"]) == (0, 4)
    assert r.runs[0]["im"] is last  # slide builds are complete in the last frame


def test_select_drops_short_holds_in_dense_mode_only():
    runs = [run(0, 2, (200, 50, 50)), run(4, 20, (50, 200, 50))]
    _, keep, _, _ = st.select([dict(r) for r in runs], dense=True)
    assert [r["start"] for r in keep] == [4]
    _, keep, _, _ = st.select([dict(r) for r in runs], dense=False)
    assert len(keep) == 2


def test_select_drops_a_recurring_camera_view_but_keeps_a_recurring_white_slide():
    runs, t = [], 0
    colors = [(200, 50, 50), (50, 200, 50), (50, 50, 200), (200, 200, 50), (200, 50, 200), (50, 200, 200)]
    for c in colors:
        runs.append(run(t, t + 10, (120, 90, 60))); t += 12      # speaker on camera
        runs.append(run(t, t + 10, c)); t += 12                  # a distinct slide
        runs.append(run(t, t + 10, (255, 255, 255))); t += 12    # a white page that comes back
    _, keep, cam, _ = st.select(runs, dense=True)
    assert len(cam) == 6 and all(r["im"].getpixel((0, 0)) == (120, 90, 60) for r in cam)
    assert len(keep) == 12


def test_select_cap_keeps_longest_holds_in_time_order():
    runs = [run(0, 5, (200, 50, 50)), run(10, 40, (50, 200, 50)), run(50, 70, (50, 50, 200))]
    _, _, _, shown = st.select(runs, dense=True, cap=2)
    assert [r["start"] for r in shown] == [10, 50]


def test_storyboard_tiles_are_labelled_one_step_late(monkeypatch):
    grid = Image.new("RGB", (20, 20))
    buf = io.BytesIO(); grid.save(buf, "JPEG")
    monkeypatch.setattr(st, "fetch", lambda url: buf.getvalue())
    d = {"duration": 40, "formats": [{"format_id": "sb0", "width": 10, "height": 10, "fps": 0.1,
                                      "rows": 2, "columns": 2, "fragments": [{"url": "x"}]}]}
    times = [t for t, _ in st.frames_storyboard(d)]
    assert times == [10, 20, 30, 40]  # tile i shows about (i+1) * step


def dark_studio(size=(64, 36)):
    """Mostly near-black, with colorful people and lights: like a dimly lit studio wide shot."""
    im = Image.new("RGB", size, (15, 15, 20))
    for x in range(0, size[0], 4):
        for y in range(size[1] // 3, size[1]):
            if (x // 4) % 2 == 0: im.putpixel((x, y), (200, 70, 40))
    return im


def test_is_page_accepts_white_and_black_slides_but_not_a_dark_studio():
    assert st.is_page(solid((255, 255, 255)))
    assert st.is_page(solid((10, 10, 10)))
    studio = dark_studio()
    assert st.paper(studio) >= st.PAPER       # the old test called this a page...
    assert not st.is_page(studio)              # ...the new one does not


def test_recurring_dark_studio_view_is_dropped():
    runs, t = [], 0
    for c in [(200, 50, 50), (50, 200, 50), (50, 50, 200), (200, 200, 50), (200, 50, 200), (50, 200, 200)]:
        im = dark_studio(); runs.append(dict(start=t, end=t + 10, im=im, sig=st.sig(im))); t += 12
        runs.append(run(t, t + 10, c)); t += 12
    _, keep, cam, _ = st.select(runs, dense=True)
    assert len(cam) == 6 and len(keep) == 6


def test_brief_page_is_kept_but_brief_other_picture_is_dropped():
    runs = [run(0, 2, (255, 255, 255)), run(4, 6, (200, 50, 50)), run(8, 30, (50, 200, 50))]
    _, keep, _, _ = st.select(runs, dense=True)
    assert [r["start"] for r in keep] == [0, 8]


def test_minute_lines_groups_snippets_by_minute():
    snippets = [(0.5, "hello"), (30, "world\nagain"), (61, "next"), (3605, "late")]
    assert st.minute_lines(snippets[:3]) == ["[00:00] hello world again", "[01:00] next"]
    assert st.minute_lines(snippets, long=True)[-1] == "[1:00:00] late"
