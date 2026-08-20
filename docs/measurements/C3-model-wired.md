# C3 — LAYER 2 wired: the corpus is mapped by a model, and the gates decide

*Run 20 Aug 2026. `deepseek-v4-flash` via `cdfc.model.transport.deepseek`. Reproduce with
`DEEPSEEK_API_KEY=… make proposals` then `make demo-evidence`.*

## What was wrong

`cdfc.model` was **orphaned** — nothing under `src/` imported it, only `tests/contract/`. The
proposals `cdfc evidence` read were **hand-written**: `fixtures/evidence/fme-proposals.json`, 11
rows. The sentence *"maps them directly against statutory rules"* was true of a fixture.

**The cause was structural.** `BindingProposal` carried `provision_eid`, `field_ref`, `quote`,
`reason` — and no `kind`. `evidence.proposal.Proposal` **requires** a `kind` from the closed
`RuleKind` vocabulary, and feeds `terms` to G-VOCAB and `refers_to` to G-XREF. LAYER 2 emitted
something LAYER 3 could not load. The shape was the defect, so the shape was fixed.

## The result

| | hand-written fixture | model-generated |
|---|---|---|
| proposals | 11 | **26** |
| admitted by the five gates | 6 | **16** |
| Rule nodes in the graph | 6 | **16** |
| graph edges | 11 | **33** |
| fields governed | 5 of 132 | **13 of 132** |

Nothing on the verdict path called a provider. The model wrote a FILE; `evidence.run(proposals=
Path)` read it; the gates adjudicated. That is the seam the architecture already had.

## Two systematic errors, both fixed at the INPUT

**1. The reasoning budget.** `deepseek-v4-flash` is a reasoning model. On a 1,539-token prompt it
spent **4,060 of 4,096** completion tokens reasoning, emitted 114 characters, and stopped with
`finish_reason: "length"` mid-JSON-string. All three batches died reporting *"the model's reply is
not JSON"* — which names the symptom and hides the cause. The transport now floors `max_tokens` at
32,768 and **refuses `finish_reason='length'` outright**: a truncated reply is a fault, not a short
answer, and parsing it would silently drop every proposal after the cut.

**2. The delimiter we chose.** Offering `[1. Introduction!D12] Legal structure` produced replies
whose `field_ref` was `"[1. Introduction!D12]"` — brackets included — on **16 of 20** raw blocks.
`parse()` refused every one correctly. The fix was the offer format, not a strip: one JSON object
per line, so the ref is a quoted string and comes back a quoted string. **Malformed 16 of 20 → 0 of
26.** Stripping brackets on the way in would have repaired this delimiter and silently mangled a
field reference that legitimately contains one.

## What this does NOT establish

* **No extraction QUALITY is measured.** 16 proposals were admitted; nobody has checked whether the
  bindings are RIGHT. The gates prove a proposal is well-formed, cites a real provision verbatim,
  names a real field, and respects its declared type and vocabulary — not that it is correct.
* **`durably addressable 0 of 1218`.** Every provision is addressed `p0146.s0013` — page and
  sentence. `qualify/provisions.py` produces durable division eIds and `evidence/provisions.py`
  does not use them. This is C2 and it is the sharpest statement of it: the statutory mapping
  currently cites the incidental axis N6 warned about.
* **Nothing bounds RECALL.** 532 `shall`-bearing provisions were offered; we measure what was
  proposed, never what nobody proposed.
