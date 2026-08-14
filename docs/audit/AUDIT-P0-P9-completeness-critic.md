# What the audit missed

## Coverage gaps (against the actual file tree)

The 11 lanes were organised by **build phase**, so files that belong to no phase were never anyone's job:

- `src/cdfc/measure/absence.py` — the mechanism behind one of the five standards. **Nobody's lane.**
- `ci/no-bare-absence.sh` — the gate enforcing it. Named twice ("unregistered"; "vocabulary is not right") but **never run by any auditor**.
- `src/cdfc/facts/` (807 LOC: `view.py` 350, `build.py` 168, `fact_table.py` 140, `anchor.py`) — only `units.py` touched, incidentally.
- `src/cdfc/attest/`, `src/cdfc/selfcheck/` — 1-line stubs, no phase owns them.
- Four modules referenced by **zero** test files: `measure/p6_kill.py`, `harvest_classes/_bounds.py`, `baselines/b0_template.py`, `corpus/_derive_calc.py`.

## The standard nobody tested

Of the five standards in the brief, four were attacked hard. **"An absence claim ships with a positive control"** was verified on exactly *one instance* (P3's cached-value claim) by the measurements auditor. Nobody asked whether the enforcement covers the population. It doesn't.

---

# FINDING 1 [major] — `ci/no-bare-absence.sh` matches zero lines in the repository it scans; its absence half is a gate that cannot fail, and both its negative controls are built from the gate's own magic phrase

The product's differentiator is reporting what it did not check — i.e. absence claims. `absence.py`'s docstring calls `assert_absent` "the ONLY sanctioned way to record an absence anywhere in this project," and says the gate "reads numbers, not prose... it does not grep for the words 'positive control', because any author who has read a lexical gate satisfies it in four words."

The gate greps for four literal phrases:

```python
ABSENCE = re.compile(r"(does not occur|zero hits|not present in|no occurrences)", re.I)
ROOTS = ["src", "tests", "docs"]
```

**Measured.** It scans 291 files and its vocabulary matches **0 lines**:

```
/Users/abishaikc/Gift/.venv/bin/python - <<'EOF'
import pathlib, re
ABSENCE = re.compile(r"(does not occur|zero hits|not present in|no occurrences)", re.I)
tot=hits=0
for root in ["src","tests","docs"]:
    for p in pathlib.Path(root).rglob("*"):
        if not p.is_file() or p.suffix not in {".py",".md",".sh",".yaml",".yml"}: continue
        tot+=1
        hits+=sum(1 for l in p.read_text(errors="replace").splitlines() if ABSENCE.search(l))
print(f"files {tot}  matched lines {hits}")   # -> files 291  matched lines 0
EOF
```

`bash ci/no-bare-absence.sh` prints `no-bare-absence: OK` having adjudicated nothing. Meanwhile 127 absence-shaped claims exist in those same roots, **0** carry a `ledger:` citation, and 45 are load-bearing ones the product rests on — `settled_fraction.py:1` "There is no bare fraction anywhere in this system", `functions.py:12` "There is no float anywhere in this build", `labels.py:54` "There is no green tick anywhere in this product".

**Two-arm demonstration** (run in a `git archive HEAD` export; repo untouched). Arm A appends three absence sentences *lifted verbatim from this repo's own source*; Arm B appends the same claim rephrased with one magic phrase:

```
ARM A: "There is no float anywhere in this build. There is no bare fraction anywhere in this system.
        We scanned every module and found no model call and no network access."   -> rc=0  GREEN
ARM B: "The float type does not occur in this build."                             -> rc=1  RED
```

The vocabulary *is* the gate.

**The negative controls cannot see this.** `NC-A01`'s two guards are `test_nc__A01_absence_must_resolve_a_live_ledger_row` and — verbatim — `test_nc__A01b_the_gate_is_not_merely_grepping_for_a_phrase`. A01b builds its probe as `phrase = "does not " + "occur"`, i.e. it feeds the gate the gate's own vocabulary. So it proves only that the string "positive control" doesn't rescue a *matched* line. Reducing the gate to one phrase and one root leaves both guards green:

```bash
# in a HEAD export
sed -i '' 's/r"(does not occur|zero hits|not present in|no occurrences)"/r"(does not occur)"/; s/ROOTS = \["src", "tests", "docs"\]/ROOTS = ["docs"]/' ci/no-bare-absence.sh
CDFC_PY=/Users/abishaikc/Gift/.venv/bin/python .venv/bin/python -m pytest tests/negative/test_nc_absence.py -q
# -> ..  2 passed
```

Both guards pass under a gate that scans one directory for one phrase. The guard named "is not merely grepping for a phrase" is satisfied *by* the grep.

**Scale of the real enforcement:** `assert_absent` has exactly **one** production caller repo-wide (`tools/measure/p3_reproduction.py:91`). `reports/validation-ledger.jsonl` holds 2 distinct absence rows, one of which is the injector fixture `injected_empty_control`. One real absence claim in the project is sanctioned; 127 are not.

**Unrecorded.** `docs/ABSENCE-SCOPE.md` exists but governs a *denominator* (which vendor pages to count), not the trigger vocabulary. No entry in `docs/GATE-CHANGES.md`, `docs/CATALOGUE-CORRECTIONS.md`, `docs/decisions/` mentions it. The gate also has **no row in `ci/GATES.md`** despite running in `make greps` (Makefile:23), and `NC-A01` binds no registry row in `tools/gate_liveness.py` — so it sits outside the published `74 of 74 live gates OBSERVED RED` entirely.

---

# FINDING 2 [minor] — `nc_sweep.py`'s `assertion_text` falls back to a **file-keyed** lookup, so a guard is published carrying its sibling's failure message — the exact defect the comment three lines above claims was fixed

`tools/nc_sweep.py:106-108` states redness is mapped by node id because file-keying "silently inflated the flipped set." Correct for redness. But the text fallback at :129-131 is file-keyed with first-match-wins:

```python
if red and not text:
    f = nid.split("::")[0]
    text = next((v for k, v in tb.items() if k.endswith(f) or f.endswith(k)), "reported failed")
```

pytest's `FAILED` line carries no inline message here, so this path always runs. **Demonstrated:** under the bound injector the two NC-A01 guards fail with *different* messages —

```
A01  -> "an absence citing a ledger row with a zero control was accepted"
A01b -> "the gate accepted the words 'positive control' with no resolvable citation"
```

but `reports/negative-control-sweep.json` publishes A01b's message for **both**. Reproduce:

```bash
cd /Users/abishaikc/Gift && PYTHONPATH=src CDFC_PY=.venv/bin/python .venv/bin/python - <<'PY'
import sys,subprocess,os; sys.path.insert(0,'.')
from injectors import DefeatAbsenceGate, inject
with inject(DefeatAbsenceGate()):
    o=subprocess.run([os.environ["CDFC_PY"],"-m","pytest","tests/negative/test_nc_absence.py","-q","-rf"],capture_output=True,text=True,env={**os.environ})
print("\n".join(l for l in (o.stdout+o.stderr).splitlines() if l.startswith("E ")))
PY
```

Across the committed report: 40 of 160 flipped guards share an identical `assertion_text` with a sibling in the same file (11 files), plus the 13 carrying the constant `"reported failed"` the completeness critic already found. `test_sweep__records_the_failing_assertion_text` only asserts non-emptiness, so it passes on a sibling's text as readily as on a constant.

---

# An auditor claim that could not have been verified as stated

**negative-control-system:** *"Failures are keyed by node id, not file path, so one red test in a file does not inflate its siblings. That is the right construction."* True of the pass/fail mapping, but the auditor generalised it to the artifact's construction. The evidence field — which the same auditor cited approvingly when reading recorded assertion texts across families — is file-keyed. Finding 2 is inside the mechanism they certified.

**p0-p2-foundation** listed `ci/no-bare-absence.sh` as executed by `make greps` and having "guard tests," and treated that as sufficient; it never ran the gate. The gate greps 291 files and adjudicates none.

---

**Tree state:** all experiments ran in a `git archive HEAD` export under the scratchpad, now deleted. I edited no file in `/Users/abishaikc/Gift`; `git diff` is empty for every file I read. `git status` shows `M src/cdfc/qualify/g4_ffr.py`, a concurrent session's in-flight injection (the tree also showed `M src/cdfc/schema/styles_mask.py` at my session start) — not mine, and deliberately not reverted.