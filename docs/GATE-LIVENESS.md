# docs/GATE-LIVENESS.md

**The measurement P0 produces, and what it deliberately does not count.**

Writing a gate is free. The quantity that carries information is how many gates have been **observed
failing on a deliberately broken build**. A gate that has never gone red is a preference with a filename.

Evidence comes from `reports/negative-control-sweep.json` under the **exact-set contract**: every
`flips: true` guard red under the injector, every `flips: false` guard green, and the tree clean again
afterwards. Never "at least one guard failed" — under that weaker rule an entry is caught the moment its
*weakest* guard goes red, and the guard the whole story rests on may never be exercised.

## Status at P0 — 15 of 15 live gates OBSERVED RED

- entries caught: **18 / 18**
- guards flipped: **19 / 19**
- provisional (excluded from caught): **1**
- entries with no injector: **1**

| gate | evidence | injector | the assertion that was observed red |
|---:|---|---|---|
| 1 | NC-CI03: OBSERVED RED | `DefeatGreenTickGate` | AssertionError: an all-clear reached a user surface and the gate reported success |
| 2 | NC-CI04: OBSERVED RED | `DefeatBareExceptGate` | ... |
| 3 | NC-CI01: OBSERVED RED | `DefeatBareExceptGate` | ... |
| 4 | NC-CI02: OBSERVED RED | `WarningsTolerated` | AssertionError: a UserWarning did not fail the run: filterwarnings = ['error'] is not in effect, which is the one line s |
| 5 | NC-CI10: OBSERVED RED | `UnpinDependency` | AssertionError: dependencies pinned by version but not by wheel hash: ['attrs==26.1.0'] |
| 6 | NC-CI06: OBSERVED RED | `DuplicateGateId` | reported failed |
| 7 | NC-CI08: OBSERVED RED | `BlankDemonstrableRed` | reported failed |
| 8 | NC-CI07: OBSERVED RED | `DemoteGateToPending` | AssertionError: the LIVE set changed without a dated argument |
| 9 | NC-CI05: OBSERVED RED | `WeakenCliTest` | AssertionError: cli.py was made to exit 0 for an unimplemented subcommand and the unit test still passed — the test does |
| 10 | NC-CI12: OBSERVED RED | `HardcodeCountAndAddRow` | Asserti... |
| 11 | NC-CI13: OBSERVED RED | `DenylistedRuntimeDep` | AssertionError: precondition: green on the real set |
| 12 | NC-CI14: OBSERVED RED | `NulByteInPlanDoc` | AssertionError: precondition: green on a clean corpus |
| 13 | NC-CI01: OBSERVED RED | `DefeatBareExceptGate` | ... |
| 17 | NC-CI15: OBSERVED RED | `ElapsedUsField` | AssertionError: precondition: green |
| 18 | NC-CI16: OBSERVED RED | `BreakCriticalPathTotal` | AssertionError: a displayed total does not equal its parts: [9.0, 8.0, 10.0, 17.0, 14.0, 12.0, 10.5, 16.0, 9.5, 6.0, 16. |

## The one entry that proves nothing yet, and says so

**NC-Q02** — *a predicate with no qualification record loads.* `load_or_refuse` refuses unconditionally
from P0 to P4, so its admission-side twin — a QUALIFIED predicate that DOES load — cannot exist until the
predicate schema does. It is reported PROVISIONAL, in its own column, and **excluded from
`entries_caught`**. A green entry with no information in it must not be counted as evidence.

## The three PENDING gates

14 (no model client reachable from the verdict path), 15 (the attestation schema cannot express a pass),
16 (the seven-term closure invariant). Their subjects do not exist until P5 and P11. Each names the phase
at which it becomes demonstrable; **there is no permanently-pending gate**, and
`test_contract__pending_rows_name_a_phase` fails the build if a row loses that field.
