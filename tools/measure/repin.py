"""N1 — the re-pinning blast radius, measured by PERTURBING a copy rather than reasoning about it.

`docs/PLAN.md §8 F4` says re-extracting the pinned instrument with layout preservation recovers
durable `reg_8__subreg_1` eIds and deletes most of the segmenter's cost. It also says the
re-extraction **changes the instrument's bytes**, and every offset, span and `text_hash` anchored
to them moves with it. This measures how much.

**Two perturbations, because they break different things.**

    SHIFT       the same text with a prefix. Every SPAN moves; the unit KEYS (`p0143.s0008`)
                do not, because they are page/sentence coordinates rather than offsets.
    RESEGMENT   the unit boundaries change, as a real re-extraction's would. The KEYS move too,
                and a rule that cited one is citing nothing.

The second is what a real re-pin does, and it is why the eId kind matters: `COORDINATE` addressing
survives neither. Nothing is inferred here — a copy of the pinned instrument is perturbed on disk
and the shipped readers are run against it.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "corpus" / "instruments" / "statute-fm-regulations-2025.text.json"


def _load() -> dict:
    return json.loads(SRC.read_text(encoding="utf-8"))


def _repin(doc: dict) -> dict:
    """Recompute the instrument's self-digest, which is what a REAL re-pin must do.

    The first run of this measurement discovered the corpus is self-verifying: `deserialise`
    recomputes the digest over the units, text and manifests and REFUSES a mismatch with *"every
    span recorded against this instrument points somewhere else."* That refusal is itself part of
    the answer — **a re-pin cannot happen by accident**, only as a deliberate act that recomputes
    the digest. So this does deliberately what a re-extraction would do.
    """
    sys.path.insert(0, str(REPO / "src"))
    from cdfc.canon import digest

    doc = json.loads(json.dumps(doc))
    doc["sha256"] = digest({
        "instrument_id": doc["instrument_id"],
        "transformations": [list(t) for t in doc["transformations"]],
        "refused_transformations": [list(t) for t in doc["refused_transformations"]],
        "units": [[u["key"], u["page"], u["corroboration"], list(u["parties"]),
                   u["external_party"], *u["span"]] for u in doc["units"]],
        "text": doc["text"],
        "manifests": [[m["extractor"], m["version"], m["external"], m["sha256"], m["n_units"],
                       m["n_disputed"], m["n_blind"], list(m["exclusion_mechanisms"])]
                      for m in doc["manifests"]],
    })
    return doc


def _write(doc: dict, root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    p = root / "statute-fm-regulations-2025.text.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    for extra in ("MANIFEST.json",):
        s = SRC.parent / extra
        if s.is_file():
            shutil.copy(s, root / extra)
    return p


def shift(doc: dict, n: int = 17) -> dict:
    """Prepend `n` characters. Spans move by n; keys are untouched."""
    out = json.loads(json.dumps(doc))
    out["text"] = (" " * n) + out["text"]
    for u in out["units"]:
        u["span"] = [u["span"][0] + n, u["span"][1] + n]
    for d in out.get("disputed", []):
        if isinstance(d, dict) and "span" in d:
            d["span"] = [d["span"][0] + n, d["span"][1] + n]
    return out


def resegment(doc: dict, drop_every: int = 7) -> dict:
    """Merge every `drop_every`-th unit into its predecessor — a coarser segmentation.

    This is what a re-extraction does incidentally: the same text, different unit boundaries. The
    keys that survive still exist, but the population they index is different, so a citation to a
    dropped key resolves to nothing.
    """
    out = json.loads(json.dumps(doc))
    units = out["units"]
    kept: list[dict] = []
    for i, u in enumerate(units):
        if i % drop_every == 0 or not kept:
            kept.append(u)
        else:
            kept[-1]["span"] = [kept[-1]["span"][0], u["span"][1]]
    out["units"] = kept
    return out


def _probe(root: Path, label: str, proposals: Path) -> dict:
    """Run the SHIPPED readers against the perturbed corpus and count what still resolves."""
    sys.path.insert(0, str(REPO / "src"))
    from cdfc.evidence.gates import adjudicate
    from cdfc.evidence.proposal import load
    from cdfc.evidence.provisions import from_instrument
    from cdfc.qualify.instruments import InstrumentStore

    it = InstrumentStore(root).get("statute-fm-regulations-2025")
    provs = from_instrument(it)
    props = load(proposals)
    known = provs.by_eid()
    resolved = sum(1 for p in props.proposals if p.eid in known)
    # a quote is only meaningful where its provision still exists
    verbatim = 0
    for p in props.proposals:
        pr = known.get(p.eid)
        if pr and " ".join(p.quote.split()) in " ".join(pr.text.split()):
            verbatim += 1
    from cdfc.evidence.fields import from_template

    fme = REPO / "fixtures/prescribed/Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
    adj = adjudicate(props, provs, from_template(fme))
    return {
        "label": label, "units": len(provs), "characters": len(it.text),
        "eids_resolving": resolved, "quotes_verbatim": verbatim,
        "proposals": len(props), "admitted": len(adj.admitted),
    }


def main() -> int:
    doc = _load()
    proposals = REPO / "fixtures/evidence/fme-proposals.json"
    rows = []
    with tempfile.TemporaryDirectory() as td:
        for label, mutate in (("BASELINE  (pinned)", lambda d: d),
                              ("SHIFT     (+17 chars)", shift),
                              ("RESEGMENT (coarser units)", resegment)):
            root = Path(td) / label.split()[0].lower()
            _write(_repin(mutate(doc)), root)
            rows.append(_probe(root, label, proposals))

    base = rows[0]
    print("=== N1 — the re-pinning blast radius, MEASURED on a perturbed copy ===\n")
    print(f"{'perturbation':28} {'units':>6} {'chars':>8} {'eIds resolve':>13} "
          f"{'quotes exact':>13} {'admitted':>9}")
    for r in rows:
        print(f"{r['label']:28} {r['units']:6} {r['characters']:8} "
              f"{r['eids_resolving']:6} of {r['proposals']:<4} "
              f"{r['quotes_verbatim']:6} of {r['proposals']:<4} "
              f"{r['admitted']:4} of {r['proposals']}")

    print("\n--- what each perturbation costs -------------------------------------------")
    for r in rows[1:]:
        d_e = base["eids_resolving"] - r["eids_resolving"]
        d_a = base["admitted"] - r["admitted"]
        print(f"  {r['label']:28} eIds lost {d_e} of {base['proposals']}   "
              f"admissions lost {d_a} of {base['admitted']}")

    # NEGATIVE CONTROL. If nothing ever moves, this measures nothing.
    moved = any(r["units"] != base["units"] or r["characters"] != base["characters"]
                for r in rows[1:])
    print(f"\n  negative control — a perturbation actually changed the corpus: "
          f"{'PASS' if moved else 'FAIL, the mutations are inert'}")
    return 0 if moved else 1


if __name__ == "__main__":
    raise SystemExit(main())
