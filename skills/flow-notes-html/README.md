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

The page is one self-contained HTML file. `assets/template.html` has the engine (stepper, blocks, tree highlight, reader, links, term index); a new page only fills in its data.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Instructions for Claude |
| `assets/template.html` | Starter page with the data block and the engine |
| `references/example-postgres-internals.html` | The full example: Postgres from request to RAM, processing in RAM, WAL to ClickHouse, and the Siphon code |

## Results

- The example page has 4 parts and about 40 steps. Each step was checked in a headless browser for script errors and clipped text.
- The template passes the same checks: no script errors; overview links, blocks, reader, tabs and term index work.

## Limits

- Facts must be checked for each new topic. The skill asks Claude to label each value as measured or as an example.
- The SVG layout is manual. Long labels need shorter text or wider boxes.
- A PDF is made only on request.
