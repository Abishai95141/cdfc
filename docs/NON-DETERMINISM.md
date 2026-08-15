# `docs/NON-DETERMINISM.md` — six sources enumerated, six removed

**If it does not reproduce, it does not ship.** Byte identity is not a box to tick; it is a claim to
be broken, and the only honest way to hold it is to enumerate every way the same inputs could
produce different bytes and remove each one — with a test that goes red when it comes back.

**The standing hazard is the enumeration itself.** `plan/01` §1.5 listed four sources and was
complete until somebody measured something: `CanaryRow.elapsed_us` sat inside the canonicalised
payload through six phases of review, and `ci/no-clock-in-core.sh` greped `datetime.now()`,
`time.time()` and `TZ` but not `perf_counter`. **It would have failed `E2E-VERIFY` on the first
green run of P11.** That is why the *contract* test — *"no duration field in a hashed object"* — is
the load-bearing artifact and the grep is the fast pre-filter, and never the other way round.

---

## The six

| # | source | how it is removed | test | injector |
|---|---|---|---|---|
| **1** | **the mutable register** | `register_snapshot_sha256` is a manifest pin; the host function never resolves live at verdict time. In this build no snapshot is bound to a verdict, so the pin is `null` — *we make no claim* — rather than a digest of something nobody fetched | `test_nc__Q49_host_fn_never_resolves_live` | `HostFnResolvesLive` |
| **2** | **the wall clock** | every timestamp is an **input** recorded in the manifest. CEL binds no clock; `expires` is derived from `timeVerified` by `attest/policy.py`, which contains no clock call at all | `test_stmt__expires_reads_no_clock` · `test_prop__expires_is_a_function_of_time_verified` · `ci/no-clock-in-core.sh` | `WallClockInCore` |
| **3** | **iteration order** | RFC 8785 for every hash — **UTF-16 code-unit key order**, not Python's code-point order — plus explicit sort keys at every emission point. `run.jsonl` sorts by `(predicate_id, version, stable_key)`; `CanaryReport.digest()` sorts its rows; the adjudication record sorts by mutant id | `test_prop__canonicalisation_is_order_invariant` · `test_prop__the_loop_is_order_independent` · `test_canon__sorts_by_utf16_code_units_not_code_points` | `UnsortedRollup` |
| **4** | **floating point** | there is none. Money is an `int64` count of 10⁻³ USD Million, tolerances are integers, **rates are integer ppm**, and `canonical_json` **refuses** a float rather than formatting one | `test_contract__no_json_float_in_the_payload` · `test_canon__refuses_a_float` · `ci/no-float-money.sh` | `FloatInCalc` · `WilsonFloat` |
| **5** | **the probe seed** *(added by P9)* | the probe layer is a **search**, and a search with an unpinned seed makes the report irreproducible in exactly the way this phase must refuse. `probe_seed` is an input recorded in the manifest and replayed by `verify` | `test_det__probe_results_are_seed_stable` — **and its other half**, `test_det__probe_results_differ_under_a_different_seed`, because a seed that changes nothing is not doing anything and the first test would then be vacuously green | `ProbeSeedFromEntropy` |
| **6** | **durations we measured ourselves** *(added by the adversary pass, F23)* | no hashed object carries a duration, a timestamp or a `perf_counter`-derived value. Timings are written to `reports/perf/<run_id>.jsonl` — outside `run.jsonl`, outside the attestation, outside the report and outside `verify`'s comparison set | `test_contract__no_duration_field_in_a_hashed_object` · `test_contract__no_clock_is_reachable_from_the_selfcheck_package` · `test_tim__timings_are_written_outside_the_payload` | `ElapsedUsInCanaryRow` |

**Six enumerated. Six removed.** Each row names a test that goes red when the source returns, and
an injector that makes it do so — except where the removal is structural, in which case the test is
a walk over the code rather than a run of it.

---

## What byte identity has actually been demonstrated against

**This matters more than the count above**, because the claim P11 makes is about a *third party on
another machine*, and what a build can verify is bounded by what it can run.

| environment | verified | what it catches |
|---|---|---|
| the same tree, twice | **yes** | nothing much on its own; it is the floor |
| a **fresh clone** at the same commit | **yes** | dependence on the working tree, on uncommitted files, on gitignored output directories, on absolute paths. This has caught four real defects across P9–P11 |
| **a second machine / runner image** | **NOT VERIFIED IN THIS BUILD** | dependence on the interpreter build, on library minor versions, on locale, on filesystem ordering, on CPU word size |

**The third row is the one `plan/05` P11 exit criterion 1 asks for, and it is unmet.** Only one
machine is available here. Everything that can be checked from one machine has been:
`make determinism` varies `TZ`, `PYTHONHASHSEED`, `LC_ALL` and the working directory within it, and
the fresh clone varies the tree — but a second *image* varies things none of those touch, and
saying otherwise would be exactly the substitution this document exists to prevent.

`docs/measurements/P11-byte-identity.md` publishes the measured result with that boundary on its
face, and G-REPRO's criterion 1 is recorded **NOT MET — no second runner image available**, not
inferred from the clone.

---

## What is deliberately NOT pinned, and why

**`libreoffice` is absent from `tool_versions`** and that is not an oversight. It is not on the
verdict path: it computes the *independently-computed* fixture's derived cells, which is a corpus
generation step, and `test_no_libreoffice_online` asserts it never runs during a verdict. Pinning it
would imply the verdict depended on it, and a pin that implies a dependency nobody has is a
statement about the system that is false.

**`code_git_sha` pins the COMMIT and not the working tree.** A dirty tree re-derives under a
`code_git_sha` that does not describe the code that ran, so `cdfc verify` reports `tree_clean`
beside its two claims. A `reproduced: true` from a dirty tree is a weaker statement than the same
value from a clean one, and the caller is told which they have.
