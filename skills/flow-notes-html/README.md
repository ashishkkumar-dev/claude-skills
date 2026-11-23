# flow-notes-html

Builds an interactive HTML study page that explains a technical flow end to end, with one example and many diagrams. It is for learning a system in depth and for revising it fast.

## The problem

Notes about a complex flow (for example, a database update from the client to the disk and on to a CDC consumer) become long text. Long text is hard to learn from and hard to revise. Terms appear before they are defined, numbers appear without names, and each follow-up question adds a new block at the end.

## How it works

1. **One example input** goes through the whole flow, with the same values everywhere.
2. **A top overview** shows the whole path in one block diagram, plus the steps in one line each. Each box and each line links to its step.
3. **One tab for each part** of the flow. Each tab has the same sections: concept, a clickable flow stepper, edge cases, "see it yourself" commands, sources and a term index.
4. **A side tree** (for example, a folder tree) highlights the items that the current step uses.
5. **A step card** shows a diagram first and little text. A click opens it full screen.

The page is one self-contained HTML file. A script joins it from 4 small files: the page markup and the data of the topic (Claude writes these), and the style and the engine (Claude never reads these). Thus a new page costs about 10 KB of reading, not the whole page.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Instructions for Claude |
| `assets/skeleton.html` | Page markup with empty sections (Claude edits a copy) |
| `assets/data.example.js` | Overview, tree and steps of the topic (Claude edits a copy) |
| `assets/style.css` | Colours and layout (never read) |
| `assets/engine.js` | Stepper, blocks, tree highlight, reader, links, term index (never read) |
| `scripts/build_page.py` | `build`: join the files into one page. `split`: get the editable files back from a built page. |
| `tests/` | Build and split tests |

## Results

- Built from a real page with 4 parts and about 40 steps (Postgres from request to RAM, WAL to ClickHouse, and the Siphon code).
- The example build has no script errors. Overview links, blocks, the reader, tabs and the term index work in a headless browser.
- `split` then `build` gives back the same page, byte for byte (tests).

## Limits

- Facts must be checked for each new topic. The skill asks Claude to label each value as measured or as an example.
- The SVG layout is manual. Long labels need shorter text or wider boxes.
- A PDF is made only on request.
