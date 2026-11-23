/* ============ ENGINE: keep as is ============ */
const $ = id => document.getElementById(id);
const NS = "http://www.w3.org/2000/svg";
function el(tag, attrs, text) { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (text !== undefined) e.textContent = text; return e; }
function esc(t) { return String(t).replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c])); }
function md(t) { return esc(t).replace(/`([^`]+)`/g, "<code>$1</code>"); }
function termsBlock(list) {
  if (!list || !list.length) return "";
  return `<div class="terms"><h3>New terms</h3><dl>${list.map(t => `<dt id="${t[0]}">${t[1]}</dt><dd>${t[2]} <em>${t[3]}</em></dd>`).join("")}</dl></div>`;
}
let activeSection = "";
const STEPPERS = {};

function buildTree() {
  const ul = $("ftree");
  TREE.forEach(([id, depth, name, note, cls]) => {
    const li = document.createElement("li");
    if (id) li.dataset.f = id;
    li.style.paddingLeft = (6 + depth * 14) + "px";
    li.innerHTML = `<span class="n ${cls}"></span><span class="c"></span>`;
    li.firstChild.textContent = name; li.lastChild.textContent = note;
    ul.appendChild(li);
  });
}
function highlight(files, label) {
  const set = new Set(files || []); let first = null;
  document.querySelectorAll("#ftree li").forEach(li => { const on = li.dataset.f && set.has(li.dataset.f); li.classList.toggle("hl", !!on); if (on && !first) first = li; });
  $("ftree-now").textContent = label || "";
  const box = $("ftree-scroll");
  if (first && box) { const top = first.offsetTop - box.offsetTop; if (top < box.scrollTop || top > box.scrollTop + box.clientHeight - 40) box.scrollTop = Math.max(0, top - 40); }
}
function refreshHighlight() {
  const st = STEPPERS[activeSection];
  if (st) {
    const s = st.steps[st.cur];
    if (s.subs) { const b = s.subs[st.sub - 1]; highlight(b.files, `Step ${st.cur + 1}, block ${st.sub}: ${b.title}`); }
    else highlight(s.files, `Step ${st.cur + 1}: ${s.title}`);
  } else if (SECTION_FILES[activeSection]) highlight(SECTION_FILES[activeSection].files, SECTION_FILES[activeSection].label);
  else highlight([], "");
}
function watchSections() {
  const ratios = {};
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => { ratios[e.target.id] = e.isIntersecting ? e.intersectionRect.height : 0; });
    let best = activeSection, max = -1;
    Object.keys(ratios).forEach(k => { if (ratios[k] > max) { max = ratios[k]; best = k; } });
    if (max > 0 && best !== activeSection && !readerState) { activeSection = best; refreshHighlight(); }
  }, { threshold: [0, 0.1, 0.25, 0.5, 0.75, 1] });
  document.querySelectorAll("section.card[id]").forEach(s => obs.observe(s));
}

function makeStepper(section, steps) {
  const st = { section, steps, cur: 0, sub: 1 };
  const P = section, svgId = "flow-" + section, marker = "m-" + section;
  function draw() {
    const svg = $(svgId); svg.innerHTML = "";
    const defs = el("defs", {}); const m = el("marker", { id: marker, viewBox: "0 0 10 10", refX: 8, refY: 5, markerWidth: 6, markerHeight: 6, orient: "auto-start-reverse" });
    m.appendChild(el("path", { d: "M2 1L8 5L2 9", class: "ln" })); defs.appendChild(m); svg.appendChild(defs);
    let y = 8, last = "";
    steps.forEach((s, i) => {
      if (s.group !== last) { svg.appendChild(el("text", { class: "lbl", x: 10, y: y + 12 }, s.group.toUpperCase())); y += 22; last = s.group; }
      const g = el("g", { class: "step", tabindex: 0, role: "button", "aria-label": `Step ${i + 1}: ${s.title}` });
      g.appendChild(el("rect", { class: s.cls, x: 10, y, width: 380, height: 66, rx: 8 }));
      g.appendChild(el("text", { class: "tt", x: 24, y: y + 20 }, `${i + 1}. ${s.title}`));
      g.appendChild(el("text", { class: "tx", x: 24, y: y + 39 }, s.sub));
      g.appendChild(el("text", { class: "tr", x: 24, y: y + 57 }, "→ " + s.result));
      g.addEventListener("click", () => go(i));
      g.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(i); } });
      svg.appendChild(g); y += 66;
      if (i < steps.length - 1) { const nn = steps[i + 1].group !== s.group; svg.appendChild(el("line", { class: "ln", x1: 350, y1: y, x2: 350, y2: y + (nn ? 30 : 16), "marker-end": `url(#${marker})` })); y += nn ? 12 : 20; }
    });
    svg.setAttribute("viewBox", `0 0 400 ${y + 8}`);
  }
  function subsHtml(s) {
    const pills = s.subs.map((b, k) => `<button type="button" role="tab" data-sub="${k + 1}">Block ${k + 1}. ${b.title}</button>`).join("");
    const blocks = s.subs.map((b, k) => `<div class="sub" data-sub-block="${k + 1}" hidden><h3 class="sub-h">Block ${k + 1} of ${s.subs.length}: ${b.title}</h3>${b.html}</div>`).join("");
    return `<div class="pills" role="tablist" aria-label="Blocks of this step">${pills}</div>${blocks}<div class="subnav"><button type="button" class="btn" data-subnav="-1">Previous block</button><button type="button" class="btn primary" data-subnav="1">Next block</button></div>`;
  }
  function showSub(n) {
    const s = steps[st.cur]; if (!s.subs) return;
    st.sub = Math.max(1, Math.min(s.subs.length, n));
    const body = $(P + "-body");
    body.querySelectorAll(".sub").forEach(b => { b.hidden = Number(b.dataset.subBlock) !== st.sub; });
    body.querySelectorAll(".pills button").forEach((b, k) => b.setAttribute("aria-selected", String(k + 1 === st.sub)));
    body.querySelector('[data-subnav="-1"]').disabled = st.sub === 1;
    body.querySelector('[data-subnav="1"]').disabled = st.sub === s.subs.length;
    $(P + "-terms").innerHTML = termsBlock(s.subs[st.sub - 1].terms);
    if (activeSection === section) refreshHighlight();
  }
  function go(i) {
    st.cur = Math.max(0, Math.min(steps.length - 1, i)); st.sub = 1;
    const s = steps[st.cur];
    $(P + "-kick").textContent = `Step ${st.cur + 1} of ${steps.length}: ${s.group}`;
    $(P + "-title").textContent = s.title;
    $(P + "-facts").innerHTML = s.facts.map(f => `<dt>${f[0]}</dt><dd>${f[1]}</dd>`).join("");
    $(P + "-body").innerHTML = s.body + (s.subs ? subsHtml(s) : "");
    $(P + "-terms").innerHTML = termsBlock(s.terms);
    if (s.subs) showSub(1);
    document.querySelectorAll(`#${svgId} g.step`).forEach((g, k) => { g.classList.toggle("current", k === st.cur); if (k === st.cur) g.setAttribute("aria-current", "step"); else g.removeAttribute("aria-current"); });
    $(P + "-prev").disabled = st.cur === 0; $(P + "-next").disabled = st.cur === steps.length - 1;
    if (activeSection === section) refreshHighlight();
    readerTitle();
  }
  $(P + "-prev").addEventListener("click", () => { go(st.cur - 1); readerTop(); });
  $(P + "-next").addEventListener("click", () => { go(st.cur + 1); readerTop(); });
  $(P + "-body").addEventListener("click", e => {
    const p = e.target.closest("[data-sub]"); if (p) { showSub(Number(p.dataset.sub)); return; }
    const n = e.target.closest("[data-subnav]"); if (n) showSub(st.sub + Number(n.dataset.subnav));
  });
  st.draw = draw; st.go = go; st.showSub = showSub;
  STEPPERS[section] = st;
  draw(); go(0);
  return st;
}

/* Tabs */
const TAB_COUNT = document.querySelectorAll('.tabs [role="tab"]').length;
function selectTab(n) {
  for (let k = 1; k <= TAB_COUNT; k++) { $("tab" + k).setAttribute("aria-selected", String(k === n)); $("panel" + k).hidden = k !== n; }
  const aside = document.querySelector(".tree-aside");
  document.querySelector(`#panel${n} .layout`).appendChild(aside);
  const first = document.querySelector(`#panel${n} section.card[id]`);
  activeSection = first ? first.id : ""; refreshHighlight();
}
for (let k = 1; k <= TAB_COUNT; k++) $("tab" + k).addEventListener("click", () => selectTab(k));
function tabOf(id) { const p = document.getElementById(id).closest('[role="tabpanel"]'); return p ? Number(p.id.slice(5)) : 1; }

/* Full-screen reader: a click on a step card opens it */
let readerState = null;
function readerTitle() { if (!readerState) return; const st = STEPPERS[readerState.section]; $("reader-title").textContent = `Part ${tabOf(readerState.section)}, step ${st.cur + 1} of ${st.steps.length}`; }
function readerTop() { if (readerState) $("reader-main").scrollTop = 0; }
function openReader(section) {
  const dlg = $("reader"); if (dlg.open) return;
  const panel = document.querySelector(`#${section} .panel`), aside = document.querySelector(".tree-aside");
  readerState = { section, panel, pParent: panel.parentNode, pNext: panel.nextSibling, aside, aParent: aside.parentNode, aNext: aside.nextSibling };
  $("reader-main").appendChild(panel); $("reader-side").appendChild(aside);
  activeSection = section; readerTitle(); refreshHighlight(); dlg.showModal(); readerTop();
}
function restoreReader() { const r = readerState; if (!r) return; r.pParent.insertBefore(r.panel, r.pNext); r.aParent.insertBefore(r.aside, r.aNext); readerState = null; }
$("reader-close").addEventListener("click", () => $("reader").close());
$("reader").addEventListener("close", restoreReader);
$("reader").addEventListener("click", e => { if (e.target === $("reader")) $("reader").close(); });
document.querySelectorAll("[data-reader]").forEach(b => b.addEventListener("click", () => openReader(b.dataset.reader)));
document.querySelectorAll(".flow .panel").forEach(panel => {
  const section = panel.closest("section.card").id;
  panel.setAttribute("title", "Click to read in full screen");
  panel.addEventListener("click", e => {
    if (readerState) return;
    if (e.target.closest("button, a, input, select, textarea, label, summary")) return;
    if (String(window.getSelection())) return;
    openReader(section);
  });
});

/* Links: data-goto="step:<section>:<n>[:<block>]" or "sec:<section>" */
document.addEventListener("click", e => {
  const b = e.target.closest("[data-goto]"); if (!b) return;
  const [kind, id, n, blk] = b.dataset.goto.split(":");
  const t = tabOf(id); if ($("panel" + t).hidden) selectTab(t);
  if (kind === "step" && STEPPERS[id]) { STEPPERS[id].go(Number(n) - 1); if (blk) STEPPERS[id].showSub(Number(blk)); }
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  document.getElementById(id).scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
});
document.addEventListener("keydown", e => { const g = e.target.closest && e.target.closest(".ov-box"); if (g && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); g.dispatchEvent(new MouseEvent("click", { bubbles: true })); } });

/* Overview: snake layout, 4 boxes per row */
function drawOverview() {
  const svg = $("ovsvg"); const W = 150, G = 20, X0 = 10;
  const defs = el("defs", {}); const m = el("marker", { id: "m-ov", viewBox: "0 0 10 10", refX: 8, refY: 5, markerWidth: 6, markerHeight: 6, orient: "auto-start-reverse" });
  m.appendChild(el("path", { d: "M2 1L8 5L2 9", class: "ln" })); defs.appendChild(m); svg.appendChild(defs);
  OVERVIEW.rows.forEach((row, k) => {
    const hy = 20 + k * 100, by = 30 + k * 100, rev = k % 2 === 1;
    svg.appendChild(el("text", { class: "lbl", x: 340, y: hy, "text-anchor": "middle" }, row.title.toUpperCase()));
    const xs = row.boxes.map((_, i) => X0 + (rev ? 3 - i : i) * (W + G));
    row.boxes.forEach((b, i) => {
      const g = el("g", { class: "ov-box", "data-goto": b.go, role: "link", tabindex: 0, "aria-label": `${b.t}: open the step` });
      g.appendChild(el("rect", { class: row.cls, x: xs[i], y: by, width: W, height: 50, rx: 6 }));
      g.appendChild(el("text", { class: "tt", x: xs[i] + W / 2, y: by + 21, "text-anchor": "middle" }, b.t));
      g.appendChild(el("text", { class: "tx", x: xs[i] + W / 2, y: by + 39, "text-anchor": "middle" }, b.sub));
      svg.appendChild(g);
      if (i < row.boxes.length - 1) {
        const x1 = rev ? xs[i] : xs[i] + W, x2 = rev ? xs[i + 1] + W + 4 : xs[i + 1] - 4;
        svg.appendChild(el("line", { class: "ln", x1, y1: by + 25, x2, y2: by + 25, "marker-end": "url(#m-ov)" }));
      }
    });
    if (k < OVERVIEW.rows.length - 1) {
      const nxt = OVERVIEW.rows[k + 1], lastX = xs[xs.length - 1];
      const nRev = (k + 1) % 2 === 1, nFirst = X0 + (nRev ? 3 : 0) * (W + G);
      const cx = lastX + W / 2, nx = nFirst + W / 2;
      svg.appendChild(el("path", { class: "ln", d: `M${cx} ${by + 50} L${cx} ${by + 62} L${nx} ${by + 62} L${nx} ${by + 96}`, fill: "none", "marker-end": "url(#m-ov)" }));
    }
  });
  const h = 30 + OVERVIEW.rows.length * 100;
  if (OVERVIEW.note) svg.appendChild(el("text", { class: "tx", x: 340, y: h - 8, "text-anchor": "middle" }, OVERVIEW.note));
  svg.setAttribute("viewBox", `0 0 680 ${h + 4}`);
  $("ovsteps").innerHTML = OVERVIEW.steps.map(([t, g, lbl]) => `<li>${md(t)} <button type="button" class="linkbtn" data-goto="${g}">${esc(lbl)}</button></li>`).join("");
}

/* Term index for each tab: section terms + step terms */
function buildTermIndexes() {
  document.querySelectorAll("ul.index[data-index-for]").forEach(ul => {
    const panel = $(ul.dataset.indexFor), list = [];
    panel.querySelectorAll("section.card > .terms dt[id]").forEach(dt => list.push([dt.textContent, dt.id, dt.closest("section.card").id, null, null]));
    Object.values(STEPPERS).forEach(st => {
      if ($(st.section).closest('[role="tabpanel"]') !== panel) return;
      st.steps.forEach((s, i) => { (s.terms || []).forEach(t => list.push([t[1], t[0], st.section, i, null])); (s.subs || []).forEach((b, k) => (b.terms || []).forEach(t => list.push([t[1], t[0], st.section, i, k + 1]))); });
    });
    const seen = new Set();
    list.filter(x => !seen.has(x[1]) && seen.add(x[1])).sort((a, b) => a[0].localeCompare(b[0])).forEach(([name, id, sec, step, blk]) => {
      const li = document.createElement("li"); const b = document.createElement("button"); b.type = "button";
      b.innerHTML = `<span></span><span class="where"></span>`; b.firstChild.textContent = name;
      b.lastChild.textContent = step === null ? `section ${sec}` : `step ${step + 1}${blk ? ", block " + blk : ""}`;
      b.addEventListener("click", () => {
        if (step !== null) { STEPPERS[sec].go(step); if (blk) STEPPERS[sec].showSub(blk); }
        const t = document.getElementById(id); if (!t) return;
        t.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "center" });
        const box = t.closest(".terms"); if (box) { box.classList.remove("flash"); void box.offsetWidth; box.classList.add("flash"); }
      });
      li.appendChild(b); ul.appendChild(li);
    });
  });
}

initPage();
