/* ============ DATA: replace for each document ============ */
// Overview: one row for each part, max 4 boxes. go = "step:<sectionId>:<n>[:<block>]" or "sec:<sectionId>".
const OVERVIEW = {
  rows: [
    { title: "Part 1: __PART1__", cls: "violet", boxes: [
      { t: "Start", sub: "one key fact", go: "step:a2:1" }, { t: "Middle", sub: "one key fact", go: "step:a2:2" },
      { t: "End of part 1", sub: "one key fact", go: "step:a2:3" } ] },
    { title: "Part 2: __PART2__", cls: "green", boxes: [
      { t: "Next stage", sub: "one key fact", go: "step:b1:1" }, { t: "Result", sub: "one key fact", go: "step:b1:2" } ] }
  ],
  note: "One line about work that happens later or in the background.",
  steps: [
    ["Step 1 in one short line, with `code` for names.", "step:a2:1", "Part 1, step 1"],
    ["Step 2 in one short line.", "step:a2:2", "Part 1, step 2"],
    ["Step 3 in one short line.", "step:b1:1", "Part 2, step 1"]
  ]
};
// Context tree: [id, depth, name, note, cls]. cls: "sh" (shared), "db", "cat", or "".
const TREE = [
  ["", 0, "root/", "the top folder", "sh"],
  ["fileA", 1, "fileA", "what it holds", ""],
  ["fileB", 1, "fileB", "what it holds", ""]
];
// Files to highlight for each section that has no stepper.
const SECTION_FILES = {
  a1: { label: "Section 1: the main items", files: ["fileA"] },
  a3: { label: "Section 3: edge cases", files: [] },
  a4: { label: "Section 4: commands", files: ["fileA", "fileB"] },
  a5: { label: "Section 5: sources", files: [] },
  b2: { label: "Part 2: term index", files: [] }
};
// Steps. terms: [id, name, definition, example], max 3. subs (optional): blocks for a heavy step.
const STEPS_A2 = [
  { files: ["fileA"], group: "Group name", cls: "violet", title: "Step title", sub: "the input of the step", result: "what the step gives",
    facts: [["Reads", "what it reads"], ["Result", "what it gives"]],
    body: `<div class="svgbox"><svg viewBox="0 0 680 80" role="img" aria-label="Step diagram"><rect class="violet" x="20" y="15" width="300" height="50" rx="6"/><text class="tt" x="170" y="45" text-anchor="middle">Diagram first</text><rect class="green" x="360" y="15" width="300" height="50" rx="6"/><text class="tt" x="510" y="45" text-anchor="middle">with the real values</text></svg></div><p>At most 3 short points.</p>`,
    terms: [["t-a2-1", "Plain meaning (name)", "One-line definition.", "Example: a value from the example."]] },
  { files: ["fileB"], group: "Group name", cls: "violet", title: "A heavy step with blocks", sub: "split into blocks", result: "each block highlights its own items",
    facts: [["Reads", "what it reads"]], body: `<p>This step has 2 blocks.</p>`, terms: [],
    subs: [
      { title: "First block", files: ["fileA"], html: `<p>Block 1 content.</p>`, terms: [] },
      { title: "Second block", files: ["fileB"], html: `<p>Block 2 content.</p>`, terms: [["t-a2-2", "Another term", "Definition.", "Example."]] } ] },
  { files: [], group: "Another group", cls: "warm", title: "Last step", sub: "the output", result: "the end of part 1",
    facts: [["Result", "what it gives"]], body: `<p>Text.</p>`, terms: [] }
];
const STEPS_B1 = [
  { files: ["fileA"], group: "Group", cls: "green", title: "First step of part 2", sub: "input", result: "output", facts: [["Reads", "x"]], body: `<p>Text.</p>`, terms: [] },
  { files: ["fileB"], group: "Group", cls: "green", title: "Second step of part 2", sub: "input", result: "output", facts: [["Reads", "y"]], body: `<p>Text.</p>`, terms: [] }
];

/* ============ INIT: one makeStepper call for each flow section (runs after the engine) ============ */
function initPage() {
  buildTree();
  drawOverview();
  makeStepper("a2", STEPS_A2);
  makeStepper("b1", STEPS_B1);
  buildTermIndexes();
  watchSections();
  activeSection = "a1"; refreshHighlight();
}
