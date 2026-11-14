# Changelog: video-notes-creator

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
