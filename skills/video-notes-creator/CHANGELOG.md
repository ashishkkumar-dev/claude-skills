# Changelog: video-notes-creator

## 2.0.0

- Output: the notes are now a web page, not a PDF. `build_html.py` replaces `build_pdf.py`. The page has a contents bar, a slider for each run of figures, and a full-size view on click. The Markdown stays next to the page, so the page can be built again after an edit.
- Output: no page previews and no page-layout fixes. `build_html.py` checks images, links, and sentence length with code. This saves the page-preview images and the layout fix loops of the PDF.
- Requirements: `reportlab` and `pymupdf` are no longer needed.
- Scan: a new test sorts each picture into slide, camera shot, or "check by eye". It uses two measures that ignore colour: **still** (at least 80% of 48 boxes do not change) and **flat** (one shade covers at least 35%). It replaces the colour test, the 4-second rule, and the "comes back 6 times" rule, which dropped dark one-template decks and colourful slides. Tested against hand labels on 8 videos (471 slide pictures): 8 lost, against 96 with the colour test. Camera shots on the sheets: 72, against 117.
- Scan: the contact sheets show the complete state of each change first, then the middle states of animations.
- Scan: typing in a screen recording is split at its pauses. In a still picture, a drift of 1.2 levels (instead of 3) starts a new picture, when the screen holds still; boxes that move in most frames (a webcam) do not count. A 9-minute coding tutorial gave 9 pictures before and 23 after; the tutorial's states were all on the sheet.
- Scan: a slow animation or zoom is split into several pictures. Before, it merged into one picture, and only its end state was kept. A new picture starts when the frame differs from the picture's first frame by 3 levels or more (64x36, grey). Tested on a 19-minute animated math video: 14 of 14 hand-picked frames are now candidates (before: 4). Hand-labelled slides in three other test videos are all still found.

## 1.1.0

Fixes from a test run as a new user (a 30-minute interview filmed with several cameras).

- Scan: a dark studio shot no longer counts as a page. A page must also have almost no color. Slide candidates in the test video: 59 before, 30 after.
- Scan: pages that show for less than 4 seconds are kept and marked "(brief page)". The test video showed a guest's name, an essay, and a paper title only this way.
- New `transcript` command: writes `transcript.txt` (one line per minute) and `meta.json`.
- PDF: no empty last page after a final table.
- PDF: table columns are never narrower than their longest word, so timestamps do not wrap.
- Skill: offer two choices per setup question; create the output folder and ask for access early; check names against on-screen text.
- Docs: data per grabbed frame is 0.3 to 2 MB, not "less than 1 MB". After a marketplace install, the command is `/video-notes-creator:video-notes-creator`.

## 1.0.0

First public release.

- Asks for the reader profile and the output path before it starts.
- Dense slide scan with chunked HTTP Range reads; no video download. Storyboard fallback.
- Full-resolution frame grab with tile matching to correct the time.
- Slides first; card diagrams only where no usable slide exists.
- Each example states why the behavior happens, if the speaker explains it.
- Numbered, clickable resources with "Cited in" back-links.
- PDF builder with internal links; unit tests for both scripts.
