"""Parser for `ci/GATES.md`, the gate registry.

One parser, read by the CLI and by every contract test, so that a row added to the
registry is visible in `cdfc --version` without anyone remembering to update a constant.

Deliberately strict: a row that does not parse is an error, never a skipped row. A
tolerant parser over a registry is how a registry comes to have fewer rows than it
appears to — which is the same defect as a spreadsheet parser that silently sees 35
validations where there are 54.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GATES_MD = REPO_ROOT / "ci" / "GATES.md"

VALID_KINDS = frozenset({"grep", "ast", "pytest", "schema", "shell", "contract"})
VALID_LIVENESS = frozenset({"LIVE", "PENDING"})
# TWO PHASE SEQUENCES, and the registry's grammar predated the second one.
#
# `P0`-`P15` are the BUILD phases. `A0`-`A5` (with `A1c`) are the ANCHOR architecture phases of
# `docs/ARCHITECTURE-rules-and-evidence.md` §9 -- a different sequence, mapped in `docs/PLAN.md`
# §14. A gate whose subject first exists in the A-sequence had no expressible phase, and the
# alternative was to write the nearest P-number, which would be a false statement in the column
# that decides whether a gate can ever be observed red.
#
# **The widening does not weaken it.** Anything outside these two closed sequences is still
# refused, and `test_contract__registry_rejects_a_phase_outside_both_sequences` pins that.
# THREE numbering sequences, not the two CLAUDE.md §7 names. `P0`-`P15` are the build phases and
# `A0`-`A5` the ANCHOR architecture phases; `N1`-`N9` are the EXPERIMENTS in
# `docs/EXPERIMENT-PROGRAMME.md`, and a gate can be born from one. Gates 128-131 were: `N1`
# measured that a coordinate eId does not survive a resegmentation, and the division map is what
# that measurement produced. Labelling them `A4` would date them to a phase that has not started;
# labelling them `A3` would backdate them to one that had already closed. Argument in
# docs/GATE-CHANGES.md, 20 Aug 2026.
PHASE_RE = re.compile(r"^(?:P(?:[0-9]|1[0-5])|A(?:[0-5]|1c)|N[1-9])$")


class RegistryError(ValueError):
    """The registry is malformed. Never downgraded to a warning."""


@dataclass(frozen=True)
class Gate:
    id: int
    kind: str
    gate: str
    subject_exists_at: str
    demonstrable_red_at: str
    broken_build: str
    liveness: str


def _cells(line: str) -> list[str]:
    # a markdown row: | a | b | ... |
    parts = line.strip().strip("|").split("|")
    return [p.strip() for p in parts]


def parse(path: Path | None = None) -> list[Gate]:
    """Parse the registry. Raises RegistryError on any malformed row."""
    p = path or GATES_MD
    raw = p.read_bytes()
    if b"\x00" in raw:
        # A NUL makes grep skip the whole file, so the id-collision gate would run
        # green over the largest instance of the problem. Found once already.
        raise RegistryError(f"{p} contains a NUL byte")
    text = raw.decode("utf-8")

    gates: list[Gate] = []
    seen: set[int] = set()
    for lineno, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = _cells(s)
        if len(cells) != 7:
            continue
        if not re.fullmatch(r"\d+", cells[0]):
            continue  # header or separator row

        gid = int(cells[0])
        if gid in seen:
            raise RegistryError(f"{p}:{lineno}: duplicate gate id {gid}")
        seen.add(gid)

        kind, gate, subj, red, broken, live = cells[1:]
        if kind not in VALID_KINDS:
            raise RegistryError(f"{p}:{lineno}: gate {gid} has unknown kind {kind!r}")
        if live not in VALID_LIVENESS:
            raise RegistryError(f"{p}:{lineno}: gate {gid} has unknown liveness {live!r}")
        if not red or not PHASE_RE.match(red):
            # THERE IS NO PERMANENTLY-PENDING GATE. A gate that can never be observed
            # red is a preference wearing a gate's name.
            raise RegistryError(
                f"{p}:{lineno}: gate {gid} has no valid demonstrable_red_at (got {red!r})"
            )
        if not PHASE_RE.match(subj):
            raise RegistryError(f"{p}:{lineno}: gate {gid} has invalid subject_exists_at {subj!r}")
        if not broken:
            raise RegistryError(f"{p}:{lineno}: gate {gid} names no broken_build")

        gates.append(Gate(gid, kind, gate, subj, red, broken, live))

    if not gates:
        raise RegistryError(f"{p}: no gate rows parsed — a registry with no rows is not a registry")
    return gates


def live_ids(gates: list[Gate] | None = None) -> set[int]:
    return {g.id for g in (gates or parse()) if g.liveness == "LIVE"}


def pending_ids(gates: list[Gate] | None = None) -> set[int]:
    return {g.id for g in (gates or parse()) if g.liveness == "PENDING"}
