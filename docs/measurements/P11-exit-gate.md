# P11 exit gate — **G-REPRO**, evaluated point by point

**Evaluable by someone who did not do the work.** Each of `plan/05` §P11's ten criteria is restated,
then answered with the command that produces the answer. Where a criterion is **not met**, it says
so and names what is missing.

**Result: 9 of 10 met, 1 NOT MET — and the one that is not met is criterion 1, the headline.**

---

### 1. A third party clones the repo and runs `cdfc verify` on a **different machine** and gets a byte-identical re-derivation. `E2E-VERIFY` green on the second runner image

**NOT MET. No second machine or runner image is available in this environment, and the claim is not
inferred from what is.**

What *is* verified, and it is not nothing:

| environment | result | catches |
|---|---|---|
| four environment variations on one machine — `TZ`, `PYTHONHASHSEED`, `LC_ALL`, working directory | **0 bytes differing of 1,568,185** | clock zone, hash seed, locale ordering, path resolution |
| a **fresh clone** at the same commit | **green**, and it has caught four real defects across P9–P11 | dependence on the working tree, on uncommitted files, on gitignored output, on absolute paths |
| a **second machine / runner image** | **NOT RUN** | interpreter build, library minor versions, filesystem ordering, CPU word size |

`E2E-VERIFY` itself is green: the payload re-derives byte for byte and the stored signature is
valid, with 10 manifest pins checked. **What is unproven is the third row**, and the difference
between it and the first two is exactly the kind of gap this project exists to name rather than
absorb. `docs/measurements/P11-byte-identity.md` and `docs/NON-DETERMINISM.md` both carry the
boundary on their own faces.

```bash
make byte-identity          # exits non-zero if anything differs
python -m pytest tests/e2e/test_e2e__verify.py -q
```

---

### 2. `E2E-TAMPER` produces a **named diff**, not a boolean

**MET.** Flip one byte of the filing and re-verify:

```
filing blob @ byte 0
      expected  'sha256:aeedbfe18c8030612e6d1b3a4f8e5c9d0a1b2c3d4e5f6…'
      actual    'ABSENT from the blob store'
```

The store is **content-addressed**, so a tampered filing is a filing whose digest is not in it —
and that is reported as the fact it is, rather than raised as a traceback that would tell a reader
the tool broke instead of the artifact. **The signature stays valid**, because the envelope was not
touched: two different events, two different answers.

---

### 3. `E2E-TAMPER-ATTEST` reports `signature_valid` and `reproduced` as **two separate facts**

**MET.** Flip one byte inside `attestation.json`'s payload: `signature_valid: false` **and**
`reproduced: false`, on separate fields of `VerifyResult` and separate lines of the CLI's output.

**The signature is checked against the stored bytes BEFORE anything is re-run**, so a
re-derivation failure cannot change the answer about the key. And `verify` never re-signs — asserted
by AST over the module, which additionally requires that the signing primitive is not even
*imported*, because importing the key operations puts them one keystroke from being used.

---

### 4. The attestation validates against its JSON Schema with `additionalProperties: false` everywhere, the recursive walk finds no banned name at any depth, and the advisory scan's hits are fully allowlisted with arguments

**MET.**

| | |
|---|---:|
| property names walked, at every depth | **95** |
| blocking hits (`result`/`status`/`pass`/…, exact, case-insensitive) | **0** |
| advisory hits (substring) | **3** |
| allowlisted with a written argument | **3**, checked equal in **both** directions |
| object schemas with `additionalProperties: false` | **16 of 16** definitions |

The three advisory hits are `canariesPassed`, `antiCanariesPassed` and `antiCanariesNotPass`, and
every argument says the same thing in a different way: **the thing that passed is our instrument,
never the filing.** A run in which `canariesPassed` equals `canariesRun` is exactly a run in which
we have made no claim about the filing at all.

The `if`/`then` constraint branches are carved out of the `additionalProperties` requirement, and
the carve-out is asserted rather than assumed: an `additionalProperties: false` inside the INVALID
branch would forbid every property the branch does not mention, turning a constraint into a
redefinition and making every INVALID statement fail validation.

---

### 5. `test_contract__no_json_float_in_the_payload` green

**MET**, and the test had to be rewritten to be about the right thing. Its first version scanned
the canonicalised bytes with a number pattern and reported a float — from inside the string
`"cdfc.calc P3 + celpy 0.5.0"`. A version string is not a JSON number. It uses `json.loads`'s
`parse_float` hook now, which fires on an actual float token and on nothing else.

The schema is checked in the same test: **no property anywhere is typed `number`.** Money is an
`int64` count of 10⁻³ USD Million, tolerances are integers, rates are integer ppm.

---

### 6. `test_no_libreoffice_online`, `test_no_tlog` and `test_no_model_in_verdict_path` green

**MET.**

- **`libreoffice`** is absent from `tool_versions` deliberately: it is not on the verdict path, and
  pinning it would imply the verdict depended on it. Asserted over the schema's **property names**,
  not its text — the schema's own `description` explains the absence, and a substring scan its own
  explanation defeats is a check on the comments.
- **There is no keyless code path at all.** `--tlog-upload=false` is not a default here; the
  capability does not exist. A keyless signature would put *the fact and the timing of a named fund
  management entity running a pre-submission compliance check* into a permanent public transparency
  log — a disclosure about the filer, made by the tool they ran to be careful.
- **`test_no_model_in_verdict_path`** covers `cdfc.attest` along with the rest of the verdict path.

---

### 7. `project_oscal` **raises** on an `INVALID` run and writes nothing

**MET, and the substance is the absence of a flag.** `test_oscal__there_is_no_flag_to_emit_it_anyway`
asserts the signature is exactly `(statement, cells)` — if any parameter could make an `INVALID` run
project, the ruling would be a preference. A flag is what somebody sets when a pipeline is failing
and the deadline is Friday.

The RO-Crate deliberately **can** carry an `INVALID` run, and `docs/PROJECTION-LOSS.md` states why
the two differ: a crate is a container for evidence, and evidence that the instrument could not be
demonstrated is still evidence. The OSCAL refusal is about a form whose vocabulary cannot say *we
did not look* — not about `INVALID` being unmentionable.

**Declared loss, as a count: 2 of 8 item states are representable as findings.**

---

### 8. `docs/NON-DETERMINISM.md` lists **six** sources enumerated and six removed, each with its test and its injector

**MET**, and the count is asserted by a test rather than trusted.

The sixth — *durations we measured ourselves* — is the one worth remembering. `plan/01` §1.5 listed
four and was complete **until somebody measured something**: a duration sat inside the canonicalised
payload through six phases of review and would have failed `E2E-VERIFY` on the first green run of
this phase. **An enumeration that was complete until someone measured something is the standing
hazard here**, which is why the contract test is load-bearing and the grep is a pre-filter.

---

### 9. `test_contract__invalid_carries_a_null_not_an_absence` green, and `E2E-INVALID` asserts the property is **present**, is `null`, and that an omission **fails** validation

**MET, all three legs, at both levels.**

The schema expresses it as a **constraint on the value** and never as a prohibition on the property:

```jsonc
{ "if":   { "properties": { "runState": { "const": "INVALID" } }, "required": ["runState"] },
  "then": { "properties": { "settledFraction": { "const": null }, "verdict": { "const": null } },
            "required": ["settledFraction", "verdict"] } }
```

**Three documents had asserted three different things about one field in one state** — present-and-
null, forbidden, and omitted-is-a-violation — and P5 and P11 each passed their own contract test
while the integration would have produced an attestation that either failed validation or dropped
the `null` that `E2E-INVALID` exists to assert.

`E2E-INVALID` runs a **real** INVALID run (all 348 harvested candidates, of which 315 carry no
stored kill case) and checks all three legs on it.

**One thing this criterion nearly got wrong in the other direction.** An early version of the
end-to-end test asserted `scope.fieldSurface is None` on an INVALID run, reasoning that a run
declaring no coverage should declare nothing. That is wrong and the schema is right: **`scope` says
what the run LOOKED AT**, and 3,747 cells is true whether or not the instrument was demonstrated.
Suppressing a fact we have would be the mirror image of the defect the `null` exists to prevent.
What must be null is the **claim**.

---

### 10. `test_contract__no_duration_field_in_a_hashed_object` green, and `ci/no-clock-in-core.sh`'s pattern set contains `perf_counter`, `monotonic` and `process_time`

**MET**, and both were done at P10 with their arguments. The shell gate and its AST twin now police
the **same scope** as well as the same tokens — they disagreed the moment P10 wrote the module the
F23 ruling asked for, and a gate and its twin that disagree about scope are two rules with nobody
having chosen which is real.

---

## The recurrence worth naming

**Six times in this build, a check was defeated by prose describing the thing it checks for.** The
float scan read `0.5` out of `"celpy 0.5.0"`; the libreoffice check matched the schema's own
explanation of why libreoffice is absent; `no-clock-in-core` fired on a docstring writing
`datetime.now()` to warn against it; `no-bare-rate` read RFC 8032's `% _p` as a percentage; the
`uuid4` check found `uuid4` in the docstring explaining why `uuid4` must not be used; and the
non-determinism row count matched a row of the wrong table.

Every one had the same cure — **walk the structure, not the text** — and every one cost a cycle. The
durable answer is that a grep is a fast pre-filter and an AST walk is the rule, which is now the
arrangement for timings, clocks, identifiers and schema names. It is worth writing down because the
next one will look different and be the same.

## Mutation, per methodology §3.5

`attest/canon.py` and `attest/verify.py` are Tier **V** (`K/V ≥ 0.90`), `attest/statement.py` and
`attest/dsse.py` Tier **Q** (0.85), `attest/projections/` Tier **S** (0.70). **The mutation run has
not been performed**, and this phase does not claim it: `make mutation-pr` still prints that
mutation testing arrives with the code it measures. Recording the tier assignment without the run
is the honest half — a phase gate quoting a bare percentage would fail its own review, and a phase
gate quoting no number at all should say so.
