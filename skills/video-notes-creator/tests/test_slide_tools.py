import io
import random

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
    assert st.dist(a, b) > st.DUP


def test_runs_merge_same_picture_and_keep_the_last_frame():
    r = st.Runs()
    first, build_step, last = solid((200, 50, 50)), solid((201, 51, 51)), solid((202, 52, 52))
    for t, im in ((0, first), (2, build_step), (4, last), (6, solid((50, 50, 200)))):
        r.feed(t, im)
    assert len(r.runs) == 2
    assert (r.runs[0]["start"], r.runs[0]["end"]) == (0, 4)
    assert r.runs[0]["im"] is last  # slide builds are complete in the last frame


def test_slow_animation_is_split_so_its_middle_states_are_kept():
    # A thin line grows across a dark screen: each 2-second step is small, but the end looks very different.
    def frame(width):
        im = Image.new("RGB", (320, 180), (10, 10, 10))
        im.paste((240, 240, 240), (20, 84, 20 + width, 96))
        return im
    r = st.Runs()
    for k in range(15):
        r.feed(2 * k, frame(20 * k))
    assert all(st.dist(st.sig(frame(20 * k)), st.sig(frame(20 * k + 20))) < st.DUP for k in range(14))   # every step looks the same
    assert len(r.runs) >= 3                                       # but the zoom is kept as several pictures
    assert any(0 < r_["end"] < 28 for r_ in r.runs)               # including a middle state


def test_typing_in_an_editor_is_split_at_its_pauses():
    # A white editor: a line of text appears, the screen holds still, then the next line appears.
    def editor(lines):
        im = Image.new("RGB", (320, 180), (250, 250, 250))
        for k in range(lines): im.paste((30, 30, 30), (20, 20 + 14 * k, 230, 26 + 14 * k))
        return im
    frames = []
    for lines in range(9):
        frames += [editor(lines)] * 3                                  # one new line, then a pause
    r = st.Runs()
    for k, im in enumerate(frames): r.feed(2 * k, im)
    assert all(st.dist(st.sig(editor(k)), st.sig(editor(k + 1))) < st.DUP for k in range(8))   # each line is a small change
    assert len(r.runs) >= 3                                                      # but the edits are kept as several pictures
    assert all(r_["mid"] for r_ in r.runs[:-1])                                  # middle states, behind whole screens on the sheets


def test_still_slide_with_moving_webcam_corner_stays_one_picture():
    r = st.Runs()
    for k in range(20):
        im = Image.new("RGB", (320, 180), (250, 250, 250))
        im.paste((20, 20, 20), (30, 30, 250, 40))                  # a line of slide text
        im.paste((90 + 60 * (k % 2),) * 3, (270, 140, 316, 176))    # a webcam corner that keeps changing
        r.feed(2 * k, im)
    assert len(r.runs) == 1


def test_storyboard_tiles_are_labelled_one_step_late(monkeypatch):
    grid = Image.new("RGB", (20, 20))
    buf = io.BytesIO(); grid.save(buf, "JPEG")
    monkeypatch.setattr(st, "fetch", lambda url: buf.getvalue())
    d = {"duration": 40, "formats": [{"format_id": "sb0", "width": 10, "height": 10, "fps": 0.1,
                                      "rows": 2, "columns": 2, "fragments": [{"url": "x"}]}]}
    times = [t for t, _ in st.frames_storyboard(d)]
    assert times == [10, 20, 30, 40]  # tile i shows about (i+1) * step


def slide(bg, size=(320, 180)):
    """A slide: one background shade with two lines of text."""
    im = Image.new("RGB", size, bg)
    ink = (20, 20, 20) if sum(bg) > 380 else (240, 240, 240)
    im.paste(ink, (30, 40, 260, 52)); im.paste(ink, (30, 70, 200, 82))
    return im


def camera(seed, size=(320, 180)):
    """A camera shot: many shades, and it changes everywhere from frame to frame."""
    rnd = random.Random(seed)
    return Image.frombytes("RGB", size, bytes(rnd.randrange(60, 200) for _ in range(size[0] * size[1] * 3)))


def feed(frames):
    r = st.Runs()
    for k, im in enumerate(frames): r.feed(2 * k, im)
    return r.runs


def test_one_shade_does_not_care_about_colour():
    for bg in ((255, 255, 255), (10, 10, 10), (20, 35, 60), (250, 220, 40), (40, 160, 70)):   # white, black, navy, yellow, green
        assert st.one_shade(slide(bg)) >= st.FLAT
    assert st.one_shade(camera(1)) < st.FLAT


def test_still_share_ignores_a_webcam_corner_but_not_a_moving_picture():
    a = st.fine(slide((20, 35, 60)))
    b_im = slide((20, 35, 60)); b_im.paste((200, 150, 120), (270, 140, 316, 176)); b = st.fine(b_im)
    assert st.still_share(a, a) == 1.0
    assert st.still_share(b, a) >= st.STILL_SHARE                      # only the corner changed
    assert st.still_share(st.fine(camera(2)), st.fine(camera(3))) < 0.2


def test_decide_sorts_slides_camera_shots_and_unsure_pictures():
    for bg in ((255, 255, 255), (20, 35, 60), (250, 220, 40)):
        assert st.decide(feed([slide(bg)] * 3)[0]) == "slide"           # still and flat, in any colour
    cam = [camera(k) for k in range(3)]
    runs = feed(cam)
    assert all(st.decide(r) == "camera" for r in runs)                  # moving and not flat
    photo = camera(9)
    assert st.decide(feed([photo] * 3)[0]) == "check"                    # still, but not flat (a photo slide)
    assert st.decide(dict(im=slide((250, 220, 40)), still=[])) == "check"   # one frame, flat: stillness unknown
    assert st.decide(dict(im=camera(4), still=[])) == "camera"          # one frame, not flat


def test_select_keeps_slides_and_check_drops_camera_and_shows_slides_first():
    runs = [dict(start=0, end=40, im=camera(5), still=[1.0] * 20, sig=None),        # long, still photo: check
            dict(start=50, end=54, im=slide((40, 160, 70)), still=[1.0, 1.0], sig=None),  # short green slide
            dict(start=60, end=90, im=camera(6), still=[0.0] * 15, sig=None)]       # camera shot
    _, keep, cam, shown = st.select(runs, cap=1)
    assert [r["start"] for r in keep] == [0, 50] and [r["start"] for r in cam] == [60]
    assert [r["start"] for r in shown] == [50]                           # the cap keeps the slide, not the longer check


def test_sheets_show_whole_screens_before_middle_states_of_a_change():
    # A slow change cut by drift: its first pieces are middle states, its last piece is the complete screen.
    runs = [dict(start=0, end=2, im=slide((250, 250, 250)), still=[1.0], mid=True),
            dict(start=4, end=6, im=slide((250, 250, 250)), still=[1.0], mid=True),
            dict(start=8, end=10, im=slide((250, 250, 250)), still=[1.0]),          # end of the change
            dict(start=20, end=22, im=slide((20, 35, 60)), still=[1.0])]            # another whole screen
    _, keep, _, shown = st.select(runs, cap=2)
    assert len(keep) == 4 and [r["start"] for r in shown] == [8, 20]


def test_minute_lines_groups_snippets_by_minute():
    snippets = [(0.5, "hello"), (30, "world\nagain"), (61, "next"), (3605, "late")]
    assert st.minute_lines(snippets[:3]) == ["[00:00] hello world again", "[01:00] next"]
    assert st.minute_lines(snippets, long=True)[-1] == "[1:00:00] late"
