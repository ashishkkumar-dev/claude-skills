# Changelog: video-notes-creator

## 1.0.0

First public release.

- Asks for the reader profile and the output path before it starts.
- Dense slide scan with chunked HTTP Range reads; no video download. Storyboard fallback.
- Full-resolution frame grab with tile matching to correct the time.
- Slides first; card diagrams only where no usable slide exists.
- Each example states why the behavior happens, if the speaker explains it.
- Numbered, clickable resources with "Cited in" back-links.
- PDF builder with internal links; unit tests for both scripts.
