/* cdfc — the application. Every screen is a REQUEST; nothing here is a snapshot.
 *
 * The surface this replaces rendered `web/data/state.json`, a file somebody else computed. That
 * obeyed one real rule — a screen that recomputes can disagree with the run it claims to show —
 * and paid for it by being a picture of a filing rather than a filing.
 *
 * The rule is kept and the cost is not. `cdfc.api.returns` stores ONLY what a human supplied (the
 * artefacts, the subject, the answers) and `cdfc.api.derive` re-derives everything else on every
 * request. So there is no second copy for a screen to disagree with, and every number on every
 * screen below came from the run that is live right now.
 *
 * THREE THINGS THIS FILE IS CAREFUL ABOUT, each one a defect that has already happened here:
 *
 *   1. `document.createElement("svg")` returns an HTMLUnknownElement — the tag is created in the
 *      HTML namespace, so `cx`/`cy`/`r` are inert and the picture renders as text at the origin.
 *      SVG is built as markup and handed to the HTML parser, which puts it in the right namespace.
 *   2. `hashchange` is ASYNC. A handler that sets `location.hash` and reads the DOM in the same
 *      tick measures the screen it was already on. Routing here is driven by the event, never by
 *      the assignment.
 *   3. A missing value is rendered as MISSING, with the reason. `absent != empty != zero`, and a
 *      fallback of `0` or `—` for a field the API did not send is a measurement nobody made.
 */
"use strict";

/* ---------------------------------------------------------------- state and transport ----- */

const S = {
  token: "",            // MEMORY ONLY. Never localStorage, never a URL parameter.
  returnId: null,
  ret: null,            // the last GET /v1/returns/{id} payload
  caps: null,
  busy: false,
};

class ApiError extends Error {
  constructor(status, body) {
    super((body && (body.detail || body.error)) || `HTTP ${status}`);
    this.status = status;
    this.body = body || {};
  }
}

async function api(method, path, {query, body, raw} = {}) {
  const url = path + (query ? "?" + new URLSearchParams(query).toString() : "");
  const headers = {};
  if (S.token) headers["Authorization"] = "Bearer " + S.token;
  let payload = body;
  if (body !== undefined && !raw) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }
  const res = await fetch(url, {method, headers, body: payload});
  const text = await res.text();
  let obj = null;
  try { obj = text ? JSON.parse(text) : null; } catch (e) { obj = {error: "not_json", detail: text.slice(0, 400)}; }
  if (!res.ok) throw new ApiError(res.status, obj);
  return obj;
}

/* ---------------------------------------------------------------- tiny DOM helpers -------- */

const el = (t, a = {}, ...kids) => {
  const n = document.createElement(t);
  for (const [k, v] of Object.entries(a)) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") n.className = v;
    else if (k.startsWith("on") && typeof v === "function") n.addEventListener(k.slice(2), v);
    else n.setAttribute(k, v);
  }
  for (const k of kids.flat()) {
    if (k === null || k === undefined || k === false) continue;
    n.appendChild(typeof k === "object" ? k : document.createTextNode(String(k)));
  }
  return n;
};

const esc = (s) => String(s).replace(/[&<>"']/g, (c) =>
  ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]));

/* A number, or an explicit ABSENCE. `n(undefined)` must never render as 0 — a zero is a
   measurement and an absence is not, and the two have been confused in this project before. */
const fig = (v, absent = "not measured") =>
  (v === null || v === undefined)
    ? el("span", {class: "abs"}, absent)
    : el("span", {class: "fig"}, Number(v).toLocaleString());

const stat = (label, value, sub, absent) => el("div", {class: "card stat"},
  el("span", {class: "lbl"}, label),
  el("b", {}, fig(value, absent || "not measured")),
  sub ? el("small", {}, sub) : null);

const sec = (title, note, ...body) => el("section", {class: "sec"},
  el("h2", {}, title), note ? el("p", {class: "note"}, note) : null, ...body);

const head = (t, p) => el("header", {class: "head"}, el("h1", {}, t), p ? el("p", {}, p) : null);

const table = (cols, rows) => el("div", {class: "scroll"}, el("table", {},
  el("thead", {}, el("tr", {}, cols.map((c) => el("th", {}, c)))),
  el("tbody", {}, rows.map((r) => el("tr", {}, r.map((c) =>
    el("td", {class: typeof c === "number" ? "num" : ""},
      typeof c === "number" ? c.toLocaleString() : c)))))));

const errBox = (e) => el("div", {class: "err"},
  el("b", {}, (e.body && e.body.error) || e.name || "error"),
  el("p", {}, e.message),
  e.body && e.body.remedy ? el("p", {}, "Remedy: " + e.body.remedy) : null);

const callout = (title, text) => el("div", {class: "callout"},
  el("b", {}, title), el("p", {}, text));

const short = (d) => (d ? String(d).slice(0, 12) + "…" : "");

/* ---------------------------------------------------------------- screens ----------------- */

const PAGES = [
  ["intake",      "01", "Intake",      "upload"],
  ["corpus",      "02", "Corpus",      "provisions"],
  ["template",    "03", "Template",    "field surface"],
  ["map",         "04", "Map",         "five gates"],
  ["graph",       "05", "Graph",       "nodes + edges"],
  ["fill",        "06", "Return",      "values + spans"],
  ["questions",   "07", "Questions",   "what we ask"],
  ["certificate", "08", "Certificate", "and its limits"],
];

const screens = {};

/* ---- 01 INTAKE ---------------------------------------------------------------------------- */

const KINDS = [
  ["instrument", "Rules corpus", "A statute, circular or rulebook — plain text, or a document " +
   "already pinned by `make pin-pdf`. It is segmented into addressable provisions with an eId " +
   "and an exact span."],
  ["template", "Filing template", "The regulator's blank — .xlsx. Its field surface is induced " +
   "from the workbook's own unlocked-cell mask, or refused with a reason."],
  ["source", "Evidence export", "A custodian feed, trial balance, cap table or pinned valuation " +
   "pack. CSV, or a pinned document. This is what values are located in."],
  ["rules", "Proposals (LAYER 2)", "A model's proposed rule→field bindings, AS DATA. The driver " +
   "reads the file; the model is never called from the verdict path because it is not called."],
];

screens.intake = async (main) => {
  main.replaceChildren(head("Intake",
    "Upload what you have. Everything is stored under its own sha-256 digest, and a run names " +
    "its inputs by digest so it can be re-derived later."));

  if (!S.caps) { try { S.caps = await api("GET", "/v1/capabilities"); } catch (e) { /* shown below */ } }

  const drops = el("div", {class: "drops"});
  for (const [kind, title, why] of KINDS) {
    const st = el("div", {class: "st"}, "");
    const input = el("input", {type: "file"});
    const card = el("div", {class: "drop"},
      el("h3", {}, title), el("p", {}, why), input, st);
    const send = async (file) => {
      if (!file) return;
      try {
        const a = await upload(kind, file, (m) => { st.className = "st"; st.textContent = m; });
        st.className = "st good";
        st.textContent = `stored ${a.digest.slice(0, 16)}…  ${a.size.toLocaleString()} bytes`;
        await refreshArtefacts();
      } catch (e) {
        st.className = "st bad";
        st.textContent = `${(e.body && e.body.error) || "refused"}: ${e.message}`;
      }
    };
    input.addEventListener("change", () => send(input.files[0]));
    for (const ev of ["dragenter", "dragover"]) card.addEventListener(ev, (e) => {
      e.preventDefault(); card.classList.add("over");
    });
    for (const ev of ["dragleave", "drop"]) card.addEventListener(ev, () => card.classList.remove("over"));
    card.addEventListener("drop", (e) => { e.preventDefault(); send(e.dataTransfer.files[0]); });
    drops.appendChild(card);
  }
  main.appendChild(sec("Upload", "The kind is DECLARED by you and never sniffed from the bytes: " +
    "the same CSV is evidence when it is a custodian feed and a corpus when it is a rules export, " +
    "and no byte pattern tells them apart.", drops));

  if (S.caps && S.caps.pdfReader && !S.caps.pdfReader.installed) {
    main.appendChild(callout("A raw PDF is refused in this deployment, with the reason",
      S.caps.pdfReader.detail));
  }

  main.appendChild(sec("Or start from the sample filing",
    "Real files, through the same upload path: the vendored IFSCA blank, the pinned FM " +
    "Regulations 2025, a plain-text corpus, two custodian exports that DISAGREE with each other, " +
    "and 172 model-written proposals. Nothing here is a fixture the pipeline treats specially.",
    await samplePanel(() => refreshArtefacts())));

  const list = el("div", {}, el("div", {class: "busy"}, "reading the registry…"));
  const open = el("div", {});
  main.appendChild(sec("What has been uploaded", null, list));
  main.appendChild(sec("Open a return", "A return names one template, one or more evidence " +
    "exports, and optionally a corpus and a proposals file. Its id is derived from the merkle " +
    "root over those inputs, so re-opening the same artefacts re-opens the same return and never " +
    "discards an answer.", open));

  async function refreshArtefacts() {
    let arts;
    try { arts = await api("GET", "/v1/artefacts"); }
    catch (e) { list.replaceChildren(errBox(e)); return; }
    if (!arts.length) {
      list.replaceChildren(el("div", {class: "empty"}, "Nothing uploaded yet."));
      open.replaceChildren(el("div", {class: "empty"}, "Upload a template and at least one " +
        "evidence export first."));
      return;
    }
    list.replaceChildren(table(["digest", "kind", "filename", "bytes"], arts.map((a) => [
      el("span", {class: "digest"}, a.digest.slice(0, 24) + "…"),
      el("span", {class: "pill n"}, a.kind), a.filename, a.size,
    ])));
    renderOpen(arts);
  }

  function pick(kind, arts, multiple) {
    const opts = arts.filter((a) => a.kind === kind);
    const s = el("select", multiple ? {multiple: "multiple", size: String(Math.min(5, Math.max(2, opts.length)))} : {});
    if (!multiple) s.appendChild(el("option", {value: ""}, "— none —"));
    for (const a of opts) s.appendChild(el("option", {value: a.digest}, `${a.filename}  ${a.digest.slice(0, 10)}…`));
    return s;
  }

  function renderOpen(arts) {
    const tpl = pick("template", arts, false);
    const src = pick("source", arts, true);
    const cor = pick("instrument", arts, false);
    const pro = pick("rules", arts, false);
    const subjKey = el("input", {type: "text", value: "PAN of FME"});
    const subjVal = el("input", {type: "text", placeholder: "e.g. AAACI1234K"});
    const label = el("input", {type: "text", placeholder: "your own name for this filing"});
    const msg = el("div", {class: "msg"});
    const go = el("button", {class: "pri"}, "Open the return");

    go.addEventListener("click", async () => {
      msg.className = "msg";
      const sources = Array.from(src.selectedOptions).map((o) => o.value);
      if (!tpl.value) { msg.className = "msg bad"; msg.textContent = "choose a template"; return; }
      if (!sources.length) { msg.className = "msg bad"; msg.textContent = "choose at least one evidence export"; return; }
      go.disabled = true; msg.textContent = "opening…";
      try {
        const subject = {};
        if (subjKey.value.trim() && subjVal.value.trim()) subject[subjKey.value.trim()] = subjVal.value.trim();
        const r = await api("POST", "/v1/returns", {body: {
          templateDigest: tpl.value, sourceDigests: sources,
          corpusDigest: cor.value || "", proposalsDigest: pro.value || "",
          subject, label: label.value.trim(),
          openedAt: new Date().toISOString(),
        }});
        S.returnId = r.id; S.ret = null;
        msg.className = "msg good";
        msg.textContent = (r.reopened ? "re-opened " : "opened ") + r.id +
          `  (merkle root ${r.merkleRoot.slice(0, 24)}…)`;
        renderRail();
        location.hash = "#/template";
      } catch (e) {
        msg.className = "msg bad"; msg.textContent = `${(e.body && e.body.error) || "refused"}: ${e.message}`;
      } finally { go.disabled = false; }
    });

    open.replaceChildren(
      el("div", {class: "grid"},
        el("div", {}, el("label", {class: "f"}, el("span", {class: "lbl"}, "Template"), tpl)),
        el("div", {}, el("label", {class: "f"}, el("span", {class: "lbl"}, "Evidence exports (multi-select)"), src)),
        el("div", {}, el("label", {class: "f"}, el("span", {class: "lbl"}, "Rules corpus"), cor)),
        el("div", {}, el("label", {class: "f"}, el("span", {class: "lbl"}, "Proposals"), pro))),
      el("div", {class: "grid"},
        el("div", {}, el("label", {class: "f"}, el("span", {class: "lbl"}, "Subject column"), subjKey)),
        el("div", {}, el("label", {class: "f"}, el("span", {class: "lbl"}, "Subject value"), subjVal)),
        el("div", {}, el("label", {class: "f"}, el("span", {class: "lbl"}, "Label (optional)"), label))),
      callout("Why a subject is asked for",
        "A custodian register holds every entity an administrator serves. Binding all of them to " +
        "one return offers several values for every cell, and the fill lane correctly refuses " +
        "each as contradicted — the count went to zero the moment the registers became " +
        "realistic. Naming the subject is the missing question, and a run whose sources describe " +
        "more than one subject with none named REFUSES rather than picking."),
      el("div", {class: "row"}, go, msg));
  }

  await refreshArtefacts();
};

/* THE ONE UPLOAD PATH. The file picker, the drop target and the sample loader all call this, so
   a sample cannot take a route the real thing does not. */
async function upload(kind, file, say) {
  if (!S.token) throw new ApiError(0, {error: "no_operator_token",
    detail: "paste the token the server printed into the sidebar; uploading is a mutating path"});
  say(`uploading ${file.name} (${file.size.toLocaleString()} bytes)…`);
  return api("POST", "/v1/artefacts", {
    query: {kind, filename: file.name}, body: await file.arrayBuffer(), raw: true,
  });
}

async function samplePanel(after) {
  let samples;
  try { samples = await (await fetch("/samples/index.json")).json(); }
  catch (e) { return el("div", {class: "empty"}, "This launcher mounts no samples."); }

  const st = el("div", {class: "st"}, "");
  const go = el("button", {class: "pri"}, "Load the sample filing");
  go.addEventListener("click", async () => {
    go.disabled = true;
    let ok = 0;
    for (const s of samples) {
      if (!s.present) { continue; }
      try {
        const res = await fetch("/samples/" + encodeURIComponent(s.name));
        const blob = await res.blob();
        const file = new File([blob], s.name);
        await upload(s.kind, file, (m) => { st.className = "st"; st.textContent = m; });
        ok += 1;
      } catch (e) {
        st.className = "st bad";
        st.textContent = `${s.name}: ${(e.body && e.body.error) || "refused"} — ${e.message}`;
        go.disabled = false;
        return;
      }
    }
    st.className = "st good";
    st.textContent = `${ok} sample artefact(s) uploaded — each stored under its own digest`;
    go.disabled = false;
    await after();
  });

  return el("div", {},
    table(["file", "declared kind", "bytes", "what it is"], samples.map((s) => [
      el("span", {class: "mono"}, s.name),
      el("span", {class: "pill n"}, s.kind),
      s.present ? s.bytes : el("span", {class: "abs"}, "not on disk"),
      s.why,
    ])),
    el("div", {class: "row", style: "margin-top:16px"}, go, st));
}

/* ---- 02 CORPUS ----------------------------------------------------------------------------- */

screens.corpus = async (main) => {
  main.replaceChildren(head("Corpus", "The rules, segmented into addressable provisions."));
  const r = await currentReturn(main);
  if (!r) return;
  if (!r.corpus_digest) {
    main.appendChild(el("div", {class: "empty"},
      "This return names no rules corpus. Upload one on Intake and open a return that includes it."));
    return;
  }
  let p;
  try { p = await api("GET", `/v1/artefacts/${r.corpus_digest}/provisions`); }
  catch (e) { main.appendChild(errBox(e)); return; }

  main.appendChild(el("div", {class: "grid"},
    stat("Provisions", p.provisionsTotal, `matching "${p.onlyWith === null ? "everything" : p.onlyWith}"`),
    stat("Durable eIds", p.durableCount, `of ${p.provisionsTotal.toLocaleString()} — the instrument's own numbering`),
    stat("Units", p.unitsTotal, "comparable regions the two readers aligned on"),
    stat("Disputed", p.disputedTotal, "excluded from the addressable text")));

  const ag = p.agreement || {};
  const two = Object.entries(ag).map(([k, v]) => el("tr", {},
    el("td", {}, el("span", {class: "pill " + (k === "EXTERNAL" ? "ok" : "n")}, k)),
    el("td", {class: "num"}, (v[0] || 0).toLocaleString()),
    el("td", {class: "num"}, (v[1] || 0).toLocaleString()),
    el("td", {}, k === "EXTERNAL"
      ? "two INDEPENDENT readers agreed on these units"
      : "two of OUR OWN readers agreed. Weaker, and never averaged with the line above")));
  main.appendChild(sec("Corroboration — two vectors, never averaged",
    "A pinned PDF is read by two independent extractors; a plain-text upload is segmented by two " +
    "of ours. Presenting them as one number would grade a text upload as though a second party " +
    "had read it.",
    el("div", {class: "scroll"}, el("table", {},
      el("thead", {}, el("tr", {}, ["kind", "agreed", "of", "what it means"].map((c) => el("th", {}, c)))),
      el("tbody", {}, two)))));

  main.appendChild(sec(`Provisions — first ${Math.min(200, p.provisions.length)} of ${p.provisionsTotal.toLocaleString()}`,
    `Addressing: ${p.addressing}. A DURABLE eId cites the instrument's own numbering and survives ` +
    "re-extraction; a COORDINATE eId cites page-and-sentence and moves.",
    table(["eId", "kind", "page", "span", "text"], p.provisions.slice(0, 200).map((x) => [
      el("span", {class: "mono"}, x.eid),
      el("span", {class: "pill n"}, x.eidKind),
      x.page === null ? el("span", {class: "abs"}, "no page") : x.page,
      el("span", {class: "prov"}, `${x.span[0]}–${x.span[1]}`),
      el("span", {}, x.text.slice(0, 220)),
    ]))));
};

/* ---- 03 TEMPLATE --------------------------------------------------------------------------- */

screens.template = async (main) => {
  main.replaceChildren(head("Template", "The field surface, induced from the workbook itself."));
  const r = await currentReturn(main);
  if (!r) return;
  let s;
  try { s = await api("GET", `/v1/artefacts/${r.template_digest}/surface`); }
  catch (e) { main.appendChild(errBox(e)); return; }

  if (!s.inducible) {
    main.appendChild(el("div", {class: "err"},
      el("b", {}, s.refusal || "not_inducible"),
      el("p", {}, `${s.filename}: ${s.detail}`)));
    main.appendChild(callout("This is a refusal, not an empty template",
      "`absent != empty != zero`. A workbook we cannot read must not be reported as a workbook " +
      "with no fields in it — the surface here is UNKNOWN, and a zero would be a measurement " +
      "nobody made. Two of the nine pinned regulator workbooks are in exactly this state."));
    return;
  }

  main.appendChild(el("div", {class: "grid"},
    stat("Field surface", s.surfaceTotal, "every unlocked cell, labelled or not"),
    stat("Labelled", s.labelled, `of ${s.surfaceTotal.toLocaleString()} — rule: ${s.labelRule}`),
    stat("Attestations", s.attestations, "a human signs; we now ASK who"),
    stat("Unlabelled", s.surfaceTotal - s.labelled, "no label resolves — not a question")));

  const types = Object.entries(s.types || {});
  main.appendChild(sec("Declared types", "Read from the workbook's own number format and data " +
    "validation. A cell the workbook formats as nothing stays UNDECLARED — that is a fact about " +
    "the workbook, not about the value.",
    table(["type", "fields"], types.map(([k, v]) => [el("span", {class: "pill n"}, k), v]))));

  main.appendChild(sec(`Fields — first ${s.sample.length} of ${s.labelled.toLocaleString()} labelled`, null,
    table(["ref", "label", "type", "asks", "vocabulary"], s.sample.map((f) => [
      el("span", {class: "mono"}, f.ref), f.label,
      el("span", {class: "pill n"}, f.type),
      el("span", {class: "pill " + (f.asks === "attestation" ? "at" : "n")}, f.asks),
      f.vocabulary.length ? f.vocabulary.join(" · ") : el("span", {class: "abs"}, "none declared"),
    ]))));
};

/* ---- 04 MAP -------------------------------------------------------------------------------- */

screens.map = async (main) => {
  main.replaceChildren(head("Map", "The statute against the template — and the five gates."));
  const r = await currentReturn(main);
  if (!r) return;
  const busy = el("div", {class: "busy"}, "running the driver over the corpus and the template…");
  main.appendChild(busy);
  let m;
  try { m = await api("GET", `/v1/returns/${r.id}/map`); }
  catch (e) { busy.remove(); main.appendChild(errBox(e)); return; }
  busy.remove();

  main.appendChild(el("div", {class: "grid"},
    stat("Provisions", m.provisionsTotal, `${m.durableCount.toLocaleString()} with a durable eId`),
    stat("Proposals read", m.proposalsTotal, "LAYER 2, as DATA in a file"),
    stat("Admitted", m.admitted, `of ${m.proposalsTotal.toLocaleString()} — became nodes`),
    stat("Refused by a gate", m.refused, "never reachable from a traversal")));

  main.appendChild(callout("The model is never called from the verdict path",
    "It is not called at all — it is READ. `evidence.run()` takes `proposals: Path`, a file. The " +
    "model wrote that file; this run adjudicated it with G-QUOTE, G-FIELD, G-TYPE, G-VOCAB and " +
    "G-XREF, and only admitted proposals became nodes."));

  const c = m.coverage;
  main.appendChild(sec("Coverage, over a denominator that is not arguable", null,
    table(["measure", "count", "of"], [
      ["field surface", c.surfaceTotal, ""],
      [`labelled (${c.labelRule})`, c.labelledTotal, c.surfaceTotal],
      ["governed by a rule", c.fieldsGoverned, c.labelledTotal],
      ["read as a condition", c.fieldsRead, c.labelledTotal],
      ["ungoverned", c.fieldsUngoverned, c.labelledTotal],
      ["of which ATTESTATION", c.attestationFields, c.labelledTotal],
      ["provisions cited", c.provisionsCited, c.provisionsTotal],
      ["rules admitted", c.rulesAdmitted, ""],
    ].map((row) => [row[0], row[1], row[2] === "" ? el("span", {class: "abs"}, "—") : row[2].toLocaleString()]))));

  if (m.refusals.length) {
    main.appendChild(sec(`What a gate refused — ${m.refusals.length} of ${m.refused.toLocaleString()} shown`,
      "Retained ALONGSIDE the graph rather than inside it, so what was refused and why stays " +
      "answerable without ever being reachable from a traversal.",
      table(["eId", "planted", "gate", "reason", "detail"], m.refusals.flatMap((x) =>
        x.refusals.map((f) => [
          el("span", {class: "mono"}, x.eid),
          el("span", {class: "pill " + (x.planted ? "at" : "n")}, x.planted ? "planted" : "genuine"),
          el("span", {class: "pill no"}, f.gate),
          f.reason, el("span", {class: "prov"}, String(f.detail).slice(0, 160)),
        ])))));
  }
};

/* ---- 05 GRAPH ------------------------------------------------------------------------------ */

const KIND_FILL = {
  Provision: "#53617A", Field: "#B45D35", Rule: "#1B7F4B", Record: "#6D28D9", Entity: "#111827",
};

screens.graph = async (main) => {
  main.replaceChildren(head("Graph", "The evidence, linked. Four populations, never merged."));
  const r = await currentReturn(main);
  if (!r) return;
  const busy = el("div", {class: "busy"}, "building the graph…");
  main.appendChild(busy);
  let g;
  try { g = await api("GET", `/v1/returns/${r.id}/graph`, {query: {limit: 600}}); }
  catch (e) { busy.remove(); main.appendChild(errBox(e)); return; }
  busy.remove();

  main.appendChild(el("div", {class: "grid"},
    stat("Nodes", g.nodesTotal, Object.entries(g.counts).map(([k, v]) => `${k} ${v}`).join(" · ")),
    stat("Edges", g.edgesTotal, Object.entries(g.edgeCounts).map(([k, v]) => `${k} ${v}`).join(" · ")),
    stat("Isolated", g.isolatedTotal, "no edge touches them — a real count, not a rendering gap"),
    stat("Drawn", g.nodesShown, g.truncated ? "TRUNCATED — see the note below" : "all connected nodes")));

  main.appendChild(sec("The four populations, kept apart",
    "A statute's FME is a CONCEPT; a custodian row's FME is an IDENTITY. A graph that cannot tell " +
    "them apart is a graph nobody can audit.",
    table(["population", "node kind", "count", "what it is"], [
      ["corpus / statute", "Provision", g.populations.corpus, "a provision with an eId and an exact span"],
      ["template", "Field", g.populations.template, "a cell with the type the workbook declares"],
      ["binding", "Rule", g.populations.binding, "an ADMITTED proposal; a refused one is not here"],
      ["source document", "Record", g.populations.record, "one row of one document, OBSERVED"],
      ["entity", "Entity", g.populations.entity, "one identity resolved across records, DERIVED"],
    ].map((row) => [row[0], el("span", {class: "pill n"}, row[1]), row[2], row[3]]))));

  main.appendChild(sec("Adjacency", g.truncated
    ? `Drawn from the ${g.nodesShown.toLocaleString()} connected nodes this response carries, of ` +
      `${g.nodesTotal.toLocaleString()}. The cut takes nodes an edge actually touches first, so ` +
      "the picture never shows more edges than nodes."
    : "Every connected node in the graph.",
    drawGraph(g)));

  main.appendChild(sec("Nodes", null,
    table(["id", "kind", "label"], g.nodes.slice(0, 120).map((n) => [
      el("span", {class: "mono"}, n.id.slice(0, 40)),
      el("span", {class: "pill n"}, n.kind),
      n.label,
    ]))));
};

/* SVG IS PARSED INTO ITS NAMESPACE. `document.createElement("svg")` makes an HTMLUnknownElement:
   the tag lands in the HTML namespace, `cx`/`cy`/`r` are inert attributes, and the picture renders
   as text jammed at the origin — which is exactly what it did here once. Handing the markup to
   the HTML parser through innerHTML creates real SVG nodes in the right namespace. */
function drawGraph(g) {
  const W = 1100, colGap = 300, top = 60, rowGap = 15, R = 5;
  const order = ["Provision", "Rule", "Field", "Record", "Entity"];
  const cols = order.filter((k) => g.nodes.some((n) => n.kind === k));
  const byKind = {};
  cols.forEach((k, i) => { byKind[k] = {x: 130 + i * colGap, items: g.nodes.filter((n) => n.kind === k)}; });
  const pos = {};
  let maxRows = 1;
  for (const k of cols) {
    const items = byKind[k].items;
    maxRows = Math.max(maxRows, items.length);
    items.forEach((n, j) => { pos[n.id] = {x: byKind[k].x, y: top + j * rowGap}; });
  }
  const H = Math.max(240, top + maxRows * rowGap + 40);

  const lines = g.edges.map((e) => {
    const a = pos[e.src], b = pos[e.dst];
    if (!a || !b) return "";
    return `<line class="lnk" x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}" opacity="0.35"/>`;
  }).join("");
  const dots = g.nodes.map((n) => {
    const p = pos[n.id];
    if (!p) return "";
    return `<circle class="nd" cx="${p.x}" cy="${p.y}" r="${R}" fill="${KIND_FILL[n.kind] || "#4B5563"}">` +
           `<title>${esc(n.kind)} · ${esc(n.id)}\n${esc(n.label)}</title></circle>`;
  }).join("");
  const heads = cols.map((k) =>
    `<text class="lg" x="${byKind[k].x}" y="30" text-anchor="middle">${esc(k)} ` +
    `${byKind[k].items.length}</text>`).join("");

  const wrap = el("div", {class: "gwrap"});
  wrap.innerHTML = `<svg class="graph" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" ` +
    `role="img" aria-label="the evidence graph, ${g.nodesShown} nodes by kind">` +
    `${lines}${dots}${heads}</svg>`;
  return wrap;
}

/* ---- 06 RETURN (the fill) ------------------------------------------------------------------- */

screens.fill = async (main) => {
  main.replaceChildren(head("Return", "What we placed, and the span each value came from."));
  const r = await currentReturn(main, true);
  if (!r) return;
  if (r.refusal) {
    main.appendChild(el("div", {class: "err"}, el("b", {}, r.refusal.reason),
      el("p", {}, r.refusal.detail)));
    return;
  }
  const f = r.filled, c = f.counts;

  main.appendChild(el("div", {class: "grid"},
    stat("Evidenced", c.admitted, "a document and a span that re-reads byte-exact"),
    stat("Derived", c.derived, "no span supports it — placed, and NOT counted as checked"),
    stat("Asserted", c.asserted, "a named human answered — placed, and never evidenced"),
    stat("Placed in the return", c.filled_total, `of ${c.surface_total.toLocaleString()} cells`)));

  const seg = (n) => (c.surface_total ? (n / c.surface_total) * 100 : 0);
  main.appendChild(el("div", {class: "card k"},
    el("div", {class: "bar"},
      el("i", {class: "e", style: `width:${seg(c.admitted)}%`}),
      el("i", {class: "d", style: `width:${seg(c.derived)}%`}),
      el("i", {class: "a", style: `width:${seg(c.asserted)}%`}),
      el("i", {class: "r", style: `width:${seg(c.refused + c.attestations)}%`})),
    el("div", {class: "legend"},
      el("span", {}, el("i", {style: "background:var(--ok)"}), `evidenced ${c.admitted}`),
      el("span", {}, el("i", {style: "background:var(--derived)"}), `derived ${c.derived}`),
      el("span", {}, el("i", {style: "background:var(--accent)"}), `asserted ${c.asserted}`),
      el("span", {}, el("i", {style: "background:#E7E9ED"}),
        `refused ${c.refused.toLocaleString()} + awaiting a signature ${c.attestations}`))));

  main.appendChild(callout("Filling coverage on this data is small, and that is the honest number",
    `${c.admitted} evidenced of ${c.surface_total.toLocaleString()} cells. The mechanism is what ` +
    "is proven here, not the coverage: no fill-accuracy number exists and none can until real " +
    "filing-plus-source-pack pairs arrive. Do not read this figure as a product figure."));

  if (f.evidenced.length) {
    main.appendChild(sec("Evidenced — the value, and the span that proves it",
      "Every one of these re-read byte-exact at the offset it cites, in the document it names. " +
      "The trigger is mechanical; no score and no model.",
      el("div", {}, f.evidenced.map((p) => el("div", {class: "card k", style: "margin-bottom:12px"},
        el("div", {class: "row"},
          el("span", {class: "pill ok"}, "EVIDENCED"),
          el("span", {class: "mono"}, p.ref),
          el("b", {}, p.label)),
        el("p", {style: "margin:8px 0 4px;font-size:20px"}, el("span", {class: "fig"}, p.value)),
        el("div", {class: "prov"},
          `${p.document} · span ${p.span[0]}–${p.span[1]}` +
          (p.page === null ? " · no page recorded" : ` · page ${p.page}`)),
        el("blockquote", {}, p.context),
        el("div", {class: "row tight", style: "margin-top:10px"},
          p.conditions.map((cd) => el("span", {class: "pill " + (cd.holds ? "ok" : "no")},
            (cd.holds ? "✓ " : "✗ ") + cd.name))))))));
  }

  if (f.derived.length) {
    main.appendChild(sec("Derived — placed, and NOT counted as checked", null,
      table(["ref", "label", "value", "basis"], f.derived.map((d) => [
        el("span", {class: "mono"}, d.ref), d.label,
        el("span", {class: "fig"}, d.value), el("span", {class: "prov"}, d.basis)]))));
  }

  if (f.asserted.length) {
    main.appendChild(sec("Asserted — a named human answered a question", null,
      table(["ref", "value", "answered by", "at", "the question it answered"], f.asserted.map((a) => [
        el("span", {class: "mono"}, a.ref), el("span", {class: "fig"}, a.value),
        a.answered_by, el("span", {class: "prov"}, a.answered_at),
        el("span", {class: "pill at"}, a.reason)]))));
  }

  main.appendChild(sec("Where the binding came from",
    "A5 adjudicates a binding and requires one as an INPUT. This is what A1c matched, column to " +
    "field, on declared evidence with EM-derived weights.",
    f.schemaMatchPairs.length
      ? table(["source column", "template field", "weight"], f.schemaMatchPairs.map((p) =>
          [p.column, el("span", {class: "mono"}, p.field), p.weight]))
      : el("div", {class: "empty"}, "No column matched a field in this run.")));
};

/* ---- 07 QUESTIONS — the heart ---------------------------------------------------------------- */

const SHAPE_NOTE = {
  value: "type the value. We do not coerce: a value that still does not parse under the type the " +
         "form declares is still refused.",
  one_of: "choose one. We supplied these options, so a value outside them is an answer to a " +
          "different question.",
  document: "name the document. This does NOT write your choice into the cell — we go and read " +
            "that document, and a value we still cannot locate is still refused.",
  signatory: "a natural person accepts liability for this statement. No system may forge one.",
};

screens.questions = async (main) => {
  main.replaceChildren(head("Questions",
    "What nothing supports, what two of your documents disagree about, and what needs your " +
    "judgement — put as questions you can answer."));
  const r = await currentReturn(main);
  if (!r) return;

  const who = el("input", {type: "text", placeholder: "your name — an assertion needs an author",
                           value: sessionName()});
  who.addEventListener("change", () => { S.who = who.value; });
  const filter = el("select", {});
  const body = el("div", {});
  main.appendChild(sec("Answering as", "An answer becomes a value labelled `resolved_by: human`, " +
    "carrying who you are, the instant, and the question you answered. An assertion whose author " +
    "is unknown is refused — there is no human in it.",
    el("div", {class: "grid"},
      el("div", {}, el("label", {class: "f"}, el("span", {class: "lbl"}, "Name"), who)),
      el("div", {}, el("label", {class: "f"}, el("span", {class: "lbl"}, "Show only"), filter)))));
  main.appendChild(body);

  let q = null;
  async function load(reason) {
    body.replaceChildren(el("div", {class: "busy"}, "deriving the questions…"));
    try { q = await api("GET", `/v1/returns/${r.id}/questions`, {query: reason ? {reason, limit: 60} : {limit: 60}}); }
    catch (e) { body.replaceChildren(errBox(e)); return; }
    render();
  }

  function render() {
    const c = q.counts;
    const tiles = {
      asked: stat("Questions we can put", c.questions, "every one has an answer you can give"),
      not: stat("Not questions", c.not_asked, "counted, and never presented as ones"),
      done: stat("Answered so far", q.answeredSoFar, "each one became a value"),
      shown: stat("Showing", q.questionsTotal, q.truncated ? "TRUNCATED by the limit" : "all of them"),
    };
    // THE TILES MOVE WHEN AN ANSWER LANDS. They did not, and the card under them said "127
    // question(s) left" while the tile above still read 128 — two numbers about the same run,
    // both on screen, disagreeing. The new figure is taken from the ANSWER RESPONSE, which is the
    // server re-deriving after the write, never a decrement this screen guessed at.
    const bump = (out) => {
      tiles.asked.querySelector("b").replaceChildren(fig(out.questionsRemaining));
      tiles.done.querySelector("b").replaceChildren(fig((q.answeredSoFar += 1)));
      const left = Number(tiles.shown.querySelector("b").textContent.replace(/[^0-9]/g, "")) - 1;
      tiles.shown.querySelector("b").replaceChildren(fig(Math.max(0, left)));
    };
    const kids = [el("div", {class: "grid"}, tiles.asked, tiles.not, tiles.done, tiles.shown)];

    kids.push(callout("The number that must not be headlined",
      `This return refuses ${(c.questions + c.not_asked).toLocaleString()} cells in total. ` +
      `Only ${c.questions.toLocaleString()} of them are questions. Presenting the total as ` +
      `"needs your judgement" would overstate the answerable work by ` +
      `${c.not_asked.toLocaleString()} — the panel below says which reasons those are and why ` +
      "each one is not a question."));

    const qs = el("div", {class: "qlist"});
    for (const item of q.questions) qs.appendChild(questionCard(r, item, who, bump));
    kids.push(qs.children.length ? qs : el("div", {class: "empty"},
      "No question of this kind is outstanding."));

    if (q.notAsked.length) {
      kids.push(el("div", {class: "notask"},
        el("h3", {}, "Refusals that are NOT questions"),
        el("ul", {}, q.notAsked.map((n) => el("li", {},
          el("b", {}, n.count.toLocaleString()), " ", el("span", {class: "pill n"}, n.reason),
          " — ", n.why)))));
    }
    body.replaceChildren(...kids);
  }

  await load("");
  const reasons = Object.keys(q ? q.counts : {}).filter((k) => k.startsWith("ask_"))
    .map((k) => k.slice(4));
  filter.appendChild(el("option", {value: ""}, "every question"));
  for (const rs of reasons) filter.appendChild(el("option", {value: rs}, rs));
  filter.addEventListener("change", () => load(filter.value));
};

function sessionName() { return S.who || ""; }

function questionCard(ret, item, whoInput, bump) {
  const msg = el("div", {class: "msg"});
  let input;
  const opts = el("div", {class: "opts"});
  const name = "q_" + item.id;

  if (item.shape === "one_of" || item.shape === "document") {
    if (!item.options.length) {
      opts.appendChild(el("div", {class: "abs"},
        "this system offered no options for this question, so there is nothing to choose"));
    }
    for (const o of item.options) {
      const radio = el("input", {type: "radio", name});
      radio.value = o.value;
      opts.appendChild(el("label", {class: "opt"}, radio,
        el("span", {}, o.value), el("em", {}, o.note)));
    }
    input = () => {
      const hit = opts.querySelector("input:checked");
      return hit ? hit.value : "";
    };
  } else {
    const box = el("input", {type: "text",
      placeholder: item.shape === "signatory" ? "what you are affirming, e.g. Yes" : "the value"});
    opts.appendChild(el("label", {class: "f"}, box));
    input = () => box.value;
  }

  const send = el("button", {class: "pri"}, item.shape === "signatory" ? "Sign it" : "Answer");
  const card = el("div", {class: "q"},
    el("div", {class: "qh"},
      el("div", {},
        el("div", {class: "ref"}, item.ref),
        el("div", {class: "lab"}, item.label || el("span", {class: "abs"}, "this cell has no label"))),
      el("span", {class: "pill " + (item.shape === "signatory" ? "at" : "no")}, item.reason)),
    el("p", {class: "ask"}, item.question),
    el("p", {class: "why"}, item.detail),
    item.certifies ? el("blockquote", {}, "Certifying: " + item.certifies) : null,
    el("p", {class: "res"}, SHAPE_NOTE[item.shape] || item.resolves),
    opts,
    el("div", {class: "ans"}, el("div", {}), el("div", {}), send),
    msg);

  send.addEventListener("click", async () => {
    msg.className = "msg";
    const value = String(input() || "").trim();
    const by = String(whoInput.value || "").trim();
    if (!value) { msg.className = "msg bad"; msg.textContent = "an empty answer is not an answer"; return; }
    if (!by) { msg.className = "msg bad"; msg.textContent = "put your name in the field above — an assertion needs an author"; return; }
    send.disabled = true; msg.textContent = "recording…";
    try {
      const out = await api("POST", `/v1/returns/${ret.id}/answers`, {body: {answers: [{
        questionId: item.id, value, answeredBy: by, answeredAt: new Date().toISOString(),
      }]}});
      card.classList.add("done");
      msg.className = "msg good";
      if (bump) bump(out);
      const a = out.asserted[0];
      if (a) {
        msg.textContent = `recorded — ${a.ref} now carries "${a.value}", resolved_by ` +
          `${a.resolved_by}, by ${a.answered_by}. Evidenced is still ${out.counts.admitted}: ` +
          `an answer is placed, never counted as checked. ${out.questionsRemaining} question(s) left.`;
      } else {
        msg.textContent = `recorded as a re-read of ${out.redirects[0] ? out.redirects[0].document : "the named document"} — ` +
          "the value is located there or it stays refused. " +
          `${out.questionsRemaining} question(s) left.`;
      }
      send.textContent = "answered";
    } catch (e) {
      msg.className = "msg bad";
      msg.textContent = `${(e.body && e.body.error) || "refused"}: ${e.message}`;
      send.disabled = false;
    }
  });
  return card;
}

/* ---- 08 CERTIFICATE ------------------------------------------------------------------------- */

screens.certificate = async (main) => {
  main.replaceChildren(head("Certificate", "The roots, the lanes, and what this does NOT say."));
  const r = await currentReturn(main);
  if (!r) return;
  let out;
  try { out = await api("GET", `/v1/returns/${r.id}/certificate`); }
  catch (e) { main.appendChild(errBox(e)); return; }
  const c = out.certificate, env = out.envelope;

  main.appendChild(el("div", {class: "grid"},
    stat("Evidenced", c.lanes.evidenced, "a document and a span"),
    stat("Derived", c.lanes.derived, "no span supports it"),
    stat("Asserted", c.lanes.asserted, "a named human answered"),
    stat("Awaiting a signature", c.lanes.awaitingSignature, "nobody has signed these yet")));

  main.appendChild(sec("The inputs this certificate covers",
    "The merkle root is over THIS run's inputs, not over the registry. A run that names three " +
    "artefacts produces the same root next year on a registry that has grown by thousands.",
    el("dl", {class: "kv"},
      el("dt", {}, "return"), el("dd", {}, c.returnId),
      el("dt", {}, "opened at"), el("dd", {}, c.openedAt),
      el("dt", {}, "merkle root"), el("dd", {}, c.merkleRoot),
      el("dt", {}, "template sha256"), el("dd", {}, c.templateSha256)),
    el("div", {style: "margin-top:16px"},
      table(["digest", "kind", "filename", "bytes"], c.inputs.map((a) => [
        el("span", {class: "digest"}, a.digest.slice(0, 24) + "…"),
        el("span", {class: "pill n"}, a.kind), a.filename, a.size])))));

  if (c.asserted.length) {
    main.appendChild(sec("Answers this certificate carries",
      "Each one is a value a named person supplied. None of them is counted as evidenced.",
      table(["ref", "value", "by", "at", "answering"], c.asserted.map((a) => [
        el("span", {class: "mono"}, a.ref), el("span", {class: "fig"}, a.value),
        a.answered_by, el("span", {class: "prov"}, a.answered_at),
        el("span", {class: "pill at"}, a.reason)]))));
  }

  main.appendChild(sec("Signature",
    "Deterministic — RFC 8032 derives the nonce from the key and the message, so the same return " +
    "signs to the same 64 bytes and the signature is part of the byte-identity claim rather than " +
    "an exception to it.",
    el("dl", {class: "kv"},
      el("dt", {}, "payload type"), el("dd", {}, env.payloadType),
      el("dt", {}, "key id"), el("dd", {}, env.keyid),
      el("dt", {}, "payload sha256"), el("dd", {}, env.payloadSha256),
      el("dt", {}, "signature"), el("dd", {class: "sig"}, env.sig))));

  main.appendChild(sec("What this certificate does NOT say",
    "Rendered into the artefact itself, not into the screen that shows it, so a certificate " +
    "detached from this application still carries its own limits.",
    el("ul", {}, c.doesNotSay.map((x) => el("li", {style: "margin-top:8px"}, x)))));

  if (c.questionsOutstanding) {
    main.appendChild(callout("Questions are still outstanding",
      `${c.questionsOutstanding.toLocaleString()} question(s) have not been answered. This ` +
      "certificate covers the return as it stands, and answering more will change it."));
  }
};

/* ---------------------------------------------------------------- shell -------------------- */

async function currentReturn(main, full) {
  if (!S.returnId) {
    main.appendChild(el("div", {class: "empty"},
      "No return is open. Go to Intake, upload a template and an evidence export, and open one."));
    return null;
  }
  if (full || !S.ret || S.ret.id !== S.returnId) {
    const busy = el("div", {class: "busy"}, "deriving this return…");
    main.appendChild(busy);
    try { S.ret = await api("GET", `/v1/returns/${S.returnId}`); }
    catch (e) { busy.remove(); main.appendChild(errBox(e)); return null; }
    busy.remove();
  }
  return S.ret;
}

function renderRail() {
  const nav = document.getElementById("nav");
  const here = (location.hash || "#/intake").slice(2);
  nav.replaceChildren(...PAGES.map(([id, n, title, note]) => {
    const a = el("a", {href: "#/" + id, class: (!S.returnId && id !== "intake") ? "off" : ""},
      el("span", {class: "n"}, n),
      el("span", {}, title, el("em", {}, note)));
    if (id === here) a.setAttribute("aria-current", "page");
    return a;
  }));
  const box = document.getElementById("retbox");
  box.replaceChildren(
    el("b", {}, "Return"),
    el("div", {}, S.returnId || "none open"));
}

async function route() {
  const main = document.getElementById("main");
  const id = (location.hash || "#/intake").slice(2) || "intake";
  const fn = screens[id] || screens.intake;
  renderRail();
  main.replaceChildren(el("div", {class: "busy"}, "…"));
  try { await fn(main); }
  catch (e) {
    main.replaceChildren(head("Something failed on this screen",
      "The error is shown as the API returned it. Nothing is defaulted."), errBox(e));
  }
}

/* `hashchange` is ASYNC: a handler that assigns `location.hash` and then reads the DOM in the
   same tick measures the screen it was already on. Routing is driven by the EVENT and by the
   initial load, never by the assignment. */
window.addEventListener("hashchange", route);
document.getElementById("tok").addEventListener("input", (e) => {
  S.token = e.target.value.trim();
  const p = document.getElementById("tokstate");
  p.className = S.token ? "set" : "";
  p.textContent = S.token
    ? "held for this page only — a reload clears it"
    : "Held in memory only — never written to disk, never in a URL.";
});

(async () => {
  try { S.caps = await api("GET", "/v1/capabilities"); } catch (e) { /* the screen reports it */ }
  try {
    const rs = await api("GET", "/v1/returns");
    if (rs.length) { S.returnId = rs[rs.length - 1].id; }
  } catch (e) { /* no returns yet */ }
  route();
})();
