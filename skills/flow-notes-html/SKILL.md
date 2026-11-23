---
name: flow-notes-html
description: Build or revise an interactive HTML study page that explains a technical flow end to end (for example, a query from client to disk to a CDC consumer). Use when Ashish asks for notes, an HTML doc or a revision page about how a system works. Make a PDF only when he asks for one.
---

# Flow notes HTML

Build one self-contained HTML page that teaches a technical flow with one example, many diagrams and little text. The page is for learning and for fast revision.

Reference example: `references/example-postgres-internals.html` ("Postgres Internals: Request to RAM", 4 parts). Copy its patterns. Starter code: `assets/template.html`. Both files are in Ashish's git repo `claude-skills/flow-notes-html/`. If they are not available, rebuild from the "Engine" section below.

## When to use

- Ashish asks to "create notes", "make an HTML doc", "add this to the page" or "make a revision page" about a flow, a system or internals.
- He asks to change a page that this skill made. Then revise it; do not rebuild it.
- Do not make a PDF unless he asks for a PDF.

## Workflow

1. Settle the example input first: one concrete example that goes through the whole flow (for example, `UPDATE accounts SET balance = 500 WHERE id = 7`). Fix its values (names, IDs, numbers, positions) and use the same values in every part.
2. Split the flow into parts (tabs), one for each stage. Usually 2 to 4 parts.
3. Gather and check the facts. Run real commands when you can (for example, a local server). Label each value as measured or as an example. Write "Not verified" when you cannot check a fact.
4. Copy `assets/template.html`. Fill the DATA block of the script and the section markup. Do not change the ENGINE block, except to fix a bug.
5. Test (see "Checks"). Then publish the page as an artifact. Revise the same artifact later.
6. Reply with a short "Changed:" list. Do not repeat the page content in chat.

## Page structure

1. **Top section, "The whole path in one picture".**
   - One block diagram: one row for each part, at most 4 boxes in a row. Each box has a short name and one key fact, for example "Search the index: accounts_pkey → (42,3)". A click on a box opens its step.
   - "The steps in words": one short line for each step, each with a link to its step. Keep each line brief. Name the key field or value, not the theory.
   - One last line for work that happens later or in the background.
2. **Tabs, one for each part.** Each tab has these sections, in this order:
   1. Concept: a structure diagram and at most 3 new terms.
   2. The flow: a clickable stepper. The flow diagram is on the left and the step card on the right.
   3. Edge cases: cards in the form "If: <case>" + 1 or 2 sentences + a "Go to step N" button.
   4. "See it yourself": commands with their real output as comments.
   5. Sources and term index. The term index is built automatically.
3. **Side panel: a context tree** (for example, a folder tree, the services or the files). It highlights, in pink (`--hl`), the items of the current section or step. Each step and each block lists its items in `files`.
4. **Full-screen reader.** A click on a step card opens it full screen, with the tree beside it.

## The step card

- Fixed parts: title, one-line `sub` (the input), `result` (the output), then `facts` such as Reads, Changes, Result, Where.
- Body: the diagram first, with the real values of the example. Then at most 3 short points.
- At most 3 new terms in a step: `[id, "Plain meaning (name)", "definition", "Example: ..."]`.
- A heavy step uses `subs` (blocks). Each block has a title, its own `files`, its own html and its own terms. The engine shows pills and Previous/Next block buttons.
- A deep topic that needs many diagrams goes in a drawer: a button in the step opens a panel of parts with Previous/Next (see the "See how the index works" drawer in the reference example). Use a drawer only when blocks are not enough.

## Content rules

- Use a diagram for every flow, branch or hierarchy. Replace a list of 3 or more steps with a diagram when you can.
- Use a table only for values to look up. Each table has a "Columns:" line that explains each column.
- Put the example input before the steps.
- Write the name next to every number, for example "OID 16390 = accounts" or "file 24576 (accounts)". A diagram and its text name the same items.
- Define each term once, at first use, with an example. Write the plain meaning first and the name second. Use at most 3 new terms in one block. Never use a term that the page or the chat has not defined.
- Keep the text short: 1 or 2 lines when that is enough. Do not add byte-level dumps or long tables unless Ashish asks. Remove text when a diagram says the same thing.
- Write in ASD-STE100: max 20 words in an instruction, max 25 in a description, one idea per sentence, active voice. Do not use em dashes.
- When a new answer in chat corrects the page, fix the page in the same turn, or ask "Add this to the page?".

## Change rules

- Revise; do not rebuild. Change only the part that he names, and keep the rest.
- Put new content in the section where it belongs, not at the end of the page.
- When he says "show it here first" or "don't update the HTML", answer in chat only. Edit the page after he confirms.
- When he retells the flow in his own words, give feedback in this form: what worked, a table "You said | Correct", what is missing, and a short better version. Do not edit the page unless he asks.

## Diagram rules (SVG in the page)

- Use `viewBox="0 0 680 H"` and `width` from CSS. Keep content inside x = 10 to 670.
- Use the page classes: `violet`, `green`, `warm`, `gray`, `hlbox` for boxes; `tt` (title), `tx` (detail), `lbl` (caption in capitals); `ln` for lines and arrows. Give each SVG its own `<marker id>`.
- Use one colour for each kind of thing, and add a one-line legend when the colours carry meaning.
- Check by eye that no text crosses a box edge, an arrow or another text. Shorten the text or widen the box.
- In a JS template literal (step body), do not use backticks or `${`.

## Engine (in assets/template.html)

The ENGINE block gives these functions; the DATA block feeds them:

- `OVERVIEW` → `drawOverview()`: the top diagram (snake layout, 4 boxes for each row) and the step list.
- `TREE` → `buildTree()`; `highlight(files, label)`; `SECTION_FILES` for sections without a stepper; `watchSections()` follows the scroll.
- `makeStepper(sectionId, STEPS)`: needs the ids `flow-<id>`, `<id>-kick`, `<id>-title`, `<id>-facts`, `<id>-body`, `<id>-terms`, `<id>-prev`, `<id>-next` in that section. It supports `subs` (blocks).
- Tabs: `tabN` buttons and `panelN` panels. `selectTab(n)` moves the tree into the active tab.
- Links: `data-goto="step:<sectionId>:<n>[:<block>]"` or `data-goto="sec:<sectionId>"`. They work from any tab.
- Reader: a click on `.flow .panel` opens it full screen; Esc closes it.
- Term index: `<ul class="index" data-index-for="panelN">` collects the section terms and the step terms of that tab.

If the template file is missing, rebuild these parts from this list and from the reference example.

## Checks before each publish

1. Extract the script and run `node --check` on it.
2. Open the page in Playwright. Confirm no page errors or console errors.
3. Click through the overview links, each stepper, the blocks, the reader and each tab.
4. Take a screenshot of each changed step or section, and look at it for clipped or overlapping text.
5. Confirm that wide code or tables do not push the side panel out of place (`min-width: 0` on grid children).

## Output

- Publish the page as an artifact, and keep revising the same artifact.
- Make a PDF only when Ashish asks for one.
