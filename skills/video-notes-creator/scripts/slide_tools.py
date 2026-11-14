#!/usr/bin/env python3
"""Get the transcript, and find and grab slides, from a YouTube video without saving the video.

  transcript  URL OUT_DIR [--lang en]
        Writes transcript.txt (one line per minute, with [mm:ss] or [h:mm:ss]) and
        meta.json (title, channel, date, length, chapters, description).

  scan  URL OUT_DIR [--storyboard] [--max N]
        Dense pass (default): reads the smallest video stream once, looks at one
        frame each 2 seconds, and keeps the last frame of each picture that stays
        on screen. Times are exact to about 2 seconds.
        --storyboard: use YouTube's thumbnail strip (one picture each 10 s, about
        1 MB for a 40-minute video). Also the automatic fallback.
        Writes contact sheets (max N candidates, default 144), tiles/, inventory.txt.
        A page (paper or slide) is kept even if it shows for less than MIN_HOLD seconds.

  grab  URL OUT_DIR [--match SCAN_DIR/tiles] TIME ...
        Full-res frames at the given times (mm:ss or h:mm:ss), read straight from
        the stream: only the bytes near each frame. With --match, each frame is
        checked against its scan tile and the time is corrected if necessary.
        Writes check.jpg, one small sheet of all frames.

Needs: yt-dlp, youtube-transcript-api, Pillow, and ffmpeg (system binary or the imageio-ffmpeg package).
"""
import io, os, re, shutil, subprocess, sys, threading, time, urllib.request

from PIL import Image, ImageDraw

STEP = 2       # dense pass: seconds between looked-at frames
MIN_HOLD = 4   # dense pass: a picture must stay this many seconds to count
DUP = 7.0      # mean abs diff (0-255) on a 16x9 thumb: below this, same picture as the frame before
VIEW = 16.0    # below this, two pictures show the same camera view (speaker, stage)
VIEW_MIN = 6   # a view that returns this many times is a camera view, not a slide
PAPER = 0.35   # share of near-white or near-black pixels: above this, the picture can be a page...
PAGE_SAT = 12  # ...if its mean saturation (max - min channel, 0-255) is also below this. Dark studio shots are colorful.
COLS, TILE_W, TW, TH = 6, 240, 320, 180


def info(url):
    import yt_dlp
    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as y:
        return y.extract_info(url, download=False)


def ffmpeg():
    p = shutil.which("ffmpeg")
    if p: return p
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def fmt(t, long=False):
    t = int(round(t))
    return f"{t // 3600}:{t % 3600 // 60:02d}:{t % 60:02d}" if long else f"{t // 60:02d}:{t % 60:02d}"


def parse(ts):
    s = 0
    for part in ts.split(":"): s = s * 60 + int(part)
    return s


def sig(im):
    return list(im.convert("RGB").resize((16, 9), Image.BILINEAR).tobytes())


def dist(a, b):
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a)


def paper(im):
    """Share of near-white or near-black pixels."""
    b = im.convert("RGB").resize((32, 18), Image.BILINEAR).tobytes()
    px = [b[i:i + 3] for i in range(0, len(b), 3)]
    return sum(1 for q in px if min(q) > 225 or max(q) < 35) / len(px)


def saturation(im):
    b = im.convert("RGB").resize((32, 18), Image.BILINEAR).tobytes()
    px = [b[i:i + 3] for i in range(0, len(b), 3)]
    return sum(max(q) - min(q) for q in px) / len(px)


def is_page(im):
    """A slide or paper page: mostly plain white or black background, and almost no color."""
    return paper(im) >= PAPER and saturation(im) < PAGE_SAT


def fetch(url, tries=4):
    for k in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read()
        except Exception:
            if k == tries - 1: raise
            time.sleep(2 * (k + 1))


def headers(f):
    return "".join(f"{k}: {v}\r\n" for k, v in (f.get("http_headers") or {}).items())


class Runs:
    """Merge consecutive frames that show the same picture. Keep the LAST frame: slide builds are complete there."""
    def __init__(self): self.runs = []
    def feed(self, t, im):
        s = sig(im)
        if self.runs and dist(s, self.runs[-1]["sig"]) < DUP: self.runs[-1].update(end=t, im=im, sig=s)
        else: self.runs.append(dict(start=t, end=t, im=im, sig=s))


def select(runs, dense=True, cap=144):
    """Split runs into slide candidates and camera views. Return (runs, keep, cam, shown)."""
    for r in runs: r["page"] = is_page(r["im"])
    if dense: runs = [r for r in runs if r["end"] - r["start"] >= MIN_HOLD or r["page"]]   # a page can flash by
    views = []      # a view that keeps coming back is a camera view (speaker, stage), not a slide...
    for r in runs:
        for v in views:
            if dist(r["sig"], v["sig"]) < VIEW: v["n"] += 1; r["view"] = v; break
        else:
            r["view"] = dict(sig=r["sig"], n=1); views.append(r["view"])
    for r in runs: r["cam"] = r["view"]["n"] >= VIEW_MIN and not r["page"]   # ...unless it looks like a page
    keep, cam = [r for r in runs if not r["cam"]], [r for r in runs if r["cam"]]
    shown = sorted(sorted(keep, key=lambda r: r["start"] - r["end"])[:cap], key=lambda r: r["start"])   # longest holds first if too many
    return runs, keep, cam, shown


def frames_dense(d):
    """One frame each STEP seconds from the smallest stream. Nothing is saved to disk."""
    fs = [f for f in d["formats"] if str(f.get("vcodec", "")).startswith("avc1") and f.get("protocol") == "https" and (f.get("height") or 0) >= 240]
    f = min(fs, key=lambda f: f["height"])
    # YouTube slows a stream that is read in one long request, so fetch it in chunks (as a player does) and pipe it in.
    p = subprocess.Popen([ffmpeg(), "-v", "error", "-i", "pipe:0", "-an", "-vf", f"fps=1/{STEP},scale={TW}:{TH}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    read = [0]

    def feed():
        size, pos, chunk = f.get("filesize") or 0, 0, 8 * 1024 * 1024
        try:
            while not size or pos < size:
                h = dict(f.get("http_headers") or {}); h["Range"] = f"bytes={pos}-{pos + chunk - 1}"
                for k in range(4):
                    try:
                        data = urllib.request.urlopen(urllib.request.Request(f["url"], headers=h), timeout=60).read(); break
                    except Exception:
                        if k == 3: raise
                        time.sleep(2 * (k + 1))
                if not data: break
                p.stdin.write(data); pos += len(data); read[0] = pos
                if len(data) < chunk: break
        except Exception:
            pass
        finally:
            try: p.stdin.close()
            except Exception: pass
    threading.Thread(target=feed, daemon=True).start()
    n, k = TW * TH * 3, 0
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n: break
        yield k * STEP, Image.frombytes("RGB", (TW, TH), buf); k += 1
    p.wait()
    if k < d["duration"] / STEP * 0.9: raise RuntimeError(f"stream ended early ({k} frames)")
    print(f"dense pass: {k} frames looked at, {read[0] / 1e6:.1f} MB read from the {f['height']}p stream, nothing saved")


def frames_storyboard(d):
    sb = max((f for f in d["formats"] if f["format_id"].startswith("sb")), key=lambda f: f["width"])
    step, tw, th, total, i, nb = 1 / sb["fps"], sb["width"], sb["height"], int(d["duration"] * sb["fps"]) + 1, 0, 0
    for fr in sb["fragments"]:
        raw = fetch(fr["url"]); nb += len(raw); im = Image.open(io.BytesIO(raw)).convert("RGB")
        for r in range(sb["rows"]):
            for c in range(sb["columns"]):
                if i < total and (c + 1) * tw <= im.width and (r + 1) * th <= im.height:
                    i += 1; yield i * step, im.crop((c * tw, r * th, (c + 1) * tw, (r + 1) * th))   # tile i shows about (i+1)*step
    print(f"storyboard: {i} tiles (one each {step:.0f}s), {nb / 1e6:.1f} MB read")


def scan(url, out, storyboard=False, cap=144):
    os.makedirs(os.path.join(out, "tiles"), exist_ok=True)
    d = info(url); long = d["duration"] >= 3600; R = Runs(); mode = "storyboard" if storyboard else "dense"
    if mode == "dense":
        try:
            for t, im in frames_dense(d): R.feed(t, im)
        except Exception as e:
            print("dense pass failed, using the storyboard:", e); mode, R = "storyboard", Runs()
    if mode == "storyboard":
        for t, im in frames_storyboard(d): R.feed(t, im)
    runs, keep, cam, shown = select(R.runs, mode == "dense", cap)
    h = int(TILE_W * TH / TW); per = COLS * 8; sheets = []
    for k in range(0, len(shown), per):
        part = shown[k:k + per]
        sh = Image.new("RGB", (COLS * TILE_W, -(-len(part) // COLS) * (h + 16)), "white"); dr = ImageDraw.Draw(sh)
        for j, r in enumerate(part):
            x, y = (j % COLS) * TILE_W, (j // COLS) * (h + 16)
            sh.paste(r["im"].resize((TILE_W, h), Image.LANCZOS), (x, y + 16))
            dr.text((x + 3, y + 3), fmt(r["end"], long) if r["start"] == r["end"] else f"{fmt(r['start'], long)}-{fmt(r['end'], long)}", fill=(200, 0, 0))
        p = os.path.join(out, f"sheet_{k // per + 1}.jpg"); sh.save(p, quality=80); sheets.append(p)
    with open(os.path.join(out, "inventory.txt"), "w") as f:
        f.write(f"# {d.get('title')} | {fmt(d['duration'], long)} | {mode} pass\n# slide candidates: start-end, * = on a contact sheet. Grab at the end time, where slide builds are complete.\n")
        for r in keep:
            brief = " (brief page)" if r["end"] - r["start"] < MIN_HOLD else ""
            f.write(f"{fmt(r['start'], long)}-{fmt(r['end'], long)}{' *' if r in shown else ''}{brief}\n")
            r["im"].save(os.path.join(out, "tiles", fmt(r["end"], long).replace(":", "") + ".jpg"), quality=85)
        f.write("# camera views (no clean slide; a slide may still show on a stage screen)\n")
        for r in cam: f.write(f"{fmt(r['start'], long)}-{fmt(r['end'], long)}\n")
    print(f"pictures that stay on screen: {len(runs)}  slide candidates: {len(keep)} ({len(shown)} on sheets)  camera views dropped: {len(cam)}")
    print("sheets:", *sheets, sep="\n  ")


def minute_lines(snippets, long=False):
    """Group (start_seconds, text) snippets into one line per minute: "[mm:ss] text"."""
    lines, cur, buf = [], None, []
    for start, text in snippets:
        m = int(start) // 60
        if cur is None: cur = m
        if m != cur:
            lines.append(f"[{fmt(cur * 60, long)}] " + " ".join(buf)); buf, cur = [], m
        buf.append(" ".join(text.split()))
    if buf: lines.append(f"[{fmt(cur * 60, long)}] " + " ".join(buf))
    return lines


def transcript(url, out, lang="en"):
    import json
    from youtube_transcript_api import YouTubeTranscriptApi
    os.makedirs(out, exist_ok=True)
    d = info(url); long = d["duration"] >= 3600
    meta = {k: d.get(k) for k in ("title", "channel", "uploader", "upload_date", "duration", "description", "webpage_url")}
    meta["chapters"] = [dict(start=fmt(c["start_time"], long), title=c["title"]) for c in d.get("chapters") or []]
    with open(os.path.join(out, "meta.json"), "w") as f: json.dump(meta, f, indent=1, ensure_ascii=False)
    t = YouTubeTranscriptApi().fetch(d["id"], languages=[lang, "en"])
    lines = minute_lines([(s.start, s.text) for s in t], long)
    with open(os.path.join(out, "transcript.txt"), "w") as f: f.write("\n".join(lines) + "\n")
    print(f"{meta['title']} | {meta['channel']} | {meta['upload_date']} | {fmt(d['duration'], long)}")
    print(f"transcript: {len(lines)} lines, {sum(map(len, lines))} characters -> {os.path.join(out, 'transcript.txt')}")
    print(f"meta: chapters={len(meta['chapters'])}, description={len(meta['description'] or '')} characters -> {os.path.join(out, 'meta.json')}")


def grab(url, out, times, tiles=None, max_h=1080):
    os.makedirs(out, exist_ok=True)
    d = info(url)
    fs = [f for f in d["formats"] if (f.get("height") or 0) <= max_h and f.get("protocol") == "https" and str(f.get("vcodec", "")).startswith("avc1")]
    f = max(fs, key=lambda f: (f["height"], -(f.get("fps") or 0)))
    hdr, ff, total, got = headers(f), ffmpeg(), 0, []

    def one(t, p):
        nonlocal total
        r = subprocess.run([ff, "-v", "verbose", "-headers", hdr, "-ss", str(t), "-i", f["url"], "-frames:v", "1", "-q:v", "2", "-y", p], capture_output=True, text=True)
        total += sum(int(x) for x in re.findall(r"Statistics: (\d+) bytes read", r.stderr))
        return os.path.exists(p)
    for ts in times:
        t, name = parse(ts), ts.replace(":", ""); p = os.path.join(out, f"slide_{name}.jpg")
        tile = os.path.join(tiles, f"{name}.jpg") if tiles else None
        if not (tile and os.path.exists(tile)):
            ok = one(t, p); note = "no tile to match"
        else:                                   # search near the given time until the frame matches the scan tile
            want, best = sig(Image.open(tile)), None
            for off in (0, -2, -5, -10, 5, -15, 10, -20, 15):
                if t + off < 0 or not one(t + off, p + ".try.jpg"): continue
                dd = dist(want, sig(Image.open(p + ".try.jpg")))
                if best is None or dd < best[0]: best = (dd, off); os.replace(p + ".try.jpg", p)
                if dd < DUP: break
            if os.path.exists(p + ".try.jpg"): os.remove(p + ".try.jpg")
            ok = best is not None
            note = f"matched at {fmt(t + best[1], t >= 3600)} (diff {best[0]:.1f})" if ok and best[0] < DUP else f"NO MATCH, closest diff {best[0]:.1f}: check by eye" if ok else ""
        if ok: got.append((ts, p))
        print(f"{ts} -> {os.path.basename(p)}  {note}" if ok else f"{ts} FAILED")
    if got:
        w, h = 320, 180; sh = Image.new("RGB", (5 * w, -(-len(got) // 5) * (h + 16)), "white"); dr = ImageDraw.Draw(sh)
        for j, (ts, p) in enumerate(got):
            x, y = (j % 5) * w, (j // 5) * (h + 16); sh.paste(Image.open(p).convert("RGB").resize((w, h), Image.LANCZOS), (x, y + 16)); dr.text((x + 3, y + 3), ts, fill=(200, 0, 0))
        sh.save(os.path.join(out, "check.jpg"), quality=80); print("check sheet:", os.path.join(out, "check.jpg"))
    print(f"stream {f['format_id']} {f['width']}x{f['height']}: {total / 1e6:.1f} MB read in total (full file: {(f.get('filesize') or 0) / 1e6:.0f} MB)")


if __name__ == "__main__":
    cmd, url, out = sys.argv[1:4]; rest = sys.argv[4:]
    def opt(name, default=None):
        if name not in rest: return default
        i = rest.index(name); v = rest[i + 1]; del rest[i:i + 2]; return v
    if cmd == "transcript":
        transcript(url, out, opt("--lang", "en"))
    elif cmd == "scan":
        sb = "--storyboard" in rest
        scan(url, out, sb, int(opt("--max", 144)))
    else:
        tiles = opt("--match"); grab(url, out, rest, tiles)
