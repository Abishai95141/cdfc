"""P13-B0 — the model package. **EMPTY of client imports. Carries only the package marker.**

`src/cdfc/model/propose.py` does not exist and `ci/barrier5.sh` enforces its absence: E6's decision
record is `PENDING`, and a proposer may only ship on a `RETAIN`. This file exists so the ban has
something to be a ban *about* — `BANNED_IN_VERDICT` names `cdfc.model` as a single rule rather than
enumerating vendors, and a rule about a package nobody created is a rule nobody can test.
"""
