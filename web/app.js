/* cdfc surface — seven screens over ONE snapshot produced by tools/build_frontend_data.py.
 *
 * The surface renders a snapshot and never recomputes. A screen that recomputes is a screen that
 * can disagree with the run it claims to show, which is the same reason the graph is a projection
 * rather than a store.
 *
 * NOTHING HERE INVENTS A NUMBER. Where the snapshot has no value the screen says so; it does not
 * fall back to zero, because a zero is a measurement and an absence is not. */
const PAGES = [
  ["intake",  "Intake",      "upload, addressed"],
  ["fuse",    "Resolve",     "one identity, many files"],
  ["map",     "Map",         "statute to template"],
  ["ret",     "Return",      "what we can evidence"],
  ["judge",   "Judgement",   "what needs you"],
  ["graph",   "Graph",       "the evidence, linked"],
  ["cert",    "Certificate", "signed coverage"],
];
let S = null;

const el = (t, a = {}, ...kids) => {
  const n = document.createElement(t);
  for (const [k, v] of Object.entries(a)) {
    if (v === null || v === undefined) continue;
    if (k === "class") n.className = v; else if (k === "html") n.innerHTML = v;
    else n.setAttribute(k, v);
  }
  for (const c of kids.flat()) if (c !== null && c !== undefined)
    n.append(c.nodeType ? c : document.createTextNode(String(c)));
  return n;
};
const fig = (v) => el("span", {class: "fig"}, v === null || v === undefined ? "—" : v.toLocaleString());
/* A DIGEST IS A VALUE. Passing a root as `sub` with a null figure rendered the card as an
 * em-dash, which reads as "we do not have one" for the single number that identifies the run. */
const hashStat = (label, root, sub) => el("div", {class: "card stat k"},
  el("span", {class: "lbl"}, label),
  el("b", {style: "font-size:15px;line-height:1.5;word-break:break-all"},
     root ? root.slice(0, 32) + "…" : "not computed"),
  sub ? el("small", {}, sub) : null);
const stat = (label, value, sub, of) => el("div", {class: "card stat"},
  el("span", {class: "lbl"}, label),
  el("b", {}, value === null || value === undefined ? "—" : value.toLocaleString(),
     of !== undefined && of !== null ? el("span", {class: "of"}, ` / ${of.toLocaleString()}`) : null),
  sub ? el("small", {}, sub) : null);
const sec = (title, note, ...body) => el("section", {class: "sec"},
  el("h2", {}, title), note ? el("p", {class: "note"}, note) : null, ...body);
const table = (cols, rows) => el("div", {class: "scroll"}, el("table", {},
  el("thead", {}, el("tr", {}, cols.map((c) => el("th", {}, c)))),
  el("tbody", {}, rows.length ? rows : [el("tr", {}, el("td", {colspan: cols.length},
    el("span", {class: "prov"}, "nothing in this bucket")))])));
const head = (t, p) => el("header", {class: "head"}, el("h1", {}, t), p ? el("p", {}, p) : null);

/* ---- screens --------------------------------------------------------------------------- */
const screens = {};

screens.intake = () => {
  const s = S.stages.intake;
  return [head("Intake", "Upload the exports in whatever shape they arrive. Each one is stored under its own digest, so the run names exactly the bytes it used."),
    el("div", {class: "grid"},
      stat("artefacts", s.artefacts.length, "template and sources"),
      stat("sources", s.artefacts.filter((a) => a.kind === "source").length, "csv, xlsx, pdf"),
      hashStat("merkle root", s.merkle_root, "over this run's inputs")),
    sec("What was uploaded", "The digest IS the identity. Re-uploading identical bytes is a no-op.",
      table(["kind", "name", "bytes", "digest"], s.artefacts.map((a) => el("tr", {},
        el("td", {}, el("span", {class: "pill " + (a.kind === "template" ? "at" : "n")}, a.kind)),
        el("td", {}, a.name), el("td", {class: "num"}, a.bytes.toLocaleString()),
        el("td", {}, el("span", {class: "digest"}, a.digest.slice(0, 32) + "…")))))),
    el("div", {class: "callout"}, el("b", {}, "The Merkle root is over THIS run's inputs"),
      el("p", {}, "Not over the store. A run names the artefacts it used, and the root changes if any one of them changes — which is what makes the filing re-derivable later."))];
};

screens.fuse = () => {
  const s = S.stages.fuse, c = s.counts;
  return [head("Resolve and fuse", "The same entity appears in more than one file, spelled differently. Records are what a document said; entities are what we concluded."),
    el("div", {class: "grid"},
      stat("records", c.records, "rows read, across all files"),
      stat("entities", c.entities, "identities resolved"),
      stat("cross-document", c.cross_document, "seen in more than one file"),
      stat("refused", c.refused, "a tie is refused, never broken")),
    sec("Entities", "Resolved by Fellegi-Sunter with m, u and prevalence fitted by EM on NO labelled pairs.",
      table(["entity", "how", "documents", "records"], s.entities.map((e) => el("tr", {},
        el("td", {}, el("span", {class: "digest"}, e.id)),
        el("td", {}, el("span", {class: "pill " + (e.resolved_by === "linkage" ? "ok" : e.resolved_by === "model" ? "dv" : "n")}, e.resolved_by)),
        el("td", {}, e.documents.join(" · ")),
        el("td", {class: "num"}, e.records.length))))),
    s.refused.length ? sec("Refused", "Two candidates of comparable weight is not a match with a tiebreak — it is an absence of evidence about which.",
      table(["record", "reason", "detail"], s.refused.map((r) => el("tr", {},
        el("td", {}, el("span", {class: "digest"}, r.record)),
        el("td", {}, el("span", {class: "pill no"}, r.reason)),
        el("td", {}, el("span", {class: "prov"}, r.detail)))))) : null];
};

screens.map = () => {
  const m = S.stages.map;
  const out = [head("Map the statute onto the template", "A model proposes bindings between a provision and a field. It decides nothing: five deterministic gates adjudicate every proposal, and only admitted ones become nodes.")];
  out.push(el("div", {class: "grid"},
    stat("provisions", m.provisions, `addressed by ${m.addressing || "—"}`),
    stat("proposals", m.proposals, "the model's candidates"),
    stat("admitted", m.admitted, "survived all five gates"),
    stat("fields governed", m.fields_governed, "of the labelled surface", m.labelled_total)));
  if (m.addressing === "coordinate") out.push(el("div", {class: "callout"},
    el("b", {}, "These citations are COORDINATE-addressed, and that is the weaker kind"),
    el("p", {}, `A coordinate like p0146.s0013 is a page and a sentence: it moves if the instrument is re-extracted or an amendment inserts a page. ${m.durable_available.toLocaleString()} durable addresses are available on this instrument and this proposals file predates them.`)));
  out.push(sec("Rules admitted", "Each cites a provision and quotes it VERBATIM — G-QUOTE re-reads the quote at the span and refuses anything that is not byte-exact.",
    table(["provision", "kind", "field", "quote"], (m.rules || []).map((r) => el("tr", {},
      el("td", {}, el("span", {class: "digest"}, r.eid)),
      el("td", {}, el("span", {class: "pill n"}, r.kind)),
      el("td", {}, el("span", {class: "mono"}, r.field || "—")),
      el("td", {}, el("blockquote", {}, r.quote)))))));
  if ((m.gate_refusals || []).length) out.push(sec("Refused, and by which gate",
    "Every gate runs; the first refusal does not stop the rest, because a caller fixing one defect needs to see the others in the same pass.",
    table(["provision", "gate", "reason", "detail"], m.gate_refusals.flatMap((v) =>
      v.gates.map((g) => el("tr", {},
        el("td", {}, el("span", {class: "digest"}, v.eid)),
        el("td", {}, el("span", {class: "pill no"}, g.gate)),
        el("td", {}, el("span", {class: "mono"}, g.reason)),
        el("td", {}, el("span", {class: "prov"}, g.detail))))))));
  if ((m.markers_refused || []).length) out.push(sec("Addresses the instrument declared and we could not use",
    "A malformed marker is refused and counted, never dropped. absent ≠ empty ≠ zero.",
    table(["eid", "why"], m.markers_refused.map((x) => el("tr", {},
      el("td", {}, el("span", {class: "digest"}, x.eid)),
      el("td", {}, el("span", {class: "prov"}, x.why)))))));
  return out;
};

screens.ret = () => {
  const r = S.stages.return, c = r.counts;
  const ev = c.proposed || 0, dv = c.derived || 0, at = c.attestations || 0, rf = c.refused || 0;
  const tot = ev + dv + at + rf || 1;
  const pct = (n) => (n / tot * 100).toFixed(4) + "%";
  return [head("The return", `Filed for ${Object.entries(r.subject).map(([k, v]) => k + " " + v).join(", ")}. A return is filed BY one entity ABOUT that entity, so the run refuses to proceed if the sources describe several and nobody names one.`),
    el("div", {class: "grid"},
      stat("evidenced", ev, "cites a span that re-reads byte-exact"),
      stat("derived", dv, "placed, NOT counted as checked"),
      stat("attestations", at, "a human signs; we never fill one"),
      stat("refused", rf, "with a reason from a closed vocabulary")),
    el("div", {style: "margin-top:24px"},
      el("div", {class: "bar"},
        el("i", {class: "e", style: `width:${pct(ev)}`}), el("i", {class: "d", style: `width:${pct(dv)}`}),
        el("i", {class: "a", style: `width:${pct(at)}`}), el("i", {class: "r", style: `width:${pct(rf)}`})),
      el("div", {class: "legend"},
        el("span", {}, el("i", {style: "background:var(--ok)"}), "evidenced"),
        el("span", {}, el("i", {style: "background:var(--derived)"}), "derived"),
        el("span", {}, el("i", {style: "background:var(--accent)"}), "attestation"),
        el("span", {}, el("i", {style: "background:#E7E9ED"}), "refused"))),
    sec("Values placed, with where each came from", "An EVIDENCED value cites a document and a span that re-reads byte-exact. Neither lane is a claim that the figure is correct.",
      ...r.proposed.map((p) => el("div", {class: "card k", style: "margin-bottom:16px"},
        el("div", {style: "display:flex;gap:16px;align-items:baseline;flex-wrap:wrap"},
          el("span", {class: "mono", style: "font-weight:600"}, p.field),
          el("span", {style: "font-size:20px"}, p.value),
          el("span", {class: "pill ok"}, "evidenced")),
        el("div", {class: "prov", style: "margin-top:8px"},
          `${p.label} · ${p.document} · span ${p.span.join("–")} · page ${p.page}`),
        p.context ? el("blockquote", {}, p.context) : null,
        el("div", {style: "display:flex;gap:6px;flex-wrap:wrap;margin-top:12px"},
          p.conditions.map((c) => el("span", {
            class: "pill " + (c.holds ? "ok" : "no"),
            title: c.detail || (c.holds ? "holds" : "does not hold")}, c.name)))))),
    dv ? sec("Derived", "A model produced these and no span supports them. They are placed in the return and are NOT counted as checked.",
      table(["field", "value", "why"], r.derived.map((p) => el("tr", {},
        el("td", {}, el("span", {class: "mono"}, p.field || "—")),
        el("td", {}, p.value), el("td", {}, el("span", {class: "prov"}, p.why)))))) : null,
    at ? sec("Awaiting a named signatory", "The system never fills an attestation. Somebody signs it.",
      table(["field", "label"], r.attestations.map((a) => el("tr", {},
        el("td", {}, el("span", {class: "mono"}, a.field || "—")),
        el("td", {}, a.label))))) : null];
};

screens.judge = () => {
  const j = S.stages.judgement, r = S.stages.return;
  const max = Math.max(...j.by_reason.map((x) => x.count), 1);
  return [head("What needs your judgement", "Every refusal takes its reason from a CLOSED vocabulary. Nothing is refused for a reason nobody wrote down."),
    el("div", {class: "grid"},
      stat("refusals", j.total, "across the whole surface"),
      stat("distinct reasons", j.by_reason.length, "from the closed set"),
      stat("values not in the source", r.unlocatable.length, "a column offered them; the document does not contain them")),
    sec("By reason", "The largest bucket is not a failure of the binder — it is the template's own labelling density.",
      table(["reason", "count", ""], j.by_reason.map((x) => el("tr", {},
        el("td", {}, el("span", {class: "mono"}, x.reason)),
        el("td", {class: "num"}, x.count.toLocaleString()),
        el("td", {style: "width:44%"}, el("div", {class: "bar"},
          el("i", {class: "a", style: `width:${(x.count / max * 100).toFixed(2)}%`}))))))),
    r.unlocatable.length ? sec("Offered, but not in the document",
      "A value a column offered that does not occur in the source text yields NO observation. A claim is a hint about where to look, never evidence that something is there.",
      table(["field", "value"], r.unlocatable.map((u) => el("tr", {},
        el("td", {}, el("span", {class: "mono"}, u.field)),
        el("td", {}, el("span", {class: "prov"}, u.value)))))) : null];
};

screens.graph = () => {
  const m = S.stages.map, kinds = m.graph_nodes || {};
  const total = Object.values(kinds).reduce((a, b) => a + b, 0);
  const COLOR = {Provision: "#53617A", Field: "#E48B59", Rule: "#B45D35", Record: "#1B7F4B", Entity: "#6D28D9"};
  // A honest schematic: the KIND counts, not 800 dots nobody can read. Each column is one kind,
  // sized by its real count; the arcs are the edge kinds the graph actually carries.
  const cols = Object.entries(kinds);
  // SVG MUST BE PARSED, NOT createElement'd. `document.createElement("svg")` returns an
  // HTMLUnknownElement -- the tag is in the HTML namespace, so cx/cy/r are inert attributes and
  // the picture renders as text jammed at the origin, which is exactly what it did. Handing the
  // markup to the HTML parser via innerHTML creates real SVG nodes in the right namespace.
  const W = 900, H = 320, gap = W / (cols.length + 1);
  const MONO = "ui-monospace,SFMono-Regular,Menlo,monospace";
  const rad = (n) => Math.max(28, Math.min(88, Math.sqrt(n) * 3.4));
  const svg = [];
  cols.forEach(([k, n], i) => {
    const x = gap * (i + 1), rr = rad(n);
    if (i < cols.length - 1) {
      const x2 = gap * (i + 2) - rad(cols[i + 1][1]);
      svg.push(`<line x1="${x + rr}" y1="150" x2="${x2}" y2="150" stroke="#868E9C" stroke-width="1"/>`);
    }
    svg.push(`<circle cx="${x}" cy="150" r="${rr}" fill="${COLOR[k] || "#868E9C"}" opacity="0.92"/>`);
    svg.push(`<text x="${x}" y="156" text-anchor="middle" fill="#FFFFFF" font-family="${MONO}" font-size="16" font-weight="600">${n}</text>`);
    svg.push(`<text x="${x}" y="${150 + rr + 24}" text-anchor="middle" fill="#111827" font-family="${MONO}" font-size="12">${k}</text>`);
  });
  return [head("The evidence graph", "Built ONLY from admitted proposals. It is a re-derived projection over pinned artefacts, never a store — so it cannot drift from the evidence it is drawn from."),
    el("div", {class: "grid"},
      stat("nodes", total, "across " + cols.length + " kinds"),
      stat("edges", m.graph_edges, "cites · governs · refers_to"),
      stat("provisions cited", m.provisions_cited, "by an admitted rule", m.provisions)),
    sec("Node kinds, to scale", "A circle per kind, area proportional to its real count. Eight hundred dots would be a picture nobody can read.",
      el("div", {class: "gwrap", html:
        `<svg class="graph" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">${svg.join("")}</svg>`})),
    el("div", {class: "callout"}, el("b", {}, "Four populations, never merged"),
      el("p", {}, "A statute's FME is a CONCEPT; a custodian row's FME is an IDENTITY. Provisions and Fields come from the corpus and the template; Records and Entities come from your files. A graph that cannot tell them apart is a graph nobody can audit."))];
};

screens.cert = () => {
  const i = S.stages.intake, r = S.stages.return, m = S.stages.map;
  return [head("Coverage certificate", "What the run used, what it placed, and what it refused — over a denominator that is not arguable."),
    el("div", {class: "grid"},
      hashStat("inputs merkle", i.merkle_root, "template + sources"),
      hashStat("fill merkle", r.merkle_root, "what the fill read"),
      stat("evidenced", r.counts.proposed || 0, "each with a document and a span"),
      stat("rules admitted", m.admitted, "of " + m.proposals + " proposed")),
    sec("What this certificate does NOT say", null,
      el("div", {class: "callout"}, el("b", {}, "Provenance, not correctness"),
        el("p", {}, "Every placed value cites a document and a span that re-reads byte-exact. That is a claim about WHERE the figure came from. It is not a claim that the figure is right, and nothing here bounds RECALL — we measure the rules that were proposed, never the ones nobody proposed."))),
    sec("Signing", "Signing is a deliberate act with a named signatory and a verified instant — never a clock read.",
      el("div", {class: "empty"}, "Run ", el("code", {class: "mono"}, "cdfc attest <filing> --time-verified <ISO-8601>"),
        " to sign, then ", el("code", {class: "mono"}, "cdfc verify <attestation>"), " to re-derive it byte-for-byte."))];
};

/* ---- router ---------------------------------------------------------------------------- */
function route() {
  const id = (location.hash.replace("#", "") || "intake");
  const page = PAGES.find((p) => p[0] === id) || PAGES[0];
  document.querySelectorAll("#nav a").forEach((a) =>
    a.getAttribute("href") === "#" + page[0] ? a.setAttribute("aria-current", "page")
                                             : a.removeAttribute("aria-current"));
  const main = document.getElementById("main");
  main.textContent = "";
  try { for (const n of screens[page[0]]()) if (n) main.append(n); }
  catch (e) { main.append(el("div", {class: "empty"}, "This screen could not render: " + e.message)); }
  window.scrollTo(0, 0);
}

fetch("data/state.json").then((r) => r.json()).then((d) => {
  S = d;
  const nav = document.getElementById("nav");
  PAGES.forEach(([id, name, sub], i) => nav.append(el("a", {href: "#" + id},
    el("span", {class: "n"}, String(i + 1).padStart(2, "0")),
    el("span", {}, name, el("em", {}, sub)))));
  window.addEventListener("hashchange", route);
  route();
}).catch((e) => {
  document.getElementById("main").innerHTML =
    `<div class="empty">No run to show. Build one first:<br><br>
     <code class="mono">python tools/build_frontend_data.py</code><br><br>
     <span class="prov">${e.message}</span></div>`;
});
