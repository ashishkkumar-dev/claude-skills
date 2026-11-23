# Changelog: flow-notes-html

## 0.1.0

First version.

- Page structure: a top overview (one block diagram and the steps in words), one tab for each part, and the same sections in each tab: concept, flow stepper, edge cases, "see it yourself", sources and term index.
- Step card: title, input, result, facts, a diagram first, at most 3 points and at most 3 terms. Heavy steps use blocks; deep topics use a drawer.
- Side panel: a context tree that highlights the items of the current section, step or block.
- A click on a step card opens it full screen.
- Content rules: diagrams for flows, tables only for lookup values, a name next to every number, one definition for each term, ASD-STE100, short text.
- Change rules: revise, do not rebuild; "show it here first" means chat only; feedback format when the user retells the flow.
- Source files: skeleton.html and data.example.js (edited), style.css and engine.js (never read). scripts/build_page.py builds one HTML page and splits a built page back, so a revision does not read the style or the engine.
- A PDF is made only on request.
- SKILL.md: "Choosing the parts" rule (cut at handoff points, 4 to 12 steps for each part, where branches and lens parts go), and a plan that Ashish confirms before the build.
